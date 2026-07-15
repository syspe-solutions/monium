import hashlib
import hmac

import mercadopago
from django.conf import settings


def _client() -> mercadopago.SDK:
    return mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)


def create_preapproval(user, plan: dict, payer_email: str, back_url: str) -> str:
    """Cria uma assinatura recorrente (preapproval) no Mercado Pago e retorna a URL de checkout.

    external_reference carrega user_id e plan_id (separados por ':') pra o webhook
    saber pra qual plano promover a assinatura quando o pagamento for confirmado."""
    sdk = _client()
    preference_data = {
        "reason": f"Monium — Plano {plan['name']}",
        "external_reference": f"{user.id}:{plan['id']}",
        "payer_email": payer_email,
        "back_url": back_url,
        "auto_recurring": {
            "frequency": 1,
            "frequency_type": "months",
            "transaction_amount": float(plan["price"]),
            "currency_id": "BRL",
        },
        "status": "pending",
    }
    response = sdk.preapproval().create(preference_data)
    return response["response"]["init_point"]


def get_preapproval(preapproval_id: str) -> dict:
    sdk = _client()
    return sdk.preapproval().get(preapproval_id)["response"]


def verify_webhook_signature(request) -> bool:
    """Valida a assinatura HMAC do webhook (x-signature/x-request-id), se um secret estiver configurado."""
    secret = settings.MERCADO_PAGO_WEBHOOK_SECRET
    if not secret:
        return True

    signature_header = request.headers.get("x-signature", "")
    request_id = request.headers.get("x-request-id", "")
    data_id = request.GET.get("data.id", "")

    parts = dict(part.split("=", 1) for part in signature_header.split(",") if "=" in part)
    ts = parts.get("ts")
    received_hash = parts.get("v1")
    if not ts or not received_hash:
        return False

    manifest = f"id:{data_id};request-id:{request_id};ts:{ts};"
    expected_hash = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_hash, received_hash)
