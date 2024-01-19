from django.views.generic.base import TemplateView

class IndexView(TemplateView):
    template_name = "core/index.html"

index = IndexView.as_view()
