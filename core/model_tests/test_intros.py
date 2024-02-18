from django.test import tag, TransactionTestCase

from .. import models

class IntroTests(TransactionTestCase):
    def test_creating_intro_creates_opposite(self):
        sender = models.User.objects.create_user(
            username='user0',
            password='password',
        )
        receiver = models.User.objects.create_user(
            username='user1',
            password='password',
        )
        introduced = models.User.objects.create_user(
            username='user2',
            password='password',
        )

        intro = models.Intro(
            sender=sender,
            receiver=receiver,
            introduced=introduced,
        )
        intro.save()

        self.assertEqual(
            intro.opposite.sender,
            sender,
        )
        self.assertEqual(
            intro.opposite.receiver,
            introduced,
        )
        self.assertEqual(
            intro.opposite.introduced,
            receiver,
        )
