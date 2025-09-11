from flask_mail import Message
from .. import mail
import logging
from flask import current_app
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

logger = logging.getLogger(__name__)

class EmailService:
    """
    Сервис для отправки email сообщений (вертикальный современный шаблон)
    """
    
    @staticmethod
    def send_email_with_timeout(msg, timeout=10):
        """
        Отправляет email с таймаутом
        
        Args:
            msg: Message объект для отправки
            timeout: Таймаут в секундах (по умолчанию 10)
            
        Returns:
            bool: True если email отправлен успешно, False в противном случае
        """
        try:
            # Устанавливаем таймаут для SMTP соединения
            import socket
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout)
            
            try:
                mail.send(msg)
                return True
            finally:
                # Восстанавливаем оригинальный таймаут
                socket.setdefaulttimeout(original_timeout)
                
        except socket.timeout:
            logger.error(f"Email send timeout after {timeout} seconds")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False

    @staticmethod
    def send_verification_email(user_email: str, verification_code: str) -> bool:
        """
        Отправляет email с кодом подтверждения

        Args:
            user_email: Email пользователя
            verification_code: Код подтверждения

        Returns:
            bool: True если email отправлен успешно, False в противном случае
        """
        try:
            subject = "Добро пожаловать в cysu! Подтвердите ваш email"
            current_app.logger.info(f"Sending verification email to {user_email} with code: '{verification_code}' (type: {type(verification_code)}, length: {len(verification_code)})")
            html_body = f"""
            <!DOCTYPE html>
            <html lang="ru">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Подтверждение регистрации - cysu</title>
                <style>
                    body {{
                        margin: 0;
                        padding: 20px;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        background-color: #f8f9fa;
                        color: #212529;
                        line-height: 1.6;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: #ffffff;
                        border-radius: 20px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        overflow: hidden;
                        border: 1px solid #e9ecef;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #B595FF 0%, #9A7FE6 100%);
                        padding: 40px 30px;
                        text-align: center;
                        color: white;
                        position: relative;
                    }}
                    .header::before {{
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: linear-gradient(45deg, rgba(181, 149, 255, 0.1) 0%, rgba(154, 127, 230, 0.1) 100%);
                    }}
                    .header-content {{
                        position: relative;
                        z-index: 1;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 600;
                    }}
                    .header p {{
                        margin: 10px 0 0 0;
                        opacity: 0.95;
                        font-size: 16px;
                        font-weight: 400;
                    }}
                    .content {{
                        padding: 40px 30px;
                        text-align: center;
                    }}
                    .verification-title {{
                        font-size: 24px;
                        font-weight: 600;
                        color: #212529;
                        margin-bottom: 15px;
                    }}
                    .verification-desc {{
                        color: #6c757d;
                        font-size: 16px;
                        margin-bottom: 35px;
                        line-height: 1.6;
                    }}
                    .code-container {{
                        background: #f8f9fa;
                        border: 2px solid #e9ecef;
                        border-radius: 20px;
                        padding: 35px;
                        margin: 25px 0;
                        display: inline-block;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    }}
                    .verification-code {{
                        font-size: 42px;
                        font-weight: 700;
                        font-family: 'Courier New', monospace;
                        color: #B595FF;
                        letter-spacing: 12px;
                        margin: 0;
                    }}
                    .code-info {{
                        color: #6c757d;
                        font-size: 14px;
                        margin-top: 20px;
                        font-weight: 500;
                    }}
                    .footer {{
                        background: #f8f9fa;
                        padding: 30px;
                        text-align: center;
                        border-top: 1px solid #e9ecef;
                    }}
                    .footer p {{
                        margin: 8px 0;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                    .warning {{
                        background: rgba(255, 152, 0, 0.1);
                        border: 1px solid #FF9800;
                        border-radius: 20px;
                        padding: 20px;
                        margin: 25px 0;
                        color: #FF9800;
                        font-size: 14px;
                        font-weight: 500;
                    }}
                    .logo {{
                        font-size: 32px;
                        font-weight: 600;
                        color: white;
                        margin-bottom: 10px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="header-content">
                            <div class="logo">cysu</div>
                            <h1>Добро пожаловать!</h1>
                            <p>Современная образовательная платформа</p>
                        </div>
                    </div>
                    <div class="content">
                        <div class="verification-title">Подтвердите ваш email</div>
                        <div class="verification-desc">
                            Для завершения регистрации введите код<br>
                            подтверждения ниже
                        </div>
                        <div class="code-container">
                            <div class="verification-code">{verification_code}</div>
                            <div class="code-info">Код действителен в течение 15 минут</div>
                        </div>
                        <div class="warning">
                            ⚠️ Если вы не регистрировались в cysu, просто проигнорируйте это письмо.
                        </div>
                    </div>
                    <div class="footer">
                        <p>© 2025 cysu. Все права защищены.</p>
                        <p>Современная образовательная платформа нового поколения</p>
                    </div>
                </div>
            </body>
            </html>
            """
            text_body = f"""
            Добро пожаловать в cysu!

            Для завершения регистрации введите следующий код подтверждения:

            {verification_code}

            Код действителен в течение 15 минут.

            Если вы не регистрировались в cysu, просто проигнорируйте это письмо.

            © 2025 cysu. Все права защищены.
            """
            msg = Message(
                subject=subject, recipients=[user_email], html=html_body, body=text_body
            )
            
            # Используем метод с таймаутом
            success = EmailService.send_email_with_timeout(msg, timeout=10)
            if success:
                logger.info(
                    f"Verification email sent successfully to {user_email} with code: {verification_code}"
                )
                return True
            else:
                logger.error(f"Failed to send verification email to {user_email} - timeout or error")
                return False
        except Exception as e:
            logger.error(f"Failed to send verification email to {user_email}: {str(e)}")
            return False

    @staticmethod
    def send_resend_verification_email(user_email: str, verification_code: str) -> bool:
        """
        Отправляет повторный email с кодом подтверждения

        Args:
            user_email: Email пользователя
            verification_code: Код подтверждения

        Returns:
            bool: True если email отправлен успешно, False в противном случае
        """
        try:
            subject = "Новый код подтверждения - cysu"
            current_app.logger.info(f"Sending resend verification email to {user_email} with code: '{verification_code}' (type: {type(verification_code)}, length: {len(verification_code)})")
            html_body = f"""
            <!DOCTYPE html>
            <html lang="ru">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Новый код подтверждения - cysu</title>
                <style>
                    body {{
                        margin: 0;
                        padding: 20px;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        background-color: #f8f9fa;
                        color: #212529;
                        line-height: 1.6;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: #ffffff;
                        border-radius: 20px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        overflow: hidden;
                        border: 1px solid #e9ecef;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                        padding: 40px 30px;
                        text-align: center;
                        color: white;
                        position: relative;
                    }}
                    .header::before {{
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: linear-gradient(45deg, rgba(76, 175, 80, 0.1) 0%, rgba(69, 160, 73, 0.1) 100%);
                    }}
                    .header-content {{
                        position: relative;
                        z-index: 1;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 600;
                    }}
                    .header p {{
                        margin: 10px 0 0 0;
                        opacity: 0.95;
                        font-size: 16px;
                        font-weight: 400;
                    }}
                    .content {{
                        padding: 40px 30px;
                        text-align: center;
                    }}
                    .verification-title {{
                        font-size: 24px;
                        font-weight: 600;
                        color: #212529;
                        margin-bottom: 15px;
                    }}
                    .verification-desc {{
                        color: #6c757d;
                        font-size: 16px;
                        margin-bottom: 35px;
                        line-height: 1.6;
                    }}
                    .code-container {{
                        background: #f8f9fa;
                        border: 2px solid #e9ecef;
                        border-radius: 20px;
                        padding: 35px;
                        margin: 25px 0;
                        display: inline-block;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    }}
                    .verification-code {{
                        font-size: 42px;
                        font-weight: 700;
                        font-family: 'Courier New', monospace;
                        color: #4CAF50;
                        letter-spacing: 12px;
                        margin: 0;
                    }}
                    .code-info {{
                        color: #6c757d;
                        font-size: 14px;
                        margin-top: 20px;
                        font-weight: 500;
                    }}
                    .footer {{
                        background: #f8f9fa;
                        padding: 30px;
                        text-align: center;
                        border-top: 1px solid #e9ecef;
                    }}
                    .footer p {{
                        margin: 8px 0;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                    .warning {{
                        background: rgba(255, 152, 0, 0.1);
                        border: 1px solid #FF9800;
                        border-radius: 20px;
                        padding: 20px;
                        margin: 25px 0;
                        color: #FF9800;
                        font-size: 14px;
                        font-weight: 500;
                    }}
                    .logo {{
                        font-size: 32px;
                        font-weight: 600;
                        color: white;
                        margin-bottom: 10px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="header-content">
                            <div class="logo">cysu</div>
                            <h1>Новый код подтверждения</h1>
                            <p>Мы отправили вам новый код для завершения регистрации</p>
                        </div>
                    </div>
                    <div class="content">
                        <div class="verification-title">Подтвердите ваш email</div>
                        <div class="verification-desc">
                            Для завершения регистрации введите новый код<br>
                            подтверждения ниже
                        </div>
                        <div class="code-container">
                            <div class="verification-code">{verification_code}</div>
                            <div class="code-info">Код действителен в течение 15 минут</div>
                        </div>
                        <div class="warning">
                            ⚠️ Если вы не регистрировались в cysu, просто проигнорируйте это письмо.
                        </div>
                    </div>
                    <div class="footer">
                        <p>© 2025 cysu. Все права защищены.</p>
                        <p>Современная образовательная платформа нового поколения</p>
                    </div>
                </div>
            </body>
            </html>
            """
            text_body = f"""
            Новый код подтверждения - cysu

            Для завершения регистрации введите следующий код подтверждения:

            {verification_code}

            Код действителен в течение 15 минут.

            Если вы не регистрировались в cysu, просто проигнорируйте это письмо.

            © 2025 cysu. Все права защищены.
            """
            msg = Message(
                subject=subject, recipients=[user_email], html=html_body, body=text_body
            )
            
            # Используем метод с таймаутом
            success = EmailService.send_email_with_timeout(msg, timeout=10)
            if success:
                logger.info(
                    f"Resend verification email sent successfully to {user_email} with code: {verification_code}"
                )
                return True
            else:
                logger.error(f"Failed to send resend verification email to {user_email} - timeout or error")
                return False
        except Exception as e:
            logger.error(
                f"Failed to send resend verification email to {user_email}: {str(e)}"
            )
            return False

    @staticmethod
    def send_password_reset_email(user_email: str, reset_code: str) -> bool:
        """
        Отправляет email с кодом восстановления пароля

        Args:
            user_email: Email пользователя
            reset_code: Код восстановления пароля

        Returns:
            bool: True если email отправлен успешно, False в противном случае
        """
        try:
            subject = "Восстановление пароля - cysu"
            current_app.logger.info(f"Sending password reset email to {user_email} with code: '{reset_code}' (type: {type(reset_code)}, length: {len(reset_code)})")

            html_body = f"""
            <!DOCTYPE html>
            <html lang="ru">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Восстановление пароля - cysu</title>
                <style>
                    body {{
                        margin: 0;
                        padding: 20px;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        background-color: #f8f9fa;
                        color: #212529;
                        line-height: 1.6;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: #ffffff;
                        border-radius: 20px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        overflow: hidden;
                        border: 1px solid #e9ecef;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #F44336 0%, #d32f2f 100%);
                        padding: 40px 30px;
                        text-align: center;
                        color: white;
                        position: relative;
                    }}
                    .header::before {{
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: linear-gradient(45deg, rgba(244, 67, 54, 0.1) 0%, rgba(211, 47, 47, 0.1) 100%);
                    }}
                    .header-content {{
                        position: relative;
                        z-index: 1;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 600;
                    }}
                    .header p {{
                        margin: 10px 0 0 0;
                        opacity: 0.95;
                        font-size: 16px;
                        font-weight: 400;
                    }}
                    .content {{
                        padding: 40px 30px;
                        text-align: center;
                    }}
                    .verification-title {{
                        font-size: 24px;
                        font-weight: 600;
                        color: #212529;
                        margin-bottom: 15px;
                    }}
                    .verification-desc {{
                        color: #6c757d;
                        font-size: 16px;
                        margin-bottom: 35px;
                        line-height: 1.6;
                    }}
                    .code-container {{
                        background: #f8f9fa;
                        border: 2px solid #e9ecef;
                        border-radius: 20px;
                        padding: 35px;
                        margin: 25px 0;
                        display: inline-block;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    }}
                    .verification-code {{
                        font-size: 36px;
                        font-weight: 700;
                        font-family: 'Courier New', monospace;
                        color: #F44336;
                        letter-spacing: 8px;
                        margin: 0;
                    }}
                    .code-info {{
                        color: #6c757d;
                        font-size: 14px;
                        margin-top: 20px;
                        font-weight: 500;
                    }}
                    .footer {{
                        background: #f8f9fa;
                        padding: 30px;
                        text-align: center;
                        border-top: 1px solid #e9ecef;
                    }}
                    .footer p {{
                        margin: 8px 0;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                    .warning {{
                        background: rgba(244, 67, 54, 0.1);
                        border: 1px solid #F44336;
                        border-radius: 20px;
                        padding: 20px;
                        margin: 25px 0;
                        color: #F44336;
                        font-size: 14px;
                        font-weight: 500;
                    }}
                    .logo {{
                        font-size: 32px;
                        font-weight: 600;
                        color: white;
                        margin-bottom: 10px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="header-content">
                            <div class="logo">cysu</div>
                            <h1>Восстановление пароля</h1>
                            <p>Безопасное восстановление доступа к вашему аккаунту</p>
                        </div>
                    </div>
                    <div class="content">
                        <div class="verification-title">Создайте новый пароль</div>
                        <div class="verification-desc">
                            Введите код ниже для создания нового пароля
                        </div>
                        <div class="code-container">
                            <div class="verification-code">{reset_code}</div>
                            <div class="code-info">Код действителен в течение 15 минут</div>
                        </div>
                        <div class="warning">
                            ⚠️ Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо.
                        </div>
                    </div>
                    <div class="footer">
                        <p>© 2025 cysu. Все права защищены.</p>
                        <p>Современная образовательная платформа нового поколения</p>
                    </div>
                </div>
            </body>
            </html>
            """
            text_body = f"""
            Восстановление пароля - cysu

            Вы запросили восстановление пароля. Введите следующий код для создания нового пароля:

            {reset_code}

            Код действителен в течение 15 минут.

            Важно: Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо.

            © 2025 cysu. Все права защищены.
            """
            msg = Message(
                subject=subject, recipients=[user_email], html=html_body, body=text_body
            )
            
            # Используем метод с таймаутом
            success = EmailService.send_email_with_timeout(msg, timeout=10)
            if success:
                logger.info(
                    f"Password reset email sent successfully to {user_email} with code: {reset_code}"
                )
                return True
            else:
                logger.error(f"Failed to send password reset email to {user_email} - timeout or error")
                return False
        except Exception as e:
            logger.error(
                f"Failed to send password reset email to {user_email}: {str(e)}"
            )
            return False
