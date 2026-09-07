from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from apps.inventory.forms.real_estate_filter_form import RealEstateFilterForm
from apps.inventory.services.real_estate_filters import filter_real_estate_assets

PAGE_SIZE = 25


class RealEstateListView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/real_estate_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        organization = self.request.organization

        form = RealEstateFilterForm(self.request.GET or None)
        filters = form.cleaned_data if form.is_valid() else {}
        real_estate_assets = filter_real_estate_assets(organization, filters)

        paginator = Paginator(real_estate_assets, PAGE_SIZE)
        page_obj = paginator.get_page(self.request.GET.get("page"))

        querystring = self.request.GET.copy()
        querystring.pop("page", None)

        ctx["form"] = form
        ctx["page_obj"] = page_obj
        ctx["real_estate_assets"] = page_obj.object_list
        ctx["total_count"] = paginator.count
        ctx["filter_querystring"] = querystring.urlencode()
        return ctx
