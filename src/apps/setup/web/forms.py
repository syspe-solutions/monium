from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.account.utils import AuthenticationUtils
from apps.setup.dtos.database_configuration_dto import DatabaseConfigurationDTO

_INPUT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-600"
_RADIO = "w-4 h-4 border-zinc-700 bg-zinc-900 text-white focus:ring-2 focus:ring-zinc-600"

DEFAULT_POSTGRESQL_PORT = "5432"


class DatabaseSetupForm(forms.Form):
    ENGINE_CHOICES = [
        ("sqlite3", _("SQLite (recommended for simple self-hosting, no extra service required)")),
        ("postgresql", _("PostgreSQL (external server)")),
    ]

    engine = forms.ChoiceField(
        label=_("Database"),
        choices=ENGINE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": _RADIO}),
        initial="sqlite3",
    )
    host = forms.CharField(
        required=False, label=_("Host"),
        widget=forms.TextInput(attrs={"class": _INPUT, "placeholder": "localhost"}),
    )
    port = forms.CharField(
        required=False, label=_("Port"),
        widget=forms.TextInput(attrs={"class": _INPUT, "placeholder": DEFAULT_POSTGRESQL_PORT}),
    )
    name = forms.CharField(
        required=False, label=_("Database name"),
        widget=forms.TextInput(attrs={"class": _INPUT}),
    )
    user = forms.CharField(
        required=False, label=_("User"),
        widget=forms.TextInput(attrs={"class": _INPUT}),
    )
    password = forms.CharField(
        required=False, label=_("Password"),
        widget=forms.PasswordInput(attrs={"class": _INPUT}, render_value=False),
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("engine") != "postgresql":
            return cleaned_data

        required_fields = ["host", "name", "user", "password"]
        missing_any = any(not cleaned_data.get(field) for field in required_fields)
        if missing_any:
            raise forms.ValidationError(
                _("Fill in host, database name, user and password to use an external PostgreSQL server.")
            )
        return cleaned_data

    def to_configuration(self) -> DatabaseConfigurationDTO:
        if self.cleaned_data["engine"] == "sqlite3":
            return DatabaseConfigurationDTO(
                engine="sqlite3",
                name=str(settings.APP_DATA_DIR / "db.sqlite3"),
            )
        return DatabaseConfigurationDTO(
            engine="postgresql",
            name=self.cleaned_data["name"],
            user=self.cleaned_data["user"],
            password=self.cleaned_data["password"],
            host=self.cleaned_data["host"],
            port=self.cleaned_data.get("port") or DEFAULT_POSTGRESQL_PORT,
        )


class AdminSetupForm(forms.Form):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={"class": _INPUT, "placeholder": _("Username")}),
    )
    email = forms.EmailField(
        label=_("Email address"),
        widget=forms.EmailInput(attrs={"class": _INPUT, "placeholder": "admin@example.com"}),
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"class": _INPUT}, render_value=False),
    )
    confirm_password = forms.CharField(
        label=_("Confirm password"),
        widget=forms.PasswordInput(attrs={"class": _INPUT}, render_value=False),
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if get_user_model().objects.filter(username=username).exists():
            raise forms.ValidationError(_("This username is already taken."))
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
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        # Se clean_password() já rejeitou a senha (ex.: curta demais), ela some
        # de cleaned_data — comparar None com confirm_password sempre dispararia
        # "as senhas não coincidem" por cima do erro real.
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("Passwords do not match."))
        return cleaned_data

    def save(self):
        return get_user_model().objects.create_superuser(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
        )
