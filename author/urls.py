# author/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('confirm/', views.confirm_code_view, name='code_confirm'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

]
