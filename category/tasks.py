# category/tasks.py
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from post.models import Post
from author.models import Author
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_weekly_newsletter():
    """
    Задача для отправки еженедельных уведомлений о новых постах подписчикам
    """
    try:
        # Получаем всех авторов, которые являются подписчиками
        subscribers = Author.objects.filter(subscriber=True)

        if not subscribers:
            logger.info("Нет подписчиков для отправки рассылки")
            return 0

        # Получаем последние посты (например, за последнюю неделю)
        latest_posts = Post.objects.filter(is_active=True).order_by('-created_at')[:5]

        if not latest_posts:
            logger.info("Нет новых постов для рассылки")
            return 0

        sent_count = 0
        for subscriber in subscribers:
            user = subscriber.author_name
            # Проверяем наличие email
            if not user.email:
                logger.warning(f"У пользователя {user.username} отсутствует email")
                continue

            # Готовим контекст для шаблона
            context = {
                'username': user.username,
                'posts': latest_posts,
                'unsubscribe_url': f"{settings.SITE_URL}/profile/unsubscribe/"
            }

            # Рендерим HTML и текстовую версии письма
            html_content = render_to_string('email/newsletter.html', context)
            text_content = strip_tags(html_content)

            # Создаем сообщение
            subject = 'Новые объявления на нашем сайте'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = user.email

            # Создаем и отправляем письмо
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            sent_count += 1
            logger.info(f"Отправлена рассылка пользователю: {user.email}")

        return sent_count

    except Exception as e:
        logger.error(f"Ошибка при отправке рассылки: {str(e)}")
        raise