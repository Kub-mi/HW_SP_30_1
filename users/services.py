"""Сервисные функции для интеграции со Stripe."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Optional

import stripe
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


@dataclass(frozen=True)
class StripeSessionData:
    """Данные, возвращаемые после подготовки платежа в Stripe."""

    product: Dict[str, Any]
    price: Dict[str, Any]
    session: Dict[str, Any]

    @property
    def checkout_url(self) -> Optional[str]:
        return self.session.get("url")

    @property
    def product_id(self) -> str:
        return self.product["id"]

    @property
    def price_id(self) -> str:
        return self.price["id"]

    @property
    def session_id(self) -> str:
        return self.session["id"]


def _configure_stripe() -> None:
    api_key = getattr(settings, "STRIPE_SECRET_KEY", "")
    if not api_key:
        raise ImproperlyConfigured("Не указан ключ STRIPE_SECRET_KEY.")
    stripe.api_key = api_key


def _to_minor_currency_units(amount: Decimal) -> int:
    return int((amount * 100).quantize(Decimal("1")))


def create_stripe_session(*, name: str, description: str = "", amount: Decimal, metadata: Optional[Dict[str, str]] = None) -> StripeSessionData:
    """Создать продукт, цену и Checkout Session в Stripe."""

    _configure_stripe()

    currency = getattr(settings, "STRIPE_CURRENCY", "rub").lower()
    success_url = getattr(settings, "STRIPE_SUCCESS_URL", "https://example.com/success")
    cancel_url = getattr(settings, "STRIPE_CANCEL_URL", "https://example.com/cancel")

    metadata = metadata or {}

    product = stripe.Product.create(
        name=name,
        description=description,
        metadata=metadata,
    ).to_dict_recursive()

    price = stripe.Price.create(
        product=product["id"],
        unit_amount=_to_minor_currency_units(amount),
        currency=currency,
        metadata=metadata,
    ).to_dict_recursive()

    session = stripe.checkout.Session.create(
        success_url=success_url,
        cancel_url=cancel_url,
        mode="payment",
        payment_method_types=["card"],
        line_items=[{"price": price["id"], "quantity": 1}],
        metadata=metadata,
    ).to_dict_recursive()

    return StripeSessionData(product=product, price=price, session=session)
