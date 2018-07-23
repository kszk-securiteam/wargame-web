import os

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Sum
from django.db.models.expressions import ExpressionWrapper
from django.db.models.fields import IntegerField
from django.db.models.functions import Coalesce
from django.dispatch import receiver
from markdownx.models import MarkdownxField


class User(AbstractUser):
    def get_score(self):
        # SELECT SUM(challenge.points)
        # FROM user_challenge
        #   JOIN challenge ON(challenge.id = user_challenge.challenge_id)
        #   JOIN submission ON (submission.user_challenge_id = user_challenge.id)
        #   , meta_config
        # WHERE ((meta_config.is_qpa = '1' AND submission.value = challenge.flag_qpa)
        #       OR (meta_config.is_hacktivity = '1' AND submission.value = challenge.flag_hacktivity))
        #   AND user_challenge.user_id = {self.id}

        # noinspection PyUnreachableCode
        if True:  # TODO: QPA/Hacktivity switch
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
        # noinspection PyUnreachableCode
        if True:  # TODO: QPA/Hacktivity switch
            flag_field = F('userchallenge__challenge__flag_qpa')
        else:
            flag_field = F('userchallenge__challenge__flag_hacktivity')

        challenge_points = F('userchallenge__challenge__points')
        hint_used = F('userchallenge__hint_used')
        user_points = ExpressionWrapper(challenge_points - (hint_used * challenge_points * 0.5),
                                        output_field=IntegerField())

        return User.objects.filter(
            userchallenge__submission__value=flag_field
        ).values(
            'username'
        ).annotate(
            total_points=Coalesce(Sum(user_points), 0)
        ).order_by('-total_points')[:40]


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

    def __str__(self):
        return self.title

    def get_flag(self):
        # TODO: QPA-Hacktivity switch
        return self.flag_qpa


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
        return self.submission_set.filter(value=self.challenge.get_flag()).count() == 1


class Submission(models.Model):
    creation_dt = models.DateTimeField(auto_now_add=True)
    value = models.CharField(max_length=256)
    user_challenge = models.ForeignKey(UserChallenge, on_delete=models.CASCADE)


class StaffMember(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name
