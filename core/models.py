import uuid

from django.conf import settings
from django.db import models, transaction
from django.urls import reverse
import django.contrib.auth.models as auth_models

class ConnectionLimitException(Exception):
    pass

class AlreadyConnectedException(Exception):
    pass

class User(auth_models.AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.display_name

    def save(self, **kwargs):
        create_default_circles = self._state.adding

        result = super().save(**kwargs)

        if create_default_circles:
            for name in ['Friends', 'Family']:
                circle = Circle(owner=self, name=name)
                circle.save()

        return result

    @property
    def display_name(self):
        return self.name or self.username

    @property
    def feed(self):
        connection_pks = Connection.objects.filter(other_user=self)

        circle_membership_pks = CircleMembership.objects.filter(
            connection__pk__in=connection_pks,
        ).values_list('pk', flat=True)

        post_pks = PostUser.objects.filter(
            circle_membership__pk__in=circle_membership_pks,
        ).values_list('post_circle__post__pk', flat=True)

        return self.posts.union(
            Post.objects.filter(pk__in=post_pks),
        ).order_by('-created_utc')

    def is_connected_with(self, other_user):
        return self.connections.filter(
            other_user=other_user,
        ).exists()

    @property
    def connected_users(self):
        return User.objects.filter(
            pk__in=Connection.objects.filter(
                owner=self,
            ).values_list('other_user', flat=True),
        )

    @transaction.atomic
    def create_invitation(self, *, circles):
        circles_count = circles.count()

        if circles_count == 0:
            raise Exception('Invitation must have at least one circle')

        if circles_count != circles.filter(owner=self).count():
            raise Exception('Cannot invite to circle you do not own')

        if self.connections.count() >= settings.MAX_CONNECTIONS_PER_USER:
            raise ConnectionLimitException('Connection limit reached')

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

        if self.is_connected_with(invitation.owner):
            raise AlreadyConnectedException('You are already connected')

        connection = Connection.objects.create(
            owner=invitation.owner,
            other_user=self,
        )

        for circle in invitation.circles.all():
            CircleMembership.objects.create(
                circle=circle,
                connection=connection,
            )

        for circle in circles:
            CircleMembership.objects.create(
                circle=circle,
                connection=connection.opposite,
            )


class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    name = models.CharField(max_length=256)
    message = models.CharField(max_length=1024)
    circles = models.ManyToManyField(
        'Circle',
        related_name='+',
    )

    def get_absolute_url(self):
        return reverse('invite_detail', args=[str(self.pk)])

class Connection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_utc = models.DateTimeField(auto_now_add=True)
    opposite = models.ForeignKey(
        'Connection',
        on_delete=models.CASCADE,
        null=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='connections',
    )
    other_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='+',
    )

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.opposite is None:
            assert self._state.adding
            create_opposite = True
        else:
            create_opposite = False

        if self._state.adding:
            if self.owner.connections.count() >= settings.MAX_CONNECTIONS_PER_USER:
                raise ConnectionLimitException()

        result = super().save(*args, **kwargs)

        if create_opposite:
            opposite = Connection(
                opposite=self,
                owner=self.other_user,
                other_user=self.owner,
            )
            opposite.save()
            self.opposite = opposite
            self.save()

        return result


class UserConnection(models.Model):
    # This exists so that if Connection is deleted, UserConnection is deleted
    connection = models.ForeignKey(
        'Connection',
        on_delete=models.CASCADE,
        related_name='+',
    )
    owner = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='+',
    )
    connected_user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='+',
    )

class Circle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    color = models.CharField(max_length=6)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='circles'
    )
    connections = models.ManyToManyField(
        'Connection',
        through='CircleMembership',
        through_fields=('circle', 'connection'),
    )

    class Meta:
        unique_together = (('name', 'owner'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('circle_detail', args=[str(self.pk)])

    @property
    def members(self):
        return User.objects.filter(
            pk__in=self.connections.all().values_list('other_user', flat=True),
        )

class CircleMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    circle = models.ForeignKey(
        'Circle',
        on_delete=models.CASCADE,
        related_name='circle_memberships',
    )
    connection = models.ForeignKey(
        'Connection',
        on_delete=models.CASCADE,
        related_name='circle_memberships',
    )

    class Meta:
        unique_together = (('circle', 'connection'),)

    def save(self, *args, **kwargs):
        assert self.circle.owner == self.connection.owner
        return super().save(*args, **kwargs)

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_utc = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    text = models.CharField(max_length=1024)
    circles = models.ManyToManyField(
        'Circle',
        through='PostCircle',
        through_fields=('post', 'circle'),
    )

    def publish(self, *, circles):
        for circle in circles:
            PostCircle.objects.create(circle=circle, post=self)

class PostCircle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    circle = models.ForeignKey(
        'Circle',
        on_delete=models.CASCADE,
        related_name='+',
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='+',
    )

    class Meta:
        unique_together = (('circle', 'post'),)

    def save(self, *args, **kwargs):
        link_to_users = self._state.adding

        result = super().save(*args, **kwargs)

        if link_to_users:
            for circle_membership in CircleMembership.objects.filter(circle=self.circle):
                PostUser.objects.create(
                    post_circle=self,
                    circle_membership=circle_membership,
                )

        return result


class PostUser(models.Model):
    post_circle = models.ForeignKey(
        'PostCircle',
        on_delete=models.CASCADE,
        related_name='+',
    )
    circle_membership = models.ForeignKey(
        'CircleMembership',
        on_delete=models.CASCADE,
        related_name='+',
    )
