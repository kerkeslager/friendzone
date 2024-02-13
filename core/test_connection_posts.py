from django.test import TestCase
from core import models

class TestPostVisibility(TestCase):
    def test_new_connection_cannot_see_old_posts(self):
        # Step 1: Create two users
        userA = models.User.objects.create_user(username='userA', password='12345')
        userB = models.User.objects.create_user(username='userB', password='12345')

        # Step 2: Have userA create a post
        post = models.Post.objects.create(owner=userA, text='Hello, world')
        post.publish(circles=userA.circles.all())

        # Step 3: Connect userB to userA
        invitation = userA.create_invitation(circles=userA.circles.all())
        userB.accept_invitation(invitation, circles=userB.circles.filter(name='Friends'))

        # Step 4: Check that userB cannot see userA's post in their feed
        self.assertNotIn(post, userB.feed.all())

