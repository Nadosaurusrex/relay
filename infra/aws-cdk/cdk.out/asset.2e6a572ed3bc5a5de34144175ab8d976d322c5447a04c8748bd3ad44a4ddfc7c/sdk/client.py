"""
Relay Gateway HTTP client.

Communicates with the Gateway to validate manifests and verify seals.
"""

import requests
from typing import Tuple, Optional
from datetime import datetime

from sdk.models import Manifest, Seal, PolicyViolationError


class RelayClient:
    """
    HTTP client for Relay Gateway.

    Provides methods to validate manifests and verify seals.
    """

    def __init__(
        self,
        gateway_url: str,
        agent_id: str,
        org_id: str,
        user_id: Optional[str] = None,
        environment: str = "production",
        timeout: int = 10,
    ):
        """
        Initialize the Relay client.

        Args:
            gateway_url: Base URL of Relay Gateway (e.g., "http://localhost:8000")
            agent_id: Unique identifier for this agent
            org_id: Organization identifier
            user_id: Optional user ID on whose behalf the agent acts
            environment: Deployment environment
            timeout: Request timeout in seconds
        """
        self.gateway_url = gateway_url.rstrip('/')
        self.agent_id = agent_id
        self.org_id = org_id
        self.user_id = user_id
        self.environment = environment
        self.timeout = timeout

    def validate_manifest(self, manifest: Manifest, dry_run: bool = False) -> Tuple[bool, Optional[Seal], Optional[str]]:
        """
        Validate a manifest against policies.

        Args:
            manifest: The manifest to validate
            dry_run: If True, don't write to audit ledger

        Returns:
            Tuple of (approved, seal, denial_reason)

        Raises:
            PolicyViolationError: If the action is denied
            RelayClientError: If Gateway is unavailable
        """
        url = f"{self.gateway_url}/v1/manifest/validate"

        payload = {
            "manifest": manifest.model_dump(mode='json'),
            "dry_run": dry_run,
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 503:
                raise RelayClientError("Relay Gateway is unavailable (fail-closed)")

            response.raise_for_status()
            result = response.json()

            approved = result["approved"]
            denial_reason = result.get("denial_reason")

            # Parse seal if approved
            seal = None
            if approved and result.get("seal"):
                seal = Seal(**result["seal"])

            return approved, seal, denial_reason

        except requests.exceptions.Timeout:
            raise RelayClientError(f"Gateway request timed out after {self.timeout}s")
        except requests.exceptions.ConnectionError:
            raise RelayClientError(f"Cannot connect to Gateway at {self.gateway_url}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                raise RelayClientError("Policy engine unavailable (fail-closed)")
            raise RelayClientError(f"Gateway HTTP error: {e}")
        except Exception as e:
            raise RelayClientError(f"Validation request failed: {str(e)}")

    def verify_seal(self, seal_id: str) -> bool:
        """
        Verify a seal's authenticity.

        Args:
            seal_id: The seal ID to verify

        Returns:
            True if seal is valid, False otherwise

        Raises:
            RelayClientError: If Gateway is unavailable
        """
        url = f"{self.gateway_url}/v1/seal/verify"

        try:
            response = requests.get(
                url,
                params={"seal_id": seal_id},
                timeout=self.timeout,
            )

            response.raise_for_status()
            result = response.json()

            return result.get("valid", False)

        except Exception as e:
            raise RelayClientError(f"Seal verification failed: {str(e)}")

    def mark_seal_executed(self, seal_id: str) -> bool:
        """
        Mark a seal as executed.

        Should be called after successfully executing the action.

        Args:
            seal_id: The seal to mark as executed

        Returns:
            True if successful

        Raises:
            RelayClientError: If marking fails
        """
        url = f"{self.gateway_url}/v1/seal/mark-executed"

        try:
            response = requests.post(
                url,
                params={"seal_id": seal_id},
                timeout=self.timeout,
            )

            response.raise_for_status()
            return True

        except Exception as e:
            raise RelayClientError(f"Failed to mark seal as executed: {str(e)}")

    def health_check(self) -> bool:
        """
        Check if Gateway is healthy.

        Returns:
            True if Gateway is reachable and healthy
        """
        try:
            response = requests.get(
                f"{self.gateway_url}/health",
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception:
            return False


class RelayClientError(Exception):
    """Raised when Relay client operations fail."""

    pass
