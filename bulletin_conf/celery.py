# bulletin_conf/celery.py
import os
from celery import Celery
from django.conf import settings

# Устанавливаем переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bulletin_conf.settings')

# Создаем экземпляр приложения Celery
app = Celery('bulletin_conf')

# Загружаем конфигурацию из настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи во всех приложениях Django
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')