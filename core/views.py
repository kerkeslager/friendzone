import io
import uuid

from django.contrib.auth import authenticate, login
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import CreateView, DeleteView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.utils import timezone

import pyqrcode

from . import forms, models

class AboutView(TemplateView):
    template_name = 'core/about.html'

about_main = AboutView.as_view()

class AboutModerationView(TemplateView):
    template_name = 'core/about_moderation.html'

about_moderation = AboutModerationView.as_view()

class AboutPhilosophyView(TemplateView):
    template_name = 'core/about_philosophy.html'

about_philosophy = AboutPhilosophyView.as_view()

class AboutPrivacy(TemplateView):
    template_name = 'core/about_privacy.html'

about_privacy = AboutPrivacy.as_view()

class CircleCreateView(CreateView):
    model = models.Circle
    form_class = forms.CircleForm
    success_url = reverse_lazy('circle_list')

    def get_context_data(self):
        result = super().get_context_data()
        result['is_new'] = True
        return result

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
    form_class = forms.CircleForm

    def get_context_data(self):
        result = super().get_context_data()
        result['is_new'] = False
        return result

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

class ConnectionBulkUpdate(View):
    def post(self, request, *args, **kwargs):
        circles_by_pk = {
            str(circle.pk): circle
            for circle in request.user.circles.all()
        }
        connections_by_other_user_pk = {
            str(conn.other_user.pk): conn
            for conn in request.user.connections.all()
        }

        selections = [
            item[len('selection:'):].split('/')
            for item in request.POST.keys()
            if item.startswith('selection:')
        ]

        # Note that the dictionaries only contain Circles/Connections owned
        # by the request.user, so KeyErrors here might mean request.user
        # is trying to modify CircleMemberships that don't belong to them
        selected_circle_memberships = [
            (
                circles_by_pk[circle_pk],
                connections_by_other_user_pk[conn_other_user_pk],
            )
            for circle_pk, conn_other_user_pk in selections
        ]

        existing_circle_memberships = models.CircleMembership.objects.filter(
            connection__owner=request.user,
        )

        # Delete existing CircleMemberships that aren't selected
        for existing_cm in existing_circle_memberships:
            ecm_as_tuple = (existing_cm.circle, existing_cm.connection)
            if ecm_as_tuple not in selected_circle_memberships:
                existing_cm.delete()

        # Add selected CircleMemberships that don't already exist
        for circle, conn in selected_circle_memberships:
            selected_cm_exists = existing_circle_memberships.filter(
                circle=circle,
                connection=conn,
            ).count() == 1

            if not selected_cm_exists:
                models.CircleMembership.objects.create(
                    circle=circle,
                    connection=conn,
                )

        return redirect(reverse('connection_list'))

conn_bulk_edit = ConnectionBulkUpdate.as_view()

class ConnectionDeleteView(DeleteView):
    model = models.Connection
    success_url = reverse_lazy('invite_list')

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            owner=self.request.user,
            other_user__pk=self.kwargs['pk'],
        )

conn_delete = ConnectionDeleteView.as_view()

class ConnectionListView(ListView):
    model = models.Connection
    template_name = 'core/connection_list.html'

    def get_queryset(self):
        return self.request.user.connections.order_by(
            'other_user__name',
            'other_user__username',
        )

connection_list = ConnectionListView.as_view()

class ConvoDetail(ListView):
    model = models.Message

    def get_queryset(self):
        other_user = get_object_or_404(
            models.User,
            pk=self.kwargs['pk'],
        )
        connection = self.request.user.connections.get(other_user=other_user)
        return models.Message.objects.filter(
            Q(connection=connection) | Q(connection=connection.opposite)
        ).order_by('created_utc')

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result['form'] = forms.MessageForm()
        result['other_user'] = models.User.objects.get(pk=self.kwargs['pk'])
        return result

convo_detail = ConvoDetail.as_view()

class ConvoList(ListView):
    model = models.Connection
    template_name = 'core/convo_list.html'

    def get_queryset(self):
        return self.request.user.connections.annotate(
            outgoing_count=Count('outgoing_messages'),
            incoming_count=Count('opposite__outgoing_messages'),
        ).filter(Q(outgoing_count__gt=0) | Q(incoming_count__gt=0))

convo_list = ConvoList.as_view()

# TODO Can we join this into the convo_detail view?
class MessageCreateView(CreateView):
    model = models.Message
    form_class = forms.MessageForm

    def form_valid(self, form):
        form.instance.connection = self.request.user.connections.get(
            other_user=models.User.objects.get(pk=self.kwargs['pk']),
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('convo_detail', args=[self.kwargs['pk']])

message_create = MessageCreateView.as_view()

class CSSView(TemplateView):
    template_name = 'core/style.css'
    content_type = 'text/css'

css_style = CSSView.as_view()

class IntroAccept(UpdateView):
    model = models.Intro
    form_class = forms.IntroAcceptForm
    success_url = reverse_lazy('connection_list')

intro_accept = IntroAccept.as_view()

class IntroCreate(CreateView):
    model = models.Intro
    form_class = forms.IntroForm

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result['connections'] = self.request.user.connected_users
        return result

    def get_success_url(self):
        return reverse('intro_detail', kwargs={ 'pk': self.object.pk })

    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super().form_valid(form)

intro_create = IntroCreate.as_view()

class IntroDetail(DetailView):
    model = models.Intro

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)

        if self.request.user == self.object.receiver:
            result['form'] = forms.IntroAcceptForm()

        return result

    def get_object(self):
        intro = get_object_or_404(
            models.Intro,
            pk=self.kwargs['pk'],
        )

        if self.request.user == intro.sender:
            return intro

        if self.request.user == intro.receiver:
            return intro

        raise Http404()

intro_detail = IntroDetail.as_view()

class IntroList(ListView):
    model = models.Intro

    def get_queryset(self):
        return self.request.user.open_intros

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result['form'] = forms.IntroForm(
            connections=self.request.user.connected_users,
        )
        return result

intro_list = IntroList.as_view()

class InvitationCreateView(CreateView):
    model = models.Invitation
    success_url = reverse_lazy('invite_list')
    form_class = forms.InvitationForm

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result['is_new'] = True
        return result

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result['circles'] = self.request.user.circles
        return result

    def form_valid(self, form):
        invitation = form.save(commit=False)
        invitation.owner = self.request.user
        if invitation.is_open:
            # Logic for open invitations
            pass
        else:
            # personal invitations (e.g., expiration)
            invitation.expires_at = timezone.now()
            invitation.expires_at += models.Invitation.DEFAULT_EXPIRATION
        invitation.save()
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

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result['is_new'] = False
        return result

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result['circles'] = self.request.user.circles
        return result

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

        if self.request.user.is_authenticated:
            if self.request.user == self.object.owner:
                qr = pyqrcode.create(self.request.build_absolute_uri())
                qr_buffer = io.BytesIO()
                qr.svg(
                    qr_buffer,
                    module_color='currentColor',
                    omithw=True,
                )

                data['qr'] = mark_safe(
                    qr_buffer.getvalue().decode('utf-8'),
                )
            else:
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

class ProfileEditView(UpdateView):
    form_class = forms.ProfileForm
    model = models.User
    template_name = 'core/profile_form.html'

    def get_object(self):
        return self.request.user

profile_edit = ProfileEditView.as_view()

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
            data['post_form'] = forms.PostForm(
                circles=self.request.user.circles,
            )

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
        result = super().form_valid(form)
        circle_ids = set(
            uuid.UUID(circle_id)
            for circle_id in form.data.getlist('circles')
        )
        circles = self.request.user.circles.filter(
            pk__in=circle_ids,
        )
        form.instance.publish(circles=circles)
        return result

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

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result['circles'] = self.request.user.circles
        return result

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

class SettingsView(UpdateView):
    form_class = forms.SettingsForm
    model = models.User
    success_url = reverse_lazy('settings')
    template_name = 'core/settings.html'

    def get_object(self):
        return self.request.user

settings = SettingsView.as_view()

class SignupView(CreateView):
    form_class = forms.SignupForm
    success_url = reverse_lazy('welcome')
    template_name = 'registration/signup.html'

    def get_success_url(self):
        return self.request.POST.get('next', None) or reverse('welcome')

    def form_valid(self, form):
        result = super().form_valid(form)

        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']

        user = authenticate(username=username, password=password)
        login(self.request, user)

        return result

signup = SignupView.as_view()

class StyleView(TemplateView):
    template_name = 'core/style.html'

style = StyleView.as_view()

class UserDetailView(DetailView):
    model = models.User

    def get_object(self):
        if 'pk' not in self.kwargs:
            return self.request.user

        user = get_object_or_404(
            models.User,
            pk=self.kwargs['pk'],
        )

        if self.request.user == user:
            return user

        if not self.request.user.is_connected_with(user):
            raise Http404()

        return user

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)

        if self.request.user != result['object']:
            result['in_circles'] = self.request.user.circles.filter(
                connections__other_user=result['object']
            )

        result['feed_for_user'] = self.request.user.feed_for_user(
            result['object'],
        )

        return result

user_detail = UserDetailView.as_view()

class WelcomeView(TemplateView):
    template_name = 'core/welcome.html'

welcome = WelcomeView.as_view()

class WhyView(TemplateView):
    template_name = 'core/why.html'

why = WhyView.as_view()
