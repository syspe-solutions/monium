from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views import View

from apps.organizations.services.onboarding_suggestion_service import OnboardingSuggestionService


class OrganizationOnboardingView(LoginRequiredMixin, View):
    template_name = "organizations/onboarding.html"

    def get(self, request):
        organization = request.organization
        suggestions = OnboardingSuggestionService.get_suggestions(organization.industry)
        return render(request, self.template_name, {
            "suggestions": suggestions,
            "is_first": request.user.memberships.count() == 1,
        })

    def post(self, request):
        category_names = request.POST.getlist("categories")
        sector_names = request.POST.getlist("sectors")

        if category_names or sector_names:
            OnboardingSuggestionService.apply(category_names, sector_names, request.user)
            messages.success(request, _("Suggestions applied! You're ready to register your first assets."))

        return redirect("inventory:home")
