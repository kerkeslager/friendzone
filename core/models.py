from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    name = models.CharField(max_length=256)

class Invitation(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    circles = models.ManyToManyField(
        'Circle',
        related_name='+',
    )

class Connection(models.Model):
    inviting_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='+'
    )
    accepting_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='+'
    )

    circles_owned_by_inviting_user = models.ManyToManyField(
        'Circle',
        related_name='+',
    )
    circles_owned_by_accepting_user = models.ManyToManyField(
        'Circle',
        related_name='+',
    )

class Circle(models.Model):
    name = models.CharField(max_length=64)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='circles'
    )
