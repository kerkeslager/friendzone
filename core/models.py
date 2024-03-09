from datetime import timedelta
import uuid
import zoneinfo

from django.conf import settings
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
import django.contrib.auth.models as auth_models

from . import images, validators

TIMEZONE_CHOICES = [
    ('', '(default)'),
] + [
    (tz, tz) for tz in sorted(zoneinfo.available_timezones())
]

class ConnectionLimitException(Exception):
    pass

class AlreadyConnectedException(Exception):
    pass

class User(auth_models.AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Profile Fields
    name = models.CharField(
        help_text='If blank, defaults to your username.',
        max_length=256,
    )

    avatar = models.ImageField(
        null=True,
        blank=True,
        height_field='avatar_height',
        width_field='avatar_width',
    )
    avatar_height = models.PositiveIntegerField(default=0)
    avatar_width = models.PositiveIntegerField(default=0)

    # Settings Fields
    timezone = models.CharField(
        default='',
        blank=True,
        max_length=64,
        choices=TIMEZONE_CHOICES,
        help_text='The timezone to display dates in.',
    )
    allow_js = models.BooleanField(default=True)
    foreground_color = models.CharField(
        blank=True,
        max_length=16,
        validators=[validators.validate_color],
    )
    background_color = models.CharField(
        blank=True,
        max_length=16,
        validators=[validators.validate_color],
    )
    error_color = models.CharField(
        blank=True,
        max_length=16,
        validators=[validators.validate_color],
    )

    def __str__(self):
        return self.display_name

    def save(self, **kwargs):
        create_default_circles = self._state.adding

        result = super().save(**kwargs)

        if create_default_circles:
            Circle.objects.create(owner=self, color='#008800', name='Family')
            Circle.objects.create(owner=self, color='#000088', name='Friends')

        return result

    def get_absolute_url(self):
        return reverse('user_detail', args=[str(self.pk)])

    @property
    def display_name(self):
        return self.name or self.username

    @property
    def avatar_crop(self):
        # TODO Allow users to set the crop values

        x0 = 0
        x1 = self.avatar_width
        y0 = 0
        y1 = self.avatar_height

        if self.avatar_height > self.avatar_width:
            y0 = (self.avatar_height - self.avatar_width) // 2
            y1 = (self.avatar_height + self.avatar_width) // 2

        elif self.avatar_width > self.avatar_height:
            x0 = (self.avatar_width - self.avatar_height) // 2
            x1 = (self.avatar_width + self.avatar_height) // 2

        return images.ImageCrop(
            image_width=self.avatar_width,
            image_height=self.avatar_height,
            x0=x0,
            x1=x1,
            y0=y0,
            y1=y1,
        )

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

    def feed_for_user(self, user):
        if self == user:
            return self.posts.all()

        connection_pks = Connection.objects.filter(
            owner=user,
            other_user=self,
        )

        circle_membership_pks = CircleMembership.objects.filter(
            connection__pk__in=connection_pks,
        ).values_list('pk', flat=True)

        post_pks = PostUser.objects.filter(
            circle_membership__pk__in=circle_membership_pks,
        ).values_list('post_circle__post__pk', flat=True)

        return Post.objects.filter(pk__in=post_pks)

    @property
    def open_intros(self):
        connected_users = self.connections.values_list(
            'other_user',
            flat=True,
        )

        # Filter out intros to users you're already conneted with. We shouldn't
        # need to filter on is_accepted because accepted intros will be
        # deleted.
        return self.intros.exclude(
            pk__in=connected_users,
        )

    @property
    def connected_users(self):
        return User.objects.filter(
            pk__in=self.connections.values_list(
                'other_user',
                flat=True,
            ),
        )

    def is_connected_with(self, other_user):
        return self.connections.filter(
            other_user=other_user,
        ).exists()

    def send_message_to(self, other_user, *, text:str):
        return Message.objects.create(
            connection=self.connections.get(other_user=other_user),
            text=text,
        )

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

        if not invitation.is_open and invitation.is_expired():
            raise Exception('The invitation has expired.')

        if not invitation.is_open and invitation.is_expired():
            raise Exception('The invitation has expired.')

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

        if not invitation.is_open:
            invitation.delete()


class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    created_utc = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=256)
    message = models.CharField(max_length=1024)
    circles = models.ManyToManyField(
        'Circle',
        related_name='+',
    )
    DEFAULT_EXPIRATION = timedelta(days=7)

    is_open = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        if not self.is_open and self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def expires_at(self):
        return self.created_utc + settings.INVITE_LIFESPAN

    def is_expired(self):
        if self.is_open:
            return False

        return timezone.now() > self.expires_at

    @property
    def type(self):
        """Return the type of the invitation for convenience."""
        return "Open" if self.is_open else "Personal"

    def __str__(self):
        return f"{self.name} from {self.owner.display_name}"

    def get_absolute_url(self):
        return reverse('invite_detail', args=[str(self.pk)])

class Intro(models.Model):
    '''
    An Intro is created by `owner` and sent to ONE user, `receiver`.
    Introes are sent two at a time, one for each user being introduced to
    the other; the second Intro is created by the save method of the first.
    This means each user being introduced to the other has their own Intro;
    you DO NOT need to query against both sides if finding Intros for a user.

    Put another way, DO NOT write queries like:

    ```
    Intro.objects.filter(Q(receiver=user) | Q(other_user=user))
    ```

    This is not correct, THIS IS WRONG, as it will return Intros not directed
    at `user`. ONLY list intros directed at a user through through
    `user.intros`.
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='+',
        help_text='The user who is introducing the other two.',
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='intros',
        help_text='The user the intro is sent to, who can accept the intro.',
    )
    introduced = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='+',
        help_text='The user the receiving user is being introduced to.',
    )
    opposite = models.OneToOneField(
        'Intro',
        on_delete=models.CASCADE,
        null=True,
        help_text=(
            'The corresponding Intro which was sent to indroduced user; '
            'ensures that deleting one intro deletes the other.'
        ),
    )
    is_accepted = models.BooleanField(default=False)

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.opposite is None:
            assert self._state.adding
            create_opposite = True
        else:
            create_opposite = False

        result = super().save(*args, **kwargs)

        if self.is_accepted and self.opposite and self.opposite.is_accepted:
            connection = Connection.objects.create(
                owner=self.receiver,
                other_user=self.introduced,
            )

        if create_opposite:
            opposite = Intro(
                opposite=self,
                sender=self.sender,
                receiver=self.introduced,
                introduced=self.receiver,
            )
            opposite.save()
            self.opposite = opposite
            self.save()

        return result

class Connection(models.Model):
    '''
    Every connection has an opposite connection, which is created on save.
    This means that if Alice and Bob are connected, Alice has a connection with
    other_user=Bob, and Bob has a connection with other_user=Alice. This is so
    that you user.connections contains ALL the user's connections. You DO NOT
    need to query Connections from both sides to get all the connections for
    a user--if you do that you'll get the connection AND its opposite.

    To reiterate in another way DO NOT write queries like:

    ```
    Connection.objects.filter(Q(owner=user) | Q(other_user=user))
    ```

    The above query is slow and IS WRONG.
    '''

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_utc = models.DateTimeField(auto_now_add=True)
    opposite = models.OneToOneField(
        'Connection',
        on_delete=models.CASCADE,
        null=True,
        help_text=(
            'The corresponding Connection which belongs to the other user. '
            'This is to ensure that if the owner disconnects from the other '
            'user, the other user also disconnects from the owner.'
        )
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
    circles = models.ManyToManyField(
        'Circle',
        through='CircleMembership',
        through_fields=('connection', 'circle'),
    )

    class Meta:
        unique_together = (('owner', 'other_user'),)

    def __repr__(self):
        return "<Connection: {}'s connection with {}>".format(
            self.owner.display_name,
            self.other_user.display_name,
        )

    @property
    def incoming_messages(self):
        return self.opposite.outgoing_messages.all()

    @property
    def messages(self):
        return self.outgoing_messages.all().union(
            self.incoming_messages.all()
        ).order_by('-created_utc')

    @property
    def unread_message_count(self):
        return self.incoming_messages.filter(is_read=False).count()

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.opposite is None:
            assert self._state.adding
            create_opposite = True
        else:
            create_opposite = False

        existing_connection_count = self.owner.connections.count()
        if self._state.adding:
            if existing_connection_count >= settings.MAX_CONNECTIONS_PER_USER:
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
    color = models.CharField(
        max_length=16,
        validators=[validators.validate_color],
    )
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

    def __repr__(self):
        return "<Circle: {}'s {} circle>".format(
            self.owner.display_name,
            self.name,
        )

    def get_absolute_url(self):
        return reverse('circle_detail', args=[str(self.pk)])

    @property
    def members(self):
        return User.objects.filter(
            pk__in=self.connections.all().values_list('other_user', flat=True),
        )

    @property
    def posts(self):
        return Post.objects.filter(
            pk__in=PostCircle.objects.filter(circle=self).values_list(
                'post',
                flat=True,
            ),
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

    def __repr__(self):
        return "<CircleMembership: {} is a member of {}>".format(
            self.connection.other_user.display_name,
            repr(self.circle),
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
        related_name='outgoing_messages',
    )
    created_utc = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    text = models.CharField(max_length=1024)

    @property
    def from_user(self):
        return self.connection.owner

    @property
    def to_user(self):
        return self.connection.other_user
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
        related_name='+',
    )
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    def clean(self):
        # Ensure that a post has either text, an image, TODO
        if not self.text and not self.image:
            raise ValidationError('A post must have either text or an image.')

    def publish(self, *, circles):
        for circle in circles:
            PostCircle.objects.get_or_create(circle=circle, post=self)

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.pk)])

    def __str__(self):
        return f"Post by {self.owner.display_name}"

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
            for circle_membership in self.circle.circle_memberships.all():
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
