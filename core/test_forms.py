from django.test import TestCase

from . import forms, models

class InvitationFormTests(TestCase):
    def test_create_links_circles(self):
        user = models.User.objects.create_user(
            username='testuser',
            password='12345',
        )

        form = forms.InvitationForm(
            data={
                'name': 'My cool invitation',
                'circles': [str(user.circles.get(name='Friends').pk)],
                'message': 'Join up!',
            },
        )
        form.instance.owner = user

        invitation = form.save()

        self.assertIn(
            user.circles.get(name='Friends'),
            invitation.circles.all(),
        )
        self.assertEqual(invitation.circles.count(), 1)
