"""
Blueprint для обработки поддоменов - обрабатывает запросы на поддомене
"""
from flask import Blueprint, render_template, request, current_app, session, redirect, url_for, flash, send_from_directory, abort
from app.views import main, auth, admin
from app.models import User
from app import db
import os

subdomain_bp = Blueprint('subdomain', __name__)

@subdomain_bp.route('/static/<path:filename>')
def subdomain_static(filename):
    """Обслуживает статические файлы на поддомене"""
    static_folder = current_app.static_folder
    return send_from_directory(static_folder, filename)

@subdomain_bp.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@subdomain_bp.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    """Обрабатывает все запросы на поддомене, делегируя их соответствующим маршрутам"""
    # Получаем метод и данные запроса
    method = request.method
    args = request.args
    form_data = dict(request.form) if request.form else {}
    json_data = request.get_json() if request.is_json else None
    
    # Определяем маршрут на основе пути
    if path == '' or path == '/':
        # Главная страница
        return main.index()
    elif path.startswith('subject/'):
        # Маршруты предметов
        subject_path = path[8:]  # Убираем 'subject/'
        if subject_path.isdigit():
            # /subject/1 -> subject_detail(1)
            subject_id = int(subject_path)
            return main.subject_detail(subject_id)
        elif '/' in subject_path:
            # /subject/1/edit, /subject/1/delete
            parts = subject_path.split('/')
            if len(parts) == 2 and parts[0].isdigit():
                subject_id = int(parts[0])
                action = parts[1]
                if action == 'edit':
                    # TODO: Реализовать редактирование предмета
                    from flask import abort
                    abort(404)
                elif action == 'delete':
                    # TODO: Реализовать удаление предмета
                    from flask import abort
                    abort(404)
        else:
            return main.index()  # Fallback на главную
    elif path == 'login':
        # Вход
        return auth.login()
    elif path == 'register':
        # Регистрация
        return auth.register()
    elif path == 'logout':
        # Выход
        return auth.logout()
    elif path == 'email/verification':
        # Подтверждение email
        return auth.email_verification()
    elif path == 'email/resend':
        # Повторная отправка email
        return auth.email_resend()
    elif path == 'password/reset':
        # Сброс пароля
        return auth.password_reset()
    elif path.startswith('password/reset/confirm'):
        # Подтверждение сброса пароля
        return auth.password_reset_confirm()
    elif path.startswith('auth/'):
        # Старые маршруты auth/ (для совместимости)
        auth_path = path[5:]  # Убираем 'auth/'
        if auth_path == 'login':
            return auth.login()
        elif auth_path == 'register':
            return auth.register()
        elif auth_path == 'logout':
            return auth.logout()
        elif auth_path.startswith('verify/'):
            token = auth_path[7:]  # Убираем 'verify/'
            return auth.verify_email(token)
        elif auth_path == 'forgot-password':
            return auth.password_reset()
        elif auth_path.startswith('reset-password/'):
            token = auth_path[15:]  # Убираем 'reset-password/'
            return auth.password_reset_confirm()
        else:
            return main.index()  # Fallback на главную
    elif path.startswith('admin/'):
        # Маршруты админки
        admin_path = path[6:]  # Убираем 'admin/'
        if admin_path == '' or admin_path == 'users':
            return admin.admin_users()
        elif admin_path == 'groups':
            return admin.admin_groups()
        elif admin_path == 'subject-groups':
            return admin.admin_subject_groups()
        elif admin_path == 'settings':
            return admin.admin_settings()
        elif admin_path.startswith('user/'):
            user_id = admin_path[5:]  # Убираем 'user/'
            # Пока нет функции admin_user_detail, перенаправляем на users
            return admin.admin_users()
        else:
            return admin.admin_users()  # Fallback на админку
    elif path.startswith('profile/'):
        # Маршруты профиля
        profile_path = path[8:]  # Убираем 'profile/'
        if profile_path == '':
            return main.profile()
        elif profile_path == 'edit':
            # TODO: Реализовать редактирование профиля
            from flask import abort
            abort(404)
        elif profile_path == 'change-password':
            # TODO: Реализовать смену пароля
            from flask import abort
            abort(404)
        else:
            return main.profile()  # Fallback на профиль
    elif path.startswith('files/'):
        # Маршруты файлов
        file_path = path[6:]  # Убираем 'files/'
        if file_path == '':
            # TODO: Реализовать страницу файлов
            from flask import abort
            abort(404)
        elif file_path.startswith('upload'):
            # TODO: Реализовать загрузку файлов
            from flask import abort
            abort(404)
        elif file_path.startswith('download/'):
            # TODO: Реализовать скачивание файлов
            from flask import abort
            abort(404)
        elif file_path.startswith('delete/'):
            # TODO: Реализовать удаление файлов
            from flask import abort
            abort(404)
        else:
            # TODO: Реализовать страницу файлов
            from flask import abort
            abort(404)
    elif path == 'profile':
        # Профиль
        return main.profile()
    elif path.startswith('material/'):
        # Маршруты материалов
        material_path = path[9:]  # Убираем 'material/'
        if material_path.isdigit():
            # /material/1 -> material_detail(1)
            material_id = int(material_path)
            return main.material_detail(material_id)
        elif '/' in material_path:
            # /material/1/add_solution, /material/1/submit_solution, /material/1/delete
            parts = material_path.split('/')
            if len(parts) == 2 and parts[0].isdigit():
                material_id = int(parts[0])
                action = parts[1]
                if action == 'add_solution':
                    return main.add_solution_file(material_id)
                elif action == 'submit_solution':
                    # TODO: Реализовать отправку решения
                    from flask import abort
                    abort(404)
                elif action == 'delete':
                    return main.delete_material(material_id)
        else:
            return main.index()  # Fallback на главную
    elif path == 'toggle-admin-mode':
        # Переключение режима админа
        return main.toggle_admin_mode()
    elif path == 'privacy':
        # Политика конфиденциальности
        return main.privacy()
    elif path == 'terms':
        # Условия использования
        return main.terms()
    elif path == 'wiki':
        # База знаний
        return main.wiki()
    elif path == 'macro/time':
        # Макро время
        return main.macro_time()
    elif path == 'macro':
        # Макро
        return main.macro()
    elif path == 'tickets':
        # Тикеты
        from app.views import tickets
        return tickets.tickets()
    elif path.startswith('tickets/'):
        # Маршруты тикетов
        from app.views import tickets
        ticket_path = path[8:]  # Убираем 'tickets/'
        if ticket_path.isdigit():
            # /tickets/1 -> ticket_detail(1)
            ticket_id = int(ticket_path)
            return tickets.ticket_detail(ticket_id)
        elif '/' in ticket_path:
            # /tickets/1/accept, /tickets/1/reject, /tickets/1/close
            parts = ticket_path.split('/')
            if len(parts) == 2 and parts[0].isdigit():
                ticket_id = int(parts[0])
                action = parts[1]
                if action == 'accept':
                    return tickets.ticket_accept(ticket_id)
                elif action == 'reject':
                    return tickets.ticket_reject(ticket_id)
                elif action == 'close':
                    return tickets.ticket_close(ticket_id)
        else:
            return tickets.tickets()  # Fallback на список тикетов
    elif path == 'subscription':
        # Подписка
        from app.views import payment
        return payment.subscription()
    elif path.startswith('payment/'):
        # Маршруты платежей
        from app.views import payment
        payment_path = path[8:]  # Убираем 'payment/'
        if payment_path == 'webhook':
            return payment.payment_webhook()
        elif payment_path == 'success':
            return payment.payment_success()
        elif payment_path == 'cancel':
            return payment.payment_cancel()
        elif payment_path == 'status':
            return payment.payment_status()
        else:
            return payment.subscription()  # Fallback на подписку
    elif path.startswith('api/'):
        # API маршруты
        from app.views import api, tickets, payment
        api_path = path[4:]  # Убираем 'api/'
        if api_path == 'notifications':
            return api.get_notifications()
        elif api_path.startswith('notifications/'):
            # /api/notifications/1/read
            parts = api_path.split('/')
            if len(parts) == 3 and parts[0] == 'notifications' and parts[1].isdigit() and parts[2] == 'read':
                notification_id = int(parts[1])
                return api.mark_notification_read(notification_id)
        elif api_path.startswith('subject/'):
            # /api/subject/1/pattern
            parts = api_path.split('/')
            if len(parts) == 3 and parts[0] == 'subject' and parts[1].isdigit() and parts[2] == 'pattern':
                subject_id = int(parts[1])
                return api.update_subject_pattern(subject_id)
        elif api_path == 'ticket/create':
            return tickets.api_create_ticket()
        elif api_path.startswith('tickets/'):
            # /api/tickets/1/files
            parts = api_path.split('/')
            if len(parts) == 3 and parts[0] == 'tickets' and parts[1].isdigit() and parts[2] == 'files':
                ticket_id = int(parts[1])
                return tickets.api_ticket_files(ticket_id)
        elif api_path == 'ticket/response':
            return tickets.api_ticket_response()
        elif api_path == 'delete_all_closed_tickets':
            return tickets.api_delete_all_closed_tickets()
        elif api_path.startswith('payment/status/'):
            # /api/payment/status/payment_id
            payment_id = api_path[15:]  # Убираем 'payment/status/'
            return payment.api_payment_status(payment_id)
        else:
            return {'error': 'API endpoint not found'}, 404
    else:
        # Для остальных путей возвращаем главную страницу
        return main.index()
