import uuid

from django import forms
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.account.services.image_processor_service import ImageProcessor
from apps.account.services.image_validator_service import ImageValidator
from apps.account.utils import AuthenticationUtils
from apps.organizations.models import ASSIGNABLE_MEMBERSHIP_ROLES, Membership, Organization

_INPUT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-600"
_SELECT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white focus:outline-none focus:ring-2 focus:ring-zinc-600"
_PASSWORD = _INPUT


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name", "logo", "industry", "size", "primary_goal"]
        labels = {
            "name": "Nome da organização",
            "logo": "Logo",
            "industry": "Setor de atuação",
            "size": "Porte da equipe",
            "primary_goal": "O que você pretende controlar?",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": _INPUT, "placeholder": "Ex: Minha Empresa"}),
            "logo": forms.ClearableFileInput(attrs={"class": "hidden", "accept": "image/*"}),
            "industry": forms.Select(attrs={"class": _SELECT}),
            "size": forms.Select(attrs={"class": _SELECT}),
            "primary_goal": forms.Select(attrs={"class": _SELECT}),
        }

    def clean_logo(self):
        logo = self.cleaned_data.get("logo")
        # Só valida/reprocessa em upload novo — sem isso, editar qualquer outro campo
        # reprocessaria e regravaria a logo já salva a cada save (recompressão JPEG
        # perdendo qualidade a cada vez, sem necessidade).
        if not logo or not isinstance(logo, UploadedFile):
            return logo
        try:
            ImageValidator.validate_size(logo)
            ImageValidator.validate_extension(logo.name)
            ImageValidator.validate_image(logo)
            logo.seek(0)
        except ValueError as error:
            raise forms.ValidationError(str(error))
        processed = ImageProcessor().resize_square(logo)
        # resize_square sempre regrava como JPEG — o nome precisa refletir isso,
        # senão o arquivo fica com extensão .png/.webp contendo bytes JPEG.
        base_name = logo.name.rsplit(".", 1)[0]
        processed.name = f"{base_name}.jpg"
        return processed

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


class MemberCreateForm(forms.Form):
    """Cria diretamente a conta de um novo membro da organização, já com papel
    definido — substitui o antigo fluxo de convite por e-mail."""

    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={"class": _INPUT, "placeholder": _("Username")}),
    )
    email = forms.EmailField(
        label=_("Email address"),
        widget=forms.EmailInput(attrs={"class": _INPUT, "placeholder": "email@exemplo.com"}),
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"class": _PASSWORD, "placeholder": _("Password")}),
    )
    confirm_password = forms.CharField(
        label=_("Confirm password"),
        widget=forms.PasswordInput(attrs={"class": _PASSWORD, "placeholder": _("Confirm password")}),
    )
    role = forms.ChoiceField(
        label=_("Role"),
        choices=[(role.value, role.label) for role in ASSIGNABLE_MEMBERSHIP_ROLES],
        widget=forms.Select(attrs={"class": _SELECT}),
    )

    def __init__(self, *args, organization=None, **kwargs):
        self.organization = organization
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if get_user_model().objects.filter(username=username).exists():
            raise forms.ValidationError(_("This username is already taken."))
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("An account with this email already exists."))
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        try:
            AuthenticationUtils.validate_password(password)
        except ValueError as error:
            raise forms.ValidationError(error)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        # Se clean_password() já rejeitou a senha (ex.: curta demais), ela some
        # de cleaned_data — comparar None com confirm_password sempre dispararia
        # "as senhas não coincidem" por cima do erro real.
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("Passwords do not match."))
        return cleaned_data

    def save(self, created_by) -> Membership:
        user = get_user_model().objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
        )
        return Membership.objects.create(
            organization=self.organization,
            user=user,
            role=self.cleaned_data["role"],
            created_by=created_by,
        )
