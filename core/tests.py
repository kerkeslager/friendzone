from django.test import TestCase, TransactionTestCase

from . import models

class UserTests(TransactionTestCase):
    def test_create_user_creates_default_circles(self):
        inviting_user = models.User.objects.create_user(
            username='testuser',
            password='12345',
        )

        self.assertEqual(inviting_user.circles.all().count(), 2)
        self.assertEqual(inviting_user.circles.filter(name='Family').count(), 1)
        self.assertEqual(inviting_user.circles.filter(name='Friends').count(), 1)
