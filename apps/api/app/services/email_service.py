import asyncio
import smtplib
import time
from email.message import EmailMessage
from typing import Any

from app.core.config import settings
from app.logging import get_logger

logger = get_logger(__name__)


def mask_email(value: str | None) -> str | None:
    if not value or "@" not in value:
        return value
    local_part, domain = value.split("@", 1)
    if len(local_part) <= 1:
        masked_local = "*"
    else:
        masked_local = f"{local_part[0]}***"
    return f"{masked_local}@{domain}"


def _missing_smtp_fields() -> list[str]:
    missing: list[str] = []
    if not settings.smtp_host:
        missing.append("SMTP_HOST")
    if not settings.smtp_port:
        missing.append("SMTP_PORT")
    if not settings.smtp_username:
        missing.append("SMTP_USERNAME")
    if not settings.smtp_password:
        missing.append("SMTP_PASSWORD")
    if not settings.smtp_from_email:
        missing.append("SMTP_FROM_EMAIL")
    return missing


class EmailService:
    def __init__(self) -> None:
        self.smtp_retry_attempts = max(1, settings.smtp_retry_attempts)

    def health_report(self) -> dict[str, Any]:
        missing = _missing_smtp_fields()
        configured = not missing
        if not configured:
            status = "disabled"
            reason = f"Missing SMTP configuration: {', '.join(missing)}"
        else:
            status = "configured"
            reason = "SMTP configured"
        return {
            "configured": configured,
            "status": status,
            "reason": reason,
            "host": settings.smtp_host,
            "port": settings.smtp_port,
            "from_email": mask_email(settings.smtp_from_email),
            "username_configured": bool(settings.smtp_username),
            "password_present": bool(settings.smtp_password),
            "use_tls": settings.smtp_use_tls,
            "missing": missing,
        }

    def validate_configuration(self) -> dict[str, Any]:
        report = self.health_report()
        if not report["configured"]:
            logger.warning(
                "smtp_not_configured",
                host=settings.smtp_host,
                from_email=mask_email(settings.smtp_from_email),
                username=mask_email(settings.smtp_username),
                password_present=bool(settings.smtp_password),
                missing=report["missing"],
            )
            return report

        logger.info(
            "smtp_configured",
            host=settings.smtp_host,
            port=settings.smtp_port,
            from_email=mask_email(settings.smtp_from_email),
            username=mask_email(settings.smtp_username),
            password_present=bool(settings.smtp_password),
            use_tls=settings.smtp_use_tls,
        )
        return report

    def _build_message(self, to_email: str, subject: str, body: str, html_body: str | None = None) -> EmailMessage:
        message = EmailMessage()
        message["Subject"] = subject
        if not settings.smtp_from_email:
            raise RuntimeError("SMTP from email is not configured")
        message["From"] = settings.smtp_from_email
        message["To"] = to_email
        message.set_content(body)
        if html_body:
            message.add_alternative(html_body, subtype="html")
        return message

    def _connect(self) -> smtplib.SMTP:
        if settings.smtp_port == 465:
            server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=settings.smtp_timeout_seconds)
        else:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=settings.smtp_timeout_seconds)
            if settings.smtp_use_tls:
                server.starttls()
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)
        return server

    def _verify_connection_sync(self) -> None:
        with self._connect() as server:
            server.noop()

    def _send_message_sync(self, message: EmailMessage) -> None:
        with self._connect() as server:
            server.send_message(message)

    def send_message(self, to_email: str, subject: str, body: str, html_body: str | None = None) -> None:
        report = self.health_report()
        if not report["configured"]:
            raise RuntimeError(report["reason"])

        message = self._build_message(to_email=to_email, subject=subject, body=body, html_body=html_body)
        last_exception: Exception | None = None
        for attempt in range(self.smtp_retry_attempts):
            try:
                self._send_message_sync(message)
                logger.info(
                    "smtp_email_sent",
                    recipient=mask_email(to_email),
                    host=settings.smtp_host,
                    attempt=attempt + 1,
                )
                return
            except (smtplib.SMTPException, OSError) as exc:
                last_exception = exc
                logger.warning(
                    "smtp_email_send_failed",
                    recipient=mask_email(to_email),
                    host=settings.smtp_host,
                    attempt=attempt + 1,
                    error=str(exc),
                )
                if attempt == self.smtp_retry_attempts - 1:
                    break
                delay = settings.smtp_retry_backoff_seconds * (2 ** attempt)
                time.sleep(delay)

        if last_exception is not None:
            raise last_exception
        raise RuntimeError("SMTP delivery failed")

    async def send_message_async(self, to_email: str, subject: str, body: str, html_body: str | None = None) -> None:
        report = self.health_report()
        if not report["configured"]:
            raise RuntimeError(report["reason"])

        await asyncio.to_thread(self.send_message, to_email, subject, body, html_body)

    async def send_shortlist_email_async(
        self,
        *,
        to_email: str,
        candidate_name: str,
        job_title: str,
        organization_name: str,
        recruiter_email: str,
    ) -> dict[str, Any]:
        subject = f"Shortlisted for {job_title} at {organization_name}"
        body = (
            f"Hi {candidate_name},\n\n"
            f"Congratulations. You have been shortlisted for the {job_title} role at {organization_name}.\n\n"
            f"Our recruiting team will review the next steps and follow up from {recruiter_email}. "
            "Please reply to this email if you would like to confirm your interest or share availability.\n\n"
            "Best regards,\n"
            f"{organization_name} Recruiting Team"
        )
        html_body = (
            f"<p>Hi {candidate_name},</p>"
            f"<p>Congratulations. You have been shortlisted for the <strong>{job_title}</strong> role at "
            f"<strong>{organization_name}</strong>.</p>"
            f"<p>Our recruiting team will review the next steps and follow up from {recruiter_email}. "
            "Please reply to confirm your interest or share availability.</p>"
            f"<p>Best regards,<br>{organization_name} Recruiting Team</p>"
        )
        await self.send_message_async(to_email=to_email, subject=subject, body=body, html_body=html_body)
        return {"subject": subject, "recipient": mask_email(to_email), "status": "sent"}

    async def verify_connection_async(self) -> dict[str, Any]:
        report = self.health_report()
        if not report["configured"]:
            return report

        try:
            await asyncio.to_thread(self._verify_connection_sync)
            report["status"] = "healthy"
            report["checked"] = True
            logger.info("smtp_health_check_passed", host=settings.smtp_host, port=settings.smtp_port)
            return report
        except (smtplib.SMTPException, OSError) as exc:
            report["status"] = "unhealthy"
            report["error"] = str(exc)
            logger.warning("smtp_health_check_failed", host=settings.smtp_host, port=settings.smtp_port, error=str(exc))
            return report
