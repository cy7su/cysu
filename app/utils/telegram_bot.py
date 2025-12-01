import os
from datetime import datetime, timedelta

import httpx
from app import create_app, db
from app.models import TelegramUser, User
from app.utils.logger import get_logger
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from werkzeug.security import generate_password_hash

logger = get_logger("telegram_bot")
BOT_TOKEN = os.getenv("TG_TOKEN")
ADMIN_TELEGRAM_ID = int(os.getenv("TG_ID", 0))
USERS_PER_PAGE = 5


class TelegramBotManager:
    def __init__(self):
        self.app = create_app()
        self.users_cache = {}
        self.current_page = {}
        self.editing_users = {}

    def get_telegram_link(self, user: User) -> str:
        if user.email.endswith("@telegram.org"):
            telegram_id = user.email.replace("@telegram.org", "")
            if telegram_id.isdigit():
                return f"tg://user?id={telegram_id}"
        telegram_user = TelegramUser.query.filter_by(user_id=user.id).first()
        if telegram_user:
            return f"tg://user?id={telegram_user.telegram_id}"
        return "Не указан"

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help - справка по командам бота"""
        help_text = "❓ <b>Справка: Бот управления cysu.ru</b>\n\n"

        if update.effective_user.id == ADMIN_TELEGRAM_ID:
            help_text += "<blockquote>Команды администратора:\n"
            help_text += "/start - Перезапуск бота\n"
            help_text += "/help - Эта справка\n"
            help_text += "/users - Управление пользователями\n"
            help_text += "/groups - Управление группами\n"
            help_text += "</blockquote>\n\n"

            help_text += "<b>🎛️ Панель администратора:</b>\n"
            help_text += "• 👑 Полные права управления пользователями\n"
            help_text += "• 👥 Создание и управление группами\n"
            help_text += "• ⭐ Назначение ролей (админ, модератор)\n"
            help_text += "• 💰 Управление подписками пользователей\n"
            help_text += "• 🔒 Временные подписки и пробные периоды\n\n"
        else:
            help_text += "<blockquote>Основные команды:\n"
            help_text += "/start - Перезапуск бота\n"
            help_text += "/help - Эта справка\n"
            help_text += "</blockquote>\n\n"

            help_text += "<b>🎯 Функции бота:</b>\n"
            help_text += "• 🌐 Авторизация на сайте cysu.ru\n"
            help_text += "• 👤 Управление личным профилем\n"
            help_text += "• 🔐 Безопасная связь с сервером\n\n"

        help_text += "<b>📝 Примечания:</b>\n"
        help_text += "• Доступ к функциям ограничен вашими правами\n"
        help_text += "• Для авторизации используйте 'Войти через Telegram'\n"
        help_text += "• Все данные защищены шифрованием"

        await update.message.reply_text(help_text, parse_mode="HTML")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        with self.app.app_context():
            try:
                TelegramUser.get_or_create(
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    is_bot=user.is_bot,
                    language_code=user.language_code,
                )
            except Exception as e:
                logger.error(f"Ошибка создания Telegram пользователя: {e}")
            if user.id == ADMIN_TELEGRAM_ID:
                await update.message.reply_text(
                    "Добро пожаловать, администратор!\n\n"
                    "<blockquote>Доступные команды:\n"
                    "/users - Управление пользователями\n"
                    "/groups - Управление группами\n"
                    "/help - Справка</blockquote>\n\n"
                    "<b>🎛️ Панель администратора</b>\n"
                    "У вас есть полный доступ к системе управления пользователями",
                    parse_mode="HTML",
                )
            else:
                await update.message.reply_text(
                    "Добро пожаловать!\n\n"
                    "<blockquote>Этот бот предназначен для управления аккаунтом на сайте cysu.ru</blockquote>\n\n"
                    "<b>🌐 Авторизация</b>\n"
                    "Для авторизации на сайте используйте кнопку 'Войти через Telegram'".replace(
                        "</b>\n", "</b>\n\n"
                    )
                    + "\n\n<b>Команды:</b> /help - справка",
                    parse_mode="HTML",
                )

    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id != ADMIN_TELEGRAM_ID:
            await update.message.reply_text(
                "У вас нет прав для выполнения этой команды"
            )
            return
        with self.app.app_context():
            await self.show_users_page(update, context, page=0)

    async def groups_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id != ADMIN_TELEGRAM_ID:
            await update.message.reply_text(
                "У вас нет прав для выполнения этой команды"
            )
            return
        with self.app.app_context():
            await self.show_groups_page(update, context, page=0)

    async def show_groups_page(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0
    ):
        with self.app.app_context():
            try:
                from app.models import Group

                total_groups = Group.query.count()
                total_pages = (total_groups + USERS_PER_PAGE - 1) // USERS_PER_PAGE
                groups = (
                    Group.query.order_by(Group.name)
                    .offset(page * USERS_PER_PAGE)
                    .limit(USERS_PER_PAGE)
                    .all()
                )
                keyboard = []
                for group in groups:
                    status_icons = []
                    if group.is_active:
                        status_icons.append("✓")
                    else:
                        status_icons.append("✗")
                    status_text = " ".join(status_icons) if status_icons else "✗"
                    keyboard.append(
                        [
                            InlineKeyboardButton(
                                f"{group.name} {status_text}",
                                callback_data=f"group_detail_{group.id}",
                            )
                        ]
                    )
                nav_buttons = []
                if page > 0:
                    nav_buttons.append(
                        InlineKeyboardButton(
                            "←", callback_data=f"groups_page_{page - 1}"
                        )
                    )
                nav_buttons.append(
                    InlineKeyboardButton(
                        "Обновить", callback_data=f"groups_page_{page}"
                    )
                )
                if page < total_pages - 1:
                    nav_buttons.append(
                        InlineKeyboardButton(
                            "→", callback_data=f"groups_page_{page + 1}"
                        )
                    )
                if nav_buttons:
                    keyboard.append(nav_buttons)
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            "Создать группу", callback_data="create_group"
                        )
                    ]
                )
                reply_markup = InlineKeyboardMarkup(keyboard)
                text = f"Группы (стр. {page + 1}/{total_pages})\nВсего: {total_groups}"
                if update.callback_query:
                    try:
                        await update.callback_query.message.delete()
                    except Exception as e:
                        logger.warning(f"Не удалось удалить сообщение: {e}")
                    await update.callback_query.message.chat.send_message(
                        text, reply_markup=reply_markup, parse_mode="HTML"
                    )
                else:
                    await update.message.reply_text(text, reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Ошибка показа групп: {e}")
                await update.message.reply_text("Ошибка при загрузке групп")

    async def show_group_detail(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import Group

                group = Group.query.get(group_id)
                if not group:
                    await update.callback_query.answer("Группа не найдена")
                    return
                text = f"Группа: {group.name}\n"
                text += f"Описание: {group.description or 'Не указано'}\n"
                text += f"Статус: {'Активна' if group.is_active else 'Неактивна'}\n"
                text += f"ID: {group.id}"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            f"Статус: {'Активна' if group.is_active else 'Неактивна'}",
                            callback_data=f"toggle_group_status_{group_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Изменить название",
                            callback_data=f"edit_group_name_{group_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Изменить описание",
                            callback_data=f"edit_group_desc_{group_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Удалить группу",
                            callback_data=f"delete_group_{group_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "← Назад к списку", callback_data="groups_page_0"
                        )
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка показа деталей группы: {e}")
                await update.callback_query.answer("Ошибка при загрузке данных")

    async def start_create_group(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        with self.app.app_context():
            try:
                user_id = update.effective_user.id
                self.editing_users[user_id] = {"action": "create_group", "step": "name"}
                text = "Создание новой группы\n\nВведите название группы:"
                keyboard = [
                    [InlineKeyboardButton("Отмена", callback_data="groups_page_0")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка начала создания группы: {e}")
                await update.callback_query.answer("Ошибка при загрузке данных")

    async def show_users_page(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0
    ):
        with self.app.app_context():
            try:
                users = (
                    User.query.order_by(User.id.desc())
                    .offset(page * USERS_PER_PAGE)
                    .limit(USERS_PER_PAGE)
                    .all()
                )
                total_users = User.query.count()
                total_pages = (total_users + USERS_PER_PAGE - 1) // USERS_PER_PAGE
                if not users:
                    await update.message.reply_text("Пользователи не найдены")
                    return
                keyboard = []
                for user in users:
                    status_icons = []
                    if user.is_admin:
                        status_icons.append("★")
                    if user.is_moderator:
                        status_icons.append("▲")
                    if user.is_subscribed or user.is_trial_subscription:
                        status_icons.append("●")
                    if user.is_verified:
                        status_icons.append("✓")
                    status_text = " ".join(status_icons) if status_icons else "✗"
                    if user.email.endswith("@telegram.org"):
                        telegram_id = user.email.replace("@telegram.org", "")
                        display_email = f"TG: {telegram_id}"
                    else:
                        display_email = user.email
                    button_text = f"{status_text} {user.username} ({display_email})"
                    callback_data = f"user_detail_{user.id}"
                    keyboard.append(
                        [InlineKeyboardButton(button_text, callback_data=callback_data)]
                    )
                nav_buttons = []
                if page > 0:
                    nav_buttons.append(
                        InlineKeyboardButton(
                            "←", callback_data=f"users_page_{page - 1}"
                        )
                    )
                if page < total_pages - 1:
                    nav_buttons.append(
                        InlineKeyboardButton(
                            "→", callback_data=f"users_page_{page + 1}"
                        )
                    )
                if nav_buttons:
                    keyboard.append(nav_buttons)
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            "Обновить", callback_data=f"users_page_{page}"
                        )
                    ]
                )
                reply_markup = InlineKeyboardMarkup(keyboard)
                text = f"Пользователи сайта (стр. {page + 1}/{total_pages})\nВсего: {total_users}"
                if update.callback_query:
                    try:
                        await update.callback_query.message.delete()
                    except Exception as e:
                        logger.warning(f"Не удалось удалить сообщение: {e}")
                    await update.callback_query.message.chat.send_message(
                        text, reply_markup=reply_markup, parse_mode="HTML"
                    )
                else:
                    await update.message.reply_text(text, reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Ошибка показа пользователей: {e}")
                await update.message.reply_text("Ошибка при загрузке пользователей")

    async def show_user_detail(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                status_info = []
                if user.is_admin:
                    status_info.append("★ Администратор")
                if user.is_moderator:
                    status_info.append("▲ Модератор")
                if user.is_subscribed:
                    status_info.append("● Подписка активна")
                elif user.is_trial_subscription:
                    status_info.append("● Пробная подписка")
                else:
                    status_info.append("✗ Без подписки")
                if user.is_verified:
                    status_info.append("✓ Email подтвержден")
                else:
                    status_info.append("✗ Email не подтвержден")
                group_info = (
                    f"Группа: {user.group.name if user.group else 'Не назначена'}"
                )
                created_info = f"Создан: {user.created_at.strftime('%d.%m.%Y %H:%M') if user.created_at else 'Не указано'}"
                telegram_link = self.get_telegram_link(user)
                if user.email.endswith("@telegram.org"):
                    telegram_id = user.email.replace("@telegram.org", "")
                    email_display = f"Telegram: {telegram_id}"
                else:
                    email_display = f"Email: {user.email}"
                text = (
                    f"👤 <b>Пользователь: {user.username}</b>\n\n"
                    f"<blockquote>ID: {user.id}\n"
                    f"{email_display}\n"
                    f"{created_info}\n"
                    f"Ссылка: {telegram_link}\n"
                    f"{group_info}\n\n"
                    f"Статус:\n" + "\n".join(status_info) + "</blockquote>"
                )
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Управление",
                            callback_data=f"user_manage_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Изменить группу",
                            callback_data=f"change_group_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Удалить", callback_data=f"user_delete_{user_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Изменить", callback_data=f"user_edit_{user_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "← Назад к списку", callback_data="users_page_0"
                        )
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка показа деталей пользователя: {e}")
                await update.callback_query.answer("Ошибка при загрузке данных")

    async def show_change_group(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import Group, User

                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                groups = (
                    Group.query.filter_by(is_active=True).order_by(Group.name).all()
                )
                text = f"Изменение группы для пользователя {user.username}\n\n"
                text += f"Текущая группа: {user.group.name if user.group else 'Не назначена'}\n\n"
                text += "Выберите новую группу:"
                keyboard = []
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            "Убрать группу",
                            callback_data=f"remove_group_{user_id}",
                        )
                    ]
                )
                for group in groups:
                    current_mark = (
                        " (текущая)" if user.group and user.group.id == group.id else ""
                    )
                    keyboard.append(
                        [
                            InlineKeyboardButton(
                                f"{group.name}{current_mark}",
                                callback_data=f"set_group_{user_id}_{group.id}",
                            )
                        ]
                    )
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            "← Назад", callback_data=f"user_detail_{user_id}"
                        )
                    ]
                )
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка показа изменения группы: {e}")
                await update.callback_query.answer("Ошибка при загрузке данных")

    async def set_user_group(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_id: int,
        group_id: int,
    ):
        with self.app.app_context():
            try:
                from app.models import Group, User

                user = User.query.get(user_id)
                group = Group.query.get(group_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                if not group:
                    await update.callback_query.answer("Группа не найдена")
                    return
                user.group_id = group_id
                db.session.commit()
                await update.callback_query.answer(f"Группа изменена на: {group.name}")
                await self.show_user_detail(update, context, user_id)
            except Exception as e:
                logger.error(f"Ошибка изменения группы: {e}")
                await update.callback_query.answer("Ошибка при изменении группы")

    async def remove_user_group(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import User

                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                user.group_id = None
                db.session.commit()
                await update.callback_query.answer("Группа убрана у пользователя")
                await self.show_user_detail(update, context, user_id)
            except Exception as e:
                logger.error(f"Ошибка удаления группы: {e}")
                await update.callback_query.answer("Ошибка при удалении группы")

    async def toggle_group_status(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import Group

                group = Group.query.get(group_id)
                if not group:
                    await update.callback_query.answer("Группа не найдена")
                    return
                group.is_active = not group.is_active
                db.session.commit()
                status = "активна" if group.is_active else "неактивна"
                await update.callback_query.answer(f"Группа теперь {status}")
                await self.show_group_detail(update, context, group_id)
            except Exception as e:
                logger.error(f"Ошибка переключения статуса группы: {e}")
                await update.callback_query.answer("Ошибка при изменении статуса")

    async def start_edit_group_name(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import Group

                group = Group.query.get(group_id)
                if not group:
                    await update.callback_query.answer("Группа не найдена")
                    return
                user_id = update.effective_user.id
                self.editing_users[user_id] = {
                    "action": "edit_group_name",
                    "group_id": group_id,
                    "current_name": group.name,
                }
                text = f"Изменение названия группы\n\nТекущее название: {group.name}\n\nВведите новое название:"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Отмена", callback_data=f"group_detail_{group_id}"
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка начала редактирования названия группы: {e}")
                await update.callback_query.answer("Ошибка при загрузке данных")

    async def start_edit_group_desc(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import Group

                group = Group.query.get(group_id)
                if not group:
                    await update.callback_query.answer("Группа не найдена")
                    return
                user_id = update.effective_user.id
                self.editing_users[user_id] = {
                    "action": "edit_group_desc",
                    "group_id": group_id,
                    "current_desc": group.description,
                }
                text = f"Изменение описания группы\n\nТекущее описание: {group.description or 'Не указано'}\n\nВведите новое описание (или отправьте '-' для удаления):"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Отмена", callback_data=f"group_detail_{group_id}"
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка начала редактирования описания группы: {e}")
                await update.callback_query.answer("Ошибка при загрузке данных")

    async def delete_group(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import Group

                group = Group.query.get(group_id)
                if not group:
                    await update.callback_query.answer("Группа не найдена")
                    return
                db.session.delete(group)
                db.session.commit()
                await update.callback_query.answer(f"Группа '{group.name}' удалена")
                await self.show_groups_page(update, context, page=0)
            except Exception as e:
                logger.error(f"Ошибка удаления группы: {e}")
                await update.callback_query.answer("Ошибка при удалении группы")

    async def show_user_management(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                text = (
                    f"Управление пользователем: {user.username}\n\nВыберите действие:"
                )
                keyboard = [
                    [
                        InlineKeyboardButton(
                            f"★ Админка: {'✓' if user.is_admin else '✗'}",
                            callback_data=f"toggle_admin_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"▲ Модерка: {'✓' if user.is_moderator else '✗'}",
                            callback_data=f"toggle_moderator_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"● Подписка: {'✓' if user.is_subscribed else '✗'}",
                            callback_data=f"toggle_subscription_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"○ Пробная: {'✓' if user.is_trial_subscription else '✗'}",
                            callback_data=f"toggle_trial_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "← Назад", callback_data=f"user_detail_{user_id}"
                        )
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")

                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка показа управления пользователем: {e}")
                await update.callback_query.answer("Ошибка при загрузке данных")

    async def show_user_edit(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                text = f"Редактирование пользователя: {user.username}\n\nВыберите что изменить:"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Изменить ник",
                            callback_data=f"edit_username_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Изменить пароль",
                            callback_data=f"edit_password_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Изменить email",
                            callback_data=f"edit_email_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Изменить ID",
                            callback_data=f"edit_user_id_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "← Назад", callback_data=f"user_detail_{user_id}"
                        )
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка показа редактирования пользователя: {e}")
                await update.callback_query.answer("Ошибка при загрузке данных")

    async def start_edit_username(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                self.editing_users[update.effective_user.id] = {
                    "action": "edit_username",
                    "user_id": user_id,
                    "current_username": user.username,
                }
                text = f"Изменение имени пользователя\n\nТекущий ник: {user.username}\n\nВведите новый ник:"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Отмена", callback_data=f"user_edit_{user_id}"
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка начала редактирования имени: {e}")
                await update.callback_query.answer("Ошибка при загрузке данных")

    async def start_edit_password(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                self.editing_users[update.effective_user.id] = {
                    "action": "edit_password",
                    "user_id": user_id,
                }
                text = f"Изменение пароля пользователя\n\nПользователь: {user.username}\n\nВведите новый пароль:"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Отмена", callback_data=f"user_edit_{user_id}"
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка начала редактирования пароля: {e}")
                await update.callback_query.answer("Ошибка при загрузке данных")

    async def start_edit_email(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                self.editing_users[update.effective_user.id] = {
                    "action": "edit_email",
                    "user_id": user_id,
                    "current_email": user.email,
                }
                text = f"Изменение email пользователя\n\nТекущий email: {user.email}\n\nВведите новый email:"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Отмена", callback_data=f"user_edit_{user_id}"
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка начала редактирования email: {e}")
                await update.callback_query.answer("Ошибка при загрузке данных")

    async def start_edit_telegram_id(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                telegram_user = TelegramUser.query.filter_by(user_id=user_id).first()
                current_telegram_id = (
                    telegram_user.telegram_id if telegram_user else "Не привязан"
                )
                self.editing_users[update.effective_user.id] = {
                    "action": "edit_telegram_id",
                    "user_id": user_id,
                    "current_telegram_id": current_telegram_id,
                }
                text = f"Изменение Telegram ID пользователя\n\nТекущий Telegram ID: {current_telegram_id}\n\nВведите новый Telegram ID (числовое значение):"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Отмена", callback_data=f"user_edit_{user_id}"
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка начала редактирования Telegram ID: {e}")
                await update.callback_query.answer("Ошибка при загрузке данных")

    async def start_edit_user_id(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                self.editing_users[update.effective_user.id] = {
                    "action": "edit_user_id",
                    "user_id": user_id,
                    "current_user_id": user.id,
                }
                text = f"Изменение ID пользователя\n\nТекущий ID: {user.id}\n\n<b>ВНИМАНИЕ: Изменение ID может нарушить целостность данных! Убедитесь что знаете что делаете.</b>\n\nВведите новый ID (числовое значение):"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Отмена", callback_data=f"user_edit_{user_id}"
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка начала редактирования ID: {e}")
                await update.callback_query.answer("Ошибка при загрузке данных")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in self.editing_users:
            return
        editing_data = self.editing_users[user_id]
        action = editing_data["action"]
        if "user_id" in editing_data:
            target_user_id = editing_data["user_id"]
        else:
            target_user_id = None
        with self.app.app_context():
            try:
                if action == "edit_username":
                    new_username = update.message.text.strip()
                    if len(new_username) < 3 or len(new_username) > 50:
                        await update.message.reply_text(
                            "Имя пользователя должно быть от 3 до 50 символов"
                        )
                        return
                    existing_user = User.query.filter(
                        User.username == new_username,
                        User.id != target_user_id,
                    ).first()
                    if existing_user:
                        await update.message.reply_text(
                            "Пользователь с таким именем уже существует"
                        )
                        return
                    user = User.query.get(target_user_id)
                    if user:
                        user.username = new_username
                        db.session.commit()
                        await update.message.reply_text(
                            f"Имя пользователя изменено на: {new_username}"
                        )
                        del self.editing_users[user_id]
                    else:
                        await update.message.reply_text("Пользователь не найден")
                        del self.editing_users[user_id]
                elif action == "edit_password":
                    new_password = update.message.text.strip()
                    if len(new_password) < 6:
                        await update.message.reply_text(
                            "Пароль должен быть не менее 6 символов"
                        )
                        return
                    user = User.query.get(target_user_id)
                    if user:
                        user.password = generate_password_hash(new_password)
                        db.session.commit()
                        await update.message.reply_text(
                            f"Пароль для пользователя {user.username} изменен"
                        )
                        del self.editing_users[user_id]
                    else:
                        await update.message.reply_text("Пользователь не найден")
                        del self.editing_users[user_id]
                elif action == "create_group":
                    step = editing_data.get("step", "name")
                    if step == "name":
                        group_name = update.message.text.strip()
                        if len(group_name) < 2 or len(group_name) > 100:
                            await update.message.reply_text(
                                "Название группы должно быть от 2 до 100 символов"
                            )
                            return
                        from app.models import Group

                        existing_group = Group.query.filter_by(name=group_name).first()
                        if existing_group:
                            await update.message.reply_text(
                                "Группа с таким названием уже существует"
                            )
                            return
                        self.editing_users[user_id]["group_name"] = group_name
                        self.editing_users[user_id]["step"] = "description"
                        await update.message.reply_text(
                            f"Название группы: {group_name}\n\nВведите описание группы (или отправьте '-' для пропуска):"
                        )
                    elif step == "description":
                        group_description = update.message.text.strip()
                        if group_description == "-":
                            group_description = None
                        from app.models import Group

                        group = Group(
                            name=self.editing_users[user_id]["group_name"],
                            description=group_description,
                            is_active=True,
                        )
                        db.session.add(group)
                        db.session.commit()
                        await update.message.reply_text(
                            f"Группа '{group.name}' успешно создана!"
                        )
                        del self.editing_users[user_id]
                        await self.show_groups_page(update, context, page=0)
                elif action == "edit_group_name":
                    new_name = update.message.text.strip()
                    if len(new_name) < 2 or len(new_name) > 100:
                        await update.message.reply_text(
                            "Название группы должно быть от 2 до 100 символов"
                        )
                        return
                    from app.models import Group

                    existing_group = Group.query.filter(
                        Group.name == new_name, Group.id != editing_data["group_id"]
                    ).first()
                    if existing_group:
                        await update.message.reply_text(
                            "Группа с таким названием уже существует"
                        )
                        return
                    group = Group.query.get(editing_data["group_id"])
                    if group:
                        group.name = new_name
                        db.session.commit()
                        await update.message.reply_text(
                            f"Название группы изменено на: {new_name}"
                        )
                        del self.editing_users[user_id]
                        await self.show_group_detail(
                            update, context, editing_data["group_id"]
                        )
                    else:
                        await update.message.reply_text("Группа не найдена")
                        del self.editing_users[user_id]
                elif action == "edit_group_desc":
                    new_desc = update.message.text.strip()
                    if new_desc == "-":
                        new_desc = None
                    group = Group.query.get(editing_data["group_id"])
                    if group:
                        group.description = new_desc
                        db.session.commit()
                        desc_text = "удалено" if new_desc is None else new_desc
                        await update.message.reply_text(
                            f"Описание группы изменено на: {desc_text}"
                        )
                        del self.editing_users[user_id]
                        await self.show_group_detail(
                            update, context, editing_data["group_id"]
                        )
                    else:
                        await update.message.reply_text("Группа не найдена")
                        del self.editing_users[user_id]
                elif action == "edit_email":
                    new_email = update.message.text.strip()
                    if not new_email or "@" not in new_email:
                        await update.message.reply_text(
                            "Введите корректный email адрес"
                        )
                        return
                    from app.services.user_management_service import (
                        UserManagementService,
                    )

                    success = UserManagementService.change_user_email(
                        User.query.get(target_user_id), new_email
                    )
                    if success:
                        await update.message.reply_text(
                            f"Email изменен на: {new_email}"
                        )
                        del self.editing_users[user_id]
                        await self.show_user_detail(update, context, target_user_id)
                    else:
                        await update.message.reply_text(
                            "Ошибка изменения email. Email уже используется или некорректен."
                        )
                        del self.editing_users[user_id]
                elif action == "edit_telegram_id":
                    new_telegram_id_str = update.message.text.strip()
                    if not new_telegram_id_str.isdigit():
                        await update.message.reply_text(
                            "Telegram ID должен быть числом"
                        )
                        return
                    new_telegram_id = int(new_telegram_id_str)
                    from app.services.user_management_service import (
                        UserManagementService,
                    )

                    success = UserManagementService.change_user_telegram_id(
                        User.query.get(target_user_id), new_telegram_id
                    )
                    if success:
                        await update.message.reply_text(
                            f"Telegram ID изменен на: {new_telegram_id}"
                        )
                        del self.editing_users[user_id]
                        await self.show_user_detail(update, context, target_user_id)
                    else:
                        await update.message.reply_text(
                            "Ошибка изменения Telegram ID. ID уже используется."
                        )
                        del self.editing_users[user_id]
                elif action == "edit_user_id":
                    new_user_id_str = update.message.text.strip()
                    if not new_user_id_str.isdigit() or int(new_user_id_str) <= 0:
                        await update.message.reply_text(
                            "ID должен быть положительным числом больше 0"
                        )
                        return
                    new_user_id = int(new_user_id_str)
                    from app.services.user_management_service import (
                        UserManagementService,
                    )

                    user = User.query.get(target_user_id)
                    if not user:
                        await update.message.reply_text("Пользователь не найден")
                        del self.editing_users[user_id]
                        return

                    success = UserManagementService.change_user_id(user, new_user_id)
                    if success:
                        await update.message.reply_text(
                            f"ID пользователя изменен на: {new_user_id}\n\n<b>ВНИМАНИЕ: Обновите страницу списка пользователей для корректного отображения!</b>"
                        )
                        del self.editing_users[user_id]
                        await self.show_users_page(update, context, page=0)
                    else:
                        await update.message.reply_text(
                            "Ошибка изменения ID. Такой ID уже существует."
                        )
                        del self.editing_users[user_id]
            except Exception as e:
                logger.error(f"Ошибка обработки сообщения: {e}", exc_info=True)
                await update.message.reply_text(
                    f"Ошибка при обработке данных: {str(e)}"
                )
                if user_id in self.editing_users:
                    del self.editing_users[user_id]

    async def handle_callback_query(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()
        data = query.data
        try:
            if data.startswith("users_page_"):
                page = int(data.split("_")[2])
                await self.show_users_page(update, context, page)
            elif data.startswith("groups_page_"):
                page = int(data.split("_")[2])
                await self.show_groups_page(update, context, page)
            elif data.startswith("group_detail_"):
                group_id = int(data.split("_")[2])
                await self.show_group_detail(update, context, group_id)
            elif data == "create_group":
                await self.start_create_group(update, context)
            elif data.startswith("user_detail_"):
                user_id = int(data.split("_")[2])
                await self.show_user_detail(update, context, user_id)
            elif data.startswith("user_manage_"):
                user_id = int(data.split("_")[2])
                await self.show_user_management(update, context, user_id)
            elif data.startswith("user_edit_"):
                user_id = int(data.split("_")[2])
                await self.show_user_edit(update, context, user_id)
            elif data.startswith("change_group_"):
                user_id = int(data.split("_")[2])
                await self.show_change_group(update, context, user_id)
            elif data.startswith("set_group_"):
                parts = data.split("_")
                user_id = int(parts[2])
                group_id = int(parts[3])
                await self.set_user_group(update, context, user_id, group_id)
            elif data.startswith("remove_group_"):
                user_id = int(data.split("_")[2])
                await self.remove_user_group(update, context, user_id)
            elif data.startswith("toggle_group_status_"):
                group_id = int(data.split("_")[3])
                await self.toggle_group_status(update, context, group_id)
            elif data.startswith("edit_group_name_"):
                group_id = int(data.split("_")[3])
                await self.start_edit_group_name(update, context, group_id)
            elif data.startswith("edit_group_desc_"):
                group_id = int(data.split("_")[3])
                await self.start_edit_group_desc(update, context, group_id)
            elif data.startswith("delete_group_"):
                group_id = int(data.split("_")[2])
                await self.delete_group(update, context, group_id)
            elif data.startswith("edit_username_"):
                user_id = int(data.split("_")[2])
                await self.start_edit_username(update, context, user_id)
            elif data.startswith("edit_password_"):
                user_id = int(data.split("_")[2])
                await self.start_edit_password(update, context, user_id)
            elif data.startswith("edit_email_"):
                user_id = int(data.split("_")[2])
                await self.start_edit_email(update, context, user_id)
            elif data.startswith("edit_user_id_"):
                user_id = int(data.split("_")[3])
                await self.start_edit_user_id(update, context, user_id)
            elif data.startswith("toggle_admin_"):
                user_id = int(data.split("_")[2])
                await self.toggle_admin(update, context, user_id)
            elif data.startswith("toggle_moderator_"):
                user_id = int(data.split("_")[2])
                await self.toggle_moderator(update, context, user_id)
            elif data.startswith("toggle_subscription_"):
                user_id = int(data.split("_")[2])
                await self.toggle_subscription(update, context, user_id)
            elif data.startswith("toggle_trial_"):
                user_id = int(data.split("_")[2])
                await self.toggle_trial_subscription(update, context, user_id)
            elif data.startswith("user_delete_"):
                user_id = int(data.split("_")[2])
                await self.confirm_delete_user(update, context, user_id)
            elif data.startswith("confirm_delete_"):
                user_id = int(data.split("_")[2])
                await self.delete_user(update, context, user_id)

        except Exception as e:
            logger.error(f"Ошибка обработки callback: {e}")
            await query.answer("Ошибка при обработке запроса")

    async def toggle_admin(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                user.is_admin = not user.is_admin
                db.session.commit()
                status = "выданы" if user.is_admin else "забраны"
                await update.callback_query.answer(f"★ Права администратора {status}")
                await self.show_user_management(update, context, user_id)
            except Exception as e:
                logger.error(f"Ошибка переключения админки: {e}")
                await update.callback_query.answer("Ошибка при изменении прав")

    async def toggle_moderator(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                user.is_moderator = not user.is_moderator
                db.session.commit()
                status = "выданы" if user.is_moderator else "забраны"
                await update.callback_query.answer(f"▲ Права модератора {status}")
                await self.show_user_management(update, context, user_id)
            except Exception as e:
                logger.error(f"Ошибка переключения модерки: {e}")
                await update.callback_query.answer("Ошибка при изменении прав")

    async def toggle_subscription(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                if user.is_subscribed:
                    user.is_subscribed = False
                    user.is_manual_subscription = False
                    user.subscription_expires = None
                else:
                    user.is_subscribed = True
                    user.is_manual_subscription = True
                    user.subscription_expires = datetime.utcnow() + timedelta(days=365)
                db.session.commit()
                status = "выдана" if user.is_subscribed else "забрана"
                await update.callback_query.answer(f"● Подписка {status}")
                await self.show_user_management(update, context, user_id)
            except Exception as e:
                logger.error(f"Ошибка переключения подписки: {e}")
                await update.callback_query.answer("Ошибка при изменении подписки")

    async def toggle_trial_subscription(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                user.is_trial_subscription = not user.is_trial_subscription
                db.session.commit()
                status = "выдана" if user.is_trial_subscription else "отменена"
                await update.callback_query.answer(f"○ Пробная подписка {status}")
                await self.show_user_management(update, context, user_id)
            except Exception as e:
                logger.error(f"Ошибка переключения пробной подписки: {e}")
                await update.callback_query.answer(
                    "Ошибка при изменении пробной подписки"
                )

    async def confirm_delete_user(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                text = f"ВНИМАНИЕ!\n\nВы действительно хотите удалить пользователя {user.username}?\n\nЭто действие нельзя отменить!"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Да, удалить",
                            callback_data=f"confirm_delete_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Отмена", callback_data=f"user_detail_{user_id}"
                        )
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка подтверждения удаления: {e}")
                await update.callback_query.answer("Ошибка при загрузке данных")

    async def delete_user(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return
                username = user.username
                TelegramUser.query.filter_by(user_id=user_id).delete()
                db.session.delete(user)
                db.session.commit()
                await update.callback_query.answer(f"Пользователь {username} удален")
                await self.show_users_page(update, context, page=0)
            except Exception as e:
                logger.error(f"Ошибка удаления пользователя: {e}")
                await update.callback_query.answer("Ошибка при удалении пользователя")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Ошибка при обработке обновления: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Произошла ошибка. Попробуйте позже."
            )

    def run_bot(self):
        if not BOT_TOKEN:
            logger.error("TG_TOKEN не найден в переменных окружения")
            return
        if not ADMIN_TELEGRAM_ID:
            logger.error("TG_ID не найден в переменных окружения")
            return

        import atexit
        import os
        import signal

        pid_file = "/tmp/telegram_bot.pid"

        def cleanup_pid_file():
            try:
                if os.path.exists(pid_file):
                    os.remove(pid_file)
            except Exception as e:
                logger.warning(f"Failed to cleanup PID file: {e}")

        def signal_handler(signum, frame):
            cleanup_pid_file()
            exit(0)

        if os.path.exists(pid_file):
            try:
                with open(pid_file, "r") as f:
                    old_pid = int(f.read().strip())

                os.kill(old_pid, 0)
                logger.error(
                    "Telegram bot is already running (PID: {}). Please stop the other instance first.".format(
                        old_pid
                    )
                )
                return
            except (OSError, ValueError):

                cleanup_pid_file()
            except Exception as e:
                logger.warning(f"Error checking PID file: {e}")

        try:
            with open(pid_file, "w") as f:
                f.write(str(os.getpid()))
        except Exception as e:
            logger.error(f"Failed to write PID file: {e}")
            return

        atexit.register(cleanup_pid_file)
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        from telegram.request import HTTPXRequest

        _orig_asyncclient_init = httpx.AsyncClient.__init__

        def _patched_asyncclient_init(self, *args, **kwargs):
            kwargs.pop("proxy", None)
            return _orig_asyncclient_init(self, *args, **kwargs)

        httpx.AsyncClient.__init__ = _patched_asyncclient_init

        application = (
            Application.builder().token(BOT_TOKEN).request(HTTPXRequest()).build()
        )

        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("users", self.users_command))
        application.add_handler(CommandHandler("groups", self.groups_command))

        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        application.add_error_handler(self.error_handler)
        application.add_handler(CallbackQueryHandler(self.handle_callback_query))

        application.run_polling()
