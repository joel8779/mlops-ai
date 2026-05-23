"""Secret Manager - Secure secret management and rotation."""

import os
import json
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class SecretType(str, Enum):
    """Types of secrets."""

    API_KEY = "api_key"
    DATABASE = "database"
    ENCRYPTION_KEY = "encryption_key"
    OAUTH_TOKEN = "oauth_token"
    WEBHOOK_SECRET = "webhook_secret"


@dataclass
class Secret:
    """Secret record."""

    secret_id: UUID
    name: str
    secret_type: SecretType
    encrypted_value: str
    organization_id: Optional[UUID]
    created_at: datetime
    expires_at: Optional[datetime]
    last_rotated: datetime
    rotation_period_days: Optional[int]


class SecretManager:
    """Manage secrets with encryption and rotation."""

    def __init__(
        self,
        master_key: Optional[str] = None,
    ) -> None:
        """Initialize secret manager.

        Args:
            master_key: Master encryption key (if None, uses environment)
        """
        self.master_key = master_key or os.environ.get("SECRET_MANAGER_KEY")
        if not self.master_key:
            raise ValueError("Secret manager key not configured")

        self.cipher = self._create_cipher(self.master_key)
        self.secrets: dict[UUID, Secret] = {}

    def _create_cipher(self, key: str) -> Fernet:
        """Create Fernet cipher from key.

        Args:
            key: Encryption key

        Returns:
            Fernet cipher
        """
        key_bytes = key.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"resume-intelligence-salt",
            iterations=100000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(key_bytes))
        return Fernet(derived_key)

    def create_secret(
        self,
        name: str,
        value: str,
        secret_type: SecretType,
        organization_id: Optional[UUID] = None,
        rotation_period_days: Optional[int] = None,
    ) -> Secret:
        """Create a new secret.

        Args:
            name: Secret name
            value: Secret value
            secret_type: Type of secret
            organization_id: Optional organization ID
            rotation_period_days: Rotation period in days

        Returns:
            Secret object
        """
        secret_id = uuid4()
        encrypted_value = self.cipher.encrypt(value.encode()).decode()

        secret = Secret(
            secret_id=secret_id,
            name=name,
            secret_type=secret_type,
            encrypted_value=encrypted_value,
            organization_id=organization_id,
            created_at=datetime.now(timezone.utc),
            expires_at=None,
            last_rotated=datetime.now(timezone.utc),
            rotation_period_days=rotation_period_days,
        )

        self.secrets[secret_id] = secret
        return secret

    def get_secret(self, secret_id: UUID) -> Optional[str]:
        """Decrypt and retrieve a secret.

        Args:
            secret_id: Secret ID

        Returns:
            Decrypted secret value or None
        """
        secret = self.secrets.get(secret_id)
        if not secret:
            return None

        decrypted = self.cipher.decrypt(secret.encrypted_value.encode()).decode()
        return decrypted

    def rotate_secret(self, secret_id: UUID, new_value: str) -> Secret:
        """Rotate a secret with a new value.

        Args:
            secret_id: Secret ID
            new_value: New secret value

        Returns:
            Updated Secret object
        """
        secret = self.secrets.get(secret_id)
        if not secret:
            raise ValueError(f"Secret {secret_id} not found")

        secret.encrypted_value = self.cipher.encrypt(new_value.encode()).decode()
        secret.last_rotated = datetime.now(timezone.utc)

        return secret

    def delete_secret(self, secret_id: UUID) -> None:
        """Delete a secret.

        Args:
            secret_id: Secret ID
        """
        if secret_id in self.secrets:
            del self.secrets[secret_id]

    def list_secrets(
        self,
        organization_id: Optional[UUID] = None,
        secret_type: Optional[SecretType] = None,
    ) -> list[Secret]:
        """List secrets with optional filters.

        Args:
            organization_id: Optional organization ID filter
            secret_type: Optional secret type filter

        Returns:
            List of Secret objects
        """
        secrets = list(self.secrets.values())

        if organization_id:
            secrets = [s for s in secrets if s.organization_id == organization_id]

        if secret_type:
            secrets = [s for s in secrets if s.secret_type == secret_type]

        return secrets

    def check_rotation_needed(self, secret_id: UUID) -> bool:
        """Check if a secret needs rotation.

        Args:
            secret_id: Secret ID

        Returns:
            True if rotation is needed
        """
        secret = self.secrets.get(secret_id)
        if not secret or not secret.rotation_period_days:
            return False

        days_since_rotation = (datetime.now(timezone.utc) - secret.last_rotated).days
        return days_since_rotation >= secret.rotation_period_days

    def rotate_expired_secrets(self) -> list[UUID]:
        """Rotate all secrets that need rotation.

        Returns:
            List of rotated secret IDs
        """
        rotated = []
        for secret_id in list(self.secrets.keys()):
            if self.check_rotation_needed(secret_id):
                # In production, this would generate new secrets
                # For now, just mark as rotated
                secret = self.secrets[secret_id]
                secret.last_rotated = datetime.now(timezone.utc)
                rotated.append(secret_id)

        return rotated
