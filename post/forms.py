from django import forms
from .models import Post
from django_ckeditor_5.widgets import CKEditor5Widget


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'content', 'thumbnail']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'content': CKEditor5Widget(
                attrs={'class': 'django_ckeditor_5'},
                config_name='extends'
            ),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
        }
