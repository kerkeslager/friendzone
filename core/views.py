from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from . import forms, models

class CircleCreateView(CreateView):
    model = models.Circle
    fields = ('name', 'color')
    success_url = reverse_lazy('circle_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

circle_create = CircleCreateView.as_view()

class CircleDeleteView(DeleteView):
    model = models.Circle
    success_url = reverse_lazy('circle_list')

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            owner=self.request.user,
            pk=self.kwargs['pk'],
        )

circle_delete = CircleDeleteView.as_view()

class CircleEditView(UpdateView):
    model = models.Circle
    fields = ('name','color')

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            owner=self.request.user,
            pk=self.kwargs['pk'],
        )

circle_edit = CircleEditView.as_view()

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
        return self.request.user.circles.order_by('name')

circle_list = CircleListView.as_view()

class ConnectionListView(ListView):
    model = models.Connection
    template_name = 'core/connection_list.html'

    def get_queryset(self):
        return self.request.user.connections.order_by('other_user__name', 'other_user__username')

connection_list = ConnectionListView.as_view()

class InvitationCreateView(CreateView):
    model = models.Invitation
    success_url = reverse_lazy('invite_list')
    form_class = forms.InvitationForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

invite_create = InvitationCreateView.as_view()

class InvitationAcceptView(FormView):
    form_class = forms.InvitationAcceptForm
    template_name = 'core/invitation_accept.html'

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result['circles'] = self.request.user.circles
        return result

    def get_success_url(self):
        return reverse('user_detail', kwargs={ 'pk': self.redirect_user.pk })

    def form_valid(self, form):
        invitation = get_object_or_404(
            models.Invitation,
            pk=self.kwargs['pk'],
        )
        circles = form.fields['circles'].queryset
        self.request.user.accept_invitation(invitation, circles=circles)

        self.redirect_user = invitation.owner

        return super().form_valid(form)

invite_accept = InvitationAcceptView.as_view()

class InvitationDeleteView(DeleteView):
    model = models.Invitation
    success_url = reverse_lazy('invite_list')

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            owner=self.request.user,
            pk=self.kwargs['pk'],
        )

invite_delete = InvitationDeleteView.as_view()

class InvitationEditView(UpdateView):
    model = models.Invitation
    form_class = forms.InvitationForm

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            owner=self.request.user,
            pk=self.kwargs['pk'],
        )

invite_edit = InvitationEditView.as_view()

class InvitationDetailView(DetailView):
    model = models.Invitation

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs['pk'],
        )

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)

        if self.request.user.is_authenticated and self.request.user != self.object.owner:
            data['form'] = forms.InvitationAcceptForm(
                circles=self.request.user.circles.all(),
            )

        return data

invite_detail = InvitationDetailView.as_view()

class InvitationListView(ListView):
    model = models.Invitation

    def get_queryset(self):
        return self.request.user.invitations.order_by('name')

invite_list = InvitationListView.as_view()

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

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)

        if self.request.user.is_authenticated:
            data['post_form'] = forms.PostForm(circles=self.request.user.circles)

        return data


index = IndexView.as_view()

class PostCreateView(CreateView):
    form_class = forms.PostForm
    model = models.Post
    success_url = reverse_lazy('index')

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result['circles'] = self.request.user.circles
        return result

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

post_create = PostCreateView.as_view()

class PostDeleteView(DeleteView):
    model = models.Post
    success_url = reverse_lazy('index')

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            owner=self.request.user,
            pk=self.kwargs['pk'],
        )

post_delete = PostDeleteView.as_view()

class PostEditView(UpdateView):
    model = models.Post
    form_class = forms.PostForm

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            owner=self.request.user,
            pk=self.kwargs['pk'],
        )

post_edit = PostEditView.as_view()

class PostDetailView(DetailView):
    model = models.Post

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs['pk'],
        )

post_detail = PostDetailView.as_view()

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

class UserDetailView(DetailView):
    model = models.User

    def get_object(self):
        user = get_object_or_404(
            models.User,
            pk=self.kwargs['pk'],
        )

        if self.request.user == user:
            return user

        if not self.request.user.is_connected_with(user):
            raise Http404()

        return user

user_detail = UserDetailView.as_view()

class WelcomeView(TemplateView):
    template_name = 'core/welcome.html'

welcome = WelcomeView.as_view()

class WhyView(TemplateView):
    template_name = 'core/why.html'

why = WhyView.as_view()
