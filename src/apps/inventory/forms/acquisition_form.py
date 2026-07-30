from django import forms

from apps.common.forms import widget_styles
from apps.inventory.models import Acquisition

_INPUT = widget_styles.INPUT


class AcquisitionForm(forms.ModelForm):
    class Meta:
        model = Acquisition
        fields = ["value", "purchase_date"]
        widgets = {
            "value": forms.NumberInput(attrs={"class": _INPUT, "placeholder": "0,00", "step": "0.01", "min": 0}),
            "purchase_date": forms.DateInput(attrs={"class": _INPUT, "type": "date"}),
        }
