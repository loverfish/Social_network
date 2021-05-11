from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from .models import Group, Post, User, Follow


class NewPostTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='q@q.com', password='12345')
        self.client.login(username='testuser', password='12345')
        self.group = Group.objects.create(title='test', slug='test', description='empty')
        self.client.post(reverse('new_post'), data={
            'author': self.user, "group": self.group.id, "text": "New_post"}, follow=True)

    def test_auth_user_could_add_post(self):
        """Авторизированный пользователь может создавать посты, сохраняются в бд"""
        response = self.client.get(reverse('new_post'))
        self.assertFalse(Post.objects.filter(text='test_post'))
        self.assertEqual(response.status_code, 200)
        self.client.post(reverse('new_post'), data={'text': 'test_post', 'group': self.group.id})
        self.assertTrue(Post.objects.filter(text='test_post'))

    def test_new_post_index_exist(self):
        """При публикации поста он появится на главной странице (index)"""
        response = self.client.get('')
        self.assertContains(response, 'New_post')

    def test_new_post_profile_exist(self):
        """При публикации поста он появится на странице профайла пользователя (profile)"""
        response = self.client.get(reverse('profile', kwargs={'username': self.user}))
        self.assertContains(response, 'New_post')

    def test_new_post_view_exist(self):
        """При публикации поста он появится на странице поста (post)"""
        post = Post.objects.last()
        response = self.client.get(reverse('post', kwargs={'username': self.user, 'post_id': post.id}))
        self.assertContains(response, 'New_post')

    def test_new_post_group_exist(self):
        """При публикации поста он появится на странице группы (group_posts)"""
        response = self.client.get(reverse('group_posts', kwargs={'slug': self.group.slug}))
        self.assertContains(response, 'New_post')

    def test_guest_redirect_from_new_post(self):
        """Гость не может создавать посты, его перенаправляет на страницу авторизации"""
        self.client.logout()
        response = self.client.get(reverse('new_post'))
        self.assertRedirects(response, '/auth/login/?next=/new/')


class CommentTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='q@q.com', password='12345')
        self.author = User.objects.create_user(username='test_author', email='w@w.com', password='12345')
        self.post = Post.objects.create(text='testtext', author=self.author)
        self.client.login(username='testuser', password='12345')

    def test_user_could_add_comment(self):
        """Авторизированный пользователь может комментировать посты"""
        self.client.post(
            reverse('add_comment', kwargs={'username': self.author, 'post_id': self.post.id}),
            data={'text': 'comment_text'}
        )
        response = self.client.get(reverse('post', kwargs={'username': self.author, 'post_id': self.post.id}))
        self.assertContains(response, 'comment_text')

    def test_guest_could_not_add_comment(self):
        """Гость не может комментировать посты, его перенаправляет на страницу авторизации """
        self.client.logout()
        response = self.client.get(
            reverse('add_comment', kwargs={'username': self.author, 'post_id': self.post.id}),
            follow=True
        )
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertEqual(
            response.redirect_chain,
            [('/auth/login/?next={}'.format(reverse(
                'add_comment', kwargs={'username': self.author, 'post_id': self.post.id})), 302)]
        )


class FollowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='q@q.com', password='12345')
        self.author = User.objects.create_user(username='test_author', email='w@w.com', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_auth_user_could_follow(self):
        """Авторизированный пользователь может создать связь в бд с другим пользователем (подписаться)"""
        self.assertEqual(Follow.objects.all().count(), 0)
        response = self.client.get(reverse('profile_follow', kwargs={'username': self.author.username}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_auth_user_could_unfollow(self):
        """Авторизированный пользователь может разорвать связь в бд с другим пользователем (отписаться)"""
        self.client.get(reverse('profile_follow', kwargs={'username': self.author.username}))
        self.assertEqual(Follow.objects.all().count(), 1)
        response = self.client.get(reverse('profile_unfollow', kwargs={'username': self.author.username}), follow=True)
        self.assertEqual(Follow.objects.all().count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_followed_user_could_see_post(self):
        """Подписанный пользователь видит пост автора в ленте"""
        self.client.get(reverse('profile_follow', kwargs={'username': self.author.username}))
        post = Post.objects.create(text='testtext', author=self.author)
        response = self.client.get(reverse('follow_index'))
        self.assertContains(response, post.text)

    def test_unfollowed_user_could_not_see_post(self):
        """Не подписанный пользователь не видит пост автора в ленте"""
        post = Post.objects.create(text='testtext', author=self.author)
        response = self.client.get(reverse('follow_index'))
        self.assertNotContains(response, post.text)


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


class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='q@q.com', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_user_profile_exist(self):
        response = self.client.get(reverse('profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)


class ErrorTest(TestCase):
    def test_404_error(self):
        response = self.client.get('fgjsfg')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, template_name='misc/404.html')


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
