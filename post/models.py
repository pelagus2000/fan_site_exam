from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from author.models import Author
from category.models import Category
# from post.utils import get_file_type, resize_image, process_video


class Post(models.Model):
    title = models.CharField(max_length=200)  # Название
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Категория
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = CKEditor5Field(verbose_name="Содержание", config_name='extends')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    is_active = models.BooleanField(default=True)  # Активен ли пост
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    updated_at = models.DateTimeField(auto_now=True)  # Дата последнего обновления

    # def save(self, *args, **kwargs):
    #     # Обработка миниатюры при загрузке
    #     if self.thumbnail and hasattr(self.thumbnail, 'read'):
    #         file_type = get_file_type(self.thumbnail)
    #
    #         if file_type.startswith('image/'):
    #             self.thumbnail = resize_image(self.thumbnail)
    #         elif file_type.startswith('video/'):
    #             # Если thumbnail это видео, можно сделать обработку
    #             processed_path = process_video(self.thumbnail)
    #             self.thumbnail.name = processed_path
    #
    #     super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ['-created_at']

    def get_absolute_url(self):
        """Возвращает абсолютный URL поста для использования в письмах."""
        from django.urls import reverse
        return reverse('post_detail', kwargs={'pk': self.pk})

    def short_content(self):
        """Возвращает сокращенную версию контента для предпросмотра в рассылках."""
        from django.utils.html import strip_tags
        text = strip_tags(self.content)
        if len(text) > 150:
            return text[:150] + '...'
        return text

    def __str__(self):
        return self.title
