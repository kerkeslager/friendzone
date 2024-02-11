from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from . import models

class CircleWidget(forms.CheckboxSelectMultiple):
    option_template_name = 'widgets/circle_checkbox.html'

class InvitationAcceptForm(forms.Form):
    circles = forms.ModelMultipleChoiceField(
        queryset=models.Circle.objects.none(),
        widget=CircleWidget,
    )

    def __init__(self, *args, **kwargs):
        circles = kwargs.pop('circles')
        super().__init__(*args, **kwargs)
        self.fields['circles'].queryset = circles

class InvitationForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = models.Invitation
        fields = ('name', 'circles', 'message')
        widgets = {
            'circles': CircleWidget,
        }

class PostForm(forms.ModelForm):
    circles = forms.ModelMultipleChoiceField(
        queryset=models.Circle.objects.none(),
        widget=CircleWidget,
    )

    class Meta:
        model = models.Post
        fields = ('circles', 'text')
        widgets = {
            'text': forms.Textarea(attrs={ 'rows': 5 }),
        }

    def __init__(self, *args, **kwargs):
        circles = kwargs.pop('circles')
        super().__init__(*args, **kwargs)
        self.fields['circles'].queryset = circles

class ProfileForm(forms.ModelForm):
    name = forms.CharField(required=False)

    class Meta:
        model = get_user_model()
        fields = ('name',)

class SignupForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = UserCreationForm.Meta.fields
