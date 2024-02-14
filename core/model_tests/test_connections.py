from django.test import TransactionTestCase

from .. import models

class ConnectionTests(TransactionTestCase):
    def test_create_connection_creates_opposite_connection(self):
        inviting_user = models.User.objects.create_user(
            username='inviting_user',
            password='12345',
        )
        accepting_user = models.User.objects.create_user(
            username='accepting_user',
            password='12345',
        )

        connection = models.Connection(
            owner=inviting_user,
            other_user=accepting_user,
        )
        connection.save()

        self.assertEqual(connection, connection.opposite.opposite)
        self.assertEqual(connection.owner, inviting_user)
        self.assertEqual(connection.other_user, accepting_user)
        self.assertEqual(connection.opposite.owner, accepting_user)
        self.assertEqual(connection.opposite.other_user, inviting_user)

    def test_connected_users_in_each_others_connected_users(self):
        inviting_user = models.User.objects.create_user(
            username='inviting_user',
            password='12345',
        )
        accepting_user = models.User.objects.create_user(
            username='accepting_user',
            password='12345',
        )

        connection = models.Connection(
            owner=inviting_user,
            other_user=accepting_user,
        )
        connection.save()

        self.assertIn(inviting_user, accepting_user.connected_users.all())
        self.assertIn(accepting_user, inviting_user.connected_users.all())

    def test_deleting_connection_deletes_opposite_connection(self):
        inviting_user = models.User.objects.create_user(
            username='inviting_user',
            password='12345',
        )
        accepting_user = models.User.objects.create_user(
            username='accepting_user',
            password='12345',
        )

        connection = models.Connection(
            owner=inviting_user,
            other_user=accepting_user,
        )
        connection.save()

        connection.delete()

        self.assertFalse(models.Connection.objects.filter(
            owner=inviting_user,
            other_user=accepting_user,
        ).exists())
        self.assertFalse(models.Connection.objects.filter(
            owner=accepting_user,
            other_user=inviting_user,
        ).exists())

    def test_deleting_opposite_connection_deletes_connection(self):
        inviting_user = models.User.objects.create_user(
            username='inviting_user',
            password='12345',
        )
        accepting_user = models.User.objects.create_user(
            username='accepting_user',
            password='12345',
        )

        connection = models.Connection(
            owner=inviting_user,
            other_user=accepting_user,
        )
        connection.save()

        connection.opposite.delete()

        self.assertFalse(models.Connection.objects.filter(
            owner=inviting_user,
            other_user=accepting_user,
        ).exists())
        self.assertFalse(models.Connection.objects.filter(
            owner=accepting_user,
            other_user=inviting_user,
        ).exists())
