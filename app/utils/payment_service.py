import base64
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict

import requests
from flask import current_app

from ..models import Payment, User, db


class YooKassaService:
    def __init__(self) -> None:
        self.shop_id = current_app.config["YOOKASSA_SHOP_ID"]
        self.secret_key = current_app.config["YOOKASSA_SECRET_KEY"]
        self.base_url = "https://api.yookassa.ru/v3"
        if not self.shop_id or not self.secret_key:
            current_app.logger.warning("Ключи ЮKassa не настроены, используется режим симуляции")
            self.simulation_mode = True
        else:
            self.simulation_mode = False
            current_app.logger.info("Режим реальных платежей ЮKassa активирован")

    def _get_auth_header(self) -> str:
        auth_string = f"{self.shop_id}:{self.secret_key}"
        return base64.b64encode(auth_string.encode()).decode()

    def _get_subscription_days(self, amount: float) -> int:
        prices = current_app.config["SUBSCRIPTION_PRICES"]
        if amount == prices.get("1", 99.0):
            return 30
        elif amount == prices.get("3", 249.0):
            return 90
        elif amount == prices.get("6", 449.0):
            return 180
        elif amount == prices.get("12", 749.0):
            return 365
        else:
            current_app.logger.warning(f"Неизвестная сумма платежа: {amount}, используем 30 дней")
            return 30

    def _make_api_request(
        self, endpoint: str, method: str = "GET", data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        if self.simulation_mode:
            current_app.logger.info(f"Симуляция API запроса: {method} {endpoint}")
            return {"simulation": True, "status": "success"}
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Basic {self._get_auth_header()}",
            "Content-Type": "application/json",
            "Idempotence-Key": str(uuid.uuid4()),
        }
        try:
            timeout = 30
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
            else:
                raise ValueError(f"Неподдерживаемый HTTP метод: {method}")
            if response.status_code == 200:
                return response.json()
            else:
                current_app.logger.error(
                    f"Ошибка API ЮKassa: {response.status_code} - {response.text}"
                )
                return {"error": f"HTTP {response.status_code}"}
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Ошибка сетевого запроса к ЮKassa: {str(e)}")
            return {"error": str(e)}

    def create_smart_payment(
        self, user: User, return_url: str, price: float = None
    ) -> Dict[str, Any]:
        payment_id = str(uuid.uuid4())
        current_app.logger.info(f"Получена цена в payment_service: {price} (тип: {type(price)})")
        if price is not None:
            try:
                payment_price = float(price)
                if payment_price > 0:
                    current_app.logger.info(f"Используем переданную цену: {payment_price}₽")
                else:
                    payment_price = current_app.config["SUBSCRIPTION_PRICES"]["1"]
                    current_app.logger.warning(
                        f"Цена <= 0, используем цену по умолчанию: {payment_price}₽"
                    )
            except (ValueError, TypeError):
                payment_price = current_app.config["SUBSCRIPTION_PRICES"]["1"]
                current_app.logger.warning(
                    f"Ошибка конвертации цены '{price}', используем цену по умолчанию: {payment_price}₽"
                )
        else:
            payment_price = current_app.config["SUBSCRIPTION_PRICES"]["1"]
            current_app.logger.warning(
                f"Цена не передана, используем цену по умолчанию: {payment_price}₽"
            )
        current_app.logger.info(
            f"Создание платежа: ID={payment_id}, Пользователь={user.username}, Цена={payment_price}₽"
        )
        try:
            if self.simulation_mode:
                current_app.logger.info("Симуляция создания платежа в ЮKassa")
                payment_record = Payment(
                    user_id=user.id,
                    yookassa_payment_id=payment_id,
                    amount=payment_price,
                    currency=current_app.config["SUBSCRIPTION_CURRENCY"],
                    status="pending",
                    description=f"Подписка - {payment_price}₽",
                )
                db.session.add(payment_record)
                db.session.commit()
                current_app.logger.info(f"Платеж сохранен в БД: {payment_id}")
                from flask import url_for

                success_url = url_for(
                    "main.payment_success",
                    payment_id=payment_id,
                    _external=True,
                )
                current_app.logger.info(f"Симуляционный URL создан: {success_url}")
                return {
                    "payment_id": payment_id,
                    "payment_url": success_url,
                    "status": "pending",
                    "amount": payment_price,
                    "currency": current_app.config["SUBSCRIPTION_CURRENCY"],
                }
            else:
                payment_data = {
                    "amount": {
                        "value": str(payment_price),
                        "currency": current_app.config["SUBSCRIPTION_CURRENCY"],
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": return_url,
                    },
                    "capture": True,
                    "description": f"Подписка для пользователя {user.username} - {payment_price}₽",
                    "metadata": {
                        "user_id": str(user.id),
                        "username": user.username,
                    },
                }
                if user.email:
                    payment_data["receipt"] = {
                        "customer": {"email": user.email},
                        "items": [
                            {
                                "description": "Подписка на образовательную платформу cysu",
                                "quantity": "1",
                                "amount": {
                                    "value": str(payment_price),
                                    "currency": current_app.config["SUBSCRIPTION_CURRENCY"],
                                },
                                "vat_code": 1,
                                "payment_subject": "service",
                                "payment_mode": "full_prepayment",
                            }
                        ],
                    }
                    current_app.logger.info(
                        f"Receipt добавлен для пользователя {user.username} с email: {user.email}"
                    )
                else:
                    current_app.logger.warning(
                        f"Receipt не добавлен - у пользователя {user.username} нет email"
                    )
                current_app.logger.info(f"Отправляем данные платежа в ЮKassa: {payment_data}")
                api_response = self._make_api_request("payments", "POST", payment_data)
                if "error" in api_response:
                    current_app.logger.error(
                        f"Ошибка создания платежа в ЮKassa: {api_response['error']}"
                    )
                    raise Exception(f"Ошибка ЮKassa: {api_response['error']}")
                payment_record = Payment(
                    user_id=user.id,
                    yookassa_payment_id=api_response.get("id", payment_id),
                    amount=payment_price,
                    currency=current_app.config["SUBSCRIPTION_CURRENCY"],
                    status=api_response.get("status", "pending"),
                    description=f"Подписка - {payment_price}₽",
                )
                db.session.add(payment_record)
                db.session.commit()
                current_app.logger.info(
                    f"Платеж сохранен в БД: {api_response.get('id', payment_id)}"
                )
                return {
                    "payment_id": api_response.get("id", payment_id),
                    "payment_url": api_response.get("confirmation", {}).get("confirmation_url"),
                    "status": api_response.get("status", "pending"),
                    "amount": payment_price,
                    "currency": current_app.config["SUBSCRIPTION_CURRENCY"],
                }
        except Exception as e:
            current_app.logger.error(f"Ошибка при создании платежа: {str(e)}")
            raise e

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        try:
            current_app.logger.info(f"Получение статуса платежа: {payment_id}")
            payment_record = Payment.query.filter_by(yookassa_payment_id=payment_id).first()
            if not payment_record:
                current_app.logger.error(f"Платеж {payment_id} не найден в базе данных")
                return {"error": "Платеж не найден"}
            if self.simulation_mode:
                current_app.logger.info(f"Симуляционный режим: проверяем платеж {payment_id}")
                current_app.logger.info(f"Время создания: {payment_record.created_at}")
                current_app.logger.info(f"Текущее время: {datetime.utcnow()}")
                current_app.logger.info(f"Разница: {datetime.utcnow() - payment_record.created_at}")
                if (datetime.utcnow() - payment_record.created_at) > timedelta(minutes=5):
                    payment_record.status = "canceled"
                    payment_record.updated_at = datetime.utcnow()
                    db.session.commit()
                    current_app.logger.info(
                        f"Симуляция: платеж {payment_id} помечен как отмененный (таймаут)"
                    )
                    return {
                        "payment_id": payment_id,
                        "status": "canceled",
                        "amount": str(payment_record.amount),
                        "currency": "RUB",
                        "description": "Подписка на образовательную платформу",
                        "created_at": payment_record.created_at.isoformat(),
                        "paid": False,
                    }
                else:
                    payment_record.status = "pending"
                    payment_record.updated_at = datetime.utcnow()
                    db.session.commit()
                    current_app.logger.info(f"Симуляция: платеж {payment_id} в обработке")
                    return {
                        "payment_id": payment_id,
                        "status": "pending",
                        "amount": str(payment_record.amount),
                        "currency": "RUB",
                        "description": "Подписка на образовательную платформу",
                        "created_at": payment_record.created_at.isoformat(),
                        "paid": False,
                    }
            else:
                api_response = self._make_api_request(f"payments/{payment_id}")
                if "error" in api_response:
                    current_app.logger.error(
                        f"Ошибка получения статуса платежа: {api_response['error']}"
                    )
                    return api_response
                payment_record.status = api_response.get("status", "pending")
                payment_record.updated_at = datetime.utcnow()
                db.session.commit()
                return {
                    "payment_id": payment_id,
                    "status": api_response.get("status", "pending"),
                    "amount": api_response.get("amount", {}).get(
                        "value", str(payment_record.amount)
                    ),
                    "currency": api_response.get("amount", {}).get("currency", "RUB"),
                    "description": api_response.get(
                        "description", "Подписка на образовательную платворму"
                    ),
                    "created_at": api_response.get(
                        "created_at", payment_record.created_at.isoformat()
                    ),
                    "paid": api_response.get("paid", False),
                }
        except Exception as e:
            current_app.logger.error(f"Ошибка при получении статуса платежа {payment_id}: {str(e)}")
            return {"error": str(e)}

    def process_successful_payment(self, payment_id: str) -> bool:
        try:
            current_app.logger.info(f"Обработка платежа: {payment_id}")
            payment_record = Payment.query.filter_by(yookassa_payment_id=payment_id).first()
            if not payment_record:
                current_app.logger.error(f"Платеж {payment_id} не найден в базе данных")
                return False
            payment_status = self.get_payment_status(payment_id)
            if payment_status.get("status") != "succeeded":
                current_app.logger.warning(
                    f"Платеж {payment_id} не успешен: {payment_status.get('status')}"
                )
                return False
            user = User.query.get(payment_record.user_id)
            if user:
                user.is_subscribed = True
                subscription_days = self._get_subscription_days(payment_record.amount)
                user.subscription_expires = datetime.utcnow() + timedelta(days=subscription_days)
                payment_record.status = "succeeded"
                payment_record.updated_at = datetime.utcnow()
                db.session.commit()
                current_app.logger.info(
                    f"Подписка активирована для пользователя {user.username} на {subscription_days} дней"
                )
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Ошибка при обработке платежа {payment_id}: {str(e)}")
            return False

    def check_user_subscription(self, user: User) -> bool:
        now = datetime.utcnow()
        trial_active = False
        if user.is_trial_subscription:
            if user.trial_subscription_expires and user.trial_subscription_expires < now:
                user.is_trial_subscription = False
                user.trial_subscription_expires = None
                db.session.commit()
                current_app.logger.info(f"Пробная подписка пользователя {user.username} истекла")
            else:
                trial_active = True
        regular_active = False
        if user.is_subscribed:
            if user.is_manual_subscription:
                current_app.logger.info(
                    f"Пользователь {user.username} имеет ручно выданную подписку"
                )
                if user.subscription_expires and user.subscription_expires < now:
                    user.is_subscribed = False
                    user.is_manual_subscription = False
                    db.session.commit()
                    current_app.logger.info(f"Ручная подписка пользователя {user.username} истекла")
                else:
                    regular_active = True
            else:
                successful_payment = (
                    Payment.query.filter_by(user_id=user.id, status="succeeded")
                    .order_by(Payment.created_at.desc())
                    .first()
                )
                if not successful_payment:
                    user.is_subscribed = False
                    db.session.commit()
                    current_app.logger.warning(
                        f"Пользователь {user.username} имеет подписку без успешного платежа - сброс"
                    )
                elif user.subscription_expires and user.subscription_expires < now:
                    user.is_subscribed = False
                    db.session.commit()
                else:
                    regular_active = True
        if trial_active and regular_active:
            trial_expires = user.trial_subscription_expires or now
            regular_expires = user.subscription_expires or now
            if regular_expires > trial_expires:
                user.is_trial_subscription = False
                user.trial_subscription_expires = None
                db.session.commit()
                current_app.logger.info(
                    f"Пользователь {user.username} имеет обычную подписку, отключаем тестовую"
                )
                return True
            else:
                user.is_subscribed = False
                user.is_manual_subscription = False
                db.session.commit()
                current_app.logger.info(
                    f"Пользователь {user.username} имеет тестовую подписку, отключаем обычную"
                )
                return True
        return trial_active or regular_active

    def get_subscription_info(self, user: User) -> dict:
        now = datetime.utcnow()
        trial_active = False
        trial_expires = None
        if user.is_trial_subscription:
            if not user.trial_subscription_expires:
                trial_active = True
                trial_expires = None
            elif user.trial_subscription_expires < now:
                user.is_trial_subscription = False
                user.trial_subscription_expires = None
                db.session.commit()
            else:
                trial_active = True
                trial_expires = user.trial_subscription_expires
        regular_active = False
        regular_expires = None
        subscription_type = "none"
        if user.is_subscribed:
            if user.is_manual_subscription:
                if user.subscription_expires and user.subscription_expires < now:
                    user.is_subscribed = False
                    user.is_manual_subscription = False
                    db.session.commit()
                else:
                    regular_active = True
                    regular_expires = user.subscription_expires
                    subscription_type = "manual"
            else:
                successful_payment = (
                    Payment.query.filter_by(user_id=user.id, status="succeeded")
                    .order_by(Payment.created_at.desc())
                    .first()
                )
                if not successful_payment:
                    user.is_subscribed = False
                    db.session.commit()
                elif user.subscription_expires and user.subscription_expires < now:
                    user.is_subscribed = False
                    db.session.commit()
                else:
                    regular_active = True
                    regular_expires = user.subscription_expires
                    subscription_type = "paid"
        if trial_active and regular_active:
            trial_expires = trial_expires or now
            regular_expires = regular_expires or now
            if regular_expires > trial_expires:
                user.is_trial_subscription = False
                user.trial_subscription_expires = None
                db.session.commit()
                trial_active = False
            else:
                user.is_subscribed = False
                user.is_manual_subscription = False
                db.session.commit()
                regular_active = False
        if trial_active:
            time_left = trial_expires - now if trial_expires else None
            days_left = time_left.days if time_left else None
            return {
                "is_subscribed": True,
                "is_trial": True,
                "expires_at": trial_expires,
                "days_left": days_left,
                "type": "trial",
            }
        elif regular_active:
            time_left = regular_expires - now if regular_expires else None
            days_left = time_left.days if time_left else None
            return {
                "is_subscribed": True,
                "is_trial": False,
                "expires_at": regular_expires,
                "days_left": days_left,
                "type": subscription_type,
            }
        else:
            return {
                "is_subscribed": False,
                "is_trial": False,
                "expires_at": None,
                "days_left": 0,
                "type": "none",
            }

    def get_trial_subscription_info(self, user: User) -> dict:
        if not user.is_trial_subscription:
            return {"is_trial": False, "days_left": 0, "expires_at": None}
        if not user.trial_subscription_expires:
            return {"is_trial": True, "days_left": 0, "expires_at": None}
        now = datetime.utcnow()
        if user.trial_subscription_expires < now:
            user.is_trial_subscription = False
            user.trial_subscription_expires = None
            db.session.commit()
            return {"is_trial": False, "days_left": 0, "expires_at": None}
        time_left = user.trial_subscription_expires - now
        days_left = time_left.days
        hours_left = time_left.seconds // 3600
        return {
            "is_trial": True,
            "days_left": days_left,
            "hours_left": hours_left,
            "expires_at": user.trial_subscription_expires,
            "total_hours_left": days_left * 24 + hours_left,
        }
