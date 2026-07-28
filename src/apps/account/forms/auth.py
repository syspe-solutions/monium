from django import forms
from django.utils.translation import gettext_lazy as _

from apps.account.models import User
from apps.account.utils import AuthenticationUtils
from apps.common.forms import widget_styles

_INPUT = widget_styles.INPUT
_PASSWORD = widget_styles.PASSWORD


class CustomRegisterForm(forms.ModelForm):
    field_order = ['full_name', 'username', 'email', 'password', 'confirm_password']

    full_name = forms.CharField(
        label=_("Full name"),
        widget=forms.TextInput(attrs={
            'placeholder': _("Your full name"),
            'class': _INPUT,
        })
    )

    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={
            'placeholder': _("Your username"),
            'class': _INPUT,
        })
    )

    email = forms.CharField(
        label=_("E-mail address"),
        widget=forms.EmailInput(attrs={
            'placeholder': _("example@email.com"),
            'class': _INPUT,
        })
    )

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': _("Your secure password"),
            'class': _PASSWORD,
        })
    )

    confirm_password = forms.CharField(
        label=_("Confirm password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': _("Confirm your password"),
            'class': _PASSWORD,
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            AuthenticationUtils.validate_password(password)
        except ValueError as error:
            raise forms.ValidationError(error)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("Passwords do not match."))

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        first_name, _sep, last_name = self.cleaned_data['full_name'].strip().partition(' ')
        user.first_name = first_name
        user.last_name = last_name
        if commit:
            user.save()
        return user


class CustomLoginForm(forms.Form):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={
            'placeholder': _("Your username"),
            'class': _INPUT,
        })
    )

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': _("Your password"),
            'class': _PASSWORD,
        })
    )
