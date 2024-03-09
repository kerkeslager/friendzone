from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from . import models

COLOR_HELP_TEXT = 'Accepts HTML color names and hex codes starting with "#".'

class CircleWidget(forms.CheckboxSelectMultiple):
    option_template_name = 'widgets/circle_checkbox.html'

class CircleMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            models.Circle.objects.none(),
            *args,
            widget=CircleWidget,
            **kwargs,
        )


class CircleForm(forms.ModelForm):
    class Meta:
        model = models.Circle
        fields = ('name', 'color')
        help_texts = {
            'name': 'This will not be shown to other users.',
            'color': f"The color of the circle's icon. { COLOR_HELP_TEXT }",
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = models.Message
        fields = ('text',)
        widgets = {
            'text': forms.TextInput(
                attrs={
                    'autofocus': 'true',
                    'placeholder': "Remember to be loving.",
                    'rows': 1,
                },
            ),
        }

class IntroForm(forms.ModelForm):
    class Meta:
        model = models.Intro
        fields = ('receiver', 'introduced')

    def __init__(self, *args, **kwargs):
        connections = kwargs.pop('connections')
        super().__init__(*args, **kwargs)
        self.fields['receiver'].queryset = connections
        self.fields['introduced'].queryset = connections

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['receiver'] == cleaned_data['introduced']:
            raise ValidationError('Cannot introduce user to themself!')

        return cleaned_data

class IntroAcceptForm(forms.ModelForm):
    is_accepted = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'style': 'display: none;'}),
        initial=True,
    )

    class Meta:
        model = models.Intro
        fields = ('is_accepted',)

class InvitationAcceptForm(forms.Form):
    circles = CircleMultipleChoiceField()

    def __init__(self, *args, **kwargs):
        circles = kwargs.pop('circles')
        super().__init__(*args, **kwargs)
        self.fields['circles'].queryset = circles

class InvitationForm(forms.ModelForm):
    circles = CircleMultipleChoiceField()
    message = forms.CharField(
        help_text='This message will be shown to the user you invite.',
        widget=forms.Textarea,
    )
    is_open = forms.BooleanField(
        required=False,  # Make optional if you want users to explicitly choose
        label='Open Invitation',
        help_text='(it will not expire and can be accepted by multiple users).'
    )

    class Meta:
        model = models.Invitation
        fields = ('name', 'circles', 'message', 'is_open')
        help_texts = {
            'name': 'Who is this invite for?',
        }
        widgets = {
            'circles': CircleWidget,
        }

    def __init__(self, *args, **kwargs):
        circles = kwargs.pop('circles')
        super().__init__(*args, **kwargs)
        self.fields['circles'].help_text = (
            'If a user accepts this invite, they will be added to the '
            'selected circles.'
        )
        self.fields['circles'].queryset = circles


class PostForm(forms.ModelForm):
    circles = forms.ModelMultipleChoiceField(
        queryset=models.Circle.objects.none(),
        help_text='This post will be visible to these circles.',
        widget=CircleWidget,
    )
    image = forms.ImageField(required=False)

    class Meta:
        model = models.Post
        fields = ('circles', 'image', 'text')
        widgets = {
            'text': forms.Textarea(
                attrs={
                    'placeholder': "What's on your mind?",
                    'rows': 5,
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        circles = kwargs.pop('circles')
        super().__init__(*args, **kwargs)
        self.fields['circles'].queryset = circles
        self.fields['text'].required = False

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data['image'] and not cleaned_data['text']:
            raise ValidationError('Post must have either an image or text.')
        return cleaned_data


class ProfileForm(forms.ModelForm):
    name = forms.CharField(required=False)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = get_user_model()
        fields = ('name', 'avatar')

class SettingsForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            'timezone',
            'allow_js',
            'foreground_color',
            'background_color',
            'error_color',
        )
        help_texts = {
            'timezone': 'The timezone to display dates in.',
            'allow_js':
                'All major functionality of the site works without JS, but '
                'some features may have fewer page loads and more '
                'interactivity.',
            'foreground_color': COLOR_HELP_TEXT,
            'background_color': COLOR_HELP_TEXT,
            'error_color': COLOR_HELP_TEXT,
        }

class SignupForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = UserCreationForm.Meta.fields


class ConnectedUserCircleForm(forms.ModelForm):
    circles = forms.ModelMultipleChoiceField(
        queryset=models.Circle.objects.none(),
        help_text='This post will be visible to these circles.',
        required=False,
        widget=CircleWidget,
    )

    class Meta:
        model = get_user_model()
        fields = ('circles', )

    def __init__(self, *args, **kwargs):
        circles = kwargs.pop('circles')
        super().__init__(*args, **kwargs)
        self.fields['circles'].queryset = circles
