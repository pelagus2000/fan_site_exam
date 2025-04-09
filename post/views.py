
from django.views.generic import ListView, DetailView
from .models import Post, Category


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

# Create your views here.
