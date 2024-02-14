from django.test import TransactionTestCase

from .. import models

class FeedTests(TransactionTestCase):
    def test_feed_starts_empty(self):
        user = models.User.objects.create_user(
            username='user',
            password='12345',
        )

        self.assertEqual(user.feed.count(), 0)

    def test_feed_contains_own_posts(self):
        user = models.User.objects.create_user(
            username='user',
            password='12345',
        )

        post = models.Post.objects.create(
            owner=user,
            text='Hello, world',
        )

        self.assertIn(post, user.feed.all())

    def test_feed_does_not_contain_old_posts_for_new_connection(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )
        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.all())

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.filter(name='Friends'),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        self.assertNotIn(post, reading_user.feed.all())

    def test_feed_contains_posts_for_circles_in(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.filter(name='Friends'),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.filter(name='Friends'))

        self.assertIn(post, reading_user.feed.all())

    def test_feed_does_not_contain_posts_for_circles_not_in(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.filter(name='Friends'),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.filter(name='Family'))

        self.assertNotIn(post, reading_user.feed.all())

    def test_feed_does_not_contain_duplicates_if_multiple_circles(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.all(),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.all())

        self.assertIn(post, reading_user.feed.all())
        self.assertEqual(reading_user.feed.count(), 1)

    def test_removing_connection_removes_post_from_feed(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.all(),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.all())

        posting_user.connections.all().delete()

        self.assertEqual(reading_user.feed.count(), 0)

    def test_removing_circle_removes_post_from_feed(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.filter(name='Friends'),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.all())

        posting_user.circles.filter(name='Friends').delete()

        self.assertEqual(reading_user.feed.count(), 0)

    def test_removing_user_from_circle_removes_post_from_feed(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.filter(name='Friends'),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.all())

        circle = posting_user.circles.get(name='Friends')
        connection = models.Connection.objects.get(other_user=reading_user)
        models.CircleMembership.objects.filter(
            circle__pk=circle.pk,
            connection__pk=connection.pk,
        ).delete()

        self.assertEqual(reading_user.feed.count(), 0)

    def test_removing_post_from_circle_removes_post_from_feed(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.filter(name='Friends'),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.all())

        models.PostCircle.objects.filter(
            post=post,
            circle=posting_user.circles.get(name='Friends'),
        ).delete()

        self.assertEqual(reading_user.feed.count(), 0)

class FeedForUserTests(TransactionTestCase):
    def test_feed_for_self_starts_empty(self):
        user = models.User.objects.create_user(
            username='user',
            password='12345',
        )

        self.assertEqual(user.feed_for_user(user).count(), 0)

    def test_feed_contains_own_posts(self):
        user = models.User.objects.create_user(
            username='user',
            password='12345',
        )

        post = models.Post.objects.create(
            owner=user,
            text='Hello, world',
        )

        self.assertIn(post, user.feed_for_user(user).all())

    def test_feed_for_other_user_starts_empty(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.filter(name='Friends'),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        self.assertEqual(reading_user.feed_for_user(posting_user).count(), 0)

    def test_feed_contains_posts_for_circles_in(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.filter(name='Friends'),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.filter(name='Friends'))

        self.assertIn(post, reading_user.feed_for_user(posting_user).all())

    def test_feed_does_not_contain_old_posts_for_new_connection(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )
        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.filter(name='Friends'))

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.filter(name='Friends'),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        self.assertNotIn(post, reading_user.feed_for_user(posting_user).all())

    def test_feed_does_not_contain_posts_for_circles_not_in(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.filter(name='Friends'),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.filter(name='Family'))

        self.assertNotIn(post, reading_user.feed_for_user(posting_user).all())

    def test_feed_does_not_contain_duplicates_if_multiple_circles(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.all(),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.all())

        self.assertIn(post, reading_user.feed_for_user(posting_user).all())
        self.assertEqual(reading_user.feed_for_user(posting_user).count(), 1)

    def test_removing_connection_removes_post_from_feed(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.all(),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.all())

        posting_user.connections.all().delete()

        self.assertEqual(reading_user.feed_for_user(posting_user).count(), 0)

    def test_removing_circle_removes_post_from_feed(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.filter(name='Friends'),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.all())

        posting_user.circles.filter(name='Friends').delete()

        self.assertEqual(reading_user.feed_for_user(posting_user).count(), 0)

    def test_removing_user_from_circle_removes_post_from_feed(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.filter(name='Friends'),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.all())

        circle = posting_user.circles.get(name='Friends')
        connection = models.Connection.objects.get(other_user=reading_user)
        models.CircleMembership.objects.filter(
            circle__pk=circle.pk,
            connection__pk=connection.pk,
        ).delete()

        self.assertEqual(reading_user.feed_for_user(posting_user).count(), 0)

    def test_removing_post_from_circle_removes_post_from_feed(self):
        posting_user = models.User.objects.create_user(
            username='posting_user',
            password='12345',
        )
        reading_user = models.User.objects.create_user(
            username='reading_user',
            password='12345',
        )

        invitation = posting_user.create_invitation(
            circles=posting_user.circles.filter(name='Friends'),
        )
        reading_user.accept_invitation(
            invitation,
            circles=reading_user.circles.filter(name='Friends'),
        )

        post = models.Post.objects.create(
            owner=posting_user,
            text='Hello, world',
        )
        post.publish(circles=posting_user.circles.all())

        models.PostCircle.objects.filter(
            post=post,
            circle=posting_user.circles.get(name='Friends'),
        ).delete()

        self.assertEqual(reading_user.feed_for_user(posting_user).count(), 0)
