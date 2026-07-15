from django import forms
from django.utils.translation import gettext_lazy as _


class ItemImportForm(forms.Form):
    csv_file = forms.FileField(
        label=_("CSV file"),
        widget=forms.ClearableFileInput(attrs={
            "class": "text-sm text-zinc-500 file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 "
                     "file:text-sm file:font-medium file:bg-zinc-800 file:text-zinc-200 hover:file:bg-zinc-700",
            "accept": ".csv,text/csv",
        }),
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]
        if not csv_file.name.lower().endswith(".csv"):
            raise forms.ValidationError(_("Please upload a .csv file."))
        return csv_file
