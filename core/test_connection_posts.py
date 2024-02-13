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

    def test_new_connection_can_see_new_posts(self):
        # Step 1: Create two users
        userA = models.User.objects.create_user(username='userA', password='12345')
        userB = models.User.objects.create_user(username='userB', password='12345')

        # Step 2: Have userA create a post
        post = models.Post.objects.create(owner=userA, text='Hello, world')
        post.publish(circles=userA.circles.all())

        # Step 3: Connect userB to userA
        invitation = userA.create_invitation(circles=userA.circles.all())
        userB.accept_invitation(invitation, circles=userB.circles.filter(name='Friends'))


        post2 = models.Post.objects.create(owner=userA, text='This is a new post')
        post2.publish(circles=userA.circles.all())

        post2b = models.Post.objects.create(owner=userB, text='This is a new post')
        post2b.publish(circles=userB.circles.all())

        # Step 4: Check that userB can only see userA's new post in their feed
        
        self.assertIn(post2, userB.feed.all())
        self.assertNotIn(post, userB.feed.all())

        # Check that userA can see userB's new post after connecting to userB
        self.assertIn(post2b, userA.feed.all())

    def test_evesdropping(self):
        # Step 1: Create two users
        userA = models.User.objects.create_user(username='userA', password='12345')
        userB = models.User.objects.create_user(username='userB', password='12345')

        userC = models.User.objects.create_user(username='userC', password='12345')

        invitation = userA.create_invitation(circles=userA.circles.all())
        userB.accept_invitation(invitation, circles=userB.circles.filter(name='Friends'))

        # Step 2: Have userA create a post
        post = models.Post.objects.create(owner=userA, text='Hello, world')
        post.publish(circles=userA.circles.all())

        

        self.assertIn(post, userB.feed.all())
        self.assertNotIn(post, userC.feed.all())