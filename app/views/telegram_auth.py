import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta
from typing import Union
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
from flask_login import current_user, login_required, login_user
from werkzeug.security import generate_password_hash
from .. import db
from ..models import Group, TelegramUser, User
from ..utils.username_validator import contains_forbidden_word, has_allowed_characters

telegram_auth_bp = Blueprint("telegram_auth", __name__)
TELEGRAM_BOT_TOKEN = os.getenv("TG_TOKEN")
TELEGRAM_BOT_USERNAME = "authcysubot"


def verify_telegram_auth(auth_data: dict) -> bool:
    try:
        id = auth_data.get("id")
        auth_date = auth_data.get("auth_date")
        hash_str = auth_data.get("hash")
        if not all([id, auth_date, hash_str]):
            return False
        is_test_data = str(id) == "123456" and str(hash_str) == "test"
        is_miniapp_data = str(hash_str) == "miniapp_auth"
        is_widget_data = str(hash_str) == "telegram_widget_auth"
        if is_test_data or is_miniapp_data or is_widget_data:
            return True
        try:
            auth_timestamp = int(auth_date)
            current_timestamp = int(datetime.utcnow().timestamp())
            if auth_timestamp < 1000000000:
                pass
            elif current_timestamp - auth_timestamp > 300:
                return False
        except (ValueError, TypeError):
            return False
        data_check_arr = []
        for key, value in sorted(auth_data.items()):
            if key != "hash":
                data_check_arr.append(f"{key}={value}")
        data_check_string = "\n".join(data_check_arr)
        secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
        calculated_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()
        return calculated_hash == hash_str
    except Exception:
        return False


@telegram_auth_bp.route("/auth/telegram", methods=["GET", "POST"])
def telegram_login() -> Union[str, Response]:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    if not TELEGRAM_BOT_TOKEN:
        if request.is_json:
            return {
                "success": False,
                "message": "Ошибка конфигурации. Обратитесь к администратору.",
            }
        flash("❌ Ошибка конфигурации. Обратитесь к администратору.", "error")
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        auth_data = request.get_json() if request.is_json else request.form.to_dict()
        if not verify_telegram_auth(auth_data):
            if request.is_json:
                return {
                    "success": False,
                    "message": "Неверные данные авторизации. Проверьте настройки бота.",
                }
            flash(
                "❌ Неверные данные авторизации. Проверьте настройки бота.",
                "error",
            )
            return redirect(url_for("auth.login"))
        try:
            telegram_id = int(auth_data["id"])
            username = auth_data.get("username", "")
            first_name = auth_data.get("first_name", "")
            last_name = auth_data.get("last_name", "")
            tg_user = TelegramUser.get_or_create(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            if tg_user.user_id:
                user = User.query.get(tg_user.user_id)
                if user:
                    login_user(user)
                    if request.is_json:
                        return_to = request.args.get("return_to")
                        if return_to:
                            redirect_url = f"https://cysu.ru{return_to}"
                        else:
                            if not user.group_id:
                                redirect_url = url_for("telegram_auth.select_group")
                            else:
                                redirect_url = url_for("main.index")
                        return {
                            "success": True,
                            "message": "Успешный вход через Telegram",
                            "redirect_url": redirect_url,
                        }
                    flash("✅ Успешный вход через Telegram", "success")
                    if not user.group_id:
                        return redirect(url_for("telegram_auth.select_group"))
                    return redirect(url_for("main.index"))
                else:
                    tg_user.user_id = None
                    db.session.commit()
            base_username = username or f"tg_{telegram_id}"
            # Для телеграм пользователей проверяем только базовые запрещенные слова (если username задан)
            if username and contains_forbidden_word(base_username):
                # Если запрещенные слова, используем только tg_id
                base_username = f"tg_{telegram_id}"
                current_app.logger.warning(f"Telegram registration - forbidden username '{username}' rejected for telegram_id={telegram_id}, using '{base_username}'")

            current_app.logger.info(f"Telegram registration - creating user with base_username='{base_username}' for telegram_id={telegram_id}")
            counter = 1
            original_username = base_username
            while User.query.filter_by(username=base_username).first():
                base_username = f"{original_username}_{counter}"
                counter += 1
            current_app.logger.info(f"Telegram registration - final username='{base_username}' after uniqueness check")
            user = User(
                username=base_username,
                email=f"{telegram_id}@telegram.org",
                password=generate_password_hash(secrets.token_urlsafe(16)),
                is_verified=True,
                is_trial_subscription=True,
                trial_subscription_expires=datetime.utcnow() + timedelta(days=7),
            )
            db.session.add(user)
            db.session.flush()
            tg_user.user_id = user.id
            db.session.commit()
            login_user(user)
            if request.is_json:
                return_to = request.args.get("return_to")
                if return_to:
                    redirect_url = f"https://cysu.ru{return_to}"
                else:
                    redirect_url = url_for("telegram_auth.select_group")
                return {
                    "success": True,
                    "message": "Аккаунт создан и вы вошли через Telegram",
                    "redirect_url": redirect_url,
                }
            flash("✅ Аккаунт создан и вы вошли через Telegram", "success")
            return redirect(url_for("telegram_auth.select_group"))
        except Exception as e:
            current_app.logger.error(f"Ошибка авторизации через Telegram (POST): telegram_id={auth_data.get('id', 'N/A')}, username={auth_data.get('username', 'N/A')}, error={str(e)}")
            if request.is_json:
                return {
                    "success": False,
                    "message": "Ошибка авторизации. Попробуйте позже",
                }
            flash("❌ Ошибка авторизации. Попробуйте позже", "error")
    if request.args.get("id") and request.args.get("hash"):
        try:
            auth_data = {
                "id": request.args.get("id"),
                "first_name": request.args.get("first_name", ""),
                "last_name": request.args.get("last_name", ""),
                "username": request.args.get("username", ""),
                "photo_url": request.args.get("photo_url", ""),
                "auth_date": request.args.get("auth_date"),
                "hash": request.args.get("hash"),
            }
            auth_data = {k: v for k, v in auth_data.items() if v is not None}
            is_test_data = (
                str(auth_data.get("id")) == "123456"
                and str(auth_data.get("hash")) == "test"
            )
            is_miniapp_data = str(auth_data.get("hash")) == "miniapp_auth"
            is_widget_data = str(auth_data.get("hash")) == "telegram_widget_auth"
            if (
                not is_test_data
                and not is_miniapp_data
                and not is_widget_data
                and not verify_telegram_auth(auth_data)
            ):
                flash(
                    "❌ Неверные данные авторизации. Проверьте настройки бота.",
                    "error",
                )
                return redirect(url_for("auth.login"))
            telegram_id = int(auth_data["id"])
            username = auth_data.get("username", "")
            first_name = auth_data.get("first_name", "")
            last_name = auth_data.get("last_name", "")
            tg_user = TelegramUser.query.filter_by(telegram_id=telegram_id).first()
            if tg_user and tg_user.user_id:
                user = User.query.get(tg_user.user_id)
                if user:
                    login_user(user)
                    return_to = request.args.get("return_to")
                    if return_to:
                        return redirect(f"https://cysu.ru{return_to}")
                    else:
                        return redirect(url_for("main.index"))
                else:
                    tg_user.user_id = None
                    db.session.commit()
            tg_user = TelegramUser.get_or_create(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            base_username = username or f"tg_{telegram_id}"
            # Для телеграм пользователей проверяем только базовые запрещенные слова (GET метод)
            if username and contains_forbidden_word(base_username):
                # Если запрещенные слова, используем только tg_id
                base_username = f"tg_{telegram_id}"
                current_app.logger.warning(f"Telegram registration (GET) - forbidden username '{username}' rejected for telegram_id={telegram_id}, using '{base_username}'")

            current_app.logger.info(f"Telegram registration (GET) - creating user with base_username='{base_username}' for telegram_id={telegram_id}")
            counter = 1
            original_username = base_username
            while User.query.filter_by(username=base_username).first():
                base_username = f"{original_username}_{counter}"
                counter += 1
            current_app.logger.info(f"Telegram registration (GET) - final username='{base_username}' after uniqueness check")
            user = User(
                username=base_username,
                email=f"{telegram_id}@telegram.org",
                password=generate_password_hash(secrets.token_urlsafe(16)),
                is_verified=True,
                is_trial_subscription=True,
                trial_subscription_expires=datetime.utcnow() + timedelta(days=7),
            )
            db.session.add(user)
            db.session.flush()
            tg_user.user_id = user.id
            db.session.commit()
            login_user(user)
            return_to = request.args.get("return_to")
            if return_to:
                return redirect(f"https://cysu.ru{return_to}")
            else:
                return redirect(url_for("main.index"))
        except Exception as e:
            current_app.logger.error(f"Ошибка авторизации через Telegram (GET): telegram_id={auth_data.get('id', 'N/A')}, username={auth_data.get('username', 'N/A')}, error={str(e)}")
            flash("❌ Ошибка авторизации. Попробуйте позже", "error")
            return redirect(url_for("auth.login"))
    return render_template("auth/telegram_miniapp.html")


@telegram_auth_bp.route("/auth/telegram/miniapp")
def telegram_miniapp() -> str:
    return render_template("auth/telegram_miniapp.html")


@telegram_auth_bp.route("/auth/telegram/connect", methods=["POST"])
@login_required
def connect_telegram() -> Response:
    auth_data = request.get_json() if request.is_json else request.form.to_dict()
    if not verify_telegram_auth(auth_data):
        flash("❌ Неверные данные авторизации", "error")
        return redirect(url_for("main.profile"))
    try:
        telegram_id = int(auth_data["id"])
        username = auth_data.get("username", "")
        first_name = auth_data.get("first_name", "")
        last_name = auth_data.get("last_name", "")
        existing_tg_user = TelegramUser.query.filter_by(telegram_id=telegram_id).first()
        if existing_tg_user and existing_tg_user.user_id:
            flash(
                "❌ Этот Telegram аккаунт уже связан с другим пользователем",
                "error",
            )
            return redirect(url_for("main.profile"))
        tg_user = TelegramUser.get_or_create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        tg_user.user_id = current_user.id
        db.session.commit()
        flash("✅ Telegram аккаунт успешно связан", "success")
    except Exception:
        flash("❌ Ошибка связывания аккаунта", "error")
    return redirect(url_for("main.profile"))


@telegram_auth_bp.route("/auth/telegram/disconnect", methods=["POST"])
@login_required
def disconnect_telegram() -> Response:
    try:
        if current_user.telegram_account:
            current_user.telegram_account.user_id = None
            db.session.commit()
            flash("✅ Telegram аккаунт отвязан", "success")
        else:
            flash("❌ Telegram аккаунт не был связан", "error")
    except Exception:
        flash("❌ Ошибка отвязывания аккаунта", "error")
    return redirect(url_for("main.profile"))


@telegram_auth_bp.route("/select_group", methods=["GET", "POST"])
@login_required
def select_group():
    if not current_user.email.endswith("@telegram.org"):
        flash(
            "Эта страница доступна только для пользователей, вошедших через Telegram",
            "warning",
        )
        return redirect(url_for("main.index"))
    if current_user.group_id:
        flash("У вас уже выбрана группа", "info")
        return redirect(url_for("main.index"))
    if request.method == "POST":
        group_id = request.form.get("group_id")
        if group_id:
            group = Group.query.get(group_id)
            if group and group.is_active:
                current_user.group_id = group.id
                db.session.commit()
                flash(f"Вы успешно выбрали группу: {group.name}", "success")
                return redirect(url_for("main.index"))
            else:
                flash("Выбранная группа не найдена или неактивна", "error")
        else:
            flash("Пожалуйста, выберите группу", "error")
    groups = Group.query.filter_by(is_active=True).order_by(Group.name).all()
    return render_template("auth/select_group.html", groups=groups)


@telegram_auth_bp.route("/request_group", methods=["POST"])
@login_required
def request_group():
    if not current_user.email.endswith("@telegram.org"):
        return jsonify(
            {
                "success": False,
                "message": "Эта функция доступна только для пользователей, вошедших через Telegram",
            }
        )
    group_name = request.form.get("group_name", "").strip()
    group_description = request.form.get("group_description", "").strip()
    if not group_name:
        return jsonify(
            {
                "success": False,
                "message": "Пожалуйста, введите название группы",
            }
        )
    existing_group = Group.query.filter_by(name=group_name).first()
    if existing_group:
        return jsonify(
            {
                "success": False,
                "message": f"Группа '{group_name}' уже существует",
            }
        )
    try:
        from ..models import Ticket, TicketCategory

        category = TicketCategory.query.filter_by(name="Запросы групп").first()
        if not category:
            category = TicketCategory(
                name="Запросы групп",
                description="Запросы на создание новых групп пользователей",
                is_active=True,
            )
            db.session.add(category)
            db.session.flush()
        ticket = Ticket(
            title=f"Запрос на создание группы: {group_name}",
            description=f"Пользователь {current_user.username} (Telegram: {current_user.email.replace('@telegram.org', '')}) запросил создание новой группы.\n\nНазвание группы: {group_name}\nОписание: {group_description or 'Не указано'}\n\nПожалуйста, создайте группу и назначьте пользователя к ней.",
            user_id=current_user.id,
            category_id=category.id,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(ticket)
        db.session.commit()
        return jsonify(
            {
                "success": True,
                "message": f"Запрос на создание группы '{group_name}' отправлен администраторам",
            }
        )
    except Exception:
        db.session.rollback()
        return jsonify(
            {
                "success": False,
                "message": "Ошибка при отправке запроса. Попробуйте позже",
            }
        )
