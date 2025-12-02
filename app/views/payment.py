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
    current_app.logger.info(f"Страница подписки: user={current_user.username}")

    prices = current_app.config.get("SUBSCRIPTION_PRICES", {})

    period = request.values.get("period")
    amount = request.values.get("amount")

    if period and amount:
        try:
            amount_float = float(amount)
            return_url = url_for("payment.payment_success", _external=True)

            payment_service = YooKassaService()
            payment_info = payment_service.create_payment(
                current_user, return_url, float(amount)
            )
            if payment_info.get("payment_url"):
                return redirect(payment_info["payment_url"])

            flash("Ошибка создания платежа. Попробуйте позже.", "error")

        except Exception as e:
            current_app.logger.error(f"Ошибка создания платежа: {e}")
            flash("Не удалось создать платеж.", "error")

    return render_template(
        "payment/subscription.html",
        prices=prices,
        payment_url=None,
        payment_id=None,
    )


@payment_bp.route("/api/yookassa/webhook", methods=["POST"])
def payment_webhook() -> Tuple[str, int]:

    try:
        data = request.json
        current_app.logger.info(f"Webhook ЮKassa: {data}")

        if not data:
            current_app.logger.error("Webhook пуст")
            return "OK", 200

        event = data.get("event")
        obj = data.get("object", {})

        payment_id = obj.get("id")
        status = obj.get("status")
        paid = obj.get("paid")

        if not payment_id:
            current_app.logger.error("Webhook без payment_id")
            return "OK", 200

        PaymentService.process_payment_webhook(
            event=event,
            payment_data=obj,
        )

        return "OK", 200

    except Exception as e:
        current_app.logger.error(f"Ошибка обработки webhook: {e}")
        return "OK", 200


@payment_bp.route("/payment/success")
@login_required
def payment_success() -> Union[str, Response]:
    payment_id = request.args.get("payment_id")

    if not payment_id:
        flash("Платеж не найден.", "warning")
        return redirect(url_for("payment.subscription"))

    payment_record = Payment.query.filter_by(
        yookassa_payment_id=payment_id, user_id=current_user.id
    ).first()

    if not payment_record:
        flash("Платеж не найден.", "error")
        return redirect(url_for("payment.subscription"))

    status = payment_record.status

    if status == "succeeded":
        flash("Подписка активирована!", "success")

    elif status == "pending" or status == "waiting_for_capture":
        flash(
            "Платёж обрабатывается. Подписка будет активирована автоматически.", "info"
        )

    elif status == "canceled":
        flash("Платёж отменён.", "error")
        return redirect(url_for("payment.payment_cancel", payment_id=payment_id))

    else:
        flash(f"Статус платежа: {status}", "warning")

    return render_template("payment/success.html", status=status)


@payment_bp.route("/payment/cancel")
@login_required
def payment_cancel() -> str:
    payment_id = request.args.get("payment_id")
    flash("Платёж отменён.", "error")
    return render_template("payment/cancel.html")


@payment_bp.route("/payment/status", methods=["GET", "POST"])
@login_required
def payment_status() -> str:
    form = PaymentStatusForm()
    if form.validate_on_submit():
        payment_id = form.payment_id.data
        status = YooKassaService().get_payment_status(payment_id)
        flash(f"Статус: {status.get('status')}", "info")

    return render_template("payment/payment_status.html", form=form)


@payment_bp.route("/api/payment/status/<payment_id>")
@login_required
def api_payment_status(payment_id: str):
    status = YooKassaService().get_payment_status(payment_id)
    return jsonify(status)
