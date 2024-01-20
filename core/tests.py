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
