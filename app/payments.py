from __future__ import annotations
from base64 import b64encode
from dataclasses import dataclass
import httpx
from .config import settings

@dataclass(frozen=True)
class PaymentResult:
    provider: str
    payment_id: str | None
    confirmation_url: str | None
    status: str
    configured: bool

class PaymentGateway:
    """Provider-agnostic payment boundary. Live charging is disabled by default."""
    def health(self) -> dict:
        return {"provider": settings.payment_provider or None,
                "configured": bool(settings.payment_shop_id and settings.payment_secret_key),
                "live_enabled": settings.payment_live_enabled}

    async def create_payment(self, *, amount_minor: int, currency: str, description: str,
                             return_url: str, metadata: dict[str, str] | None = None,
                             idempotency_key: str | None = None) -> PaymentResult:
        if not settings.payment_shop_id or not settings.payment_secret_key:
            return PaymentResult("yookassa", None, None, "NOT_CONFIGURED", False)
        if not settings.payment_live_enabled:
            return PaymentResult("yookassa", None, None, "DISABLED", True)
        if settings.payment_provider != "yookassa":
            raise RuntimeError("Unsupported payment provider")
        if not idempotency_key or len(idempotency_key) > 64:
            raise RuntimeError("Idempotency-Key is required for live payments and must be <= 64 characters")
        if currency.upper() != "RUB":
            raise RuntimeError("Only RUB payments are enabled until currency handling is verified")
        trusted_return_url = settings.payment_return_url.strip()
        if not trusted_return_url.startswith("https://"):
            raise RuntimeError("PAYMENT_RETURN_URL must be configured as a trusted HTTPS URL before live payments")
        return_url = trusted_return_url
        auth = b64encode(f"{settings.payment_shop_id}:{settings.payment_secret_key}".encode()).decode()
        body = {"amount": {"value": f"{amount_minor / 100:.2f}", "currency": currency.upper()},
                "capture": True, "description": description[:128],
                "confirmation": {"type": "redirect", "return_url": return_url},
                "metadata": metadata or {}}
        async with httpx.AsyncClient(timeout=settings.payment_timeout_seconds) as client:
            response = await client.post("https://api.yookassa.ru/v3/payments",
                headers={"Authorization": f"Basic {auth}", "Idempotence-Key": idempotency_key, "Content-Type": "application/json"},
                json=body)
        if response.status_code >= 400:
            raise RuntimeError("Payment provider rejected the request")
        data = response.json()
        confirmation = data.get("confirmation") or {}
        return PaymentResult("yookassa", data.get("id"), confirmation.get("confirmation_url"),
                             data.get("status", "pending"), True)
