from random import random

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from datetime import timedelta


class Author(models.Model):
    author_name = models.OneToOneField(User, on_delete=models.CASCADE)
    subscriber = models.BooleanField(default=True)

    # Поле для хранения кода подтверждения
    verification_code = models.CharField(max_length=5, blank=True, null=True, unique=True)
    # Поле для времени истечения кода
    code_expires_at = models.DateTimeField(blank=True, null=True)


    class Meta:
        indexes = [
            models.Index(fields=['code_expires_at']),
        ]

    def set_verification_code(self, code=None):
        """Sets a unique verification code and expiration time."""
        if code is None:
            code = ''.join(random.choices('0123456789', k=5))

        # Attempt to save code, retrying if a uniqueness error occurs
        for _ in range(5):  # Allow 5 attempts to generate a unique code
            self.verification_code = code
            self.code_expires_at = now() + timedelta(minutes=10)
            try:
                self.save()
                return
            except:  # Catch integrity errors, such as violating unique constraints
                code = ''.join(random.choices('0123456789', k=5))
        raise Exception("Unable to generate unique verification code after 5 attempts.")


    def is_verification_code_valid(self, code):
        """Проверяет, корректен ли код и не истекло ли его время действия."""
        if self.verification_code == code and self.code_expires_at and now() <= self.code_expires_at:
            return True
        return False

    def clear_verification_code(self):
        """Очищает код подтверждения после успешной проверки."""
        self.verification_code = None
        self.code_expires_at = None
        self.save()

    def subscribe(self):
        """Подписывает пользователя на рассылку."""
        if not self.subscriber:
            self.subscriber = True
            self.save()
            return True
        return False

    def unsubscribe(self):
        """Отписывает пользователя от рассылки."""
        if self.subscriber:
            self.subscriber = False
            self.save()
            return True
        return False

    def __str__(self):
        return self.author_name.username
