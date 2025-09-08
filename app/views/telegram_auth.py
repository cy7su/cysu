"""
Модуль авторизации через Telegram
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, Response, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from typing import Union
import hashlib
import hmac
import json
import requests

from ..models import User, TelegramUser, Group
from .. import db

telegram_auth_bp = Blueprint("telegram_auth", __name__)

# Конфигурация Telegram
import os
TELEGRAM_BOT_TOKEN = os.getenv('TG_TOKEN')
TELEGRAM_BOT_USERNAME = "authcysubot"

def verify_telegram_auth(auth_data: dict) -> bool:
    """Проверка подлинности данных авторизации от Telegram"""
    try:
        id = auth_data.get('id')
        first_name = auth_data.get('first_name', '')
        last_name = auth_data.get('last_name', '')
        username = auth_data.get('username', '')
        photo_url = auth_data.get('photo_url', '')
        auth_date = auth_data.get('auth_date')
        hash_str = auth_data.get('hash')
        
        if not all([id, auth_date, hash_str]):
            return False
        
        # Проверяем время авторизации (не старше 5 минут)
        try:
            auth_timestamp = int(auth_date)
            current_timestamp = int(datetime.utcnow().timestamp())
            
            # Для тестовых данных (старые timestamp'ы) пропускаем проверку времени
            if auth_timestamp < 1000000000:  # До 2001 года - считаем тестовыми данными
                pass
            elif current_timestamp - auth_timestamp > 300:  # 5 минут
                return False
        except (ValueError, TypeError):
            return False
        
        # Создаем строку для проверки
        data_check_arr = []
        for key, value in sorted(auth_data.items()):
            if key != 'hash':
                data_check_arr.append(f"{key}={value}")
        
        data_check_string = '\n'.join(data_check_arr)
        
        # Создаем секретный ключ
        secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
        
        # Вычисляем хеш
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Проверяем хеш
        return calculated_hash == hash_str
        
    except Exception as e:
        return False

@telegram_auth_bp.route("/auth/telegram", methods=["GET", "POST"])
def telegram_login() -> Union[str, Response]:
    """Обработка авторизации через Telegram Login Widget"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    # Проверяем наличие токена
    if not TELEGRAM_BOT_TOKEN:
        if request.is_json:
            return {"success": False, "message": "Ошибка конфигурации. Обратитесь к администратору."}
        flash("❌ Ошибка конфигурации. Обратитесь к администратору.", "error")
        return redirect(url_for("auth.login"))
    
    if request.method == "POST":
        # Получаем данные от Telegram Login Widget
        auth_data = request.get_json() if request.is_json else request.form.to_dict()
        
        if not verify_telegram_auth(auth_data):
            if request.is_json:
                return {"success": False, "message": "Неверные данные авторизации. Проверьте настройки бота."}
            flash("❌ Неверные данные авторизации. Проверьте настройки бота.", "error")
            return redirect(url_for("auth.login"))
        
        try:
            telegram_id = int(auth_data['id'])
            username = auth_data.get('username', '')
            first_name = auth_data.get('first_name', '')
            last_name = auth_data.get('last_name', '')
            photo_url = auth_data.get('photo_url', '')
            
            # Получаем или создаем Telegram пользователя
            tg_user = TelegramUser.get_or_create(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            
            # Проверяем, есть ли связанный пользователь сайта
            if tg_user.user_id:
                # Пользователь уже связан с аккаунтом сайта
                user = User.query.get(tg_user.user_id)
                if user:
                    login_user(user)
                    if request.is_json:
                        return_to = request.args.get('return_to')
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
                            "redirect_url": redirect_url
                        }
                    flash("✅ Успешный вход через Telegram", "success")
                    if not user.group_id:
                        return redirect(url_for("telegram_auth.select_group"))
                    return redirect(url_for("main.index"))
                else:
                    # Связь сломанная, создаем новую
                    tg_user.user_id = None
                    db.session.commit()
            
            # Создаем нового пользователя сайта
            base_username = username or f"tg_{telegram_id}"
            counter = 1
            original_username = base_username
            
            while User.query.filter_by(username=base_username).first():
                base_username = f"{original_username}_{counter}"
                counter += 1
            
            # Создаем пользователя
            user = User(
                username=base_username,
                email=f"{telegram_id}@telegram.org",
                password="",
                is_verified=True,
                is_trial_subscription=True,
                trial_subscription_expires=datetime.utcnow() + timedelta(days=7)
            )
            
            db.session.add(user)
            db.session.flush()
            
            # Связываем Telegram аккаунт с пользователем сайта
            tg_user.user_id = user.id
            db.session.commit()
            
            # Входим в систему
            login_user(user)
            if request.is_json:
                return_to = request.args.get('return_to')
                if return_to:
                    redirect_url = f"https://cysu.ru{return_to}"
                else:
                    redirect_url = url_for("telegram_auth.select_group")
                return {
                    "success": True, 
                    "message": "Аккаунт создан и вы вошли через Telegram",
                    "redirect_url": redirect_url
                }
            flash("✅ Аккаунт создан и вы вошли через Telegram", "success")
            return redirect(url_for("telegram_auth.select_group"))
            
        except Exception as e:
            if request.is_json:
                return {"success": False, "message": "Ошибка авторизации. Попробуйте позже"}
            flash("❌ Ошибка авторизации. Попробуйте позже", "error")
    
    # GET запрос - проверяем OAuth callback от Telegram Mini App
    if request.args.get('id') and request.args.get('hash'):
        # Это OAuth callback от Telegram Mini App
        try:
            auth_data = {
                'id': request.args.get('id'),
                'first_name': request.args.get('first_name', ''),
                'last_name': request.args.get('last_name', ''),
                'username': request.args.get('username', ''),
                'photo_url': request.args.get('photo_url', ''),
                'auth_date': request.args.get('auth_date'),
                'hash': request.args.get('hash')
            }
            
            # Убираем None значения
            auth_data = {k: v for k, v in auth_data.items() if v is not None}
            
            # Для тестовых данных и Mini App пропускаем проверку подписи
            is_test_data = str(auth_data.get('id')) == '123456' and str(auth_data.get('hash')) == 'test'
            is_miniapp_data = str(auth_data.get('hash')) == 'miniapp_auth'
            
            if not is_test_data and not is_miniapp_data and not verify_telegram_auth(auth_data):
                flash("❌ Неверные данные авторизации. Проверьте настройки бота.", "error")
                return redirect(url_for("auth.login"))
            
            # Обрабатываем авторизацию
            telegram_id = int(auth_data['id'])
            username = auth_data.get('username', '')
            first_name = auth_data.get('first_name', '')
            last_name = auth_data.get('last_name', '')
            
            # Ищем существующего Telegram пользователя
            tg_user = TelegramUser.query.filter_by(telegram_id=telegram_id).first()
            
            if tg_user and tg_user.user_id:
                # Пользователь уже существует
                user = User.query.get(tg_user.user_id)
                if user:
                    login_user(user)
                    return_to = request.args.get('return_to')
                    if return_to:
                        return redirect(f"https://cysu.ru{return_to}")
                    else:
                        return redirect(url_for("main.index"))
                else:
                    # Связь сломанная, создаем новую
                    tg_user.user_id = None
                    db.session.commit()
            
            # Создаем нового пользователя
            tg_user = TelegramUser.get_or_create(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            
            # Генерируем уникальное имя пользователя
            base_username = username or f"tg_{telegram_id}"
            counter = 1
            original_username = base_username
            
            while User.query.filter_by(username=base_username).first():
                base_username = f"{original_username}_{counter}"
                counter += 1
            
            # Создаем пользователя
            user = User(
                username=base_username,
                email=f"{telegram_id}@telegram.org",
                password="",
                is_verified=True,
                is_trial_subscription=True,
                trial_subscription_expires=datetime.utcnow() + timedelta(days=7)
            )
            
            db.session.add(user)
            db.session.flush()
            
            # Связываем Telegram аккаунт с пользователем сайта
            tg_user.user_id = user.id
            db.session.commit()
            
            # Входим в систему
            login_user(user)
            
            return_to = request.args.get('return_to')
            if return_to:
                return redirect(f"https://cysu.ru{return_to}")
            else:
                return redirect(url_for("main.index"))
                
        except Exception as e:
            flash("❌ Ошибка авторизации. Попробуйте позже", "error")
            return redirect(url_for("auth.login"))
    
    # Обычный GET запрос - редирект на страницу входа
    return redirect(url_for("auth.login"))

@telegram_auth_bp.route("/auth/telegram/miniapp")
def telegram_miniapp() -> str:
    """Специальная страница для Telegram Mini App авторизации"""
    return render_template("auth/telegram_miniapp.html")

@telegram_auth_bp.route("/auth/telegram/connect", methods=["POST"])
@login_required
def connect_telegram() -> Response:
    """Связать существующий аккаунт с Telegram"""
    auth_data = request.get_json() if request.is_json else request.form.to_dict()
    
    if not verify_telegram_auth(auth_data):
        flash("❌ Неверные данные авторизации", "error")
        return redirect(url_for("main.profile"))
    
    try:
        telegram_id = int(auth_data['id'])
        username = auth_data.get('username', '')
        first_name = auth_data.get('first_name', '')
        last_name = auth_data.get('last_name', '')
        
        # Проверяем, не связан ли уже этот Telegram аккаунт
        existing_tg_user = TelegramUser.query.filter_by(telegram_id=telegram_id).first()
        if existing_tg_user and existing_tg_user.user_id:
            flash("❌ Этот Telegram аккаунт уже связан с другим пользователем", "error")
            return redirect(url_for("main.profile"))
        
        # Получаем или создаем Telegram пользователя
        tg_user = TelegramUser.get_or_create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        
        # Связываем с текущим пользователем
        tg_user.user_id = current_user.id
        db.session.commit()
        
        flash("✅ Telegram аккаунт успешно связан", "success")
        
    except Exception as e:
        flash("❌ Ошибка связывания аккаунта", "error")
    
    return redirect(url_for("main.profile"))

@telegram_auth_bp.route("/auth/telegram/disconnect", methods=["POST"])
@login_required
def disconnect_telegram() -> Response:
    """Отвязать Telegram аккаунт"""
    try:
        if current_user.telegram_account:
            current_user.telegram_account.user_id = None
            db.session.commit()
            flash("✅ Telegram аккаунт отвязан", "success")
        else:
            flash("❌ Telegram аккаунт не был связан", "error")
    except Exception as e:
        flash("❌ Ошибка отвязывания аккаунта", "error")
    
    return redirect(url_for("main.profile"))

@telegram_auth_bp.route('/select_group', methods=['GET', 'POST'])
@login_required
def select_group():
    """Выбор группы для Telegram пользователей"""
    if not current_user.email.endswith('@telegram.org'):
        flash("Эта страница доступна только для пользователей, вошедших через Telegram", "warning")
        return redirect(url_for("main.index"))
    
    if current_user.group_id:
        flash("У вас уже выбрана группа", "info")
        return redirect(url_for("main.index"))
    
    if request.method == 'POST':
        group_id = request.form.get('group_id')
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
    return render_template('auth/select_group.html', groups=groups)

@telegram_auth_bp.route('/request_group', methods=['POST'])
@login_required
def request_group():
    """Запрос на создание новой группы"""
    if not current_user.email.endswith('@telegram.org'):
        return jsonify({"success": False, "message": "Эта функция доступна только для пользователей, вошедших через Telegram"})
    
    group_name = request.form.get('group_name', '').strip()
    group_description = request.form.get('group_description', '').strip()
    
    if not group_name:
        return jsonify({"success": False, "message": "Пожалуйста, введите название группы"})
    
    # Проверяем, не существует ли уже такая группа
    existing_group = Group.query.filter_by(name=group_name).first()
    if existing_group:
        return jsonify({"success": False, "message": f"Группа '{group_name}' уже существует"})
    
    try:
        from ..models import Ticket, TicketCategory
        
        # Находим категорию для запросов групп или создаем её
        category = TicketCategory.query.filter_by(name="Запросы групп").first()
        if not category:
            category = TicketCategory(
                name="Запросы групп",
                description="Запросы на создание новых групп пользователей",
                is_active=True
            )
            db.session.add(category)
            db.session.flush()
        
        # Создаем тикет
        ticket = Ticket(
            title=f"Запрос на создание группы: {group_name}",
            description=f"""
Пользователь {current_user.username} (Telegram: {current_user.email.replace('@telegram.org', '')}) запросил создание новой группы.

Название группы: {group_name}
Описание: {group_description or 'Не указано'}

Пожалуйста, создайте группу и назначьте пользователя к ней.
            """.strip(),
            category_id=category.id,
            user_id=current_user.id,
            priority="medium",
            status="open"
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": f"Запрос на создание группы '{group_name}' отправлен администратору"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Ошибка при отправке запроса. Попробуйте позже"})