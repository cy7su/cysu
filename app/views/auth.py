from datetime import datetime, timedelta
from typing import Union

from flask import (
    Blueprint,
    Response,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from .. import db, login_manager
from ..forms import (
    EmailVerificationForm,
    LoginForm,
    PasswordResetForm,
    PasswordResetRequestForm,
    RegistrationForm,
)
from ..models import EmailVerification, PasswordReset, SiteSettings, User
from ..utils.email_service import EmailService
from ..utils.notifications import redirect_with_notification

auth_bp = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id: str):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        current_app.logger.error(f"Error loading user {user_id}: {e}")
        return None


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        # Пытаемся найти пользователя по username или email
        user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.username.data)
        ).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect_with_notification("main.index", "Вход выполнен успешно", "success")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    current_app.logger.info(f"Регистрация - метод: {request.method}")

    if form.validate_on_submit():
        current_app.logger.info(
            f"Форма валидна, проверяем данные: {form.username.data}, {form.email.data}"
        )
        try:
            existing_user = User.query.filter(
                (User.username == form.username.data)
                | (User.email == form.email.data)
            ).first()

            if existing_user:
                error_msg = f'Пользователь с именем "{form.username.data}" уже существует' if existing_user.username == form.username.data else f'Пользователь с email "{form.email.data}" уже существует'
                return render_template("auth/register.html", form=form, error=error_msg)

            session["pending_registration"] = {
                "username": form.username.data,
                "email": form.email.data,
                "password": form.password.data,
                "group_id": form.group_id.data,
            }

            verification = EmailVerification.create_verification(
                email=form.email.data
            )
            db.session.add(verification)
            db.session.commit()

            current_app.logger.info(
                f"Verification code created for pending registration ({form.email.data}): {' '.join(verification.code)} (type: {type(verification.code)}, length: {len(verification.code)})"
            )

            current_app.logger.info(
                f"Attempting to send verification email to {form.email.data}"
            )

            # Проверяем, включен ли режим разработки (пропускаем email)
            debug_mode = current_app.config.get("DEBUG", False)
            skip_email = current_app.config.get(
                "SKIP_EMAIL_VERIFICATION", False
            )

            current_app.logger.info(
                f"Debug mode: {debug_mode}, Skip email: {skip_email}"
            )

            if debug_mode or skip_email:
                current_app.logger.info(
                    f"Debug mode: skipping email send, code is {verification.code}"
                )
                session["pending_verification_id"] = verification.id
                return redirect_with_notification("auth.email_verification", f"Режим разработки: код подтверждения - {verification.code}", "info")

            email_sent = EmailService.send_verification_email(
                form.email.data, verification.code
            )
            current_app.logger.info(f"Email send result: {email_sent}")

            if email_sent:
                session["pending_verification_id"] = verification.id
                return redirect_with_notification("auth.email_verification", "Проверьте вашу почту для подтверждения email", "info")
            else:
                db.session.delete(verification)
                db.session.commit()
                return render_template("auth/register.html", form=form, error="Ошибка отправки email. Попробуйте еще раз")

        except Exception as e:
            current_app.logger.error(
                f"Ошибка при обработке регистрации: {str(e)}"
            )
            db.session.rollback()
            return render_template("auth/register.html", form=form, error="Ошибка при обработке регистрации. Попробуйте еще раз")
    else:
        current_app.logger.warning(f"Форма не валидна: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                current_app.logger.warning(f"Ошибка в поле {field}: {error}")

    return render_template("auth/register.html", form=form)


@auth_bp.route("/email/verification", methods=["GET", "POST"])
def email_verification() -> Union[str, Response]:
    verification_id = session.get("pending_verification_id")
    pending_registration = session.get("pending_registration")

    if not verification_id or not pending_registration:
        flash("Сначала зарегистрируйтесь.")
        return redirect(url_for("auth.register"))

    form = EmailVerificationForm()

    if request.method == "POST" and form.validate():
        verification = EmailVerification.query.filter_by(
            id=verification_id, code=form.code.data, is_used=False
        ).first()

        if verification and verification.expires_at > datetime.utcnow():
            try:
                hashed_password = generate_password_hash(
                    pending_registration["password"]
                )
                trial_enabled = SiteSettings.get_setting(
                    "trial_subscription_enabled", True
                )
                trial_days = int(
                    SiteSettings.get_setting("trial_subscription_days", 7)
                )

                user = User(
                    username=pending_registration["username"],
                    email=pending_registration["email"],
                    password=hashed_password,
                    is_verified=True,  # Пользователь подтвержден
                    group_id=(
                        pending_registration.get("group_id")
                        if pending_registration.get("group_id")
                        else None
                    ),
                    is_trial_subscription=trial_enabled,  # Активируем пробную подписку только если включено
                    trial_subscription_expires=(
                        datetime.utcnow() + timedelta(days=trial_days)
                        if trial_enabled
                        else None
                    ),  # Используем настройку количества дней
                )
                db.session.add(user)
                db.session.commit()

                verification.user_id = user.id
                verification.email = None
                verification.is_used = True
                db.session.commit()

                current_app.logger.info(
                    f"User created and email verified: {user.username} ({user.email}) with code: {' '.join(form.code.data)}"
                )

                session.pop("pending_verification_id", None)
                session.pop("pending_registration", None)

                return redirect_with_notification("auth.login", "Регистрация успешно завершена! Теперь вы можете войти в систему", "success")

            except Exception as e:
                current_app.logger.error(
                    f"Ошибка при создании пользователя после подтверждения: {str(e)}"
                )
                db.session.rollback()
                return redirect_with_notification("auth.register", "Ошибка при завершении регистрации. Попробуйте еще раз", "error")
        else:
            # Добавляем ошибку к полю формы вместо flash сообщения
            form.code.errors.append("Неверный код или код истек. Попробуйте еще раз.")
    elif request.method == "POST":
        # Если форма не валидна, добавляем ошибку
        if not form.code.data:
            form.code.errors.append("Введите код подтверждения.")
        else:
            form.code.errors.append("Неверный код или код истек. Попробуйте еще раз.")

    return render_template(
        "auth/email_verification.html",
        form=form,
        user_email=pending_registration["email"],
    )


@auth_bp.route("/email/resend", methods=["GET", "POST"])
def resend_verification() -> Union[str, Response]:
    verification_id = session.get("pending_verification_id")
    pending_registration = session.get("pending_registration")

    if not verification_id or not pending_registration:
        flash("Сначала зарегистрируйтесь.")
        return redirect(url_for("auth.register"))

    try:
        EmailVerification.query.filter_by(
            id=verification_id, is_used=False
        ).delete()

        verification = EmailVerification.create_verification(
            email=pending_registration["email"]
        )
        db.session.add(verification)
        db.session.commit()

        current_app.logger.info(
            f"New verification code created for pending registration ({pending_registration['email']}): {' '.join(verification.code)}"
        )

        session["pending_verification_id"] = verification.id

        EmailService.send_resend_verification_email(
            pending_registration["email"], verification.code
        )

    except Exception as e:
        current_app.logger.error(
            f"Ошибка при повторной отправке кода: {str(e)}"
        )
        db.session.rollback()
        flash("Ошибка при отправке кода. Попробуйте еще раз.")

    return redirect(url_for("auth.email_verification"))


@auth_bp.route("/password/reset", methods=["GET", "POST"])
def password_reset_request() -> Union[str, Response]:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if user:
            PasswordReset.query.filter_by(email=email, is_used=False).delete()

            reset = PasswordReset.create_reset(email)
            db.session.add(reset)
            db.session.commit()

            current_app.logger.info(
                f"Password reset code created for {email}: {' '.join(reset.code)}"
            )

            if EmailService.send_password_reset_email(email, reset.code):
                flash(
                    "Код восстановления отправлен на вашу почту. Проверьте email и введите код.",
                    "info",
                )
                return redirect(url_for("auth.password_reset_confirm"))
            else:
                flash("Ошибка отправки email. Попробуйте позже.", "error")
        else:
            flash(
                "Если указанный email зарегистрирован, код восстановления будет отправлен.",
                "info",
            )
            return redirect(url_for("auth.password_reset_confirm"))

    return render_template("auth/password_reset_request.html", form=form)


@auth_bp.route("/password/reset/confirm", methods=["GET", "POST"])
def password_reset_confirm() -> Union[str, Response]:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = PasswordResetForm()
    if form.validate_on_submit():
        code = form.code.data
        new_password = form.new_password.data

        reset = (
            PasswordReset.query.filter_by(code=code, is_used=False)
            .filter(PasswordReset.expires_at > datetime.utcnow())
            .first()
        )

        if reset:
            user = User.query.filter_by(email=reset.email).first()
            if user:
                user.password = generate_password_hash(new_password)
                reset.is_used = True
                db.session.commit()

                current_app.logger.info(
                    f"Password reset successful for user {user.username} ({user.email})"
                )
                flash(
                    "Пароль успешно изменен! Теперь вы можете войти с новым паролем.",
                    "success",
                )
                return redirect(url_for("auth.login"))
            else:
                flash("Ошибка: пользователь не найден.", "error")
        else:
            flash("Неверный код или код истек. Попробуйте еще раз.", "error")

    return render_template("auth/password_reset_confirm.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout() -> Response:
    logout_user()
    return redirect(url_for("main.index"))
