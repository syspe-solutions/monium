from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views import View

from apps.inventory.forms.acquisition_form import AcquisitionForm
from apps.inventory.forms.movable_asset_form import AssetSpecForm, MovableAssetForm
from apps.inventory.models import Brand
from apps.organizations.mixins import InventoryWriteRequiredMixin

from .brand_views import resolve_brand


class MovableAssetCreateView(LoginRequiredMixin, InventoryWriteRequiredMixin, View):
    template_name = "inventory/item_form.html"

    def _context(self, form, spec_form, acquisition_form, selected_brand_id="", brand_error=""):
        return {
            "form": form,
            "spec_form": spec_form,
            "acquisition_form": acquisition_form,
            "brands": Brand.objects.order_by("name"),
            "selected_brand_id": str(selected_brand_id),
            "brand_error": brand_error,
        }

    def get(self, request):
        return render(request, self.template_name,
                      self._context(MovableAssetForm(), AssetSpecForm(), AcquisitionForm()))

    def post(self, request):
        form = MovableAssetForm(request.POST)
        spec_form = AssetSpecForm(request.POST, request.FILES)
        acquisition_form = AcquisitionForm(request.POST)
        brand_id = request.POST.get("brand_id", "").strip()
        new_brand_name = request.POST.get("new_brand_name", "").strip()

        if not form.is_valid() or not spec_form.is_valid() or not acquisition_form.is_valid():
            return render(request, self.template_name,
                          self._context(form, spec_form, acquisition_form, brand_id))

        brand_instance, brand_error = resolve_brand(brand_id, new_brand_name, request.user)
        if brand_error:
            return render(request, self.template_name,
                          self._context(form, spec_form, acquisition_form, "__new__", brand_error))

        # Save item
        item = form.save(commit=False)
        item.organization = request.organization
        item.created_by = request.user
        item.updated_by = request.user
        item.save()

        # Save spec if any data provided
        has_spec = any([
            brand_instance,
            spec_form.cleaned_data.get("model_name"),
            spec_form.cleaned_data.get("serial_number"),
            spec_form.cleaned_data.get("image"),
        ])
        if has_spec:
            spec = spec_form.save(commit=False)
            spec.asset = item
            spec.brand = brand_instance
            spec.created_by = request.user
            spec.updated_by = request.user
            spec.save()

        # Save acquisition if any data provided
        has_acquisition = any([
            acquisition_form.cleaned_data.get("value") is not None,
            acquisition_form.cleaned_data.get("purchase_date"),
            acquisition_form.cleaned_data.get("warranty_months") is not None,
        ])
        if has_acquisition:
            acquisition = acquisition_form.save(commit=False)
            acquisition.item = item
            acquisition.created_by = request.user
            acquisition.updated_by = request.user
            acquisition.save()

        messages.success(request, _('Item "%(name)s" registered successfully.') % {"name": item.name})
        return redirect("inventory:item_detail", pk=item.id)
