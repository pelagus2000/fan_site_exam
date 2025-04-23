# author/views.py
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from post.models import Post
from response.models import Response
from .models import Author
from .forms import RegistrationForm, LoginForm
from django.core.mail import send_mail
from django.conf import settings



# def register_view(request):
#     """Handles user registration with email verification code."""
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#
#             # Check if the email already exists
#             if User.objects.filter(email=email).exists():
#                 return render(request, 'author/register.html', {'form': form, 'error': 'Email already exists!'})
#
#             # Check if the username already exists
#             if User.objects.filter(username=username).exists():
#                 return render(request, 'author/register.html', {'form': form, 'error': 'Username already exists!'})
#
#             try:
#                 # Create User and Author
#                 user = User.objects.create_user(username=username, email=email, password=password)
#                 verification_code = get_random_string(5, '0123456789')
#                 author = Author.objects.create(author_name=user)
#                 author.set_verification_code(verification_code)
#
#                 # Send email with verification code
#                 subject = 'Your Registration Verification Code'
#                 message = f'Hello {username},\n\nHere is your verification code: {verification_code}\n\n' \
#                           f'Please enter this code to complete your registration.'
#
#                 send_mail(
#                     subject,
#                     message,
#                     settings.DEFAULT_FROM_EMAIL,
#                     [email],
#                     fail_silently=False,
#                 )
#                 return redirect('code_confirm')
#             except IntegrityError as e:
#                 return render(request, 'author/register.html', {
#                     'form': form,
#                     'error': 'A registration error occurred. Please try again or contact support.',
#                 })
#             except Exception as e:
#                 return render(request, 'author/register.html', {
#                     'form': form,
#                     'error': 'Failed to send the verification email. Please try again.'
#                 })
#
#     else:
#         form = RegistrationForm()
#     return render(request, 'author/register.html', {'form': form})
#

def register_view(request):
    """Handles user registration with email verification code."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Check if the email already exists
            if User.objects.filter(email=email).exists():
                return render(request, 'author/register.html', {'form': form, 'error': 'Email already exists!'})

            # Check if the username already exists
            if User.objects.filter(username=username).exists():
                return render(request, 'author/register.html', {'form': form, 'error': 'Username already exists!'})

            try:
                # Create User and Author
                user = User.objects.create_user(username=username, email=email, password=password)
                verification_code = get_random_string(5, '0123456789')
                author = Author.objects.create(author_name=user)
                author.set_verification_code(verification_code)

                # Send email with verification code
                subject = 'Your Registration Verification Code'
                message = f'Hello {username},\n\nHere is your verification code: {verification_code}\n\n' \
                          f'Please enter this code to complete your registration.'

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return redirect('code_confirm')
            except IntegrityError as e:
                return render(request, 'author/register.html', {
                    'form': form,
                    'error': 'A registration error occurred. Please try again or contact support.',
                })
            except Exception as e:
                return render(request, 'author/register.html', {
                    'form': form,
                    'error': 'Failed to send the verification email. Please try again.'
                })

    else:
        form = RegistrationForm()
    return render(request, 'author/register.html', {'form': form})

def login_view(request):
    """Handles user login using credentials."""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Debug: Check if user exists
            if not User.objects.filter(username=username).exists():
                return render(request, 'author/login.html', {'form': form, 'error': 'User does not exist!'})

            # Authenticate user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')  # Redirect to home page on successful login
            else:
                return render(request, 'author/login.html', {'form': form, 'error': 'Invalid credentials'})

    else:
        form = LoginForm()
    return render(request, 'author/login.html', {'form': form})


def confirm_code_view(request):
    """Validates the confirmation code sent to the user's email."""
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        try:
            user = User.objects.get(email=email)
            author = Author.objects.get(author_name=user)
            if author.is_verification_code_valid(code):
                author.clear_verification_code()
                return render(request, 'author/code_confirm.html', {'success': 'Email verified successfully!'})
            else:
                return render(request, 'author/code_confirm.html', {'error': 'Invalid code!'})

        except (User.DoesNotExist, Author.DoesNotExist):
            return render(request, 'author/code_confirm.html', {'error': 'User not found!'})

    return render(request, 'author/code_confirm.html')

def logout_view(request):
    """Handles user logout."""
    logout(request)  # Logs out the user
    return redirect('/')

@login_required
def profile_view(request):
    try:
        # Get the author object associated with the current user
        author = Author.objects.get(author_name=request.user)

        # Get user's posts
        user_posts = Post.objects.filter(author=author)

        # Get user's responses (responses made by the current user)
        user_responses = Response.objects.filter(author=author)

        # Get responses to user's posts
        post_responses = Response.objects.filter(post__author=author)

        context = {
            'user_posts': user_posts,
            'user_responses': user_responses,
            'post_responses': post_responses,
            'author': author,
        }
        return render(request, 'author/profile.html', context)

    except Author.DoesNotExist:
        # If Author object doesn't exist, create it
        author = Author.objects.create(author_name=request.user)

        context = {
            'user_posts': [],
            'user_responses': [],
            'post_responses': [],
            'author': author,
            'message': 'Профиль был создан автоматически.'
        }
        return render(request, 'author/profile.html', context)
