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

        # Create an invitation that is expired
        past_date = timezone.now() - timedelta(weeks=1, days=1)
        invitation = models.Invitation.objects.create(
            owner=test_user,
            is_open=False,  # personal invitation
        )
        invitation.created_utc = past_date
        invitation.save(update_fields=['created_utc'])

        # Invitation should be expired
        self.assertTrue(
            invitation.is_expired(),
            "The invitation should be expired.",
        )

        with self.assertRaises(Exception, msg="The invitation has expired."):
            accepting_user.accept_invitation(
                invitation,
                circles=accepting_user.circles.filter(name='Family'),
            )

    def test_invitation_acceptance_before_expiration(self):
        # Create a test user for the owner of the invitation
        test_user = models.User.objects.create_user(
            username='inviting_user_before',
            password='12345',
        )
        accepting_user = models.User.objects.create_user(
            username='accepting_user_before',
            password='12345',
        )

        invitation = models.Invitation.objects.create(
            owner=test_user,
            is_open=False,
        )

        self.assertFalse(invitation.is_expired())

        accepting_user.accept_invitation(
            invitation,
            circles=accepting_user.circles.filter(
                name='Family',
            ),
        )

    def test_invitation_deletion_after_accepting(self):
        # Create a test user for the owner of the invitation
        test_user = models.User.objects.create_user(
            username='inviting_user_before',
            password='12345',
        )
        accepting_user = models.User.objects.create_user(
            username='accepting_user_before',
            password='12345',
        )

        # Create an invitation that expires in the future
        invitation = models.Invitation.objects.create(
            owner=test_user,
            is_open=False,
        )

        # Attempt to accept the invitation before it expires

        accepting_user.accept_invitation(
            invitation,
            circles=accepting_user.circles.filter(name='Family'),
        )

        # If throws exception, the invitation acceptance was successful
        with self.assertRaises(models.Invitation.DoesNotExist):
            models.Invitation.objects.get(id=invitation.id)
