from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from . import models

COLOR_HELP_TEXT = 'Accepts HTML color names and hex codes starting with "#".'

class CircleWidget(forms.CheckboxSelectMultiple):
    option_template_name = 'widgets/circle_checkbox.html'

class CircleForm(forms.ModelForm):
    class Meta:
        model = models.Circle
        fields = ('name', 'color')
        help_texts = {
            'color': f"The color of the circle's icon. { COLOR_HELP_TEXT }",
        }

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

class SettingsForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('allow_js', 'foreground_color', 'background_color')
        help_texts = {
            'allow_js':
                'All major functionality of the site works without JS, but some '
                'features may have fewer page loads and more interactivity.',
            'foreground_color': COLOR_HELP_TEXT,
            'background_color': COLOR_HELP_TEXT,
        }

class SignupForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = UserCreationForm.Meta.fields
