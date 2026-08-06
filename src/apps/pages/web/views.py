from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

DIFFERENTIALS = [
    {
        "icon": "bolt",
        "title": _("Up and running in minutes"),
        "description": _("No lengthy onboarding. Create an account, import your items via CSV or add them one by one, and your team is productive the same day."),
    },
    {
        "icon": "search",
        "title": _("Find any item instantly"),
        "description": _("Search by name, code, sector, responsible, or scan a QR label. What used to take 20 minutes now takes seconds."),
    },
    {
        "icon": "notifications_active",
        "title": _("Proactive alerts — not reactive panic"),
        "description": _("Automatic emails for overdue loans, long-running maintenance, and items in poor condition. You're always one step ahead."),
    },
    {
        "icon": "lock",
        "title": _("Secure and LGPD compliant"),
        "description": _("All data stored in Brazil with TLS 1.3 encryption, daily backups, and role-based access control so only the right people see the right data."),
    },
    {
        "icon": "devices",
        "title": _("Works on any device"),
        "description": _("Fully responsive web app. Use it on desktop for full management or on mobile for quick lookups and QR scanning — no app install needed."),
    },
    {
        "icon": "support_agent",
        "title": _("Community-driven support"),
        "description": _("Open an issue on GitHub or contribute a fix yourself — the codebase is open for anyone to read, audit, and improve."),
    },
]


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("inventory:home")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["differentials"] = DIFFERENTIALS
        return ctx
