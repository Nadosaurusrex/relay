"""
Relay SDK - Main entry point.

Provides a simple interface for integrating Relay into agent applications.
"""

from typing import Optional

from sdk.client import RelayClient, RelayClientError
from sdk.decorator import protect
from sdk.models import PolicyViolationError, Manifest, Seal

# Export main classes and decorators
__all__ = [
    'RelayClient',
    'protect',
    'PolicyViolationError',
    'RelayClientError',
    'Manifest',
    'Seal',
    'init',
]


# Global client instance
_global_client: Optional[RelayClient] = None


def init(
    gateway_url: str,
    agent_id: str,
    org_id: str,
    user_id: Optional[str] = None,
    environment: str = "production",
    timeout: int = 10,
) -> RelayClient:
    """
    Initialize a global Relay client.

    This is a convenience function for simple integrations.
    For more control, instantiate RelayClient directly.

    Usage:
        import relay
        relay.init(
            gateway_url="http://localhost:8000",
            agent_id="sales-agent-001",
            org_id="acme-corp",
        )

        @relay.protect(provider="stripe", method="create_payment")
        def create_payment(amount: int):
            ...

    Args:
        gateway_url: Base URL of Relay Gateway
        agent_id: Unique identifier for this agent
        org_id: Organization identifier
        user_id: Optional user ID
        environment: Deployment environment
        timeout: Request timeout in seconds

    Returns:
        Initialized RelayClient instance
    """
    global _global_client

    _global_client = RelayClient(
        gateway_url=gateway_url,
        agent_id=agent_id,
        org_id=org_id,
        user_id=user_id,
        environment=environment,
        timeout=timeout,
    )

    return _global_client


def get_client() -> Optional[RelayClient]:
    """
    Get the global Relay client instance.

    Returns:
        RelayClient if initialized, None otherwise
    """
    return _global_client
