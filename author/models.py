from django.contrib.auth.models import User
from django.db import models

class Author(models.Model):
    author_name = models.OneToOneField(User, on_delete=models.CASCADE)
    subscriber = models.BooleanField(default=True)
# Create your models here.

    def __str__(self):
        return self.author_name.username# User = get_user_model()