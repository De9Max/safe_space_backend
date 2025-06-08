import logging
from app.models.incident import Incident, IncidentSeverity

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, body: str):
    """
    Надсилає email сповіщення.
    Примітка: в реальній системі тут буде використано реальний SMTP сервіс.
    """
    logger.info(f"Sending email to {to_email}, subject: {subject}")
    logger.info(f"Email body: {body}")
    # У реальному проекті тут буде код для надсилання email


def send_sms(phone_number: str, message: str):
    """
    Надсилає SMS сповіщення.
    Примітка: в реальній системі тут буде використано реальний SMS сервіс.
    """
    logger.info(f"Sending SMS to {phone_number}")
    logger.info(f"SMS message: {message}")
    # У реальному проекті тут буде код для надсилання SMS


def send_incident_notification(incident: Incident):
    """
    Надсилає сповіщення про інцидент користувачу.
    """
    # Отримуємо інформацію про простір та власника
    space = incident.event.device.space
    owner = space.owner

    # Формуємо текст сповіщення
    subject = f"[{incident.severity.name}] {incident.title} in {space.name}"
    body = f"""
    Incident details:
    -----------------
    Description: {incident.description}
    Severity: {incident.severity.name}
    Location: {incident.event.device.location or 'Unknown location'}
    Device: {incident.event.device.name}
    Time: {incident.created_at}

    Please check your dashboard for more details.
    """

    # Надсилаємо сповіщення залежно від налаштувань користувача та серйозності інциденту
    # Тут можна додати логіку для вибору способу сповіщення на основі серйозності інциденту
    if incident.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
        # Для серйозних інцидентів надсилаємо і email, і SMS
        if owner.email:
            send_email(owner.email, subject, body)
        if owner.phone:
            message = f"{incident.severity.name}: {incident.title} in {space.name} at {incident.event.device.location or 'unknown location'}"
            send_sms(owner.phone, message)
    else:
        # Для менш серйозних інцидентів надсилаємо лише email
        if owner.email:
            send_email(owner.email, subject, body)
