from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, SelectField, BooleanField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, URL, Optional, NumberRange
from .models import User, Group

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    group_id = SelectField('Группа', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Заполняем выбор групп активными группами
        self.group_id.choices = [('', 'Выберите группу')] + [
            (str(group.id), group.name) for group in Group.query.filter_by(is_active=True).order_by(Group.name).all()
        ]


class AdminUserForm(FlaskForm):
    """Форма для создания пользователей в админке (группа необязательна)"""
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    group_id = SelectField('Группа', validators=[Optional()])  # Группа необязательна в админке
    is_admin = BooleanField('Администратор')
    is_moderator = BooleanField('Модератор')
    submit = SubmitField('Зарегистрироваться')

    def __init__(self, *args, **kwargs):
        super(AdminUserForm, self).__init__(*args, **kwargs)
        # Заполняем выбор групп активными группами
        self.group_id.choices = [('', 'Без группы')] + [
            (str(group.id), group.name) for group in Group.query.filter_by(is_active=True).order_by(Group.name).all()
        ]

    # Временно отключаем валидаторы уникальности для диагностики
    # def validate_username(self, username):
    #     user = User.query.filter_by(username=username.data).first()
    #     if user:
    #         raise ValidationError('Это имя пользователя уже занято. Выберите другое.')

    # def validate_email(self, email):
    #     user = User.query.filter_by(email=email.data).first()
    #     if user:
    #         raise ValidationError('Этот email уже зарегистрирован.')

class EmailVerificationForm(FlaskForm):
    """Форма для ввода кода подтверждения email"""
    code = StringField('Код подтверждения', validators=[
        DataRequired(message='Введите код подтверждения'),
        Length(min=6, max=6, message='Код должен содержать 6 цифр')
    ])
    submit = SubmitField('Подтвердить')

class PasswordResetRequestForm(FlaskForm):
    """Форма для запроса сброса пароля"""
    email = StringField('Email', validators=[
        DataRequired(message='Введите email'),
        Email(message='Введите корректный email')
    ])
    submit = SubmitField('Отправить код восстановления')

class PasswordResetForm(FlaskForm):
    """Форма для сброса пароля с кодом подтверждения"""
    code = StringField('Код подтверждения', validators=[
        DataRequired(message='Введите код подтверждения'),
        Length(min=8, max=8, message='Код должен содержать 8 символов')
    ])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Введите новый пароль'),
        Length(min=6, message='Пароль должен содержать минимум 6 символов')
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message='Подтвердите пароль'),
        EqualTo('new_password', message='Пароли не совпадают')
    ])
    submit = SubmitField('Сменить пароль')

class MaterialForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[Length(max=300, message='Описание не должно превышать 300 символов')])
    type = SelectField('Тип', choices=[('lecture', 'Лекция'), ('assignment', 'Задание')])
    subject_id = SelectField('Предмет', coerce=int, validators=[DataRequired()])
    file = FileField('Файл')
    solution_file = FileField('Готовое решение (только для заданий)')
    submit = SubmitField('Сохранить')

class SubjectForm(FlaskForm):
    title = StringField('Название предмета', validators=[DataRequired()])
    description = TextAreaField('Описание')
    pattern_type = SelectField('Фон предмета', choices=[
        ('circles', 'Круги'),
        ('quilt', 'Лоскутное одеяло'),
        ('waves', 'Волны')
    ], default='circles')
    submit = SubmitField('Сохранить')

class SubmissionForm(FlaskForm):
    text = TextAreaField('Ответ')
    file = FileField('Файл')
    submit = SubmitField('Отправить')

class SubscriptionForm(FlaskForm):
    """Форма для создания подписки"""
    agree_terms = BooleanField('Я согласен с условиями подписки', validators=[DataRequired()])
    submit = SubmitField('Оформить подписку за 349₽/месяц')

class PaymentStatusForm(FlaskForm):
    """Форма для проверки статуса платежа"""
    payment_id = StringField('ID платежа', validators=[DataRequired()])
    submit = SubmitField('Проверить статус')

class TicketForm(FlaskForm):
    """Форма для создания тикета поддержки"""
    subject = StringField('Тема', validators=[
        DataRequired(message='Введите тему тикета'),
        Length(min=5, max=255, message='Тема должна содержать от 5 до 255 символов')
    ])
    message = TextAreaField('Сообщение', validators=[
        DataRequired(message='Введите сообщение'),
        Length(min=10, message='Сообщение должно содержать минимум 10 символов')
    ])
    files = FileField('Прикрепить файлы (до 5 МБ каждый)', render_kw={'multiple': True})
    submit = SubmitField('Отправить тикет') 


class GroupForm(FlaskForm):
    """Форма для создания/редактирования группы"""
    name = StringField('Название группы', validators=[
        DataRequired(message='Введите название группы'),
        Length(min=2, max=300, message='Название должно содержать от 2 до 300 символов')
    ])
    description = TextAreaField('Описание')
    is_active = BooleanField('Активна')
    submit = SubmitField('Сохранить')

class SolutionForm(FlaskForm):
    """Форма для загрузки решения задания"""
    text = TextAreaField('Текстовое решение', validators=[Optional()])
    file = FileField('Файл решения', validators=[Optional()])
    submit = SubmitField('Загрузить решение')

class SubjectGroupForm(FlaskForm):
    """Форма для назначения предметов группам"""
    subject_id = SelectField('Предмет', coerce=int, validators=[DataRequired()])
    group_ids = SelectMultipleField('Группы', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(SubjectGroupForm, self).__init__(*args, **kwargs)
        # Данные будут заполнены позже в views.py

    def populate_choices(self, subjects, groups):
        """Заполняет выборы актуальными данными"""
        # Заполняем выбор предметов
        self.subject_id.choices = [(0, 'Выберите предмет')] + [
            (subject.id, subject.title) for subject in subjects
        ]
        # Заполняем выбор групп
        self.group_ids.choices = [
            (group.id, group.name) for group in groups
        ]


class SiteSettingsForm(FlaskForm):
    """Форма для управления настройками сайта"""
    maintenance_mode = BooleanField('Технические работы')
    trial_subscription_enabled = BooleanField('Включить пробную подписку для новых аккаунтов')
    trial_subscription_days = IntegerField('Количество дней пробной подписки', validators=[
        NumberRange(min=1, max=365, message='Количество дней должно быть от 1 до 365')
    ])
    pattern_generation_enabled = BooleanField('Включить кнопку генерации паттернов')
    submit = SubmitField('Сохранить настройки')