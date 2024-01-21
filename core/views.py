from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.base import TemplateView

class IndexView(TemplateView):
    template_name = 'core/index.html'

index = IndexView.as_view()

class SettingsView(TemplateView):
    template_name = 'core/settings.html'

settings = SettingsView.as_view()

class SignupView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('welcome') # TODO Redirect to a welcome page
    template_name = 'registration/signup.html'

signup = SignupView.as_view()

class WelcomeView(TemplateView):
    template_name = 'core/welcome.html'

welcome = WelcomeView.as_view()
