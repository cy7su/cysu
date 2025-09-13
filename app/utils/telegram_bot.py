import logging
import os
from datetime import datetime, timedelta


from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import TelegramUser, User

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TG_TOKEN")
ADMIN_TELEGRAM_ID = int(os.getenv("TG_ID", 0))
USERS_PER_PAGE = 5


class TelegramBotManager:
    def __init__(self):
        self.app = create_app()
        self.users_cache = {}
        self.current_page = {}
        self.editing_users = {}  # Для хранения состояния редактирования

    def get_telegram_link(self, user: User) -> str:
        if user.email.endswith("@telegram.org"):
            telegram_id = user.email.replace("@telegram.org", "")
            if telegram_id.isdigit():
                return f"tg://user?id={telegram_id}"

        telegram_user = TelegramUser.query.filter_by(user_id=user.id).first()
        if telegram_user:
            return f"tg://user?id={telegram_user.telegram_id}"

        return "Не указан"

    async def start_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
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
                    "👋 Добро пожаловать, администратор!\n\n"
                    "Доступные команды:\n"
                    "/users - Управление пользователями\n"
                    "/help - Справка"
                )
            else:
                await update.message.reply_text(
                    "👋 Добро пожаловать!\n\n"
                    "Этот бот предназначен для управления аккаунтом на сайте cysu.ru\n\n"
                    "Для авторизации на сайте используйте кнопку 'Войти через Telegram'"
                )

    async def help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user

        if user.id == ADMIN_TELEGRAM_ID:
            help_text = (
                "🔧 Команды администратора:\n\n"
                "/users - Управление пользователями сайта\n"
                "/help - Показать эту справку\n\n"
                "В меню пользователей вы можете:\n"
                "• Просматривать список пользователей\n"
                "• Выдавать/забирать права администратора\n"
                "• Выдавать/забирать права модератора\n"
                "• Управлять подписками\n"
                "• Удалять аккаунты\n"
                "• Изменять данные пользователей"
            )
        else:
            help_text = (
                "ℹ️ Справка:\n\n"
                "Этот бот предназначен для управления аккаунтом на сайте cysu.ru\n\n"
                "Для авторизации на сайте используйте кнопку 'Войти через Telegram'"
            )

        await update.message.reply_text(help_text)

    async def users_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user

        if user.id != ADMIN_TELEGRAM_ID:
            await update.message.reply_text(
                "❌ У вас нет прав для выполнения этой команды"
            )
            return

        with self.app.app_context():
            await self.show_users_page(update, context, page=0)

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
                total_pages = (
                    total_users + USERS_PER_PAGE - 1
                ) // USERS_PER_PAGE

                if not users:
                    await update.message.reply_text(
                        "📭 Пользователи не найдены"
                    )
                    return

                keyboard = []
                for user in users:
                    status_icons = []
                    if user.is_admin:
                        status_icons.append("👑")
                    if user.is_moderator:
                        status_icons.append("🛡️")
                    if user.is_subscribed or user.is_trial_subscription:
                        status_icons.append("⭐")
                    if user.is_verified:
                        status_icons.append("✅")

                    status_text = (
                        " ".join(status_icons) if status_icons else "❌"
                    )

                    if user.email.endswith("@telegram.org"):
                        telegram_id = user.email.replace("@telegram.org", "")
                        display_email = f"TG: {telegram_id}"
                    else:
                        display_email = user.email

                    button_text = (
                        f"{status_text} {user.username} ({display_email})"
                    )
                    callback_data = f"user_detail_{user.id}"
                    keyboard.append(
                        [
                            InlineKeyboardButton(
                                button_text, callback_data=callback_data
                            )
                        ]
                    )

                nav_buttons = []
                if page > 0:
                    nav_buttons.append(
                        InlineKeyboardButton(
                            "⬅️", callback_data=f"users_page_{page-1}"
                        )
                    )
                if page < total_pages - 1:
                    nav_buttons.append(
                        InlineKeyboardButton(
                            "➡️", callback_data=f"users_page_{page+1}"
                        )
                    )

                if nav_buttons:
                    keyboard.append(nav_buttons)

                keyboard.append(
                    [
                        InlineKeyboardButton(
                            "🔄 Обновить", callback_data=f"users_page_{page}"
                        )
                    ]
                )

                reply_markup = InlineKeyboardMarkup(keyboard)

                text = f"👥 Пользователи сайта (стр. {page + 1}/{total_pages})\nВсего: {total_users}"

                if update.callback_query:
                    await update.callback_query.edit_message_text(
                        text, reply_markup=reply_markup
                    )
                else:
                    await update.message.reply_text(
                        text, reply_markup=reply_markup
                    )

            except Exception as e:
                logger.error(f"Ошибка показа пользователей: {e}")
                await update.message.reply_text(
                    "❌ Ошибка при загрузке пользователей"
                )

    async def show_user_detail(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "❌ Пользователь не найден"
                    )
                    return

                status_info = []
                if user.is_admin:
                    status_info.append("👑 Администратор")
                if user.is_moderator:
                    status_info.append("🛡️ Модератор")
                if user.is_subscribed:
                    status_info.append("⭐ Подписка активна")
                elif user.is_trial_subscription:
                    status_info.append("⭐ Пробная подписка")
                else:
                    status_info.append("❌ Без подписки")
                if user.is_verified:
                    status_info.append("✅ Email подтвержден")
                else:
                    status_info.append("❌ Email не подтвержден")

                group_info = f"Группа: {user.group.name if user.group else 'Не назначена'}"
                created_info = f"Создан: {user.created_at.strftime('%d.%m.%Y %H:%M') if user.created_at else 'Не указано'}"

                telegram_link = self.get_telegram_link(user)

                if user.email.endswith("@telegram.org"):
                    telegram_id = user.email.replace("@telegram.org", "")
                    email_display = f"📱 Telegram: {telegram_id}"
                else:
                    email_display = f"📧 Email: {user.email}"

                text = (
                    f"👤 Пользователь: {user.username}\n"
                    f"{email_display}\n"
                    f"🔗 Ссылка: {telegram_link}\n"
                    f"🆔 ID: {user.id}\n"
                    f"📅 {created_info}\n"
                    f"👥 {group_info}\n\n"
                    "Статус:\n" + "\n".join(status_info)
                )

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "🔧 Управление",
                            callback_data=f"user_manage_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🗑️ Удалить", callback_data=f"user_delete_{user_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "✏️ Изменить", callback_data=f"user_edit_{user_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⬅️ Назад к списку", callback_data="users_page_0"
                        )
                    ],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.callback_query.edit_message_text(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка показа деталей пользователя: {e}")
                await update.callback_query.answer(
                    "❌ Ошибка при загрузке данных"
                )

    async def show_user_management(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "❌ Пользователь не найден"
                    )
                    return

                text = f"🔧 Управление пользователем: {user.username}\n\nВыберите действие:"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            f"👑 Админка: {'✅' if user.is_admin else '❌'}",
                            callback_data=f"toggle_admin_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"🛡️ Модерка: {'✅' if user.is_moderator else '❌'}",
                            callback_data=f"toggle_moderator_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"⭐ Подписка: {'✅' if user.is_subscribed else '❌'}",
                            callback_data=f"toggle_subscription_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⬅️ Назад", callback_data=f"user_detail_{user_id}"
                        )
                    ],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.callback_query.edit_message_text(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка показа управления пользователем: {e}")
                await update.callback_query.answer(
                    "❌ Ошибка при загрузке данных"
                )

    async def show_user_edit(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "❌ Пользователь не найден"
                    )
                    return

                text = f"✏️ Редактирование пользователя: {user.username}\n\nВыберите что изменить:"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "👤 Изменить ник",
                            callback_data=f"edit_username_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🔒 Изменить пароль",
                            callback_data=f"edit_password_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⬅️ Назад", callback_data=f"user_detail_{user_id}"
                        )
                    ],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.callback_query.edit_message_text(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка показа редактирования пользователя: {e}")
                await update.callback_query.answer(
                    "❌ Ошибка при загрузке данных"
                )

    async def start_edit_username(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "❌ Пользователь не найден"
                    )
                    return

                self.editing_users[update.effective_user.id] = {
                    "action": "edit_username",
                    "user_id": user_id,
                    "current_username": user.username,
                }

                text = f"✏️ Изменение имени пользователя\n\nТекущий ник: {user.username}\n\nВведите новый ник:"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "❌ Отмена", callback_data=f"user_edit_{user_id}"
                        )
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.callback_query.edit_message_text(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка начала редактирования имени: {e}")
                await update.callback_query.answer(
                    "❌ Ошибка при загрузке данных"
                )

    async def start_edit_password(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "❌ Пользователь не найден"
                    )
                    return

                self.editing_users[update.effective_user.id] = {
                    "action": "edit_password",
                    "user_id": user_id,
                }

                text = f"🔒 Изменение пароля пользователя\n\nПользователь: {user.username}\n\nВведите новый пароль:"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "❌ Отмена", callback_data=f"user_edit_{user_id}"
                        )
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.callback_query.edit_message_text(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка начала редактирования пароля: {e}")
                await update.callback_query.answer(
                    "❌ Ошибка при загрузке данных"
                )

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user_id = update.effective_user.id

        if user_id not in self.editing_users:
            return

        editing_data = self.editing_users[user_id]
        action = editing_data["action"]
        target_user_id = editing_data["user_id"]

        with self.app.app_context():
            try:
                if action == "edit_username":
                    new_username = update.message.text.strip()

                    if len(new_username) < 3 or len(new_username) > 50:
                        await update.message.reply_text(
                            "❌ Имя пользователя должно быть от 3 до 50 символов"
                        )
                        return

                    existing_user = User.query.filter(
                        User.username == new_username,
                        User.id != target_user_id,
                    ).first()
                    if existing_user:
                        await update.message.reply_text(
                            "❌ Пользователь с таким именем уже существует"
                        )
                        return

                    user = User.query.get(target_user_id)
                    if user:
                        user.username = new_username
                        db.session.commit()

                        await update.message.reply_text(
                            f"✅ Имя пользователя изменено на: {new_username}"
                        )
                        del self.editing_users[user_id]

                        await self.show_user_detail(
                            update, context, target_user_id
                        )
                    else:
                        await update.message.reply_text(
                            "❌ Пользователь не найден"
                        )
                        del self.editing_users[user_id]

                elif action == "edit_password":
                    new_password = update.message.text.strip()

                    if len(new_password) < 6:
                        await update.message.reply_text(
                            "❌ Пароль должен быть не менее 6 символов"
                        )
                        return

                    user = User.query.get(target_user_id)
                    if user:
                        user.password = generate_password_hash(new_password)
                        db.session.commit()

                        await update.message.reply_text(
                            f"✅ Пароль для пользователя {user.username} изменен"
                        )
                        del self.editing_users[user_id]

                        await self.show_user_detail(
                            update, context, target_user_id
                        )
                    else:
                        await update.message.reply_text(
                            "❌ Пользователь не найден"
                        )
                        del self.editing_users[user_id]

            except Exception as e:
                logger.error(f"Ошибка обработки сообщения: {e}")
                await update.message.reply_text(
                    "❌ Ошибка при обработке данных"
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

            elif data.startswith("user_detail_"):
                user_id = int(data.split("_")[2])
                await self.show_user_detail(update, context, user_id)

            elif data.startswith("user_manage_"):
                user_id = int(data.split("_")[2])
                await self.show_user_management(update, context, user_id)

            elif data.startswith("user_edit_"):
                user_id = int(data.split("_")[2])
                await self.show_user_edit(update, context, user_id)

            elif data.startswith("edit_username_"):
                user_id = int(data.split("_")[2])
                await self.start_edit_username(update, context, user_id)

            elif data.startswith("edit_password_"):
                user_id = int(data.split("_")[2])
                await self.start_edit_password(update, context, user_id)

            elif data.startswith("toggle_admin_"):
                user_id = int(data.split("_")[2])
                await self.toggle_admin(update, context, user_id)

            elif data.startswith("toggle_moderator_"):
                user_id = int(data.split("_")[2])
                await self.toggle_moderator(update, context, user_id)

            elif data.startswith("toggle_subscription_"):
                user_id = int(data.split("_")[2])
                await self.toggle_subscription(update, context, user_id)

            elif data.startswith("user_delete_"):
                user_id = int(data.split("_")[2])
                await self.confirm_delete_user(update, context, user_id)

            elif data.startswith("confirm_delete_"):
                user_id = int(data.split("_")[2])
                await self.delete_user(update, context, user_id)

        except Exception as e:
            logger.error(f"Ошибка обработки callback: {e}")
            await query.answer("❌ Ошибка при обработке запроса")

    async def toggle_admin(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "❌ Пользователь не найден"
                    )
                    return

                user.is_admin = not user.is_admin
                db.session.commit()

                status = "выданы" if user.is_admin else "забраны"
                await update.callback_query.answer(
                    f"👑 Права администратора {status}"
                )
                await self.show_user_management(update, context, user_id)

            except Exception as e:
                logger.error(f"Ошибка переключения админки: {e}")
                await update.callback_query.answer(
                    "❌ Ошибка при изменении прав"
                )

    async def toggle_moderator(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "❌ Пользователь не найден"
                    )
                    return

                user.is_moderator = not user.is_moderator
                db.session.commit()

                status = "выданы" if user.is_moderator else "забраны"
                await update.callback_query.answer(
                    f"🛡️ Права модератора {status}"
                )
                await self.show_user_management(update, context, user_id)

            except Exception as e:
                logger.error(f"Ошибка переключения модерки: {e}")
                await update.callback_query.answer(
                    "❌ Ошибка при изменении прав"
                )

    async def toggle_subscription(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "❌ Пользователь не найден"
                    )
                    return

                if user.is_subscribed:
                    user.is_subscribed = False
                    user.is_manual_subscription = False
                    user.subscription_expires = None
                else:
                    user.is_subscribed = True
                    user.is_manual_subscription = True
                    user.subscription_expires = datetime.utcnow() + timedelta(
                        days=365
                    )  # Год подписки

                db.session.commit()

                status = "выдана" if user.is_subscribed else "забрана"
                await update.callback_query.answer(f"⭐ Подписка {status}")
                await self.show_user_management(update, context, user_id)

            except Exception as e:
                logger.error(f"Ошибка переключения подписки: {e}")
                await update.callback_query.answer(
                    "❌ Ошибка при изменении подписки"
                )

    async def confirm_delete_user(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "❌ Пользователь не найден"
                    )
                    return

                text = f"⚠️ ВНИМАНИЕ!\n\nВы действительно хотите удалить пользователя {user.username}?\n\nЭто действие нельзя отменить!"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "✅ Да, удалить",
                            callback_data=f"confirm_delete_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "❌ Отмена", callback_data=f"user_detail_{user_id}"
                        )
                    ],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.callback_query.edit_message_text(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка подтверждения удаления: {e}")
                await update.callback_query.answer(
                    "❌ Ошибка при загрузке данных"
                )

    async def delete_user(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "❌ Пользователь не найден"
                    )
                    return

                username = user.username

                TelegramUser.query.filter_by(user_id=user_id).delete()

                db.session.delete(user)
                db.session.commit()

                await update.callback_query.answer(
                    f"🗑️ Пользователь {username} удален"
                )
                await self.show_users_page(update, context, page=0)

            except Exception as e:
                logger.error(f"Ошибка удаления пользователя: {e}")
                await update.callback_query.answer(
                    "❌ Ошибка при удалении пользователя"
                )

    async def error_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        logger.error(f"Ошибка при обработке обновления: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка. Попробуйте позже."
            )

    def run_bot(self):
        if not BOT_TOKEN:
            logger.error("TG_TOKEN не найден в переменных окружения")
            return

        if not ADMIN_TELEGRAM_ID:
            logger.error("TG_ID не найден в переменных окружения")
            return

        application = Application.builder().token(BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("users", self.users_command))
        application.add_handler(
            CallbackQueryHandler(self.handle_callback_query)
        )
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, self.handle_message
            )
        )
        application.add_error_handler(self.error_handler)

        commands = [
            BotCommand("start", "Запустить бота"),
            BotCommand("help", "Справка"),
            BotCommand(
                "users", "Управление пользователями (только для админов)"
            ),
        ]

        async def post_init(application):
            await application.bot.set_my_commands(commands)

        application.post_init = post_init

        logger.info("Запуск Telegram бота...")
        application.run_polling()


if __name__ == "__main__":
    bot_manager = TelegramBotManager()
    bot_manager.run_bot()
