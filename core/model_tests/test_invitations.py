from django.test import TransactionTestCase
from django.utils import timezone
from datetime import timedelta


from .. import models

class InvitationExpirationTests(TransactionTestCase):
    def test_invitation_expiration(self):
        # Create a test user for the owner of the invitation
        test_user = models.User.objects.create_user(
            username='inviting_user',
            password='12345',
        )
        accepting_user = models.User.objects.create_user(
            username='accepting_user',
            password='12345',
        )

        # Create an invitation that is supposed to expire a week ago
        past_date = timezone.now() - timedelta(weeks=1, days=1)
        invitation = models.Invitation.objects.create(
            owner=test_user,
            is_open=False,  # personal invitation
            expires_at=past_date
        )

        # Invitation should be expired
        self.assertTrue(
            invitation.is_expired(),
            "The invitation should be expired.")

        with self.assertRaises(Exception, msg="The invitation has expired."):
            accepting_user.accept_invitation(
                invitation,
                circles=accepting_user.circles.filter(name='Family'),
            )

    def test_invitation_acceptance_before_expiration(self):
        # Create a test user for the owner of the invitation
        test_user = models.User.objects.create_user(
            username='inviting_user_before', password='12345')
        accepting_user = models.User.objects.create_user(
            username='accepting_user_before', password='12345')
        # Invitation expires in the future
        future_date = timezone.now() + timedelta(days=7)
        invitation = models.Invitation.objects.create(
            owner=test_user, is_open=False, expires_at=future_date)

        self.assertFalse(invitation.is_expired())

        # Create an invitation that expires in the future
        future_date = timezone.now()
        future_date += timedelta(days=7)
        invitation = models.Invitation.objects.create(
            owner=test_user,
            is_open=False,
            expires_at=future_date
        )

        # Attempt to accept the invitation before it expires
        try:
            accepting_user.accept_invitation(
                invitation,
                circles=accepting_user.circles.filter(name='Family'),
            )
            # If we reach here, the invitation acceptance was successful
            self.assertFalse(
                invitation.is_expired(),
                "The invitation should not be expired yet.")
        except Exception as e:
            # If an exception is raised, the test should fail
            self.fail(f"Accepting the invitation raised an exception: {e}")

    def test_invitation_deletion_after_accepting(self):
        # Create a test user for the owner of the invitation
        test_user = models.User.objects.create_user(
            username='inviting_user_before', password='12345')
        accepting_user = models.User.objects.create_user(
            username='accepting_user_before', password='12345')
        # Invitation expires in the future
        future_date = timezone.now() + timedelta(days=7)
        invitation = models.Invitation.objects.create(
            owner=test_user, is_open=False, expires_at=future_date)

        self.assertFalse(invitation.is_expired())

        # Create an invitation that expires in the future
        future_date = timezone.now()
        future_date += timedelta(days=7)
        invitation = models.Invitation.objects.create(
            owner=test_user,
            is_open=False,
            expires_at=future_date
        )

        # Attempt to accept the invitation before it expires

        accepting_user.accept_invitation(
            invitation,
            circles=accepting_user.circles.filter(name='Family'),
        )
        # If we reach here, the invitation acceptance was successful
        with self.assertRaises(models.Invitation.DoesNotExist):
            models.Invitation.objects.get(id=invitation.id)
