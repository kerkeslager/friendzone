from django.test import TestCase, TransactionTestCase

from . import models

class UserTests(TransactionTestCase):
    def test_create_user_creates_default_circles(self):
        user = models.User.objects.create_user(
            username='testuser',
            password='12345',
        )

        self.assertEqual(user.circles.all().count(), 2)
        self.assertEqual(user.circles.filter(name='Family').count(), 1)
        self.assertEqual(user.circles.filter(name='Friends').count(), 1)

    def test_user_create_invitation_sets_owner_and_circles(self):
        inviting_user = models.User.objects.create_user(
            username='testuser',
            password='12345',
        )

        invitation = inviting_user.create_invitation(
            circles=inviting_user.circles.all(),
        )

        for circle in inviting_user.circles.all():
            self.assertIn(circle, invitation.circles.all())


    def test_user_create_invitation_requires_at_least_one_circle(self):
        inviting_user = models.User.objects.create_user(
            username='testuser',
            password='12345',
        )

        with self.assertRaises(Exception):
            inviting_user.create_invitation(
                circles=inviting_user.circles.filter(
                    name='nonexistent circle name',
                )
            )

    def test_cannot_invite_to_circle_not_owned(self):
        inviting_user = models.User.objects.create_user(
            username='inviting_user',
            password='12345',
        )
        other_user = models.User.objects.create_user(
            username='other_user',
            password='12345',
        )

        with self.assertRaises(Exception):
            inviting_user.create_invitation(
                circles=other_user.circles.all(),
            )

    def test_accepting_invitation_creates_connection(self):
        inviting_user = models.User.objects.create_user(
            username='inviting_user',
            password='12345',
        )
        accepting_user = models.User.objects.create_user(
            username='accepting_user',
            password='12345',
        )

        invitation = inviting_user.create_invitation(
            circles=inviting_user.circles.filter(name='Friends'),
        )

        accepting_user.accept_invitation(
            invitation,
            circles=accepting_user.circles.filter(name='Family'),
        )

        self.assertEqual(
            models.Connection.objects.filter(
                inviting_user=inviting_user,
                accepting_user=accepting_user,
            ).count(),
            1,
        )

    def test_accepting_into_no_circles_throws_exception(self):
        inviting_user = models.User.objects.create_user(
            username='inviting_user',
            password='12345',
        )
        accepting_user = models.User.objects.create_user(
            username='accepting_user',
            password='12345',
        )

        invitation = inviting_user.create_invitation(
            circles=inviting_user.circles.filter(name='Friends'),
        )

        with self.assertRaises(Exception):
            accepting_user.accept_invitation(
                invitation,
                circles=accepting_user.circles.filter(name='nonexistent name'),
            )

    def test_accepting_into_circles_you_do_not_own_throws_exception(self):
        inviting_user = models.User.objects.create_user(
            username='inviting_user',
            password='12345',
        )
        accepting_user = models.User.objects.create_user(
            username='accepting_user',
            password='12345',
        )
        other_user = models.User.objects.create_user(
            username='other_user',
            password='12345',
        )

        invitation = inviting_user.create_invitation(
            circles=inviting_user.circles.filter(name='Friends'),
        )

        with self.assertRaises(Exception):
            accepting_user.accept_invitation(
                invitation,
                circles=other_user.circles.all(),
            )


    def test_accepting_invitation_adds_user_to_circles(self):
        inviting_user = models.User.objects.create_user(
            username='inviting_user',
            password='12345',
        )
        accepting_user = models.User.objects.create_user(
            username='accepting_user',
            password='12345',
        )

        invitation = inviting_user.create_invitation(
            circles=inviting_user.circles.filter(name='Friends'),
        )

        accepting_user.accept_invitation(
            invitation,
            circles=accepting_user.circles.filter(name='Family'),
        )

        self.assertIn(
            accepting_user,
            inviting_user.circles.get(name='Friends').members.all(),
        )

        self.assertIn(
            inviting_user,
            accepting_user.circles.get(name='Family').members.all(),
        )
