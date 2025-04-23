from django.urls import path
from .views import SubmitResponseView, AcceptResponseView, DeleteResponseView

urlpatterns = [
    path('submit/<int:post_id>/', SubmitResponseView.as_view(), name='submit_response'),
    path('accept/<int:response_id>/', AcceptResponseView.as_view(), name='accept_response'),
    path('delete/<int:response_id>/', DeleteResponseView.as_view(), name='delete_response'),
]
