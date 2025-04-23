# from PIL import Image
# from io import BytesIO
# from django.core.files.uploadedfile import InMemoryUploadedFile
# import subprocess
# import os
# import tempfile
# from django.conf import settings
# import uuid
# import magic
#
#
# def resize_image(image_field, max_width=800, max_height=None, quality=85):
#     """
#     Изменяет размер изображения до указанного максимального размера,
#     с сохранением пропорций.
#
#     :param image_field: Объект ImageField
#     :param max_width: Максимальная ширина
#     :param max_height: Максимальная высота (опционально)
#     :param quality: Качество JPEG (1-100)
#     :return: Обработанное изображение
#     """
#     img = Image.open(image_field)
#
#     # Проверка формата изображения
#     img_format = img.format if img.format else 'JPEG'
#
#     # Получение размеров
#     width, height = img.size
#
#     # Если изображение меньше указанных размеров, возвращаем его без изменений
#     if (max_width is None or width <= max_width) and (max_height is None or height <= max_height):
#         return image_field
#
#     # Вычисление нового размера с сохранением пропорций
#     if max_width and width > max_width:
#         ratio = max_width / width
#         new_width = max_width
#         new_height = int(height * ratio)
#     else:
#         new_width, new_height = width, height
#
#     if max_height and new_height > max_height:
#         ratio = max_height / new_height
#         new_height = max_height
#         new_width = int(new_width * ratio)
#
#     # Преобразование RGBA изображений в RGB
#     if img.mode == 'RGBA' and img_format == 'JPEG':
#         img = img.convert('RGB')
#
#     # Изменяем размер
#     img = img.resize((new_width, new_height), Image.LANCZOS)
#
#     output = BytesIO()
#
#     # Сохраняем изображение
#     img.save(output, format=img_format, quality=quality)
#     output.seek(0)
#
#     # Возвращаем новый объект InMemoryUploadedFile
#     return InMemoryUploadedFile(
#         output,
#         'ImageField',
#         f"{image_field.name.split('.')[0]}.{img_format.lower()}",
#         f'image/{img_format.lower()}',
#         output.getbuffer().nbytes,
#         None
#     )
#
#
# def process_video(video_field, max_width=720, max_bitrate="1000k"):
#     """
#     Обрабатывает видео файл, изменяя его размер и битрейт.
#     Требует установленного ffmpeg.
#
#     :param video_field: Поле с видео
#     :param max_width: Максимальная ширина (высота рассчитывается пропорционально)
#     :param max_bitrate: Максимальный битрейт
#     :return: Путь к обработанному видео
#     """
#     try:
#         # Создаем временный файл для входного видео
#         input_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{video_field.name.split('.')[-1]}")
#         input_file.write(video_field.read())
#         input_file.close()
#
#         # Создаем уникальное имя для выходного файла
#         output_filename = f"{uuid.uuid4()}.mp4"
#         output_path = os.path.join(settings.MEDIA_ROOT, 'videos', output_filename)
#         os.makedirs(os.path.dirname(output_path), exist_ok=True)
#
#         # Команда для ffmpeg
#         cmd = [
#             'ffmpeg',
#             '-i', input_file.name,
#             '-vf', f'scale={max_width}:-2',  # -2 сохраняет пропорции
#             '-b:v', max_bitrate,
#             '-movflags', '+faststart',  # Для лучшего стриминга
#             '-y',  # Перезаписывать файл если существует
#             output_path
#         ]
#
#         subprocess.run(cmd, check=True)
#
#         # Удаляем временный файл
#         os.unlink(input_file.name)
#
#         # Возвращаем относительный путь для сохранения в БД
#         return os.path.join('videos', output_filename)
#
#     except (subprocess.SubprocessError, Exception) as e:
#         # В случае ошибки удаляем временные файлы и возвращаем оригинал
#         if os.path.exists(input_file.name):
#             os.unlink(input_file.name)
#         if os.path.exists(output_path):
#             os.unlink(output_path)
#         print(f"Error processing video: {e}")
#         return video_field
#
#
# def get_file_type(file_field):
#     """
#     Определяет тип файла с помощью python-magic
#     """
#     # Сохраним текущую позицию в файле
#     current_position = file_field.tell()
#
#     # Прочитаем начало файла
#     file_data = file_field.read(2048)
#
#     # Вернемся к сохраненной позиции
#     file_field.seek(current_position)
#
#     # Определим MIME-тип файла
#     mime = magic.Magic(mime=True)
#     file_type = mime.from_buffer(file_data)
#
#     return file_type
#
#
# def process_media_file(file_field):
#     """
#     Обрабатывает медиа-файл в зависимости от его типа
#     """
#     file_type = get_file_type(file_field)
#
#     if file_type.startswith('image/'):
#         return resize_image(file_field)
#     elif file_type.startswith('video/'):
#         return process_video(file_field)
#     else:
#         # Если тип файла не распознан или не требует обработки
#         return file_field
