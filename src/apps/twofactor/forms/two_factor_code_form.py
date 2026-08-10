from django import forms
from django.utils.translation import gettext_lazy as _

from apps.common.forms import widget_styles


class TwoFactorCodeForm(forms.Form):
    code = forms.CharField(
        label=_("Authentication code"),
        max_length=12,
        widget=forms.TextInput(attrs={
            "class": widget_styles.INPUT,
            "placeholder": _("6-digit code or recovery code"),
            "autocomplete": "one-time-code",
            "autofocus": True,
        }),
    )
