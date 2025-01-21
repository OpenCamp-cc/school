from typing import Any, Dict, List

import stripe
from stripe import PaymentIntent


class StripeClient:
    client: stripe.StripeClient

    def __init__(self, api_key):
        self.client = stripe.StripeClient(api_key)
        stripe.api_key = api_key

    def create_payment_intent(self, amount: int, currency: str) -> PaymentIntent:
        return stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            automatic_payment_methods={'enabled': True},
        )

    def get_payment_intent(self, intent_id: str) -> PaymentIntent:
        return stripe.PaymentIntent.retrieve(intent_id)

    def create_checkout_session(
        self, redirect_url: str, email: str, items: List[Dict[str, Any]]
    ):
        return self.client.checkout.sessions.create(
            {
                'customer_email': email,
                'line_items': items,  # type: ignore
                'mode': 'payment',
                'ui_mode': 'embedded',
                'allow_promotion_codes': True,
                'return_url': redirect_url,
            }
        )

    def get_checkout_session(self, session_id: str):
        return stripe.checkout.Session.retrieve(session_id)
