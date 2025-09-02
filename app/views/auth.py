"""
Модуль аутентификации и регистрации
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app, Response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from typing import Union

from ..models import User, EmailVerification, PasswordReset, SiteSettings
from ..forms import LoginForm, RegistrationForm, EmailVerificationForm, PasswordResetRequestForm, PasswordResetForm
from ..utils.email_service import EmailService
from .. import db, login_manager

auth_bp = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id: str):
    """Загрузчик пользователя для Flask-Login"""
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        current_app.logger.error(f"Error loading user {user_id}: {e}")
        return None


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    """Страница входа"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("main.index"))
        flash("Неверное имя пользователя или пароль")
    
    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    """Страница регистрации"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    form = RegistrationForm()
    current_app.logger.info(f"Регистрация - метод: {request.method}")

    if form.validate_on_submit():
        current_app.logger.info(
            f"Форма валидна, проверяем данные: {form.username.data}, {form.email.data}"
        )
        try:
            # Проверяем, что пользователь с таким username или email не существует
            existing_user = User.query.filter(
                (User.username == form.username.data) | (User.email == form.email.data)
            ).first()

            if existing_user:
                if existing_user.username == form.username.data:
                    flash(
                        f'Пользователь с именем "{form.username.data}" уже существует',
                        "error",
                    )
                else:
                    flash(
                        f'Пользователь с email "{form.email.data}" уже существует',
                        "error",
                    )
                return render_template("auth/register.html", form=form)

            # Сохраняем данные регистрации в сессии
            session["pending_registration"] = {
                "username": form.username.data,
                "email": form.email.data,
                "password": form.password.data,
                "group_id": form.group_id.data,
            }

            # Создаем временный код подтверждения
            verification = EmailVerification.create_verification(email=form.email.data)
            db.session.add(verification)
            db.session.commit()

            current_app.logger.info(
                f"Verification code created for pending registration ({form.email.data}): {' '.join(verification.code)} (type: {type(verification.code)}, length: {len(verification.code)})"
            )

            # Отправляем email с кодом
            if EmailService.send_verification_email(form.email.data, verification.code):
                flash("Проверьте вашу почту для подтверждения email.")
                session["pending_verification_id"] = verification.id
                return redirect(url_for("auth.email_verification"))
            else:
                flash("Ошибка отправки email. Попробуйте еще раз.")
                db.session.delete(verification)
                db.session.commit()

        except Exception as e:
            current_app.logger.error(f"Ошибка при обработке регистрации: {str(e)}")
            db.session.rollback()
            flash("Ошибка при обработке регистрации. Попробуйте еще раз.")
    else:
        current_app.logger.warning(f"Форма не валидна: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                current_app.logger.warning(f"Ошибка в поле {field}: {error}")

    return render_template("auth/register.html", form=form)


@auth_bp.route("/email/verification", methods=["GET", "POST"])
def email_verification() -> Union[str, Response]:
    """Страница подтверждения email"""
    verification_id = session.get("pending_verification_id")
    pending_registration = session.get("pending_registration")

    if not verification_id or not pending_registration:
        flash("Сначала зарегистрируйтесь.")
        return redirect(url_for("auth.register"))

    form = EmailVerificationForm()

    if form.validate_on_submit():
        # Проверяем код подтверждения
        verification = EmailVerification.query.filter_by(
            id=verification_id, code=form.code.data, is_used=False
        ).first()

        if verification and verification.expires_at > datetime.utcnow():
            # Код верный и не истек - создаем пользователя
            try:
                hashed_password = generate_password_hash(
                    pending_registration["password"]
                )
                # Проверяем настройку пробной подписки
                trial_enabled = SiteSettings.get_setting('trial_subscription_enabled', True)
                
                user = User(
                    username=pending_registration["username"],
                    email=pending_registration["email"],
                    password=hashed_password,
                    is_verified=True,  # Пользователь подтвержден
                    group_id=pending_registration.get("group_id") if pending_registration.get("group_id") else None,
                    is_trial_subscription=trial_enabled,  # Активируем пробную подписку только если включено
                    trial_subscription_expires=datetime.utcnow() + timedelta(days=14) if trial_enabled else None,  # 14 дней пробной подписки
                )
                db.session.add(user)
                db.session.commit()

                # Обновляем verification с правильным user_id и очищаем email
                verification.user_id = user.id
                verification.email = None
                verification.is_used = True
                db.session.commit()

                current_app.logger.info(
                    f"User created and email verified: {user.username} ({user.email}) with code: {' '.join(form.code.data)}"
                )

                # Очищаем сессию
                session.pop("pending_verification_id", None)
                session.pop("pending_registration", None)

                flash(
                    "Регистрация успешно завершена! Теперь вы можете войти в систему."
                )
                return redirect(url_for("auth.login"))

            except Exception as e:
                current_app.logger.error(
                    f"Ошибка при создании пользователя после подтверждения: {str(e)}"
                )
                db.session.rollback()
                flash("Ошибка при завершении регистрации. Попробуйте еще раз.")
                return redirect(url_for("auth.register"))
        else:
            flash("Неверный код или код истек. Попробуйте еще раз.")

    return render_template(
        "auth/email_verification.html",
        form=form,
        user_email=pending_registration["email"],
    )


@auth_bp.route("/email/resend", methods=["GET", "POST"])
def resend_verification() -> Union[str, Response]:
    """Повторная отправка кода подтверждения"""
    verification_id = session.get("pending_verification_id")
    pending_registration = session.get("pending_registration")

    if not verification_id or not pending_registration:
        flash("Сначала зарегистрируйтесь.")
        return redirect(url_for("auth.register"))

    try:
        # Удаляем старый код подтверждения
        EmailVerification.query.filter_by(id=verification_id, is_used=False).delete()

        # Создаем новый код подтверждения
        verification = EmailVerification.create_verification(
            email=pending_registration["email"]
        )
        db.session.add(verification)
        db.session.commit()

        current_app.logger.info(
            f"New verification code created for pending registration ({pending_registration['email']}): {' '.join(verification.code)}"
        )

        # Обновляем ID в сессии
        session["pending_verification_id"] = verification.id

        # Отправляем email с новым кодом
        if EmailService.send_resend_verification_email(
            pending_registration["email"], verification.code
        ):
            flash("Новый код подтверждения отправлен на ваш email.")
        else:
            flash("Ошибка отправки email. Попробуйте еще раз.")

    except Exception as e:
        current_app.logger.error(f"Ошибка при повторной отправке кода: {str(e)}")
        db.session.rollback()
        flash("Ошибка при отправке кода. Попробуйте еще раз.")

    return redirect(url_for("auth.email_verification"))


@auth_bp.route("/password/reset", methods=["GET", "POST"])
def password_reset_request() -> Union[str, Response]:
    """Страница запроса восстановления пароля"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if user:
            # Удаляем старые коды восстановления для этого email
            PasswordReset.query.filter_by(email=email, is_used=False).delete()

            # Создаем новый код восстановления
            reset = PasswordReset.create_reset(email)
            db.session.add(reset)
            db.session.commit()

            current_app.logger.info(
                f"Password reset code created for {email}: {' '.join(reset.code)}"
            )

            # Отправляем email с кодом
            if EmailService.send_password_reset_email(email, reset.code):
                flash(
                    "Код восстановления отправлен на вашу почту. Проверьте email и введите код.",
                    "info",
                )
                return redirect(url_for("auth.password_reset_confirm"))
            else:
                flash("Ошибка отправки email. Попробуйте позже.", "error")
        else:
            # Для безопасности не показываем, что email не найден
            flash(
                "Если указанный email зарегистрирован, код восстановления будет отправлен.",
                "info",
            )
            return redirect(url_for("auth.password_reset_confirm"))

    return render_template("auth/password_reset_request.html", form=form)


@auth_bp.route("/password/reset/confirm", methods=["GET", "POST"])
def password_reset_confirm() -> Union[str, Response]:
    """Страница подтверждения кода и смены пароля"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = PasswordResetForm()
    if form.validate_on_submit():
        code = form.code.data
        new_password = form.new_password.data

        # Ищем активный код восстановления
        reset = (
            PasswordReset.query.filter_by(code=code, is_used=False)
            .filter(PasswordReset.expires_at > datetime.utcnow())
            .first()
        )

        if reset:
            # Находим пользователя по email
            user = User.query.filter_by(email=reset.email).first()
            if user:
                # Обновляем пароль
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
    """Выход из системы"""
    logout_user()
    return redirect(url_for("main.index"))
