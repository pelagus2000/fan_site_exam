from django.contrib import admin
from .models import Category
from django.db import migrations
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Поля для отображения в списке
    search_fields = ('name',)  # Поля для поиска
    ordering = ('name',)


def create_periodic_tasks(apps, schema_editor):
    # Создаем расписание - выполнение раз в неделю
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=7,
        period=IntervalSchedule.DAYS,
    )

    # Создаем периодическую задачу
    PeriodicTask.objects.get_or_create(
        interval=schedule,
        name='Еженедельная рассылка',
        task='category.tasks.send_weekly_newsletter',
        kwargs=json.dumps({}),
        description='Отправляет еженедельную рассылку о новых постах подписчикам',
    )


def delete_periodic_tasks(apps, schema_editor):
    PeriodicTask.objects.filter(task='category.tasks.send_weekly_newsletter').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('category', 'xxxx_previous_migration'),  # Замените на предыдущую миграцию
    ]

    operations = [
        migrations.RunPython(create_periodic_tasks, delete_periodic_tasks),
    ]

