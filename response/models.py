from django.db import models
from django.db.models.signals import post_save
# from django.dispatch import receiver
from post.models import Post
from author.models import Author



class Response(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='responses')  # Пост, к которому относится отклик
    author = models.ForeignKey(Author, on_delete=models.CASCADE)  # Автор отклика
    response_text = models.TextField()  # Текст отклика
    is_accepted = models.BooleanField(default=False)  # Принят ли отклик
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания

    def __str__(self):
        return self.response_text

from .signals import notify_post_author

# Подключение сигнала post_save к Response
post_save.connect(notify_post_author, sender=Response)
