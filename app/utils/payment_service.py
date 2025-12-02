import base64
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import requests
from flask import current_app
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..models import Payment, User, db


class YooKassaService:
    def __init__(self) -> None:
        self.shop_id = current_app.config["YOOKASSA_SHOP_ID"]
        self.secret_key = current_app.config["YOOKASSA_SECRET_KEY"]
        self.base_url = "https://api.yookassa.ru/v3"

        if not self.shop_id or not self.secret_key:
            raise RuntimeError("YooKassa credentials are not configured!")

        current_app.logger.info("YooKassaService initialized for real payments")

        # Настройка сессии с retry
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods={
                "HEAD",
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "OPTIONS",
                "TRACE",
            },
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _auth_header(self) -> str:
        auth = f"{self.shop_id}:{self.secret_key}"
        return base64.b64encode(auth.encode()).decode()

    def _make_request(
        self, endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Basic {self._auth_header()}",
            "Content-Type": "application/json",
            "Idempotence-Key": str(uuid.uuid4()),
        }
        try:
            if method == "GET":
                resp = self.session.get(url, headers=headers, timeout=10)
            elif method == "POST":
                resp = self.session.post(url, headers=headers, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            current_app.logger.error(f"YooKassa request error ({method} {url}): {e}")
            return {"error": str(e)}

    def _get_subscription_days(self, amount: float) -> int:
        prices = current_app.config["SUBSCRIPTION_PRICES"]
        mapping = {
            prices.get("1"): 30,
            prices.get("3"): 90,
            prices.get("6"): 180,
            prices.get("12"): 365,
        }
        return mapping.get(amount, 30)

    def create_payment(
        self, user: User, return_url: str, amount: float
    ) -> Dict[str, Any]:
        payment_id = str(uuid.uuid4())
        payment_data = {
            "amount": {
                "value": str(amount),
                "currency": current_app.config["SUBSCRIPTION_CURRENCY"],
            },
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": f"Subscription for {user.username} - {amount}₽",
            "metadata": {"user_id": str(user.id), "username": user.username},
        }
        if user.email:
            payment_data["receipt"] = {
                "customer": {"email": user.email},
                "items": [
                    {
                        "description": "Subscription on CYSU platform",
                        "quantity": "1",
                        "amount": {
                            "value": str(amount),
                            "currency": current_app.config["SUBSCRIPTION_CURRENCY"],
                        },
                        "vat_code": 1,
                        "payment_subject": "service",
                        "payment_mode": "full_prepayment",
                    }
                ],
            }

        response = self._make_request("payments", method="POST", data=payment_data)
        if "error" in response:
            raise Exception(f"YooKassa payment creation failed: {response['error']}")

        payment_record = Payment(
            user_id=user.id,
            yookassa_payment_id=response.get("id", payment_id),
            amount=amount,
            currency=current_app.config["SUBSCRIPTION_CURRENCY"],
            status=response.get("status", "pending"),
            description=f"Subscription - {amount}₽",
        )
        db.session.add(payment_record)
        db.session.commit()

        return {
            "payment_id": payment_record.yookassa_payment_id,
            "payment_url": response.get("confirmation", {}).get("confirmation_url"),
            "status": payment_record.status,
            "amount": amount,
            "currency": payment_record.currency,
        }

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        payment_record = Payment.query.filter_by(yookassa_payment_id=payment_id).first()
        if not payment_record:
            return {"error": "Payment not found"}

        response = self._make_request(f"payments/{payment_id}")
        if "error" in response:
            return response

        payment_record.status = response.get("status", payment_record.status)
        db.session.commit()

        return {
            "payment_id": payment_id,
            "status": payment_record.status,
            "amount": str(payment_record.amount),
            "currency": payment_record.currency,
            "description": payment_record.description,
            "created_at": payment_record.created_at.isoformat(),
            "paid": response.get("paid", False),
        }

    def process_successful_payment(self, payment_id: str) -> bool:
        payment_record = Payment.query.filter_by(yookassa_payment_id=payment_id).first()
        if not payment_record:
            current_app.logger.error(f"Payment {payment_id} not found")
            return False

        status = self.get_payment_status(payment_id)
        if not status.get("paid"):
            return False

        user = User.query.get(payment_record.user_id)
        if not user:
            return False

        user.is_subscribed = True
        days = self._get_subscription_days(payment_record.amount)
        user.subscription_expires = datetime.utcnow() + timedelta(days=days)
        payment_record.status = "succeeded"
        db.session.commit()
        current_app.logger.info(
            f"Subscription activated for {user.username} for {days} days"
        )
        return True

    def check_user_subscription(self, user: User) -> bool:
        now = datetime.utcnow()
        active_trial = (
            user.is_trial_subscription
            and user.trial_subscription_expires
            and user.trial_subscription_expires > now
        )
        active_regular = (
            user.is_subscribed
            and user.subscription_expires
            and user.subscription_expires > now
        )
        return active_trial or active_regular

    def get_subscription_info(self, user: User) -> Dict[str, Any]:
        now = datetime.utcnow()
        info = {
            "is_subscribed": False,
            "is_trial": False,
            "expires_at": None,
            "days_left": 0,
            "type": "none",
        }

        if user.is_trial_subscription and user.trial_subscription_expires:
            if user.trial_subscription_expires > now:
                info.update(
                    {
                        "is_subscribed": True,
                        "is_trial": True,
                        "expires_at": user.trial_subscription_expires,
                        "days_left": (user.trial_subscription_expires - now).days,
                        "type": "trial",
                    }
                )
            else:
                user.is_trial_subscription = False
                user.trial_subscription_expires = None
                db.session.commit()

        if (
            user.is_subscribed
            and user.subscription_expires
            and user.subscription_expires > now
        ):
            info.update(
                {
                    "is_subscribed": True,
                    "is_trial": False,
                    "expires_at": user.subscription_expires,
                    "days_left": (user.subscription_expires - now).days,
                    "type": "paid",
                }
            )
        return info

    def get_trial_subscription_info(self, user: User) -> Dict[str, Any]:
        now = datetime.utcnow()
        if not user.is_trial_subscription or not user.trial_subscription_expires:
            return {"is_trial": False, "days_left": 0, "expires_at": None}

        if user.trial_subscription_expires < now:
            user.is_trial_subscription = False
            user.trial_subscription_expires = None
            db.session.commit()
            return {"is_trial": False, "days_left": 0, "expires_at": None}

        time_left = user.trial_subscription_expires - now
        days = time_left.days
        hours = time_left.seconds // 3600
        return {
            "is_trial": True,
            "days_left": days,
            "hours_left": hours,
            "expires_at": user.trial_subscription_expires,
            "total_hours_left": days * 24 + hours,
        }
