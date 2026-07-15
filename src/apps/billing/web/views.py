import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.billing import services
from apps.billing.gateways import mercadopago_gateway
from apps.billing.models import Subscription, SubscriptionStatus
from apps.billing.plans import PLANS, PLANS_BY_ID

logger = logging.getLogger(__name__)


class PlansView(LoginRequiredMixin, TemplateView):
    template_name = "billing/plans.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        current_plan_id = services.get_plan_for_user(self.request.user)["id"]
        ctx["plans"] = [
            {**plan, "cta_disabled": plan["id"] == current_plan_id}
            for plan in PLANS
        ]
        return ctx


class SubscribeView(LoginRequiredMixin, View):
    def post(self, request, plan_id):
        plan = PLANS_BY_ID.get(plan_id)
        if not plan or not plan.get("price"):
            messages.error(request, "Plano inválido para assinatura online. Fale com nosso time.")
            return redirect("billing:plans")

        back_url = request.build_absolute_uri(reverse("billing:plans"))

        try:
            checkout_url = mercadopago_gateway.create_preapproval(
                user=request.user,
                plan=plan,
                payer_email=request.user.email,
                back_url=back_url,
            )
        except Exception:
            logger.exception("Falha ao criar preapproval no Mercado Pago para user=%s plan=%s", request.user.id, plan_id)
            messages.error(request, "Não foi possível iniciar o checkout agora. Tente novamente em instantes.")
            return redirect("billing:plans")

        return redirect(checkout_url)


@method_decorator(csrf_exempt, name="dispatch")
class MercadoPagoWebhookView(View):
    def post(self, request):
        if not mercadopago_gateway.verify_webhook_signature(request):
            return HttpResponseBadRequest("invalid signature")

        topic = request.GET.get("topic") or request.GET.get("type")
        preapproval_id = request.GET.get("id") or request.GET.get("data.id")

        if topic != "preapproval" or not preapproval_id:
            return HttpResponse(status=200)

        try:
            preapproval = mercadopago_gateway.get_preapproval(preapproval_id)
        except Exception:
            logger.exception("Falha ao buscar preapproval %s no Mercado Pago", preapproval_id)
            return HttpResponse(status=200)

        external_reference = preapproval.get("external_reference") or ""
        user_id, _, referenced_plan_id = external_reference.partition(":")
        mp_status = preapproval.get("status")
        if not user_id:
            return HttpResponse(status=200)

        status_map = {
            "authorized": SubscriptionStatus.ACTIVE,
            "paused": SubscriptionStatus.PAST_DUE,
            "cancelled": SubscriptionStatus.CANCELED,
        }
        status = status_map.get(mp_status)
        if status is None:
            return HttpResponse(status=200)

        update_fields = {"status": status, "mp_preapproval_id": preapproval_id}
        if status == SubscriptionStatus.ACTIVE and referenced_plan_id:
            update_fields["plan_id"] = referenced_plan_id
        elif status == SubscriptionStatus.CANCELED:
            update_fields["plan_id"] = "free"

        Subscription.objects.filter(user_id=user_id).update(**update_fields)

        return HttpResponse(status=200)
