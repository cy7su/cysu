import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Union

from .. import db
from ..models import Payment, User


class PaymentService:
    """Сервис для управления платежами и подписками"""

    @staticmethod
    def create_subscription_payment(
        user: User,
        period: str,
        amount: float
    ) -> Tuple[Optional[str], str]:
        """Создать платеж для подписки"""
        try:
            from flask import url_for, current_app
            from ..utils.payment_service import YooKassaService

            if not period or not amount:
                return None, "Период и сумма обязательны"

            try:
                amount_float = float(amount)
                if amount_float <= 0:
                    return None, "Сумма должна быть положительной"
            except ValueError:
                return None, "Неверный формат суммы"

            # Создаем платеж через YooKassa
            payment_service = YooKassaService()
            return_url = url_for("payment.payment_success", _external=True)
            return_url += "?source=yookassa"

            payment_info = payment_service.create_smart_payment(
                user, return_url, amount_float
            )

            if payment_info.get("payment_url"):
                return payment_info["payment_url"], f"Платеж на {amount_float} руб. создан"
            else:
                return None, "Ошибка создания платежа"

        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"Ошибка создания платежа: {str(e)}")
            return None, "Ошибка при создании платежа"

    @staticmethod
    def process_payment_webhook(event: str, payment_data: Dict) -> bool:
        """Обработать webhook от платежной системы"""
        try:
            payment_id = payment_data.get("id")
            status = payment_data.get("status", "pending")
            paid = payment_data.get("paid", False)

            if not payment_id:
                return False

            # Находим платеж в БД
            payment_record = Payment.query.filter_by(
                yookassa_payment_id=payment_id
            ).first()

            if not payment_record:
                return False

            # Обновляем статус платежа
            payment_record.status = status
            payment_record.updated_at = datetime.utcnow()

            # Обрабатываем успешный платеж
            if status == "succeeded" and paid:
                success = PaymentService._activate_subscription_for_payment(payment_record)
                if success:
                    from flask import current_app
                    current_app.logger.info(f"Подписка активирована для платежа {payment_id}")
                else:
                    from flask import current_app
                    current_app.logger.warning(f"Ошибка активации подписки для платежа {payment_id}")

            # Обрабатываем отмененный платеж
            elif status == "canceled":
                success = PaymentService._deactivate_subscription_for_payment(payment_record)
                if success:
                    from flask import current_app
                    current_app.logger.info(f"Подписка деактивирована для платежа {payment_id}")

            db.session.commit()
            return True

        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"Ошибка обработки webhook: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def _activate_subscription_for_payment(payment_record: Payment) -> bool:
        """Активировать подписку для успешного платежа"""
        try:
            user = User.query.get(payment_record.user_id)
            if not user:
                return False

            user.is_subscribed = True

            # Вычисляем срок подписки
            from ..utils.payment_service import YooKassaService
            payment_service = YooKassaService()
            subscription_days = payment_service._get_subscription_days(payment_record.amount)
            user.subscription_expires = datetime.utcnow() + timedelta(days=subscription_days)

            db.session.commit()
            return True

        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"Ошибка активации подписки: {str(e)}")
            return False

    @staticmethod
    def _deactivate_subscription_for_payment(payment_record: Payment) -> bool:
        """Деактивировать подписку для отмененного платежа"""
        try:
            user = User.query.get(payment_record.user_id)
            if not user:
                return False

            user.is_subscribed = False
            user.subscription_expires = None

            db.session.commit()
            return True

        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"Ошибка деактивации подписки: {str(e)}")
            return False

    @staticmethod
    def check_payment_status(payment_id: str, user: User) -> Tuple[str, str]:
        """Проверить статус платежа для пользователя"""
        try:
            from ..utils.payment_service import YooKassaService

            # Находим платеж в БД
            payment_record = Payment.query.filter_by(
                yookassa_payment_id=payment_id,
                user_id=user.id
            ).first()

            if not payment_record:
                # Ищем по ID если принадлежит другому пользователю
                payment_record = Payment.query.filter_by(
                    yookassa_payment_id=payment_id
                ).first()

                if payment_record:
                    return "error", "Платеж не принадлежит вам"
                else:
                    return "error", "Платеж не найден"

            # Получаем статус от платежной системы
            payment_service = YooKassaService()
            status_info = payment_service.get_payment_status(payment_id)

            if "error" in status_info:
                # Обрабатываем в режиме симуляции
                if payment_service.simulation_mode or "HTTP 401" in str(status_info["error"]):
                    if payment_service.process_successful_payment(payment_id):
                        return "succeeded", "Платеж успешно обработан"
                    else:
                        return "error", "Ошибка активации подписки"
                else:
                    return "error", f"Ошибка проверки: {status_info['error']}"

            return status_info.get("status", "unknown"), f"Статус: {status_info.get('status', 'неизвестен')}"

        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"Ошибка проверки статуса платежа: {str(e)}")
            return "error", "Ошибка проверки статуса"

    @staticmethod
    def cancel_payment(payment_id: str, user: User) -> Tuple[bool, str]:
        """Отменить платеж"""
        try:
            payment_record = Payment.query.filter_by(
                yookassa_payment_id=payment_id
            ).first()

            if payment_record:
                if payment_record.user_id != user.id:
                    return False, "Платеж не принадлежит вам"

                payment_record.status = "canceled"
                payment_record.updated_at = datetime.utcnow()
                db.session.commit()

                # Деактивируем подписку
                PaymentService._deactivate_subscription_for_payment(payment_record)

                return True, "Платеж отменен"
            else:
                return False, "Платеж не найден"

        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"Ошибка отмены платежа: {str(e)}")
            db.session.rollback()
            return False, "Ошибка отмены платежа"

    @staticmethod
    def get_subscription_prices() -> Dict:
        """Получить цены подписок"""
        try:
            from flask import current_app
            return current_app.config.get("SUBSCRIPTION_PRICES", {})
        except Exception:
            return {}
