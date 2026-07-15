import uuid

from django import forms
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as translate

from apps.account.utils import AuthenticationUtils
from apps.organizations.models import Organization

_INPUT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-600"
_SELECT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white focus:outline-none focus:ring-2 focus:ring-zinc-600"
_PASSWORD = _INPUT


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name", "industry", "size", "primary_goal"]
        labels = {
            "name": "Nome da organização",
            "industry": "Setor de atuação",
            "size": "Porte da equipe",
            "primary_goal": "O que você pretende controlar?",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": _INPUT, "placeholder": "Ex: Minha Empresa"}),
            "industry": forms.Select(attrs={"class": _SELECT}),
            "size": forms.Select(attrs={"class": _SELECT}),
            "primary_goal": forms.Select(attrs={"class": _SELECT}),
        }

    def save(self, commit=True):
        organization = super().save(commit=False)
        if organization._state.adding:
            # organization.pk já vem preenchido (UUIDField com default=uuid.uuid4 no
            # cliente) mesmo antes do primeiro save — não dá pra usar "pk truthy" pra
            # saber se é criação ou edição, precisa checar _state.adding mesmo.
            organization.slug = f"{slugify(organization.name)}-{uuid.uuid4().hex[:6]}"
        if commit:
            organization.save()
        return organization


class InvitationForm(forms.Form):
    email = forms.EmailField(
        label=translate("Email address"),
        widget=forms.EmailInput(attrs={"class": _INPUT, "placeholder": "email@exemplo.com"}),
    )

    def __init__(self, *args, organization=None, **kwargs):
        self.organization = organization
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if self.organization.memberships.filter(user__email__iexact=email).exists():
            raise forms.ValidationError(translate("This person is already a member of this organization."))

        if self.organization.invitations.filter(email=email, status="pending").exists():
            raise forms.ValidationError(translate("There's already a pending invitation for this email."))

        return email


class InvitationSignupForm(forms.Form):
    """Cria a conta de quem aceita um convite sem ainda ter usuário no Monium.
    Duplica username/password/confirm_password de CustomRegisterForm de propósito
    (e-mail é fixo, vindo do convite) pra não acoplar organizations a account."""

    username = forms.CharField(
        label=translate("Username"),
        widget=forms.TextInput(attrs={"class": _INPUT, "placeholder": translate("Your username")}),
    )
    password = forms.CharField(
        label=translate("Password"),
        widget=forms.PasswordInput(attrs={"class": _PASSWORD, "placeholder": translate("Your secure password")}),
    )
    confirm_password = forms.CharField(
        label=translate("Confirm password"),
        widget=forms.PasswordInput(attrs={"class": _PASSWORD, "placeholder": translate("Confirm your password")}),
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if get_user_model().objects.filter(username=username).exists():
            raise forms.ValidationError(translate("This username is already taken."))
        return username

    def clean_password(self):
        password = self.cleaned_data.get("password")
        try:
            AuthenticationUtils.validate_password(password)
        except ValueError as error:
            raise forms.ValidationError(error)
        return password

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError(translate("Passwords do not match."))
        return cleaned_data
