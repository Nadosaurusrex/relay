"""
Policy engine integration with Open Policy Agent (OPA).

Evaluates manifests against Rego policies to determine approval/denial.
"""

import requests
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

from gateway.models.manifest import Manifest


class PolicyEngine:
    """
    Client for Open Policy Agent (OPA) policy evaluation.

    OPA provides deterministic policy decisions based on Rego rules.
    """

    def __init__(
        self,
        opa_url: str = "http://localhost:8181",
        policy_path: str = "relay/policies/main",
        timeout: int = 5,
    ):
        """
        Initialize the policy engine.

        Args:
            opa_url: Base URL of OPA server
            policy_path: Path to the policy package (e.g., "relay/policies/main")
            timeout: Request timeout in seconds
        """
        self.opa_url = opa_url.rstrip('/')
        self.policy_path = policy_path
        self.timeout = timeout
        self.policy_version = "v1.0.0"  # Will be loaded from OPA metadata

    def evaluate(self, manifest: Manifest) -> Tuple[bool, Optional[str]]:
        """
        Evaluate a manifest against OPA policies.

        Args:
            manifest: The manifest to evaluate

        Returns:
            Tuple of (approved: bool, denial_reason: Optional[str])

        Raises:
            PolicyEngineError: If OPA is unreachable or returns an error
        """
        # Convert manifest to OPA input format
        policy_input = manifest.to_policy_input()

        # Build OPA query URL
        # Example: http://localhost:8181/v1/data/relay/policies/main
        query_url = f"{self.opa_url}/v1/data/{self.policy_path.replace('.', '/')}"

        try:
            # Send policy query to OPA
            response = requests.post(
                query_url,
                json={"input": policy_input},
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )

            response.raise_for_status()
            result = response.json()

            # Extract decision from OPA response
            # Expected format: {"result": {"allow": true, "reason": "..."}}
            if "result" not in result:
                raise PolicyEngineError("Invalid OPA response: missing 'result' field")

            policy_result = result["result"]

            # Check for allow decision
            approved = policy_result.get("allow", False)

            # Get denial reason if not approved
            denial_reason = None
            if not approved:
                denial_reason = policy_result.get("reason", "Policy violation")

            return approved, denial_reason

        except requests.exceptions.Timeout:
            raise PolicyEngineError(f"OPA request timed out after {self.timeout}s")
        except requests.exceptions.ConnectionError:
            raise PolicyEngineError(f"Cannot connect to OPA at {self.opa_url}")
        except requests.exceptions.HTTPError as e:
            raise PolicyEngineError(f"OPA HTTP error: {e}")
        except Exception as e:
            raise PolicyEngineError(f"Policy evaluation failed: {str(e)}")

    def health_check(self) -> bool:
        """
        Check if OPA is healthy and reachable.

        Returns:
            True if OPA is healthy, False otherwise
        """
        try:
            response = requests.get(
                f"{self.opa_url}/health",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_policy_version(self) -> str:
        """
        Get the current policy version from OPA.

        Returns:
            Policy version string (e.g., "v1.2.3")
        """
        try:
            # Try to get policy metadata
            response = requests.get(
                f"{self.opa_url}/v1/data/relay/metadata/version",
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    return result["result"]

        except Exception:
            pass

        # Fallback to default version
        return self.policy_version

    def load_policy(self, policy_name: str, policy_rego: str) -> bool:
        """
        Load a Rego policy into OPA.

        Args:
            policy_name: Name of the policy (e.g., "finance")
            policy_rego: Rego policy code

        Returns:
            True if policy was loaded successfully

        Raises:
            PolicyEngineError: If policy loading fails
        """
        try:
            response = requests.put(
                f"{self.opa_url}/v1/policies/{policy_name}",
                data=policy_rego,
                timeout=self.timeout,
                headers={"Content-Type": "text/plain"}
            )

            response.raise_for_status()
            return True

        except Exception as e:
            raise PolicyEngineError(f"Failed to load policy '{policy_name}': {str(e)}")


class PolicyEngineError(Exception):
    """Raised when policy engine operations fail."""

    pass


class PolicyDecision:
    """
    Represents a policy decision with full context.
    """

    def __init__(
        self,
        approved: bool,
        policy_version: str,
        denial_reason: Optional[str] = None,
        evaluated_at: Optional[datetime] = None,
    ):
        self.approved = approved
        self.policy_version = policy_version
        self.denial_reason = denial_reason
        self.evaluated_at = evaluated_at or datetime.utcnow()

    def __repr__(self):
        status = "APPROVED" if self.approved else "DENIED"
        reason = f" ({self.denial_reason})" if self.denial_reason else ""
        return f"<PolicyDecision: {status}{reason}>"
