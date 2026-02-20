import logging
from django.core.mail import mail_admins


class ShortAdminEmailHandler(logging.Handler):
    """Отправляет только короткие сообщения на почту админам"""

    def emit(self, record):
        try:
            message = self.format(record)
            mail_admins(
                subject="[Django] Действие пользователя",
                message=message,
                html_message=None,
            )
        except Exception:
            pass
