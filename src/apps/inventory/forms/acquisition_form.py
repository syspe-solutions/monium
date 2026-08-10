from dateutil.relativedelta import relativedelta
from django import forms

from apps.common.forms import widget_styles
from apps.inventory.models import Acquisition

_INPUT = widget_styles.INPUT


class AcquisitionForm(forms.ModelForm):
    class Meta:
        model = Acquisition
        fields = ["value", "purchase_date", "warranty_months"]
        widgets = {
            "value": forms.NumberInput(attrs={"class": _INPUT, "placeholder": "0,00", "step": "0.01", "min": 0}),
            "purchase_date": forms.DateInput(attrs={"class": _INPUT, "type": "date"}),
            "warranty_months": forms.NumberInput(attrs={"class": _INPUT, "placeholder": "12", "min": 0}),
        }

    def save(self, commit=True):
        acquisition = super().save(commit=False)

        # Vencimento da garantia é sempre derivado de data da compra + meses —
        # não é um campo editável diretamente, pra não correr o risco de ficar
        # dessincronizado dos dois campos que o originam.
        purchase_date = self.cleaned_data.get("purchase_date")
        warranty_months = self.cleaned_data.get("warranty_months")
        if purchase_date and warranty_months:
            new_expiry = purchase_date + relativedelta(months=warranty_months)
            if new_expiry != acquisition.warranty_expiry:
                acquisition.warranty_expiry = new_expiry
                acquisition.warranty_alert_sent_at = None
        else:
            acquisition.warranty_expiry = None

        if commit:
            acquisition.save()
        return acquisition
