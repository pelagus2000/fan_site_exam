from django.db import models
from django.db.models import TextField

from author.models import Author
from category.models import Category

class Post(models.Model):
    title = models.CharField(max_length=200)  # Название
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Категория
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = TextField()  # Текст поста (CKEditor)
    is_active = models.BooleanField(default=True)  # Активен ли пост
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    updated_at = models.DateTimeField(auto_now=True)  # Дата последнего обновления

    def __str__(self):
        return self.title
