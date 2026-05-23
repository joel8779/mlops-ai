import json

from app.logging import configure_logging, get_logger


def test_structured_logger_emits_json(capsys):
    configure_logging()
    logger = get_logger("test.logger", organization_id="org-1", recruiter_id="user-1")

    logger.info("contract_event", status="ok")

    output = capsys.readouterr().out.strip()
    payload = json.loads(output)
    assert payload["event"] == "contract_event"
    assert payload["organization_id"] == "org-1"
    assert payload["recruiter_id"] == "user-1"
    assert payload["status"] == "ok"
