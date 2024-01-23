from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from . import models

class InvitationAcceptForm(forms.Form):
    circles = forms.ModelMultipleChoiceField(
        queryset=models.Circle.objects.none(),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        circles = kwargs.pop('circles')
        super().__init__(*args, **kwargs)
        self.fields['circles'].queryset = circles

class SignupForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = UserCreationForm.Meta.fields
