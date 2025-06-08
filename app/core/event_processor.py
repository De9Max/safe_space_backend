from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.event import Event, EventType
from app.models.incident import Incident, IncidentStatus, IncidentSeverity
from app.core.notification import send_incident_notification


def process_event(event_id: int):
    """
    Обробляє подію, визначає чи це інцидент, і якщо так - створює запис про інцидент.
    """
    db = SessionLocal()
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return

        # Позначаємо подію як оброблену
        event.processed = True
        db.add(event)
        db.commit()

        # Аналізуємо подію для визначення, чи це інцидент
        incident_data = analyze_event(event)

        if incident_data:
            # Створюємо запис про інцидент
            incident = Incident(
                title=incident_data["title"],
                description=incident_data["description"],
                severity=incident_data["severity"],
                data=incident_data["data"],
                event_id=event.id
            )
            db.add(incident)
            db.commit()
            db.refresh(incident)

            # Надсилаємо сповіщення про інцидент
            send_incident_notification(incident)

    finally:
        db.close()


def analyze_event(event: Event) -> dict:
    """
    Аналізує подію і визначає, чи є вона інцидентом.
    Повертає None, якщо подія не є інцидентом, або словник з даними інциденту.
    """
    # Логіка для визначення, чи є подія інцидентом, залежить від типу події
    if event.type == EventType.SMOKE_DETECTED:
        return {
            "title": "Smoke detected",
            "description": f"Smoke was detected by device {event.device.name} in {event.device.location or 'unknown location'}",
            "severity": IncidentSeverity.HIGH,
            "data": event.data
        }

    elif event.type == EventType.WATER_LEAK_DETECTED:
        return {
            "title": "Water leak detected",
            "description": f"Water leak was detected by device {event.device.name} in {event.device.location or 'unknown location'}",
            "severity": IncidentSeverity.MEDIUM,
            "data": event.data
        }

    elif event.type == EventType.MOTION_DETECTED:
        return None

    elif event.type == EventType.DOOR_OPENED:
        # Аналогічно, можна додати логіку для визначення, чи відкриття дверей є підозрілим
        return None

    elif event.type == EventType.TEMPERATURE:
        # Перевіряємо, чи температура перевищує певний поріг
        temperature = event.data.get("temperature", 0)
        if temperature > 15:
            return {
                "title": "High temperature detected",
                "description": f"Temperature of {temperature}°C was detected by device {event.device.name} in {event.device.location or 'unknown location'}",
                "severity": IncidentSeverity.MEDIUM,
                "data": event.data
            }
        elif temperature < 15:
            return {
                "title": "Low temperature detected",
                "description": f"Temperature of {temperature}°C was detected by device {event.device.name} in {event.device.location or 'unknown location'}",
                "severity": IncidentSeverity.MEDIUM,
                "data": event.data
            }
        return None

    elif event.type == EventType.HUMIDITY:
        humidity = event.data.get("humidity", 0)
        if humidity > 15:
            return {
                "title": "High humidity detected",
                "description": f"Humidity: {humidity}% was detected by device {event.device.name} in {event.device.location or 'unknown location'}",
                "severity": IncidentSeverity.MEDIUM,
                "data": event.data
            }
        elif humidity < 15:
            return {
                "title": "Low humidity detected",
                "description": f"Humidity: {humidity}% was detected by device {event.device.name} in {event.device.location or 'unknown location'}",
                "severity": IncidentSeverity.MEDIUM,
                "data": event.data
            }
        return None

    elif event.type == EventType.DEVICE_OFFLINE:
        # Можемо вважати втрату зв'язку з критичними пристроями (наприклад, димовими детекторами) як інцидент
        device_type = event.device.type
        if device_type in ["smoke_detector", "water_leak_sensor"]:
            return {
                "title": f"{device_type.replace('_', ' ').title()} is offline",
                "description": f"Lost connection with {event.device.name} in {event.device.location or 'unknown location'}",
                "severity": IncidentSeverity.LOW,
                "data": event.data
            }
        return None

    return None
