from django.db import models
from django.contrib.auth.models import User

import uuid
import os

from .utils import crop_square


def avatar_upload_path(instance, filename):

    ext = filename.split('.')[-1]

    filename = f"{uuid.uuid4()}.{ext}"

    return os.path.join('avatars', filename)


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        null=True,
        blank=True
    )

    email = models.EmailField(unique=True)

    nickname = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if self.avatar:
            crop_square(self.avatar.path)


class Tag(models.Model):

    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name


class Question(models.Model):

    title = models.CharField(max_length=50)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    body = models.TextField()

    rating = models.IntegerField(default=0)

    tags = models.ManyToManyField(Tag)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    correct_answer = models.ForeignKey(
        'Answer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='correct_for'
    )

    def __str__(self):
        return self.title


class QuestionReaction(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='reactions'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    positive = models.BooleanField(default=True)

    class Meta:
        unique_together = ('question', 'user')

    def __str__(self):

        return (
            "Reaction for "
            + self.question.title
            + " by "
            + self.user.username
        )


class Answer(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    body = models.TextField()

    rating = models.IntegerField(default=0)

    def __str__(self):

        return (
            "Answer for "
            + self.question.title
            + " by "
            + self.user.username
        )


class AnswerReaction(models.Model):

    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='reactions'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    positive = models.BooleanField(default=True)

    class Meta:
        unique_together = ('answer', 'user')