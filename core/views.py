from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from . import forms, models

class CircleDetailView(DetailView):
    model = models.Circle

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            owner=self.request.user,
            pk=self.kwargs['pk'],
        )

circle_detail = CircleDetailView.as_view()

class CircleListView(ListView):
    model = models.Circle

    def get_queryset(self):
        return self.request.user.circles.all()

circle_list = CircleListView.as_view()

class DeleteUserView(DeleteView):
    model = models.User
    success_url = reverse_lazy('delete_done')

    def get_object(self):
        return self.request.user

delete = DeleteUserView.as_view()

class DeleteDoneView(TemplateView):
    template_name = 'core/delete_done.html'

delete_done = DeleteDoneView.as_view()

class IndexView(TemplateView):
    template_name = 'core/index.html'

index = IndexView.as_view()

class SettingsView(TemplateView):
    template_name = 'core/settings.html'

settings = SettingsView.as_view()

class SignupView(CreateView):
    form_class = forms.SignupForm
    success_url = reverse_lazy('welcome') # TODO Redirect to a welcome page
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        result = super().form_valid(form)

        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']

        user = authenticate(username=username, password=password)
        login(self.request, user)

        return result

signup = SignupView.as_view()

class WelcomeView(TemplateView):
    template_name = 'core/welcome.html'

welcome = WelcomeView.as_view()
