from app.models.alerts import AlertPayload


def normalize_alert_payload(value) -> AlertPayload | None:
    if value is None:
        return None
    if isinstance(value, AlertPayload):
        return value
    if isinstance(value, dict):
        return AlertPayload.model_validate(value)
    raise TypeError(f"Unsupported alert payload type: {type(value)!r}")
