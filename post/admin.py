from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'category', 'created_at', 'is_active')  # Поля для просмотра
    list_filter = ('category', 'is_active')  # Фильтры в панели
    search_fields = ('title', 'content')  # Поля для поиска
    ordering = ('-created_at',)  # Сортировка по дате создания (по убыванию)
    list_editable = ('is_active',)  # Возможность редактировать поле "is_active" со страницы списка
