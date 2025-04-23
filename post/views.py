from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from author.models import Author
from .forms import PostForm
from .models import Post, Category
from django.shortcuts import redirect
from django.contrib import messages
from response.models import Response
from response.forms import ResponseForm




class PostListView(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 5  # Adjust as needed

    def get_queryset(self):
        # If a category is specified in the URL, filter by category
        category = self.request.GET.get('category')
        if category:
            return Post.objects.filter(category__name=category).order_by('-created_at')
        return Post.objects.all().order_by('-created_at')


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ResponseForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Проверяем, не является ли пользователь автором поста
        if request.user.author == self.object.author:
            messages.warning(request, "Вы не можете комментировать свой собственный пост.")
            return redirect('post_detail', pk=self.object.pk)

        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.author = request.user.author
            response.post = self.object
            response.save()
            messages.success(request, "Ваш комментарий успешно добавлен.")
        else:
            messages.error(request, "Произошла ошибка при добавлении комментария.")

        return redirect('post_detail', pk=self.object.pk)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_create.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        # Получаем или создаем автора для текущего пользователя
        author, created = Author.objects.get_or_create(author_name=self.request.user)
        form.instance.author = author
        return super().form_valid(form)



class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_update.html'
    success_url = reverse_lazy('post_list')


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')

# views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from .utils import resize_image, process_video, get_file_type
# import os
from django.conf import settings

#
# @csrf_exempt
# def ckeditor_upload_view(request):
#     """
#     Обработчик загрузки файлов для CKEditor с автоматическим
#     изменением размера изображений и видео
#     """
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
#
#     if 'upload' not in request.FILES:
#         return JsonResponse({'error': 'Файл не найден'}, status=400)
#
#     upload = request.FILES['upload']
#     file_type = get_file_type(upload)
#
#     # Обработка в зависимости от типа файла
#     if file_type.startswith('image/'):
#         # Обработка изображения
#         processed_file = resize_image(upload, max_width=1200)
#
#         # Определяем путь для сохранения
#         file_path = os.path.join('ckeditor_uploads', processed_file.name)
#         save_path = os.path.join(settings.MEDIA_ROOT, file_path)
#
#         # Создаем директорию, если она не существует
#         os.makedirs(os.path.dirname(save_path), exist_ok=True)
#
#         # Сохраняем файл
#         with open(save_path, 'wb+') as destination:
#             for chunk in processed_file.chunks():
#                 destination.write(chunk)
#
#         # URL для доступа к изображению
#         url = request.build_absolute_uri(settings.MEDIA_URL + file_path)
#
#     elif file_type.startswith('video/'):
#         # Обработка видео
#         file_path = process_video(upload)
#         url = request.build_absolute_uri(settings.MEDIA_URL + file_path)
#     else:
#         return JsonResponse({'error': 'Тип файла не поддерживается'}, status=400)
#
#     # Ответ в формате, ожидаемом CKEditor
#     return JsonResponse({
#         'url': url,
#         'uploaded': 1,
#         'fileName': os.path.basename(file_path)
#     })
#
# # Create your views here.
