from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Connection
from django.urls import reverse


User = get_user_model()

class MessageModelTests(TestCase):

    def setUp(self):
        # Set up non-modified objects used by all test methods
        self.user1 = User.objects.create_user(username='user1', password='foo')
        self.user2 = User.objects.create_user(username='user2', password='foo')
        self.connection = Connection.objects.create(owner=self.user1, other_user=self.user2)
        self.message = Message.objects.create(connection=self.connection, from_user=self.user1, text="Hello")

    def test_message_content(self):
        self.assertEqual(self.message.from_user, self.user1)
        self.assertEqual(self.message.text, "Hello")

    # Add more tests for other model methods if you have any

class ConnectionModelTests(TestCase):

    def setUp(self):
        # Set up non-modified objects used by all test methods
        self.user1 = User.objects.create_user(username='user1', password='foo')
        self.user2 = User.objects.create_user(username='user2', password='foo')
        self.connection = Connection.objects.create(owner=self.user1, other_user=self.user2)

    def test_connection_content(self):
        self.assertEqual(self.connection.owner, self.user1)
        self.assertEqual(self.connection.other_user, self.user2)

    # Add more tests for other model methods if you have any


class MessageListViewTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='foo')
        self.user2 = User.objects.create_user(username='user2', password='foo')
        self.connection = Connection.objects.create(owner=self.user1, other_user=self.user2)
        self.message = Message.objects.create(connection=self.connection, from_user=self.user1, text="Hello")
        self.client.login(username='user1', password='foo')  # Login the user

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/messages/{self.connection.id}/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('message_list', args=[self.connection.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/message_list.html')

    # Add more tests to check the context data, etc.
    
class MessageCreateViewTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='foo')
        self.user2 = User.objects.create_user(username='user2', password='foo')
        self.connection = Connection.objects.create(owner=self.user1, other_user=self.user2)
        self.client.login(username='user1', password='foo')  # Login the user

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/messages/{self.connection.id}/create/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('message_create', args=[self.connection.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/message_form.html')

    # Add more tests to check form behavior, redirection after the form is submitted, etc.
