from django import forms

from apps.common.forms import widget_styles
from apps.inventory.models import Category

_INPUT = widget_styles.INPUT


class CategoryUsefulLifeForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["useful_life_months"]
        widgets = {
            "useful_life_months": forms.NumberInput(attrs={"class": _INPUT, "placeholder": "60", "min": 1}),
        }
