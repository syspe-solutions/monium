import uuid

from django import forms
from django.utils.text import slugify

from apps.organizations.models import Organization

_INPUT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-600"
_SELECT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white focus:outline-none focus:ring-2 focus:ring-zinc-600"


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
        organization.slug = f"{slugify(organization.name)}-{uuid.uuid4().hex[:6]}"
        if commit:
            organization.save()
        return organization
