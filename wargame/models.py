from django.db import models
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.contrib.auth.models import AbstractUser
from markdownx.models import MarkdownxField


class User(AbstractUser):
    def get_score(self):
        # TODO: qpa/hacktivity switch
        # SELECT SUM(challenge.points)
        # FROM user_challenge
        #   JOIN challenge ON(challenge.id = user_challenge.challenge_id)
        #   JOIN submission ON (submission.user_challenge_id = user_challenge.id)
        #   , meta_config
        # WHERE ((meta_config.is_qpa = '1' AND submission.value = challenge.flag_qpa)
        #       OR (meta_config.is_hacktivity = '1' AND submission.value = challenge.flag_hacktivity))
        #   AND user_challenge.user_id = {self.id}
        return UserChallenge.objects.filter(user=self, submission__value=F('challenge__flag_qpa')) \
            .only('challenge__points') \
            .aggregate(total_points=Coalesce(Sum('challenge__points'), 0))['total_points']


class File(models.Model):
    path = models.CharField(max_length=512)
    private = models.BooleanField(default=False)


class Tag(models.Model):
    name = models.CharField(max_length=64, primary_key=True)


class Challenge(models.Model):
    title = models.CharField(max_length=256)
    creation_dt = models.DateTimeField(auto_now_add=True)
    description = MarkdownxField()
    level = models.IntegerField()
    flag_qpa = models.CharField(max_length=256, null=True)
    flag_hacktivity = models.CharField(max_length=256, null=True)
    points = models.IntegerField()
    hint = models.CharField(max_length=8192, null=True)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title


class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    hint_used = models.BooleanField(default=False)

    class Meta:
        unique_together = (('user', 'challenge'),)


class Submission(models.Model):
    creation_dt = models.DateTimeField(auto_now_add=True)
    value = models.CharField(max_length=256)
    user_challenge = models.ForeignKey(UserChallenge, on_delete=models.CASCADE)
