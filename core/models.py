from django.conf import settings
from django.db import models, transaction
import django.contrib.auth.models as auth_models

class UserManager(auth_models.UserManager):
    @transaction.atomic
    def create_user(self, *args, **kwargs):
        user = super().create_user(*args, **kwargs)

        for name in ['Friends', 'Family']:
            circle = Circle(owner=user, name=name)
            circle.save()

        return user

class User(auth_models.AbstractUser):
    objects = UserManager()

    name = models.CharField(max_length=256)

    @transaction.atomic
    def create_invitation(self, *, circles):
        if len(circles) == 0:
            raise Exception('Invitation must have at least one circle')

        invitation = Invitation.objects.create(owner=self)
        invitation.circles.set(circles)
        return invitation

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
