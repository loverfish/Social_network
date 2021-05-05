# from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from .models import Group, Post, User


class UserPagesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='q@q.com', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_user_profile_exist(self):
        response = self.client.get(reverse('profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)

    def test_auth_user_new_post(self):
        group = Group.objects.create(
            title='test',
            slug='test',
            description='empty',
        )
        group_id = group.id

        response = self.client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)
        self.client.post(
            reverse('new_post'),
            data={
                'text': 'text',
                'group': group_id,
            }
        )
        post = Post.objects.get(text='text', group=group_id)
        self.assertTrue(post)
        for url in ('', f'/author/{self.user.username}/', f'/author/{self.user.username}/{post.id}'):
            response = self.client.get(url)
            self.assertContains(response, post.text)
        response = self.client.get('/author/{}/{}'.format(self.user.username, post.id))
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/author/{}/{}/edit'.format(self.user.username, post.id))
        self.assertEqual(response.status_code, 200)
        self.client.post(
            '/author/{}/{}/edit'.format(self.user.username, post.id),
            data={
                'text': 'edit_text',
                'group': group_id,
            }
        )
        post = Post.objects.get(text='edit_text', group=group_id)
        self.assertTrue(post)
        for url in ('', f'/author/{self.user.username}/', f'/author/{self.user.username}/{post.id}'):
            response = self.client.get(url)
            self.assertContains(response, post.text)

    def test_guest_redirect_from_new_post(self):
        self.client.logout()
        response = self.client.get('/new/')
        self.assertRedirects(response, '/auth/login/?next=/new/')
