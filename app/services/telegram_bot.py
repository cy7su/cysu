# type: ignore
import logging
from typing import Optional, Dict, Any, List
from flask import current_app
from app.models import User

logger = logging.getLogger(__name__)


class TelegramBotService:

    def __init__(self):

        self.bot_token = current_app.config.get("TELEGRAM_BOT_TOKEN")
        self.bot_username = current_app.config.get("TELEGRAM_BOT_USERNAME", "cysu_bot")

    def process_telegram_auth(self, auth_data: str) -> Optional[User]:
        try:
            logger.info(f"Processing Telegram auth: {auth_data}")
            return None
        except Exception as e:
            logger.error(f"Error processing Telegram auth: {e}")
            return None

    def handle_webhook(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"Handling webhook update: {update_data}")
            return {"status": "ok"}
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return {"error": str(e)}

    def link_telegram_account(self, user: User) -> str:
        try:
            token = f"link_{user.id}_token"
            return f"https://t.me/{self.bot_username}?start={token}"
        except Exception as e:
            logger.error(f"Error generating link for user {user.id}: {e}")
            return ""

    def unlink_telegram_account(self, user: User) -> bool:
        try:
            if not user.telegram_id:
                return False

            user.telegram_id = None
            user.save()
            return True
        except Exception as e:
            logger.error(f"Error unlinking Telegram account for user {user.id}: {e}")
            return False

    def send_notification(self, user: User, message: str) -> bool:
        try:
            if not user.telegram_id or not self.bot_token:
                return False

            logger.info(f"Sending notification to {user.telegram_id}: {message}")
            return True
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False

    def get_user_stats(self, user: User) -> Dict[str, Any]:
        try:
            return {
                "telegram_id": user.telegram_id,
                "messages_sent": 0,
                "last_activity": "2025-01-15",
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}


telegram_bot_service = TelegramBotService()
