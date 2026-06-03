import importlib

import pytest

from app.core import config as config_module
from app.services import email_service as email_service_module


@pytest.mark.asyncio
async def test_email_service_reports_disabled_without_smtp_configuration(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "")
    monkeypatch.setenv("SMTP_USERNAME", "")
    monkeypatch.setenv("SMTP_PASSWORD", "")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "")
    config_module.get_settings.cache_clear()
    config_module.settings = config_module.get_settings()
    importlib.reload(email_service_module)

    service = email_service_module.EmailService()
    report = service.health_report()

    assert report["configured"] is False
    assert report["status"] == "disabled"
    assert report["password_present"] is False
