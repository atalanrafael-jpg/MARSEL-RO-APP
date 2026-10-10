import pytest

from app.config import settings
from app.payments import PaymentGateway


@pytest.mark.asyncio
async def test_live_payment_rejects_non_rub_currency(monkeypatch):
    monkeypatch.setattr(settings, "payment_shop_id", "test-shop")
    monkeypatch.setattr(settings, "payment_secret_key", "test-secret")
    monkeypatch.setattr(settings, "payment_live_enabled", True)
    monkeypatch.setattr(settings, "payment_provider", "yookassa")
    monkeypatch.setattr(settings, "payment_return_url", "https://marsel.example/payment-return")

    with pytest.raises(RuntimeError, match="Only RUB"):
        await PaymentGateway().create_payment(
            amount_minor=1000,
            currency="USD",
            description="test",
            return_url="https://attacker.example",
            idempotency_key="test-idempotency-key",
        )


@pytest.mark.asyncio
async def test_live_payment_requires_trusted_https_return_url(monkeypatch):
    monkeypatch.setattr(settings, "payment_shop_id", "test-shop")
    monkeypatch.setattr(settings, "payment_secret_key", "test-secret")
    monkeypatch.setattr(settings, "payment_live_enabled", True)
    monkeypatch.setattr(settings, "payment_provider", "yookassa")
    monkeypatch.setattr(settings, "payment_return_url", "")

    with pytest.raises(RuntimeError, match="PAYMENT_RETURN_URL"):
        await PaymentGateway().create_payment(
            amount_minor=1000,
            currency="RUB",
            description="test",
            return_url="https://attacker.example",
            idempotency_key="test-idempotency-key",
        )
