from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FileField,
    IntegerField,
    PasswordField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)

from .models import Group
from .utils.email_validator import is_allowed_email_domain, get_allowed_domains_display
from .utils.username_validator import contains_forbidden_word


def validate_allowed_email_domain(form, field):
    """
    Валидатор для проверки разрешенных email доменов
    """
    if field.data:
        if not is_allowed_email_domain(field.data):
            raise ValidationError(
                "Регистрация недоступна для этого почтового сервиса"
            )


def validate_username_allowed(form, field):
    """
    Валидатор для проверки username на запрещенные слова
    """
    if field.data:
        if contains_forbidden_word(field.data):
            raise ValidationError(
                "Это имя пользователя недоступно"
            )


class LoginForm(FlaskForm):
    username = StringField("Имя пользователя или Email", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Имя пользователя",
        validators=[
            DataRequired(),
            Length(min=3, max=20),
            validate_username_allowed
        ]
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Введите корректный email адрес"),
            validate_allowed_email_domain
        ],
        render_kw={"data-description": get_allowed_domains_display()}
    )
    password = PasswordField(
        "Пароль", validators=[DataRequired(), Length(min=6)]
    )
    group_id = SelectField("Группа", validators=[DataRequired()])
    submit = SubmitField("Зарегистрироваться")

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.group_id.choices = [("", "Выберите группу")] + [
            (str(group.id), group.name)
            for group in Group.query.filter_by(is_active=True)
            .order_by(Group.name)
            .all()
        ]


class AdminUserForm(FlaskForm):
    username = StringField(
        "Имя пользователя",
        validators=[
            DataRequired(),
            Length(min=3, max=20),
            validate_username_allowed
        ]
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Введите корректный email адрес"),
            validate_allowed_email_domain
        ],
        render_kw={"data-description": get_allowed_domains_display()}
    )
    password = PasswordField(
        "Пароль", validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField(
        "Подтвердите пароль", validators=[DataRequired(), EqualTo("password")]
    )
    group_id = SelectField(
        "Группа", validators=[Optional()]
    )  # Группа необязательна в админке
    is_admin = BooleanField("Администратор")
    is_moderator = BooleanField("Модератор")
    submit = SubmitField("Зарегистрироваться")

    def __init__(self, *args, **kwargs):
        super(AdminUserForm, self).__init__(*args, **kwargs)
        self.group_id.choices = [("", "Без группы")] + [
            (str(group.id), group.name)
            for group in Group.query.filter_by(is_active=True)
            .order_by(Group.name)
            .all()
        ]


class EmailVerificationForm(FlaskForm):
    code = StringField(
        "Код подтверждения",
        validators=[
            DataRequired(message="Введите код подтверждения"),
            Length(min=6, max=6, message="Код должен содержать 6 цифр"),
        ],
    )
    submit = SubmitField("Подтвердить")


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Введите email"),
            Email(message="Введите корректный email"),
        ],
    )
    submit = SubmitField("Отправить код восстановления")


class PasswordResetForm(FlaskForm):
    code = StringField(
        "Код подтверждения",
        validators=[
            DataRequired(message="Введите код подтверждения"),
            Length(min=6, max=6, message="Код должен содержать 6 символов"),
        ],
    )
    new_password = PasswordField(
        "Новый пароль",
        validators=[
            DataRequired(message="Введите новый пароль"),
            Length(
                min=6, message="Пароль должен содержать минимум 6 символов"
            ),
        ],
    )
    confirm_password = PasswordField(
        "Подтвердите пароль",
        validators=[
            DataRequired(message="Подтвердите пароль"),
            EqualTo("new_password", message="Пароли не совпадают"),
        ],
    )
    submit = SubmitField("Сменить пароль")


class MaterialForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired()])
    description = TextAreaField(
        "Описание",
        validators=[
            Length(
                max=300, message="Описание не должно превышать 300 символов"
            )
        ],
    )
    type = SelectField(
        "Тип", choices=[("lecture", "Лекция"), ("assignment", "Задание")]
    )
    subject_id = SelectField(
        "Предмет", coerce=int, validators=[DataRequired()]
    )
    file = FileField("Файл")
    solution_file = FileField("Готовое решение (только для заданий)")
    submit = SubmitField("Сохранить")


class SubjectForm(FlaskForm):
    title = StringField("Название предмета", validators=[DataRequired()])
    description = TextAreaField("Описание")
    pattern_type = SelectField(
        "Фон предмета",
        choices=[
            ("circles", "Круги"),
            ("quilt", "Лоскутное одеяло"),
            ("waves", "Волны"),
        ],
        default="circles",
    )
    submit = SubmitField("Сохранить")


class SubmissionForm(FlaskForm):
    text = TextAreaField("Ответ")
    file = FileField("Файл")
    submit = SubmitField("Отправить")


class SubscriptionForm(FlaskForm):
    agree_terms = BooleanField(
        "Я согласен с условиями подписки", validators=[DataRequired()]
    )
    submit = SubmitField("Оформить подписку за 349₽/месяц")


class PaymentStatusForm(FlaskForm):
    payment_id = StringField("ID платежа", validators=[DataRequired()])
    submit = SubmitField("Проверить статус")


class TicketForm(FlaskForm):
    subject = StringField(
        "Тема",
        validators=[
            DataRequired(message="Введите тему тикета"),
            Length(
                min=5,
                max=255,
                message="Тема должна содержать от 5 до 255 символов",
            ),
        ],
    )
    message = TextAreaField(
        "Сообщение",
        validators=[
            DataRequired(message="Введите сообщение"),
            Length(
                min=10,
                message="Сообщение должно содержать минимум 10 символов",
            ),
        ],
    )
    files = FileField(
        "Прикрепить файлы (до 5 МБ каждый)", render_kw={"multiple": True}
    )
    submit = SubmitField("Отправить тикет")


class GroupForm(FlaskForm):
    name = StringField(
        "Название группы",
        validators=[
            DataRequired(message="Введите название группы"),
            Length(
                min=2,
                max=300,
                message="Название должно содержать от 2 до 300 символов",
            ),
        ],
    )
    description = TextAreaField("Описание")
    is_active = BooleanField("Активна")
    submit = SubmitField("Сохранить")


class SolutionForm(FlaskForm):
    text = TextAreaField("Текстовое решение", validators=[Optional()])
    file = FileField("Файл решения", validators=[Optional()])
    submit = SubmitField("Загрузить решение")


class SubjectGroupForm(FlaskForm):
    subject_id = SelectField(
        "Предмет", coerce=int, validators=[DataRequired()]
    )
    group_ids = SelectMultipleField(
        "Группы", coerce=int, validators=[DataRequired()]
    )
    submit = SubmitField("Сохранить")

    def __init__(self, *args, **kwargs):
        super(SubjectGroupForm, self).__init__(*args, **kwargs)

    def populate_choices(self, subjects, groups):
        self.subject_id.choices = [(0, "Выберите предмет")] + [
            (subject.id, subject.title) for subject in subjects
        ]
        self.group_ids.choices = [(group.id, group.name) for group in groups]


class SiteSettingsForm(FlaskForm):
    maintenance_mode = BooleanField("Технические работы")
    trial_subscription_enabled = BooleanField(
        "Включить пробную подписку для новых аккаунтов"
    )
    trial_subscription_days = IntegerField(
        "Количество дней пробной подписки",
        validators=[
            NumberRange(
                min=1,
                max=365,
                message="Количество дней должно быть от 1 до 365",
            )
        ],
    )
    pattern_generation_enabled = BooleanField(
        "Включить кнопку генерации паттернов"
    )
    support_enabled = BooleanField(
        "Включить систему тикетов и поддержки"
    )
    telegram_only_registration = BooleanField(
        "Регистрация только через Telegram"
    )
    submit = SubmitField("Сохранить настройки")
