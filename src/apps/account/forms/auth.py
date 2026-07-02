from django import forms
from django.utils.translation import gettext_lazy as translate

from apps.account.models import User
from apps.account.utils import AuthenticationUtils

_INPUT = "w-full text-sm p-2 border border-zinc-700 rounded bg-zinc-950 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-600"
_PASSWORD = "w-full text-sm p-2 border border-zinc-700 rounded bg-zinc-950 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-600"


class CustomRegisterForm(forms.ModelForm):
    username = forms.CharField(
        label=translate("Username"),
        widget=forms.TextInput(attrs={
            'placeholder': translate("Your username"),
            'class': _INPUT,
        })
    )

    email = forms.CharField(
        label=translate("E-mail address"),
        widget=forms.EmailInput(attrs={
            'placeholder': translate("example@email.com"),
            'class': _INPUT,
        })
    )

    password = forms.CharField(
        label=translate("Password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': translate("Your secure password"),
            'class': _PASSWORD,
        })
    )

    confirm_password = forms.CharField(
        label=translate("Confirm password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': translate("Confirm your password"),
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
            raise forms.ValidationError(translate("Passwords do not match."))

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class CustomLoginForm(forms.Form):
    username = forms.CharField(
        label=translate("Username"),
        widget=forms.TextInput(attrs={
            'placeholder': translate("Your username"),
            'class': _INPUT,
        })
    )

    password = forms.CharField(
        label=translate("Password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': translate("Your password"),
            'class': _PASSWORD,
        })
    )
