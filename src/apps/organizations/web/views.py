from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import TemplateView

from apps.billing import services as billing_services
from apps.organizations.middleware import ACTIVE_ORG_SESSION_KEY
from apps.organizations.mixins import (
    OrganizationNotLockedRequiredMixin,
    OrganizationOwnerRequiredMixin,
)
from apps.organizations.models import Invitation, InvitationStatus, Membership, MembershipRole
from apps.organizations.services.invitation_email_service import send_invitation_email

from .forms import InvitationForm, InvitationSignupForm, OrganizationForm

User = get_user_model()


class OrganizationCreateView(LoginRequiredMixin, View):
    template_name = "organizations/create.html"

    def get(self, request):
        if request.user.organization is None:
            return render(request, self.template_name, {"form": OrganizationForm(), "is_first": True})

        if not billing_services.can_create_organization(request.user):
            messages.error(request, "Você atingiu o limite de organizações do seu plano. Faça upgrade para criar mais.")
            return redirect("billing:plans")

        return render(request, self.template_name, {"form": OrganizationForm(), "is_first": False})

    def post(self, request):
        is_first = request.user.organization is None
        if not is_first and not billing_services.can_create_organization(request.user):
            messages.error(request, "Você atingiu o limite de organizações do seu plano. Faça upgrade para criar mais.")
            return redirect("billing:plans")

        form = OrganizationForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "is_first": is_first})

        organization = form.save(commit=False)
        organization.created_by = request.user
        organization.updated_by = request.user
        organization.save()
        Membership.objects.create(
            organization=organization,
            user=request.user,
            role=MembershipRole.OWNER,
            created_by=request.user,
        )
        request.session[ACTIVE_ORG_SESSION_KEY] = str(organization.id)

        messages.success(request, f'Organização "{organization.name}" criada com sucesso.')
        return redirect("inventory:home")


class SwitchOrganizationView(LoginRequiredMixin, View):
    def post(self, request, organization_id):
        is_member = Membership.objects.filter(organization_id=organization_id, user=request.user).exists()
        if not is_member:
            raise PermissionDenied("Você não é membro dessa organização.")

        request.session[ACTIVE_ORG_SESSION_KEY] = str(organization_id)

        next_url = request.POST.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect("inventory:home")


class OrganizationSettingsView(LoginRequiredMixin, OrganizationOwnerRequiredMixin, View):
    template_name = "organizations/settings.html"

    def get(self, request):
        form = OrganizationForm(instance=request.organization)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = OrganizationForm(request.POST, instance=request.organization)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        organization = form.save(commit=False)
        organization.updated_by = request.user
        organization.save()

        messages.success(request, "Dados da organização atualizados com sucesso.")
        return redirect("organizations:settings")


class OrganizationMembersView(LoginRequiredMixin, OrganizationOwnerRequiredMixin, TemplateView):
    template_name = "organizations/members.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        organization = self.request.organization
        ctx["members"] = organization.memberships.select_related("user").order_by("role", "user__email")
        ctx["pending_invitations"] = organization.invitations.filter(
            status=InvitationStatus.PENDING
        ).order_by("-created_at")
        ctx["is_within_user_limit"] = billing_services.is_within_user_limit_including_pending(organization)
        return ctx


class OrganizationDeleteView(LoginRequiredMixin, View):
    template_name = "organizations/delete_confirm.html"

    def _get_organization_or_404(self, request, organization_id):
        return get_object_or_404(
            Membership, organization_id=organization_id, user=request.user, role=MembershipRole.OWNER
        ).organization

    def get(self, request, organization_id):
        organization = self._get_organization_or_404(request, organization_id)
        return render(request, self.template_name, {"organization": organization})

    def post(self, request, organization_id):
        organization = self._get_organization_or_404(request, organization_id)

        owned_count = billing_services.get_owned_organizations(request.user).count()
        if owned_count <= 1:
            messages.error(request, "Você precisa ter ao menos uma organização.")
            return redirect("organizations:members")

        confirmation = request.POST.get("confirmation_name", "").strip()
        if confirmation != organization.name:
            messages.error(request, "O nome digitado não confere. A organização não foi apagada.")
            return render(request, self.template_name, {"organization": organization})

        name = organization.name
        organization.delete()

        if request.session.get(ACTIVE_ORG_SESSION_KEY) == str(organization_id):
            del request.session[ACTIVE_ORG_SESSION_KEY]

        messages.success(request, f'Organização "{name}" apagada.')
        return redirect("inventory:home")


class MemberRemoveView(LoginRequiredMixin, OrganizationOwnerRequiredMixin, View):
    def post(self, request, membership_id):
        membership = get_object_or_404(Membership, id=membership_id, organization=request.organization)

        if membership.user_id == request.user.id:
            messages.error(request, "Você não pode remover a si mesmo da organização.")
            return redirect("organizations:members")

        if request.organization.memberships.count() <= 1:
            messages.error(request, "A organização precisa ter ao menos um membro.")
            return redirect("organizations:members")

        membership.delete()
        messages.success(request, "Membro removido da organização.")
        return redirect("organizations:members")


class InvitationRevokeView(LoginRequiredMixin, OrganizationOwnerRequiredMixin, View):
    def post(self, request, invitation_id):
        invitation = get_object_or_404(
            Invitation, id=invitation_id, organization=request.organization, status=InvitationStatus.PENDING
        )
        invitation.status = InvitationStatus.REVOKED
        invitation.updated_by = request.user
        invitation.save()

        messages.success(request, "Convite revogado.")
        return redirect("organizations:members")


class InvitationCreateView(LoginRequiredMixin, OrganizationOwnerRequiredMixin, OrganizationNotLockedRequiredMixin, View):
    def post(self, request):
        organization = request.organization
        if not billing_services.is_within_user_limit_including_pending(organization):
            messages.error(request, "Você atingiu o limite de membros do seu plano.")
            return redirect("organizations:members")

        form = InvitationForm(request.POST, organization=organization)
        if not form.is_valid():
            for error in form.errors.get("email", []):
                messages.error(request, error)
            return redirect("organizations:members")

        invitation = Invitation.objects.create(
            organization=organization,
            email=form.cleaned_data["email"],
            created_by=request.user,
        )
        accept_url = request.build_absolute_uri(
            reverse("organizations:invitation_accept", args=[invitation.token])
        )
        send_invitation_email(invitation, accept_url)

        messages.success(request, f"Convite enviado para {invitation.email}.")
        return redirect("organizations:members")


class InvitationAcceptView(View):
    template_name = "organizations/invitation_accept.html"

    def get(self, request, token):
        invitation = get_object_or_404(Invitation, token=token)
        return self._render_state(request, invitation)

    def post(self, request, token):
        invitation = get_object_or_404(Invitation, token=token)

        if invitation.status != InvitationStatus.PENDING or invitation.is_expired:
            return self._render_state(request, invitation)

        if request.user.is_authenticated:
            if request.user.email.lower() != invitation.email:
                return self._render_state(request, invitation)
            return self._accept(request, invitation, request.user)

        if User.objects.filter(email__iexact=invitation.email).exists():
            return self._render_state(request, invitation)

        form = InvitationSignupForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"invitation": invitation, "state": "signup", "form": form})

        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=invitation.email,
            password=form.cleaned_data["password"],
        )
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return self._accept(request, invitation, user)

    def _accept(self, request, invitation, user):
        if not billing_services.is_within_user_limit(invitation.organization):
            return render(request, self.template_name, {"invitation": invitation, "state": "org_full"})

        Membership.objects.get_or_create(
            organization=invitation.organization,
            user=user,
            defaults={"role": invitation.role, "created_by": invitation.created_by},
        )
        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_at = timezone.now()
        invitation.accepted_by = user
        invitation.save()

        request.session[ACTIVE_ORG_SESSION_KEY] = str(invitation.organization_id)
        messages.success(request, f"Você agora faz parte de {invitation.organization.name}.")
        return redirect("inventory:home")

    def _render_state(self, request, invitation):
        if invitation.status != InvitationStatus.PENDING or invitation.is_expired:
            return render(request, self.template_name, {"invitation": invitation, "state": "invalid"})

        if request.user.is_authenticated:
            if request.user.email.lower() == invitation.email:
                return render(request, self.template_name, {"invitation": invitation, "state": "confirm"})
            return render(request, self.template_name, {"invitation": invitation, "state": "mismatch"})

        if User.objects.filter(email__iexact=invitation.email).exists():
            return render(request, self.template_name, {"invitation": invitation, "state": "login_required"})

        return render(request, self.template_name, {
            "invitation": invitation, "state": "signup", "form": InvitationSignupForm()
        })
