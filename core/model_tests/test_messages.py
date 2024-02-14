from django.test import TransactionTestCase

from .. import models

class MessageTests(TransactionTestCase):
    def test_send_message_to_user(self):
        sending_user = models.User.objects.create_user(
            username='sending_user',
            password='12345',
        )
        receiving_user = models.User.objects.create_user(
            username='receiving_user',
            password='12345',
        )

        invitation = sending_user.create_invitation(
            circles=sending_user.circles.filter(name='Friends'),
        )
        receiving_user.accept_invitation(
            invitation,
            circles=receiving_user.circles.filter(name='Friends'),
        )

        text = 'Hello, world'

        sending_user.send_message_to(receiving_user, text=text)

        # TODO There are a ton of assertions here, which could probably go in
        # their own tests.

        message = models.Message.objects.first()
        self.assertEqual(message.text, text)
        self.assertEqual(message.from_user, sending_user)
        self.assertEqual(message.to_user, receiving_user)

        self.assertEqual(sending_user.connections.count(), 1)
        sending_connection = sending_user.connections.first()
        self.assertEqual(sending_connection.outgoing_messages.count(), 1)
        self.assertEqual(sending_connection.outgoing_messages.first(), message)
        self.assertEqual(sending_connection.incoming_messages.count(), 0)
        self.assertEqual(sending_connection.messages.count(), 1)
        self.assertEqual(sending_connection.messages.first(), message)

        self.assertEqual(receiving_user.connections.count(), 1)
        receiving_connection = receiving_user.connections.first()
        self.assertEqual(receiving_connection.outgoing_messages.count(), 0)
        self.assertEqual(receiving_connection.incoming_messages.count(), 1)
        self.assertEqual(receiving_connection.incoming_messages.first(), message)
        self.assertEqual(receiving_connection.messages.count(), 1)
        self.assertEqual(receiving_connection.messages.first(), message)
