from django.test import tag, TransactionTestCase

from .. import models

class IntroTests(TransactionTestCase):
    def test_creating_intro_creates_opposite(self):
        sender = models.User.objects.create_user(
            username='user0',
            password='password',
        )
        introed_user = models.User.objects.create_user(
            username='user1',
            password='password',
        )
        other_user = models.User.objects.create_user(
            username='user2',
            password='password',
        )

        intro = models.Intro(
            sender=sender,
            introed_user=introed_user,
            other_user=other_user,
        )
        intro.save()

        self.assertEqual(
            intro.opposite.sender,
            sender,
        )
        self.assertEqual(
            intro.opposite.introed_user,
            other_user,
        )
        self.assertEqual(
            intro.opposite.other_user,
            introed_user,
        )
