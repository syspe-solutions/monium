from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

SERVICES = [
    {
        "slug": "inventory-control",
        "name": _("Inventory Control"),
        "icon": "inventory_2",
        "tagline": _("Complete visibility over every physical asset."),
        "description": _(
            "Register, categorize, and locate every item in your organization in seconds. "
            "Monium's inventory control gives you a live view of assets distributed across "
            "sectors, locations, and responsible parties — eliminating manual spreadsheets."
        ),
        "for_whom": [
            _("Operations and facilities managers"),
            _("IT departments tracking equipment"),
            _("Schools and universities managing lab assets"),
            _("NGOs and public institutions controlling patrimony"),
        ],
        "steps": [
            {"icon": "add_box",       "title": _("Add"),       "desc": _("Add items with code, category, sector, condition, and responsible party.")},
            {"icon": "qr_code_2",     "title": _("Label"),     "desc": _("Generate and print QR code labels to physically identify each asset.")},
            {"icon": "manage_search", "title": _("Track"),     "desc": _("Search, filter, and locate items instantly from any device.")},
            {"icon": "bar_chart",     "title": _("Report"),    "desc": _("Generate PDF and CSV reports for audits, insurance, or internal reviews.")},
        ],
        "benefits": [
            _("Reduce time spent searching for items by up to 80%"),
            _("Eliminate duplicate asset registration"),
            _("Ensure audit readiness at any time"),
            _("Track asset lifecycle from acquisition to write-off"),
        ],
    },
    {
        "slug": "loan-management",
        "name": _("Loan Management"),
        "icon": "swap_horiz",
        "tagline": _("Know exactly who has what — and when it's due back."),
        "description": _(
            "Track every item that leaves its designated location. Register loans to employees, "
            "sectors, or external parties with expected return dates. Receive automatic alerts "
            "when items are overdue, preventing losses and improving accountability."
        ),
        "for_whom": [
            _("HR teams managing tool or equipment loans"),
            _("IT departments tracking laptops and peripherals"),
            _("Events teams lending AV equipment"),
            _("Labs managing shared instruments"),
        ],
        "steps": [
            {"icon": "person_add",        "title": _("Assign"),  "desc": _("Associate an item to a person or sector with a return date.")},
            {"icon": "notifications",     "title": _("Alert"),   "desc": _("Receive automatic alerts when the return deadline approaches.")},
            {"icon": "assignment_return", "title": _("Return"),  "desc": _("Register the return and automatically restore item availability.")},
            {"icon": "history",           "title": _("History"), "desc": _("Full loan history per item and per person for accountability.")},
        ],
        "benefits": [
            _("Zero items lost due to untracked loans"),
            _("Automated overdue reminders via email"),
            _("Full accountability trail for audits"),
            _("Real-time view of item availability"),
        ],
    },
    {
        "slug": "maintenance-tracking",
        "name": _("Maintenance Tracking"),
        "icon": "build",
        "tagline": _("Keep your assets running. Never miss a maintenance."),
        "description": _(
            "Schedule preventive maintenances and track corrective ones. Log every intervention, "
            "associate costs and technicians, and monitor open tickets. Monium alerts you when "
            "items have been in maintenance for too long or when preventive dates are due."
        ),
        "for_whom": [
            _("Maintenance teams in factories and warehouses"),
            _("Facilities managers in office buildings"),
            _("Fleet managers tracking vehicle upkeep"),
            _("Technical support teams managing repair workflows"),
        ],
        "steps": [
            {"icon": "event",     "title": _("Schedule"), "desc": _("Set preventive maintenance dates per item category or individually.")},
            {"icon": "handyman",  "title": _("Execute"),  "desc": _("Log the intervention with technician, date, cost, and notes.")},
            {"icon": "task_alt",  "title": _("Close"),    "desc": _("Mark the ticket as resolved and restore the item to active status.")},
            {"icon": "insights",  "title": _("Analyze"),  "desc": _("View maintenance history and cost per asset for ROI decisions.")},
        ],
        "benefits": [
            _("Reduce unplanned downtime with preventive scheduling"),
            _("Track maintenance costs per asset over its lifetime"),
            _("Immediate visibility into items currently under repair"),
            _("Alert when maintenance exceeds expected duration"),
        ],
    },
    {
        "slug": "reports-analytics",
        "name": _("Reports & Analytics"),
        "icon": "bar_chart",
        "tagline": _("Turn inventory data into actionable decisions."),
        "description": _(
            "From real-time dashboards to scheduled PDF reports, Monium gives you the data "
            "you need to make informed asset decisions. Export to CSV for custom analysis, "
            "or receive weekly summary emails directly in your inbox."
        ),
        "for_whom": [
            _("CFOs and finance teams needing asset valuation"),
            _("Operations managers monitoring sector performance"),
            _("Auditors requiring documented asset registers"),
            _("Directors wanting executive summary dashboards"),
        ],
        "steps": [
            {"icon": "dashboard",      "title": _("Dashboard"), "desc": _("Real-time overview of inventory status, alerts, and trends.")},
            {"icon": "picture_as_pdf", "title": _("PDF"),       "desc": _("Generate formatted inventory reports ready for printing or emailing.")},
            {"icon": "download",       "title": _("CSV Export"),"desc": _("Export any filtered view to CSV for use in Excel or BI tools.")},
            {"icon": "schedule_send",  "title": _("Schedule"),  "desc": _("Set up weekly or monthly report emails delivered automatically.")},
        ],
        "benefits": [
            _("Ready-made audit reports in one click"),
            _("CSV compatibility with Excel, Power BI, and Google Sheets"),
            _("Executive dashboard accessible from any device"),
            _("Trend analysis to anticipate asset replacement needs"),
        ],
    },
    {
        "slug": "qr-labels",
        "name": _("QR Code Labels"),
        "icon": "qr_code_2",
        "tagline": _("Scan any asset and get its full history instantly."),
        "description": _(
            "Generate print-ready QR code label sheets for your entire inventory. "
            "Attach them to physical assets and scan from any smartphone to instantly "
            "view or update item details, current location, and loan status."
        ),
        "for_whom": [
            _("Asset managers labeling physical equipment"),
            _("Warehouse teams doing quick inventory checks"),
            _("IT departments tagging computers and peripherals"),
            _("Schools labeling books, furniture, and lab equipment"),
        ],
        "steps": [
            {"icon": "select_all",      "title": _("Select"), "desc": _("Choose items or categories to generate labels for.")},
            {"icon": "print",           "title": _("Print"),  "desc": _("Download a PDF label sheet ready for standard label printers.")},
            {"icon": "attach_file",     "title": _("Attach"), "desc": _("Stick labels on assets — done once, useful forever.")},
            {"icon": "qr_code_scanner", "title": _("Scan"),   "desc": _("Any smartphone camera scans the QR and opens the item's full profile.")},
        ],
        "benefits": [
            _("Eliminate manual item lookup during physical audits"),
            _("Compatible with standard A4 label sheets"),
            _("No app installation needed to scan"),
            _("Instant access to full asset history on scan"),
        ],
    },
    {
        "slug": "team-management",
        "name": _("Team Management"),
        "icon": "group",
        "tagline": _("Collaborate with your entire team, with proper access control."),
        "description": _(
            "Create accounts for your team directly, with a role assigned right away to control "
            "what each person can see and do. Operators can register items, while managers and "
            "admins get broader access. Every action is logged with the responsible user for full "
            "accountability."
        ),
        "for_whom": [
            _("Organizations with multiple departments accessing inventory"),
            _("Operations managers delegating data entry"),
            _("Security-conscious teams needing role separation"),
            _("Businesses with external auditors needing read-only access"),
        ],
        "steps": [
            {"icon": "person_add",      "title": _("Create"),  "desc": _("Create an account for each team member directly from the Members page.")},
            {"icon": "manage_accounts", "title": _("Assign"),  "desc": _("Set roles: Admin, Manager, Operator, or Viewer.")},
            {"icon": "verified_user",   "title": _("Control"), "desc": _("Each role sees and can do only what's relevant to their function.")},
            {"icon": "history",         "title": _("Audit"),   "desc": _("Full action log: who changed what, when, and from where.")},
        ],
        "benefits": [
            _("Delegate data entry without losing control"),
            _("Prevent unauthorized changes with role-based access"),
            _("Full audit trail for compliance and security"),
            _("Onboard new team members in under 2 minutes"),
        ],
    },
]

SERVICES_BY_SLUG = {s["slug"]: s for s in SERVICES}

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

FAQ_ITEMS = [
    {
        "question": _("Is Monium really free?"),
        "answer": _(
            "Yes. Monium is open source and free to use, with no usage limits, no paid "
            "tiers, and no credit card required. You self-host it on your own "
            "infrastructure, so there's no subscription to manage."
        ),
    },
    {
        "question": _("How do I self-host Monium?"),
        "answer": _(
            "Monium ships with a Docker Compose setup covering the app, PostgreSQL, "
            "and a background worker. Clone the repository, configure your "
            "environment variables, and run it with Docker Compose to have your own "
            "instance running in minutes."
        ),
    },
    {
        "question": _("Where is my data stored?"),
        "answer": _(
            "Entirely on the infrastructure you choose to run Monium on. Since it's "
            "self-hosted, no data is sent to or stored by a third-party service — you "
            "have full control over your database and backups."
        ),
    },
    {
        "question": _("Are there limits on items, users, or organizations?"),
        "answer": _(
            "No. Monium has no built-in limits on the number of items, users, or "
            "organizations you can create. The only constraints are the resources of "
            "the server you run it on."
        ),
    },
    {
        "question": _("How is my data protected?"),
        "answer": _(
            "Monium supports TLS in transit when deployed behind a reverse proxy like "
            "Nginx, and stores data in PostgreSQL, which you can back up on your own "
            "schedule. Since you control the infrastructure, security and backup "
            "policies are up to you."
        ),
    },
    {
        "question": _("Can I import my existing inventory from Excel or CSV?"),
        "answer": _(
            "Yes. Monium supports bulk import via CSV. Download the template, fill it "
            "in with your existing data, and upload — items are created in seconds."
        ),
    },
    {
        "question": _("Does Monium have a mobile app?"),
        "answer": _(
            "Monium is a fully responsive web app that works on any smartphone browser. "
            "QR code label scanning works via any mobile camera without installing an app."
        ),
    },
    {
        "question": _("Can I contribute or request a feature?"),
        "answer": _(
            "Yes. Monium is open source — issues and pull requests are welcome on the "
            "project's repository."
        ),
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
        ctx["services"] = SERVICES[:3]
        ctx["differentials"] = DIFFERENTIALS
        return ctx


class ServicesView(TemplateView):
    template_name = "pages/services/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["services"] = SERVICES
        return ctx


class ServiceDetailView(TemplateView):
    template_name = "pages/services/detail.html"

    def get(self, request, slug, *args, **kwargs):
        self.service = SERVICES_BY_SLUG.get(slug)
        if not self.service:
            from django.http import Http404
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["service"] = self.service
        ctx["other_services"] = [s for s in SERVICES if s["slug"] != self.service["slug"]][:3]
        return ctx


class FAQView(TemplateView):
    template_name = "pages/faq.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["faq_items"] = FAQ_ITEMS
        return ctx


class PrivacyView(TemplateView):
    template_name = "pages/privacy.html"


class TermsView(TemplateView):
    template_name = "pages/terms.html"
