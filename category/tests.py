# category/test.py

from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.test.utils import override_settings
from django.utils import timezone
from unittest.mock import patch, MagicMock

from post.models import Post
from author.models import Author
from category.models import Category
from category.tasks import send_weekly_newsletter

import datetime


class NewsletterTaskTest(TestCase):
    """Тесты для задачи периодической рассылки"""

    def setUp(self):
        """Настройка тестовых данных"""
        # Создаём категории
        self.category = Category.objects.create(name="Тестовая категория")

        # Создаём пользователей с подпиской
        self.user1 = User.objects.create_user(
            username="subscriber1",
            email="subscriber1@example.com",
            password="password"
        )
        self.author1 = Author.objects.create(
            author_name=self.user1,
            subscriber=True
        )

        self.user2 = User.objects.create_user(
            username="subscriber2",
            email="subscriber2@example.com",
            password="password"
        )
        self.author2 = Author.objects.create(
            author_name=self.user2,
            subscriber=True
        )

        # Создаём пользователя без подписки
        self.user3 = User.objects.create_user(
            username="nonsubscriber",
            email="nonsubscriber@example.com",
            password="password"
        )
        self.author3 = Author.objects.create(
            author_name=self.user3,
            subscriber=False
        )

        # Создаём пользователя без email
        self.user4 = User.objects.create_user(
            username="noemailuser",
            email="",
            password="password"
        )
        self.author4 = Author.objects.create(
            author_name=self.user4,
            subscriber=True
        )

        # Создаём тестовые посты
        self.post1 = Post.objects.create(
            title="Тестовый пост 1",
            content="Содержание первого тестового поста",
            author=self.author1,
            category=self.category,
            is_active=True,
        )

        self.post2 = Post.objects.create(
            title="Тестовый пост 2",
            content="Содержание второго тестового поста",
            author=self.author2,
            category=self.category,
            is_active=True,
        )

        # Создаём неактивный пост, который не должен попасть в рассылку
        self.post3 = Post.objects.create(
            title="Неактивный пост",
            content="Этот пост не должен попасть в рассылку",
            author=self.author1,
            category=self.category,
            is_active=False,
        )

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        CELERY_TASK_ALWAYS_EAGER=True,
        SITE_URL='http://testserver'
    )
    @patch('category.tasks.render_to_string')
    def test_send_weekly_newsletter(self, mock_render):
        """Тест отправки еженедельной рассылки"""
        # Настраиваем мок для render_to_string
        mock_render.return_value = '<html><body>Тестовая рассылка</body></html>'

        # Вызываем задачу
        result = send_weekly_newsletter()

        # Проверяем, что рассылка была отправлена только подписчикам с email
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(result, 2)  # должно быть отправлено 2 письма

        # Проверяем, что письма были отправлены правильным получателям
        recipients = [msg.to[0] for msg in mail.outbox]
        self.assertIn(self.user1.email, recipients)
        self.assertIn(self.user2.email, recipients)
        self.assertNotIn(self.user3.email, recipients)  # неподписанный

        # Проверяем тему письма
        for msg in mail.outbox:
            self.assertEqual(msg.subject, 'Новые объявления на нашем сайте')

        # Проверяем, что пользователю без email письмо не отправлялось
        for msg in mail.outbox:
            self.assertNotEqual(msg.to[0], "")

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_no_subscribers(self):
        """Тест случая, когда нет подписчиков"""
        # Удаляем всех подписчиков
        Author.objects.all().update(subscriber=False)

        # Вызываем задачу
        result = send_weekly_newsletter()

        # Проверяем, что писем не отправлено
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(result, 0)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_no_active_posts(self):
        """Тест случая, когда нет активных постов"""
        # Делаем все посты неактивными
        Post.objects.all().update(is_active=False)

        # Вызываем задачу
        result = send_weekly_newsletter()

        # Проверяем, что писем не отправлено
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(result, 0)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @patch('category.tasks.render_to_string')
    @patch('category.tasks.EmailMultiAlternatives.send')
    def test_error_handling(self, mock_send, mock_render):
        """Тест обработки ошибок при отправке писем"""
        # Настраиваем мок для render_to_string
        mock_render.return_value = '<html><body>Тестовая рассылка</body></html>'

        # Настраиваем мок для email.send, чтобы он вызывал исключение
        mock_send.side_effect = Exception("Ошибка отправки")

        # Проверяем, что задача обрабатывает исключение
        with self.assertRaises(Exception):
            send_weekly_newsletter()

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @patch('category.tasks.logger')
    def test_logging(self, mock_logger):
        """Тест логирования в задаче рассылки"""
        # Удаляем все посты
        Post.objects.all().delete()

        # Вызываем задачу
        send_weekly_newsletter()

        # Проверяем, что сообщение о отсутствии постов записано в лог
        mock_logger.info.assert_called_with("Нет новых постов для рассылки")

    def test_author_subscribe_unsubscribe(self):
        """Тест методов подписки/отписки автора"""
        # Проверяем метод отписки
        self.assertTrue(self.author1.subscriber)
        self.author1.unsubscribe()
        self.assertFalse(self.author1.subscriber)

        # Проверяем метод подписки
        self.assertFalse(self.author3.subscriber)
        self.author3.subscribe()
        self.assertTrue(self.author3.subscriber)

        # Проверяем повторный вызов метода
        result = self.author3.subscribe()
        self.assertTrue(result is False)  # уже подписан

    def test_post_methods(self):
        """Тест дополнительных методов модели Post"""
        # Тест метода short_content
        long_content = 'a' * 200
        self.post1.content = long_content
        self.post1.save()

        # Проверяем сокращение длинного контента
        short = self.post1.short_content()
        self.assertEqual(len(short), 153)  # 150 символов + '...'
        self.assertTrue(short.endswith('...'))

        # Проверяем короткий контент
        self.post2.content = 'Короткий контент'
        self.post2.save()
        self.assertEqual(self.post2.short_content(), 'Короткий контент')

        # Тест метода get_absolute_url
        with patch('django.urls.reverse') as mock_reverse:
            mock_reverse.return_value = f'/posts/{self.post1.pk}/'
            url = self.post1.get_absolute_url()
            self.assertEqual(url, f'/posts/{self.post1.pk}/')
            mock_reverse.assert_called_once_with('post_detail', kwargs={'pk': self.post1.pk})
