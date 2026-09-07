from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views import View

from apps.inventory.forms.acquisition_form import AcquisitionForm
from apps.inventory.forms.movable_asset_form import MovableAssetForm, AssetSpecForm
from apps.inventory.models import Brand, MovableAsset
from apps.organizations.mixins import InventoryWriteRequiredMixin

from .brand_views import resolve_brand


class MovableAssetUpdateView(LoginRequiredMixin, InventoryWriteRequiredMixin, View):
    template_name = "inventory/item_form.html"

    def _get_item(self, request, pk):
        return get_object_or_404(
            MovableAsset.objects.select_related("category", "sector", "location", "acquisition").prefetch_related("spec__brand"),
            pk=pk,
            organization=request.organization,
        )

    def _context(self, item, form, spec_form, acquisition_form, selected_brand_id="", brand_error=""):
        return {
            "item": item,
            "form": form,
            "spec_form": spec_form,
            "acquisition_form": acquisition_form,
            "brands": Brand.objects.order_by("name"),
            "selected_brand_id": str(selected_brand_id),
            "brand_error": brand_error,
        }

    def get(self, request, pk):
        item = self._get_item(request, pk)
        spec = getattr(item, "spec", None)
        acquisition = getattr(item, "acquisition", None)
        selected_brand_id = spec.brand_id if spec and spec.brand_id else ""
        return render(request, self.template_name, self._context(
            item, MovableAssetForm(instance=item), AssetSpecForm(instance=spec),
            AcquisitionForm(instance=acquisition), selected_brand_id,
        ))

    def post(self, request, pk):
        item = self._get_item(request, pk)
        spec = getattr(item, "spec", None)
        acquisition = getattr(item, "acquisition", None)
        form = MovableAssetForm(request.POST, instance=item)
        spec_form = AssetSpecForm(request.POST, request.FILES, instance=spec)
        acquisition_form = AcquisitionForm(request.POST, instance=acquisition)
        brand_id = request.POST.get("brand_id", "").strip()
        new_brand_name = request.POST.get("new_brand_name", "").strip()

        if not form.is_valid() or not spec_form.is_valid() or not acquisition_form.is_valid():
            return render(request, self.template_name,
                          self._context(item, form, spec_form, acquisition_form, brand_id))

        brand_instance, brand_error = resolve_brand(brand_id, new_brand_name, request.user)
        if brand_error:
            return render(request, self.template_name,
                          self._context(item, form, spec_form, acquisition_form, "__new__", brand_error))

        item = form.save(commit=False)
        item.updated_by = request.user
        item.save()

        has_spec = any([
            brand_instance,
            spec_form.cleaned_data.get("model_name"),
            spec_form.cleaned_data.get("serial_number"),
            spec_form.cleaned_data.get("image"),
        ])
        if has_spec:
            new_spec = spec_form.save(commit=False)
            new_spec.asset = item
            new_spec.brand = brand_instance
            new_spec.updated_by = request.user
            if not new_spec.created_by_id:
                new_spec.created_by = request.user
            new_spec.save()

        has_acquisition = any([
            acquisition_form.cleaned_data.get("value") is not None,
            acquisition_form.cleaned_data.get("purchase_date"),
            acquisition_form.cleaned_data.get("warranty_months") is not None,
        ])
        if has_acquisition:
            new_acquisition = acquisition_form.save(commit=False)
            new_acquisition.item = item
            new_acquisition.updated_by = request.user
            if not new_acquisition.created_by_id:
                new_acquisition.created_by = request.user
            new_acquisition.save()

        messages.success(request, _('Item "%(name)s" updated successfully.') % {"name": item.name})
        return redirect("inventory:item_detail", pk=item.id)
