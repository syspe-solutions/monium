from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

PLANS = [
    {
        "id": "free",
        "name": _("Free"),
        "price": None,
        "period": None,
        "description": _("For individuals getting started with inventory control."),
        "cta": _("Current plan"),
        "cta_disabled": True,
        "highlight": False,
        "badge": None,
        "features": [
            ("check", _("Up to 50 items")),
            ("check", _("1 user")),
            ("check", _("Basic dashboard")),
            ("check", _("Export CSV (50 rows/month)")),
            ("close", _("Overdue alerts")),
            ("close", _("PDF reports")),
            ("close", _("QR code labels")),
            ("close", _("API access")),
            ("close", _("Priority support")),
        ],
    },
    {
        "id": "starter",
        "name": _("Starter"),
        "price": "49",
        "period": _("month"),
        "description": _("For small teams that need more items and basic automation."),
        "cta": _("Get Starter"),
        "cta_disabled": False,
        "highlight": False,
        "badge": None,
        "features": [
            ("check", _("Up to 500 items")),
            ("check", _("Up to 3 users")),
            ("check", _("Full dashboard")),
            ("check", _("Unlimited CSV export")),
            ("check", _("Overdue loan alerts by email")),
            ("close", _("PDF reports")),
            ("close", _("QR code labels")),
            ("close", _("API access")),
            ("close", _("Priority support")),
        ],
    },
    {
        "id": "pro",
        "name": _("Pro"),
        "price": "149",
        "period": _("month"),
        "description": _("For growing teams with complete control and integrations."),
        "cta": _("Get Pro"),
        "cta_disabled": False,
        "highlight": True,
        "badge": _("Most popular"),
        "features": [
            ("check", _("Unlimited items")),
            ("check", _("Up to 10 users")),
            ("check", _("Full dashboard")),
            ("check", _("Unlimited CSV export")),
            ("check", _("Overdue loan alerts by email")),
            ("check", _("PDF reports")),
            ("check", _("QR code labels (print-ready)")),
            ("check", _("REST API access")),
            ("check", _("Priority support")),
        ],
    },
    {
        "id": "enterprise",
        "name": _("Enterprise"),
        "price": None,
        "period": None,
        "description": _("For organizations with custom requirements and SLA."),
        "cta": _("Talk to us"),
        "cta_disabled": False,
        "highlight": False,
        "badge": None,
        "features": [
            ("check", _("Unlimited items")),
            ("check", _("Unlimited users")),
            ("check", _("All Pro features")),
            ("check", _("Custom integrations (ERP, SAP)")),
            ("check", _("On-premise deployment option")),
            ("check", _("SSO / Active Directory")),
            ("check", _("SLA agreement")),
            ("check", _("Dedicated account manager")),
            ("check", _("Custom branding (white-label)")),
        ],
    },
]


class PlansView(LoginRequiredMixin, TemplateView):
    template_name = "billing/plans.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["plans"] = PLANS
        return ctx
