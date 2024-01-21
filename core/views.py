from django.views.generic.base import TemplateView

class IndexView(TemplateView):
    template_name = 'core/index.html'

index = IndexView.as_view()

class SettingsView(TemplateView):
    template_name = 'core/settings.html'

settings = SettingsView.as_view()
