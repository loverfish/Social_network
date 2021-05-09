from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from .models import Group, Post, User


class ErrorTest(TestCase):
    def test_404_error(self):
        response = self.client.get('fgjsfg')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, template_name='misc/404.html')


class NewImageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='q@q.com', password='12345')
        self.client.login(username='testuser', password='12345')
        self.group = Group.objects.create(title='test_group', slug='test', description='about_test')
        with open('media/posts/sal.png', 'rb') as img:
            self.post = self.client.post(reverse('new_post'), data={
                'author': self.user, "group": self.group.id, "text": "Test image post", "image": img
            }, follow=True)

    def test_new_image_index(self):
        """При публикации поста с изображнием на главной странице (index) есть тег <img>"""
        cache.clear()
        response = self.client.get("")
        self.assertContains(response, '<img')

    def test_new_image_profile(self):
        """При публикации поста с изображнием на странице пользователя (profile) есть тег <img>"""
        response = self.client.get(f"/author/{self.user.username}/")
        self.assertContains(response, '<img')

    def test_new_image_view(self):
        """При публикации поста с изображнием на странице поста (post) есть тег <img>"""
        post = Post.objects.last()
        response = self.client.get(f"/author/{self.user.username}/{post.id}")
        self.assertContains(response, '<img')

    def test_new_image_group(self):
        """При публикации поста с изображнием на странице группы (group_posts) есть тег <img>"""
        response = self.client.get(reverse('group_posts', kwargs={'slug': self.group.slug}))
        self.assertContains(response, '<img')

    def test_no_image(self):
        """Попытка добавить файл, не являющийся изображением"""
        with open('media/posts/text.txt', 'rb') as img:
            post = self.client.post(reverse('new_post'), data={
                'author': self.user, "group": self.group.id, "text": "Test no image post", "image": img
            }, follow=True)
        self.assertEqual(post.status_code, 200)
        # Проверка, что осталась всего 1 запись в БД
        self.assertEqual(Post.objects.count(), 1)

    def test_2_image(self):
        with open('media/posts/sal.gif', 'rb') as img:
            post = self.client.post(reverse('new_post'), data={
                'author': self.user, "group": self.group.id, "text": "Test 2 image post", "image": img
            }, follow=True)
        self.assertEqual(post.status_code, 200)
        self.assertEqual(Post.objects.count(), 2)


class EditImageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='q@q.com', password='12345')
        self.client.login(username='testuser', password='12345')
        self.group = Group.objects.create(title='test_group', slug='test', description='about_test')
        self.post = Post.objects.create(text="Test post", author=self.user)
        with open('media/posts/sal.png', 'rb') as img:
            self.post = self.client.post(
                reverse('post_edit', kwargs={'username': self.user.username, 'post_id': self.post.id}),
                data={'author': self.user, "group": self.group.id, "text": "Test image post", "image": img},
                follow=True)

    def test_count(self):
        self.assertEqual(Post.objects.count(), 1)

    def test_edit_image_index(self):
        """После добавления изображения к посту, на главной странице (index) есть тег <img>"""
        cache.clear()
        response = self.client.get("")
        self.assertContains(response, '<img')

    def test_edit_image_profile(self):

        """После добавления изображения к посту, на странице пользователя (profile) есть тег <img>"""
        response = self.client.get(f"/author/{self.user.username}/")
        self.assertContains(response, '<img')

    def test_edit_image_view(self):
        """После добавления изображения к посту, на странице поста (post) есть тег <img>"""
        post = Post.objects.last()
        response = self.client.get(f"/author/{self.user.username}/{post.id}")
        self.assertContains(response, '<img')

    def test_edit_image_group(self):
        """После добавления изображения к посту, на странице группы (group_posts) есть тег <img>"""
        response = self.client.get(reverse('group_posts', kwargs={'slug': self.group.slug}))
        self.assertContains(response, '<img')


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
                'text': 'edit text',
                'group': group_id,
            }
        )
        post = Post.objects.get(text='edit text', group=group_id)
        self.assertTrue(post)

        cache.clear()
        for url in ('', f'/author/{self.user.username}/', f'/author/{self.user.username}/{post.id}'):
            response = self.client.get(url)
            self.assertContains(response, post.text)

    def test_guest_redirect_from_new_post(self):
        self.client.logout()
        response = self.client.get('/new/')
        self.assertRedirects(response, '/auth/login/?next=/new/')


class CacheTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='q@q.com', password='12345')
        self.client.login(username='testuser', password='12345')
        self.post = Post.objects.create(text="Test post", author=self.user)

    def test_cache_index(self):
        """Тестирование функции кэша на главной странице"""
        response = self.client.get('')
        self.assertContains(response, self.post.text)
        post = Post.objects.create(text="Test cache post", author=self.user)
        response = self.client.get("")
        self.assertNotContains(response, post.text)
        cache.clear()
        response = self.client.get("")
        self.assertContains(response, post.text)
