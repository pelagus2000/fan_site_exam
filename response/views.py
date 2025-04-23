from django.shortcuts import get_object_or_404, redirect
from django.views import View
from .models import Response
from .forms import ResponseForm


class SubmitResponseView(View):
    def post(self, request, post_id):
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.author = request.user.author
            response.post_id = post_id
            response.save()
        return redirect('post_detail', pk=post_id)


class AcceptResponseView(View):
    def post(self, request, response_id):
        response = get_object_or_404(Response, id=response_id)
        response.is_accepted = True
        response.save()
        return redirect('profile')


class DeleteResponseView(View):
    def post(self, request, response_id):
        response = get_object_or_404(Response, id=response_id)
        response.delete()
        return redirect('profile')
