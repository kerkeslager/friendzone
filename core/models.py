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
        circles_count = circles.count()

        if circles_count == 0:
            raise Exception('Invitation must have at least one circle')

        if circles_count != circles.filter(owner=self).count():
            raise Exception('Cannot invite to circle you do not own')

        invitation = Invitation.objects.create(owner=self)

        invitation.circles.set(circles)
        return invitation

    @transaction.atomic
    def accept_invitation(self, invitation, *, circles):
        circles_count = circles.count()

        if circles_count == 0:
            raise Exception('Must accept into at least one circle')

        if circles_count != circles.filter(owner=self).count():
            raise Exception('Cannot cannot accept into circle you do not own')

        connection = Connection.objects.create(
            inviting_user=invitation.owner,
            accepting_user=self,
        )

        for circle in invitation.circles.all():
            connection.circles.add(circle)
        for circle in circles.all():
            connection.circles.add(circle)

        connection.save()

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
    created_utc = models.DateTimeField(auto_now_add=True)
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
    circles = models.ManyToManyField(
        'Circle',
        related_name='connections',
    )

class Circle(models.Model):
    name = models.CharField(max_length=64)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='circles'
    )

    @property
    def members(self):
        return User.objects.filter(
            pk__in=self.connections.filter(
                accepting_user=self.owner,
            ).values_list(
                'inviting_user',
                flat=True,
            ).union(
                self.connections.filter(
                    inviting_user=self.owner,
                ).values_list(
                    'accepting_user',
                    flat=True,
                )
            )
        )

class Message(models.Model):
    connection = models.ForeignKey(
        'Connection',
        on_delete=models.CASCADE,
        related_name='messages',
    )
    from_user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='messages',
    )
    created_utc = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    text = models.CharField(max_length=1024)

class Post(models.Model):
    circle = models.ForeignKey(
        'Circle',
        on_delete=models.CASCADE,
        related_name='posts',
    )
    created_utc = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=1024)
