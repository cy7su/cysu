from typing import Tuple, Union

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from ..forms import PaymentStatusForm
from ..models import Payment
from ..services import PaymentService
from ..utils.payment_service import YooKassaService

payment_bp = Blueprint("payment", __name__)


@payment_bp.route("/subscription", methods=["GET", "POST"])
@login_required
def subscription() -> Union[str, Response]:
    current_app.logger.info(f"Запрос страницы подписки для пользователя: {current_user.username}")
    current_app.logger.info(f"Все параметры запроса: {dict(request.args)}")
    current_app.logger.info(f"URL запроса: {request.url}")
    current_app.logger.info(f"Метод запроса: {request.method}")
    try:
        prices = current_app.config["SUBSCRIPTION_PRICES"]
    except Exception as e:
        current_app.logger.error(f"Error getting subscription prices: {e}")
        prices = {}
        flash("Ошибка загрузки цен подписки.", "error")
    period = request.args.get("period")
    amount = request.args.get("amount")
    if period and amount:
        try:
            current_app.logger.info(f"Создание платежа - period: {period}, amount: {amount}")
            payment_service = YooKassaService()
            current_app.logger.info("Сервис платежей создан")
            return_url = url_for("payment.payment_success", _external=True)
            current_app.logger.info(f"Return URL: {return_url}")
            return_url += "?source=yookassa"
            current_app.logger.info(f"Return URL с параметром: {return_url}")
            current_app.logger.info(
                f"Передаем цену в payment_service: {amount} (тип: {type(amount)})"
            )
            payment_info = payment_service.create_smart_payment(
                current_user, return_url, float(amount)
            )
            current_app.logger.info(
                f"Платеж создан: {payment_info['payment_id']} с суммой: {payment_info.get('amount')}"
            )
            if payment_info.get("payment_url"):
                current_app.logger.info(
                    f"Перенаправление на страницу оплаты: {payment_info['payment_url']}"
                )
                return redirect(payment_info["payment_url"])
            else:
                current_app.logger.error("URL для оплаты не получен от ЮKassa")
                flash("Ошибка создания платежа. Попробуйте позже.", "error")
                return render_template(
                    "payment/subscription.html",
                    payment_url=None,
                    payment_id=None,
                    prices=prices,
                )
        except Exception as e:
            current_app.logger.error(f"Ошибка при создании платежа: {str(e)}")
            import traceback

            current_app.logger.error(f"Traceback: {traceback.format_exc()}")
            flash(
                "Произошла ошибка при создании платежа. Попробуйте позже.",
                "error",
            )
            return render_template("payment/subscription.html", payment_url=None, prices=prices)
    current_app.logger.info("Показываем страницу выбора подписки")
    return render_template(
        "payment/subscription.html",
        payment_url=None,
        payment_id=None,
        prices=prices,
    )


@payment_bp.route("/payment/webhook", methods=["POST"])
def payment_webhook() -> Tuple[str, int]:
    try:
        data = request.get_json()
        current_app.logger.info(f"Получен webhook от ЮKassa: {data}")
        if not data:
            current_app.logger.error("Пустые данные в webhook")
            return "OK", 200
        event = data.get("event")
        payment_data = data.get("object", {})
        payment_id = payment_data.get("id")
        if not payment_id:
            current_app.logger.error("Payment ID не найден в webhook")
            return "OK", 200
        current_app.logger.info(f"Обработка webhook: event={event}, payment_id={payment_id}")
        success = PaymentService.process_payment_webhook(event, payment_data)
        if success:
            current_app.logger.info(f"Webhook обработан успешно: payment_id={payment_id}")
        else:
            current_app.logger.error(f"Ошибка обработки webhook: payment_id={payment_id}")
        return "OK", 200
    except Exception as e:
        current_app.logger.error(f"Ошибка обработки webhook: {str(e)}")
        return "OK", 200


@payment_bp.route("/payment/success")
@login_required
def payment_success() -> Union[str, Response]:
    current_app.logger.info("=== ВХОД В PAYMENT_SUCCESS ===")
    current_app.logger.info(f"Все параметры запроса: {dict(request.args)}")
    current_app.logger.info(f"Полный URL: {request.url}")
    payment_id = request.args.get("payment_id")
    source = request.args.get("source")
    current_app.logger.info(f"Обработка платежа: {payment_id}, источник: {source}")
    current_app.logger.info(f"Пользователь: {current_user.username}")
    if source == "yookassa":
        current_app.logger.info("Обнаружен возврат от ЮKassa - проверяем статус платежа")
        payment_service = YooKassaService()
        if payment_id:
            payment_status = payment_service.get_payment_status(payment_id)
            current_app.logger.info(f"Статус платежа от ЮKassa: {payment_status}")
            if payment_status.get("status") == "canceled":
                current_app.logger.info("Платеж отменен - перенаправляем на страницу отмены")
                return redirect(url_for("payment.payment_cancel", payment_id=payment_id))
            elif payment_status.get("status") == "pending":
                current_app.logger.info("Платеж в обработке - показываем страницу ожидания")
                flash(
                    "Платеж в обработке. Подписка будет активирована после подтверждения оплаты.",
                    "info",
                )
                return render_template("payment/pending.html")
    if request.args.get("cancel") == "true":
        current_app.logger.info("Обнаружена отмена платежа через параметр cancel")
        return redirect(url_for("payment.payment_cancel", payment_id=payment_id))
    if not payment_id:
        current_app.logger.info(
            "Payment ID не найден в параметрах, ищем последний платеж пользователя"
        )
        try:
            payment_record = (
                Payment.query.filter_by(user_id=current_user.id)
                .order_by(Payment.created_at.desc())
                .first()
            )
            if payment_record:
                payment_id = payment_record.yookassa_payment_id
                current_app.logger.info(f"Найден последний платеж: {payment_id}")
            else:
                current_app.logger.error("Платежи пользователя не найдены")
                current_app.logger.info("Попытка найти платеж по email пользователя")
                flash(
                    "Платеж не найден. Попробуйте оформить подписку снова.",
                    "warning",
                )
                return redirect(url_for("payment.subscription"))
        except Exception as e:
            current_app.logger.error(f"Error searching for user payments: {e}")
            flash(
                "Ошибка поиска платежей. Попробуйте оформить подписку снова.",
                "error",
            )
            return redirect(url_for("payment.subscription"))
    payment_service = YooKassaService()
    current_app.logger.info("Обработка платежа")
    try:
        payment_record = Payment.query.filter_by(
            yookassa_payment_id=payment_id, user_id=current_user.id
        ).first()
        if not payment_record:
            current_app.logger.error(
                f"Платеж {payment_id} не найден для пользователя {current_user.id}"
            )
            payment_record = Payment.query.filter_by(yookassa_payment_id=payment_id).first()
            if payment_record:
                current_app.logger.warning(
                    f"Платеж найден, но принадлежит другому пользователю: {payment_record.user_id}"
                )
                flash("Платеж не принадлежит вам.", "error")
                return redirect(url_for("main.index"))
            else:
                current_app.logger.error(f"Платеж {payment_id} не найден в базе данных")
                flash(
                    "Платеж не найден. Попробуйте оформить подписку снова.",
                    "warning",
                )
                return redirect(url_for("payment.subscription"))
    except Exception as e:
        current_app.logger.error(f"Error searching for payment {payment_id}: {e}")
        flash("Ошибка поиска платежа. Попробуйте позже.", "error")
        return redirect(url_for("main.index"))
    current_app.logger.info(f"Платеж найден: {payment_record.status}")
    payment_status = payment_service.get_payment_status(payment_id)
    current_app.logger.info(f"Статус платежа от ЮKassa: {payment_status}")
    if "error" in payment_status:
        current_app.logger.error(f"Ошибка получения статуса: {payment_status['error']}")
        if payment_service.simulation_mode or "HTTP 401" in str(payment_status["error"]):
            current_app.logger.info("Обработка платежа в режиме симуляции или при ошибке API")
            if payment_service.process_successful_payment(payment_id):
                current_app.logger.info("Подписка успешно активирована")
                flash(
                    "Платеж успешно обработан! Подписка активирована.",
                    "success",
                )
            else:
                current_app.logger.error("Ошибка при активации подписки")
                flash(
                    "Произошла ошибка при активации подписки. Обратитесь в поддержку.",
                    "error",
                )
        else:
            flash(
                f"Ошибка при проверке платежа: {payment_status['error']}. Обратитесь в поддержку.",
                "error",
            )
    elif payment_status.get("status") == "succeeded":
        current_app.logger.info("Платеж успешен, активируем подписку")
        if payment_service.process_successful_payment(payment_id):
            current_app.logger.info("Подписка успешно активирована")
            flash(
                "Подписка успешно оформлена! Теперь у вас есть доступ ко всем материалам.",
                "success",
            )
        else:
            current_app.logger.error("Ошибка при активации подписки")
            flash(
                "Произошла ошибка при активации подписки. Обратитесь в поддержку.",
                "error",
            )
    elif payment_status.get("status") == "pending":
        current_app.logger.info("Платеж в обработке")
        flash(
            "Платеж в обработке. Подписка будет активирована после подтверждения оплаты.",
            "info",
        )
    elif payment_status.get("status") == "canceled":
        current_app.logger.info("Платеж отменен - перенаправляем на страницу отмены")
        return redirect(url_for("payment.payment_cancel", payment_id=payment_id))
    elif payment_status.get("status") == "waiting_for_capture":
        current_app.logger.info("Платеж ожидает подтверждения")
        flash(
            "Платеж ожидает подтверждения. Подписка будет активирована после подтверждения.",
            "info",
        )
    else:
        current_app.logger.warning(f"Неизвестный статус: {payment_status.get('status')}")
        flash(
            f"Статус платежа: {payment_status.get('status', 'неизвестен')}. Обратитесь в поддержку.",
            "error",
        )
    return render_template("payment/success.html")


@payment_bp.route("/payment/cancel")
@login_required
def payment_cancel() -> str:
    payment_id = request.args.get("payment_id")
    current_app.logger.info(
        f"Отмена платежа: payment_id={payment_id}, пользователь={current_user.username}"
    )
    if payment_id:
        success, message = PaymentService.cancel_payment(payment_id, current_user)
        if success:
            flash(message, "warning")
        else:
            flash(message, "error")
    else:
        current_app.logger.info("Отмена платежа без payment_id")
        flash("Информация о платеже не найдена.", "error")
    return render_template("payment/cancel.html")


@payment_bp.route("/payment/status", methods=["GET", "POST"])
@login_required
def payment_status() -> str:
    form = PaymentStatusForm()
    if form.validate_on_submit():
        payment_id = form.payment_id.data
        try:
            payment_service = YooKassaService()
            status = payment_service.get_payment_status(payment_id)
            if "error" in status:
                flash(f"Ошибка при получении статуса: {status['error']}", "error")
            else:
                flash(f"Статус платежа: {status['status']}", "info")
        except Exception as e:
            current_app.logger.error(f"Error checking payment status: {e}")
            flash("Ошибка при проверке статуса платежа.", "error")
    return render_template("payment/payment_status.html", form=form)


@payment_bp.route("/api/payment/status/<payment_id>")
@login_required
def api_payment_status(payment_id: str) -> dict:
    try:
        payment_service = YooKassaService()
        status = payment_service.get_payment_status(payment_id)
        return jsonify(status)
    except Exception as e:
        current_app.logger.error(f"Error in api_payment_status: {e}")
        return jsonify({"error": "Internal server error"}), 500
