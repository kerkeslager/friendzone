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

    def test_invitation_acceptance_status_for_sender(self):
        invitation = self.user0.create_invitation(
            circles=self.user0.circles.all(),
        )
        response = self.client0.get(reverse('invite_detail', args=[invitation.pk]))
        self.assertContains(response, 'Acceptance Status:')
        self.assertContains(response, 'Not Accepted')

        self.user1.accept_invitation(
            invitation,
            circles=self.user1.circles.all(),
        )
        response = self.client0.get(reverse('invite_detail', args=[invitation.pk]))
        self.assertContains(response, 'Acceptance Status:')
        self.assertContains(response, 'Accepted')

    def test_invitation_acceptance_status_for_receiver(self):
        invitation = self.user0.create_invitation(
            circles=self.user0.circles.all(),
        )
        response = self.client1.get(reverse('invite_detail', args=[invitation.pk]))
        self.assertNotContains(response, 'Acceptance Status:')
