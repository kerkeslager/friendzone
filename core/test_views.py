from django.test import Client, TestCase
from django.urls import reverse

from . import models, views

class InvitationViewTests(TestCase):
    def setUp(self):
        self.user0 = models.User.objects.create_user(
            username='test0',
            password='password0',
        )
        self.user1 = models.User.objects.create_user(
            username='test1',
            password='password1',
        )
        self.client0 = Client()
        self.client0.login(username='test0', password='password0')
        self.client1 = Client()
        self.client1.login(username='test1', password='password1')
