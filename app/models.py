import secrets
from datetime import datetime, timedelta

from flask_login import UserMixin

from . import db


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    users = db.relationship("User", backref="group", lazy=True)
    subjects = db.relationship(
        "SubjectGroup",
        backref="group",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Group {self.name}>"


class SubjectGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("subject_id", "group_id"),)

    def __repr__(self) -> str:
        return f"<SubjectGroup subject_id={self.subject_id} group_id={self.group_id}>"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_moderator = db.Column(db.Boolean, default=False)
    admin_mode_enabled = db.Column(db.Boolean, default=False)
    is_subscribed = db.Column(db.Boolean, default=False)
    subscription_expires = db.Column(db.DateTime)
    is_manual_subscription = db.Column(db.Boolean, default=False)
    is_trial_subscription = db.Column(db.Boolean, default=False)
    trial_subscription_expires = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    submissions = db.relationship(
        "Submission", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    payments = db.relationship("Payment", backref="user", lazy=True, cascade="all, delete-orphan")
    tickets = db.relationship(
        "Ticket",
        foreign_keys="Ticket.user_id",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )
    notifications = db.relationship(
        "Notification", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def is_effective_admin(self):
        return self.is_admin and self.admin_mode_enabled

    def can_manage_materials(self):
        return (self.is_admin and self.admin_mode_enabled) or self.is_moderator

    def can_see_all_subjects(self):
        return self.is_admin and self.admin_mode_enabled

    def get_accessible_subjects(self):
        from .models import Subject, SubjectGroup

        if self.can_see_all_subjects():
            return Subject.query.all()
        elif self.group_id:
            return (
                Subject.query.join(SubjectGroup)
                .filter(SubjectGroup.group_id == self.group_id)
                .all()
            )
        else:
            return []

    def can_add_materials_to_subject(self, subject):
        if self.is_admin and self.admin_mode_enabled:
            return True
        elif self.is_moderator and self.group_id:
            from .models import SubjectGroup

            return (
                SubjectGroup.query.filter_by(subject_id=subject.id, group_id=self.group_id).first()
                is not None
            )
        else:
            return False

    def can_manage_subject_materials(self, subject):
        return self.can_add_materials_to_subject(subject)

    def has_active_subscription(self):
        from .utils.payment_service import YooKassaService

        payment_service = YooKassaService()
        return payment_service.check_user_subscription(self)

    def get_role_display(self):
        if self.is_admin:
            return "Администратор" + (
                " (Админ режим)" if self.admin_mode_enabled else " (Пользователь режим)"
            )
        elif self.is_moderator:
            return "Модератор"
        else:
            return "Пользователь"


class EmailVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    user = db.relationship(
        "User",
        backref=db.backref("email_verifications", cascade="all, delete-orphan"),
    )

    def __repr__(self) -> str:
        return f'<EmailVerification {self.id}: {self.user.email if self.user else "Unknown"}>'

    @classmethod
    def generate_code(cls) -> str:
        import logging

        logger = logging.getLogger(__name__)
        code = "".join(secrets.choice("0123456789") for _ in range(6))
        logger.info(
            f"Generated verification code: '{code}' (type: {type(code)}, length: {len(code)})"
        )
        return code

    @classmethod
    def create_verification(
        cls,
        user_id: int = None,
        email: str = None,
        expires_in_minutes: int = 15,
    ) -> "EmailVerification":
        code = cls.generate_code()
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        return cls(user_id=user_id, email=email, code=code, expires_at=expires_at)


class PasswordReset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return f"<PasswordReset {self.id}: {self.email}>"

    @classmethod
    def generate_code(cls) -> str:
        import logging

        logger = logging.getLogger(__name__)
        code = "".join(secrets.choice("0123456789") for _ in range(6))
        logger.info(
            f"Generated password reset code: '{code}' (type: {type(code)}, length: {len(code)})"
        )
        return code

    @classmethod
    def create_reset(cls, email: str, expires_in_minutes: int = 15) -> "PasswordReset":
        code = cls.generate_code()
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        return cls(email=email, code=code, expires_at=expires_at)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    pattern_type = db.Column(db.String(50), default="dots")
    pattern_svg = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    materials = db.relationship(
        "Material", backref="subject", lazy=True, cascade="all, delete-orphan"
    )
    groups = db.relationship(
        "SubjectGroup",
        backref="subject",
        lazy=True,
        cascade="all, delete-orphan",
    )


class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    file = db.Column(db.String(255))
    type = db.Column(db.String(20))
    solution_file = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    submissions = db.relationship(
        "Submission",
        backref="material",
        lazy=True,
        cascade="all, delete-orphan",
    )


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey("material.id"), nullable=False)
    file = db.Column(db.String(255))
    text = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    yookassa_payment_id = db.Column(db.String(255), unique=True, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default="RUB")
    status = db.Column(db.String(20), default="pending")
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Payment {self.yookassa_payment_id}: {self.status}>"


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255))
    file_name = db.Column(db.String(255))
    file_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship(
        "User",
        backref=db.backref("chat_messages", cascade="all, delete-orphan"),
    )

    def __repr__(self) -> str:
        return f'<ChatMessage {self.id}: {self.user.username if self.user else "Unknown"}>'


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    admin_response = db.Column(db.Text)
    admin_response_at = db.Column(db.DateTime)
    admin_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user_response = db.Column(db.Text)
    user_response_at = db.Column(db.DateTime)
    files = db.relationship("TicketFile", backref="ticket", lazy=True, cascade="all, delete-orphan")
    admin = db.relationship("User", foreign_keys=[admin_id], backref="administered_tickets")

    def __repr__(self) -> str:
        return f"<Ticket {self.id}: {self.subject}>"


class TicketFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<TicketFile {self.id}: {self.file_name}>"


class TicketMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ticket = db.relationship("Ticket", backref="messages")
    user = db.relationship("User", backref="ticket_messages")

    def __repr__(self) -> str:
        return f'<TicketMessage {self.id}: {"Admin" if self.is_admin else "User"}>'


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default="info")
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    link = db.Column(db.String(255))

    def __repr__(self) -> str:
        return f"<Notification {self.id}: {self.title}>"


class ShortLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), unique=True, nullable=False, index=True)
    original_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    clicks = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<ShortLink {self.code} -> {self.original_url}>"

    @staticmethod
    def generate_code(length: int = 3) -> str:
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @classmethod
    def create_unique(cls, original_url: str, max_tries: int = 5) -> "ShortLink":
        for _ in range(max_tries):
            code = cls.generate_code()
            if not cls.query.filter_by(code=code).first():
                link = cls(code=code, original_url=original_url)
                db.session.add(link)
                db.session.commit()
                return link
        code = cls.generate_code(8)
        link = cls(code=code, original_url=original_url)
        db.session.add(link)
        db.session.commit()
        return link


class ShortLinkRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_link_id = db.Column(
        db.Integer, db.ForeignKey("short_link.id"), nullable=False, unique=True
    )
    expires_at = db.Column(db.DateTime, nullable=True)
    max_clicks = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    short_link = db.relationship(
        "ShortLink",
        backref=db.backref("rule", uselist=False, cascade="all, delete-orphan"),
    )

    def __repr__(self) -> str:
        return f"<ShortLinkRule link_id={self.short_link_id} expires_at={self.expires_at} max_clicks={self.max_clicks}>"


class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<SiteSettings {self.key}: {self.value}>"

    @classmethod
    def get_setting(cls, key: str, default=None):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            if setting.value.lower() in ["true", "false"]:
                return setting.value.lower() == "true"
            return setting.value
        return default

    @classmethod
    def set_setting(cls, key: str, value: str, description: str = None):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
            if description:
                setting.description = description
        else:
            setting = cls(key=key, value=str(value), description=description)
            db.session.add(setting)
        db.session.commit()
        return setting


class TelegramUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    is_bot = db.Column(db.Boolean, default=False)
    language_code = db.Column(db.String(10), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref="telegram_account", uselist=False)

    def __repr__(self) -> str:
        return f"<TelegramUser {self.telegram_id}: {self.username or self.first_name}>"

    @classmethod
    def get_or_create(
        cls,
        telegram_id,
        username=None,
        first_name=None,
        last_name=None,
        is_bot=False,
        language_code=None,
    ):
        tg_user = cls.query.filter_by(telegram_id=telegram_id).first()
        if not tg_user:
            tg_user = cls(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_bot=is_bot,
                language_code=language_code,
            )
            db.session.add(tg_user)
            db.session.commit()
        else:
            tg_user.username = username
            tg_user.first_name = first_name
            tg_user.last_name = last_name
            tg_user.is_bot = is_bot
            tg_user.language_code = language_code
            tg_user.last_activity = datetime.utcnow()
            db.session.commit()
        return tg_user
