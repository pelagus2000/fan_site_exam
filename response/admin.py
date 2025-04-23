from django.contrib import admin
from .models import Response


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'response_text', 'is_accepted', 'created_at')  # Поля для просмотра
    list_filter = ('is_accepted', 'post')  # Фильтры
    search_fields = ('response_text',)  # Поля для поиска
    ordering = ('-created_at',)  # Сортировка по дате создания (по убыванию)
    list_editable = ('is_accepted',)  # Возможность изменять статус "is_accepted" на странице списка


# Register your models here.
