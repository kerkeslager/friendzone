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

    def test_accept_current_side_does_not_create_connection(self):
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

        intro.is_accepted = True
        intro.save()

        self.assertFalse(receiver.is_connected_with(introduced))
        self.assertFalse(introduced.is_connected_with(receiver))

    def test_accept_opposite_side_does_not_create_connection(self):
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

        intro.opposite.is_accepted = True
        intro.opposite.save()

        self.assertFalse(receiver.is_connected_with(introduced))
        self.assertFalse(introduced.is_connected_with(receiver))

    def test_accept_both_sides_connects_users(self):
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

        intro.is_accepted = True
        intro.save()
        intro.opposite.is_accepted = True
        intro.opposite.save()

        self.assertTrue(receiver.is_connected_with(introduced))
        self.assertTrue(introduced.is_connected_with(receiver))

    def test_accept_both_sides_in_opposite_order_connects_users(self):
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

        intro.opposite.is_accepted = True
        intro.opposite.save()
        intro.is_accepted = True
        intro.save()

        self.assertTrue(receiver.is_connected_with(introduced))
        self.assertTrue(introduced.is_connected_with(receiver))
