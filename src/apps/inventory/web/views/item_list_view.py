from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from apps.inventory.forms.movel_filter_form import MovelFilterForm
from apps.inventory.services.movel_filters import filter_items

PAGE_SIZE = 25


class MovelListView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/item_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        organization = self.request.organization

        form = MovelFilterForm(self.request.GET or None)
        filters = form.cleaned_data if form.is_valid() else {}
        items = filter_items(organization, filters)

        paginator = Paginator(items, PAGE_SIZE)
        page_obj = paginator.get_page(self.request.GET.get("page"))

        querystring = self.request.GET.copy()
        querystring.pop("page", None)

        ctx["form"] = form
        ctx["page_obj"] = page_obj
        ctx["items"] = page_obj.object_list
        ctx["total_count"] = paginator.count
        ctx["filter_querystring"] = querystring.urlencode()
        return ctx
