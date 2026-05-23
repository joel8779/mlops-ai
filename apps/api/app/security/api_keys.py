import secrets

from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_api_key() -> tuple[str, str, str]:
    raw = f"rai_{secrets.token_urlsafe(32)}"
    prefix = raw[:12]
    return raw, prefix, password_context.hash(raw)


def verify_api_key(raw_key: str, hashed_key: str) -> bool:
    return password_context.verify(raw_key, hashed_key)
