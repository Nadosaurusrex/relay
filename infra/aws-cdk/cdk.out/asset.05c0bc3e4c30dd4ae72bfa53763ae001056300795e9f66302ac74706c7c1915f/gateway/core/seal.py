"""
Cryptographic seal generation and verification using Ed25519.

This module provides tamper-proof cryptographic proofs that an action
was approved by the Relay policy engine.
"""

import base64
import json
from datetime import datetime
from typing import Dict, Any, Tuple
from uuid import UUID

import nacl.encoding
import nacl.signing

from gateway.models.manifest import Manifest
from gateway.models.seal import Seal


class SealGenerator:
    """
    Generates and verifies Ed25519 cryptographic seals.

    Seals prove that a manifest was validated against policies at a specific time.
    """

    def __init__(self, private_key_base64: str):
        """
        Initialize the seal generator with a private key.

        Args:
            private_key_base64: Base64-encoded Ed25519 private key (64 bytes)
        """
        private_key_bytes = base64.b64decode(private_key_base64)
        self.signing_key = nacl.signing.SigningKey(private_key_bytes)
        self.verify_key = self.signing_key.verify_key

    @classmethod
    def generate_keypair(cls) -> Tuple[str, str]:
        """
        Generate a new Ed25519 keypair.

        Returns:
            Tuple of (private_key_base64, public_key_base64)
        """
        signing_key = nacl.signing.SigningKey.generate()
        verify_key = signing_key.verify_key

        private_key_b64 = base64.b64encode(bytes(signing_key)).decode('utf-8')
        public_key_b64 = base64.b64encode(bytes(verify_key)).decode('utf-8')

        return private_key_b64, public_key_b64

    def _create_signable_payload(self, manifest: Manifest, policy_version: str, approved: bool) -> bytes:
        """
        Create a deterministic payload for signing.

        The payload includes all critical fields to prevent tampering.
        """
        payload = {
            "manifest_id": str(manifest.manifest_id),
            "timestamp": manifest.timestamp.isoformat(),
            "agent_id": manifest.agent.agent_id,
            "org_id": manifest.agent.org_id,
            "provider": manifest.action.provider,
            "method": manifest.action.method,
            "parameters": manifest.action.parameters,
            "policy_version": policy_version,
            "approved": approved,
        }

        # Serialize to JSON with sorted keys for determinism
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return payload_json.encode('utf-8')

    def create_seal(
        self,
        manifest: Manifest,
        approved: bool,
        policy_version: str,
        denial_reason: str = None,
        ttl_minutes: int = 5
    ) -> Seal:
        """
        Create a cryptographic seal for a manifest.

        Args:
            manifest: The manifest to seal
            approved: Whether the action was approved
            policy_version: Version of policies that were evaluated
            denial_reason: Reason for denial if not approved
            ttl_minutes: Time-to-live in minutes (default: 5)

        Returns:
            A Seal object with Ed25519 signature
        """
        # Create signable payload
        payload = self._create_signable_payload(manifest, policy_version, approved)

        # Sign the payload
        signed = self.signing_key.sign(payload)
        signature_b64 = base64.b64encode(signed.signature).decode('utf-8')

        # Get public key for verification
        public_key_b64 = base64.b64encode(bytes(self.verify_key)).decode('utf-8')

        # Generate seal ID and expiry
        seal_id = Seal.generate_seal_id(manifest.manifest_id)
        expires_at = Seal.create_expiry(ttl_minutes)

        return Seal(
            seal_id=seal_id,
            manifest_id=manifest.manifest_id,
            approved=approved,
            policy_version=policy_version,
            denial_reason=denial_reason,
            signature=signature_b64,
            public_key=public_key_b64,
            issued_at=datetime.utcnow(),
            expires_at=expires_at,
            was_executed=False,
        )

    def verify_seal(
        self,
        seal: Seal,
        manifest: Manifest,
    ) -> bool:
        """
        Verify that a seal is authentic and matches the manifest.

        Args:
            seal: The seal to verify
            manifest: The manifest that was sealed

        Returns:
            True if the seal is authentic, False otherwise
        """
        try:
            # Recreate the payload that was signed
            payload = self._create_signable_payload(
                manifest,
                seal.policy_version,
                seal.approved
            )

            # Decode signature and public key
            signature_bytes = base64.b64decode(seal.signature)
            public_key_bytes = base64.b64decode(seal.public_key)

            # Create verify key from public key
            verify_key = nacl.signing.VerifyKey(public_key_bytes)

            # Verify the signature
            verify_key.verify(payload, signature_bytes)

            return True

        except Exception:
            return False

    @staticmethod
    def verify_seal_static(
        signature_b64: str,
        public_key_b64: str,
        payload: bytes
    ) -> bool:
        """
        Statically verify a signature without needing the SealGenerator instance.

        Useful for verifying seals in other services (e.g., target APIs).

        Args:
            signature_b64: Base64-encoded signature
            public_key_b64: Base64-encoded public key
            payload: The original payload that was signed

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            signature_bytes = base64.b64decode(signature_b64)
            public_key_bytes = base64.b64decode(public_key_b64)

            verify_key = nacl.signing.VerifyKey(public_key_bytes)
            verify_key.verify(payload, signature_bytes)

            return True

        except Exception:
            return False


class SealValidationError(Exception):
    """Raised when a seal fails validation."""

    pass
