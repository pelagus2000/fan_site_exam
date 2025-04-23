from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from bulletin_conf import settings
from response.models import Response


@receiver(post_save, sender=Response)
def notify_post_author(sender, instance, created, **kwargs):
    try:
        if created:
            # Уведомление автора поста об отклике
            send_mail(
                subject='New Response to Your Post',
                message=f'Your post "{instance.post.title}" has received a new response.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.post.author.author_name.email]
            )
            print(f"Письмо отправлено автору поста: {instance.post.author.author_name.email}")
        elif instance.is_accepted:
            # Уведомление автора отклика о принятии отклика
            send_mail(
                subject='Your Response Has Been Accepted',
                message=f'Your response to the post "{instance.post.title}" was accepted.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.author.author_name.email]
            )
            print(f"Письмо отправлено автору отклика: {instance.author.author_name.email}")
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")
