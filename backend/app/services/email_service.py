"""Outbound email for low-stock alerts. Failures are logged, never raised."""

import logging
import smtplib
import threading
from collections.abc import Callable
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.config import settings

logger = logging.getLogger(__name__)

_PLACEHOLDER_HOSTS = {"", "smtp.example.com"}


def smtp_configured() -> bool:
    return settings.SMTP_HOST.strip().lower() not in _PLACEHOLDER_HOSTS


def _send(to: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
        try:
            smtp.starttls()
        except smtplib.SMTPNotSupportedError:
            pass
        if settings.SMTP_USER:
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(msg)


def send_alert_emails(
    alert_ids: list[int], session_factory: Callable[[], Session] | None = None
) -> None:
    """Email each alert's owner and mark email_sent. Safe to call after commit."""
    if not alert_ids:
        return
    if not smtp_configured():
        logger.info("SMTP not configured; skipping %d alert email(s)", len(alert_ids))
        return
    try:
        from app.database import SessionLocal
        from app.models.alert import Alert

        db = (session_factory or SessionLocal)()
    except Exception:
        logger.exception("Could not open session for alert emails")
        return
    try:
        for alert_id in alert_ids:
            try:
                alert = db.get(Alert, alert_id)
                if alert is None or alert.email_sent or alert.user is None:
                    continue
                _send(alert.user.email, "Low stock alert", str(alert.message))
                alert.email_sent = True
                db.commit()
            except Exception:
                db.rollback()
                logger.exception("Failed to send alert email for alert %s", alert_id)
    finally:
        db.close()


def send_alert_emails_in_thread(alert_ids: list[int]) -> None:
    threading.Thread(target=send_alert_emails, args=(alert_ids,), daemon=True).start()
