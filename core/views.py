from django.contrib.auth import authenticate, get_user_model, login
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

class SignupForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = UserCreationForm.Meta.fields

class SignupView(CreateView):
    form_class = SignupForm
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
