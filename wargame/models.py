import os

from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.auth.validators import UnicodeUsernameValidator, ASCIIUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Sum, Max
from django.db.models.expressions import ExpressionWrapper
from django.db.models.fields import IntegerField
from django.db.models.functions import Coalesce
from django.dispatch import receiver
from markdownx.models import MarkdownxField
import wargame_web.settings.base as settings

from wargame_admin.models import Config


def custom_username_validator(username):
    message = "Enter a valid username. This value may contain only letters, numbers, and @/+/-/_ characters."
    if '~' in username or '/' in username or '.' in username:
        raise ValidationError(message)
    return UnicodeUsernameValidator(message=message).__call__(username)


class User(AbstractUser):
    hidden = models.BooleanField(default=False)

    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/+/-/_ only.',
        validators=[custom_username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )

    def admin_str(self):
        if self.is_superuser:
            return "Admin"
        return "Not admin"

    def hidden_str(self):
        if self.hidden:
            return "Hidden from scoreboard"
        return "Visible on scoreboard"

    def active_str(self):
        if self.is_active:
            return "Active"
        return "Not active"

    def get_score(self):
        # SELECT SUM(challenge.points)
        # FROM user_challenge
        #   JOIN challenge ON(challenge.id = user_challenge.challenge_id)
        #   JOIN submission ON (submission.user_challenge_id = user_challenge.id)
        #   , meta_config
        # WHERE ((meta_config.is_qpa = '1' AND submission.value = challenge.flag_qpa)
        #       OR (meta_config.is_hacktivity = '1' AND submission.value = challenge.flag_hacktivity))
        #   AND user_challenge.user_id = {self.id}

        if Config.objects.get(key='qpa_hack').value == 'qpa':
            flag_field = F('challenge__flag_qpa')
        else:
            flag_field = F('challenge__flag_hacktivity')

        challenge_points = F('challenge__points')
        hint_used = F('hint_used')
        user_points = ExpressionWrapper(challenge_points - (hint_used * challenge_points * 0.5),
                                        output_field=IntegerField())

        return UserChallenge.objects.filter(
            user=self,
            submission__value=flag_field
        ).annotate(
            points_with_hint=user_points
        ).aggregate(
            total_points=Coalesce(Sum('points_with_hint'), 0)
        ).get('total_points')

    @staticmethod
    def get_top_40_by_score():
        if Config.objects.is_qpa():
            flag_field = F('userchallenge__challenge__flag_qpa')
        else:
            flag_field = F('userchallenge__challenge__flag_hacktivity')

        challenge_points = F('userchallenge__challenge__points')
        hint_used = F('userchallenge__hint_used')
        user_points = ExpressionWrapper(challenge_points - (hint_used * challenge_points * 0.5),
                                        output_field=IntegerField())

        return User.objects.filter(
            userchallenge__submission__value=flag_field,
            hidden=False
        ).values(
            'username'
        ).annotate(
            total_points=Coalesce(Sum(user_points), 0)
        ).order_by('-total_points')[:40]

    def get_visible_level(self):
        if Config.objects.is_qpa():
            flag_field = F('challenge__flag_qpa')
        else:
            flag_field = F('challenge__flag_hacktivity')

        user_max_level = self.userchallenge_set.all().aggregate(max_level=Coalesce(Max('challenge__level'), 1))[
            'max_level']
        solved_challenges_at_max_level = UserChallenge.objects.filter(challenge__level=user_max_level,
                                                                      user=self,
                                                                      submission__value=flag_field
                                                                      ).count()

        if solved_challenges_at_max_level >= Config.objects.stage_tasks():
            user_max_level += 1

        return user_max_level

    def get_visible_challenges(self):
        return self.get_challenges_for_level(self.get_visible_level())

    def get_challenges_for_level(self, level):
        query = """SELECT challenge.*, submission.value IS NOT NULL AS solved
                   FROM wargame_challenge challenge
                   LEFT JOIN wargame_userchallenge userchallenge ON challenge.id = userchallenge.challenge_id AND userchallenge.user_id == %s
                   LEFT JOIN wargame_submission submission ON userchallenge.id = submission.user_challenge_id AND submission.value == challenge.flag_qpa
                   WHERE challenge.level <= %s
                   ORDER BY level, title"""
        return Challenge.objects.raw(query, [self.id, level])

    def is_challenge_visible(self, challenge):
        return challenge.level <= self.get_visible_level()


@receiver(models.signals.post_save, sender=User)
def generate_vpn_key(sender, instance, created, *args, **kwargs):
    if created and not settings.DEBUG:
        os.system(F"sudo getcert.sh '{instance.username}'")


class Tag(models.Model):
    name = models.CharField(max_length=64, primary_key=True)


class Challenge(models.Model):
    title = models.CharField(max_length=256)
    creation_dt = models.DateTimeField(auto_now_add=True)
    description = MarkdownxField()
    short_description = models.CharField(max_length=512, default="")
    level = models.IntegerField()
    flag_qpa = models.CharField(max_length=256, null=True, verbose_name='Flag (QPA)')
    flag_hacktivity = models.CharField(max_length=256, null=True, verbose_name='Flag (Hacktivity)')
    points = models.IntegerField()
    hint = models.CharField(max_length=8192, null=True)
    tags = models.ManyToManyField(Tag)
    solution = models.CharField(max_length=8192, null=True)
    setup = models.CharField(max_length=8192, null=True)
    import_name = models.CharField(max_length=64, null=True)

    def __str__(self):
        return self.title

    def get_flag(self):
        if Config.objects.is_qpa():
            return self.flag_qpa
        else:
            return self.flag_hacktivity


class File(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='challenge-files/')
    display_name = models.CharField(max_length=256)
    private = models.BooleanField(default=False)


# Deletes file from filesystem when File object is deleted.
@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    hint_used = models.BooleanField(default=False)

    class Meta:
        unique_together = (('user', 'challenge'),)

    @staticmethod
    def get_or_create(user, challenge):
        try:
            ret = UserChallenge.objects.get(user=user, challenge=challenge)
        except UserChallenge.DoesNotExist:
            ret = UserChallenge()
            ret.user = user
            ret.challenge = challenge
            ret.save()

        return ret

    def solved(self):
        return self.submission_set.filter(value__iexact=self.challenge.get_flag()).exists()


class Submission(models.Model):
    creation_dt = models.DateTimeField(auto_now_add=True)
    value = models.CharField(max_length=256)
    user_challenge = models.ForeignKey(UserChallenge, on_delete=models.CASCADE)


class StaffMember(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name
