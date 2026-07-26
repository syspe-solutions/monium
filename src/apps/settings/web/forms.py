from django import forms
from django.utils.translation import gettext_lazy as _

from apps.settings.models import EmailSettings

_INPUT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-600"
_CHECKBOX = "w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-white focus:ring-2 focus:ring-zinc-600"

PASSWORD_PLACEHOLDER = "•" * 12


class EmailSettingsForm(forms.ModelForm):
    host_password = forms.CharField(
        label=_("SMTP password"),
        required=False,
        widget=forms.PasswordInput(attrs={"class": _INPUT, "placeholder": PASSWORD_PLACEHOLDER}, render_value=False),
        help_text=_("Leave blank to keep the currently saved password."),
    )

    class Meta:
        model = EmailSettings
        fields = [
            "is_enabled", "host", "port", "use_tls", "use_ssl",
            "host_user", "host_password", "default_from_email",
        ]
        labels = {
            "is_enabled": _("Enable SMTP server"),
            "host": _("SMTP host"),
            "port": _("Port"),
            "use_tls": _("Use TLS"),
            "use_ssl": _("Use SSL"),
            "host_user": _("SMTP username"),
            "default_from_email": _("Default sender address"),
        }
        widgets = {
            "is_enabled": forms.CheckboxInput(attrs={"class": _CHECKBOX}),
            "host": forms.TextInput(attrs={"class": _INPUT, "placeholder": "smtp.example.com"}),
            "port": forms.NumberInput(attrs={"class": _INPUT, "min": 1, "max": 65535}),
            "use_tls": forms.CheckboxInput(attrs={"class": _CHECKBOX}),
            "use_ssl": forms.CheckboxInput(attrs={"class": _CHECKBOX}),
            "host_user": forms.TextInput(attrs={"class": _INPUT}),
            "default_from_email": forms.EmailInput(attrs={"class": _INPUT, "placeholder": "no-reply@example.com"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("use_tls") and cleaned_data.get("use_ssl"):
            raise forms.ValidationError(_("TLS and SSL cannot be enabled at the same time."))
        if cleaned_data.get("is_enabled") and not cleaned_data.get("host"):
            raise forms.ValidationError(_("Inform the SMTP host to enable the server."))
        if cleaned_data.get("is_enabled") and not cleaned_data.get("default_from_email"):
            raise forms.ValidationError(_("Inform the default sender address to enable the server."))
        return cleaned_data

    def save(self, commit=True):
        email_settings = super().save(commit=False)
        if not self.cleaned_data.get("host_password"):
            email_settings.host_password = self.initial_password
        if commit:
            email_settings.save()
        return email_settings

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_password = self.instance.host_password if self.instance.pk else ""
        if self.initial_password:
            self.fields["host_password"].widget.attrs["placeholder"] = PASSWORD_PLACEHOLDER
