"""
@relay.protect() decorator implementation.

Intercepts function calls and validates them against Relay policies.
"""

import functools
from typing import Callable, Optional, Any

from sdk.models import PolicyViolationError
from sdk.client import RelayClient, RelayClientError
from sdk.manifest_builder import ManifestBuilder


def protect(
    provider: str,
    method: str,
    reasoning: Optional[str] = None,
    confidence_score: Optional[float] = None,
    fail_open: bool = False,
):
    """
    Decorator to protect a function with Relay policy enforcement.

    Usage:
        @relay.protect(provider="stripe", method="create_payment")
        def create_payment(amount: int, currency: str):
            return stripe.Charge.create(amount=amount, currency=currency)

    Args:
        provider: Service provider (e.g., "stripe", "aws", "github")
        method: Method name (e.g., "create_payment", "delete_bucket")
        reasoning: Optional explicit reasoning (auto-generated if not provided)
        confidence_score: Agent's confidence in this action (0.0 to 1.0)
        fail_open: If True, allow execution if Gateway is unavailable (default: False)

    Returns:
        Decorated function that validates against policies before execution
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get Relay client from the instance or global context
            relay_client = _get_relay_client(args)

            if not relay_client:
                raise RelayClientError(
                    "No Relay client found. Initialize RelayClient and pass as first argument "
                    "or set as global."
                )

            # Build manifest builder
            manifest_builder = ManifestBuilder(
                agent_id=relay_client.agent_id,
                org_id=relay_client.org_id,
                user_id=relay_client.user_id,
                environment=relay_client.environment,
            )

            # Extract parameters
            parameters = manifest_builder.extract_parameters(func, args, kwargs)

            # Generate reasoning if not provided
            action_reasoning = reasoning or manifest_builder.generate_reasoning(
                provider, method, parameters
            )

            # Build manifest
            manifest = manifest_builder.build(
                provider=provider,
                method=method,
                parameters=parameters,
                reasoning=action_reasoning,
                confidence_score=confidence_score,
            )

            # Validate manifest
            try:
                approved, seal, denial_reason = relay_client.validate_manifest(manifest)

                if not approved:
                    raise PolicyViolationError(
                        denial_reason=denial_reason or "Policy violation",
                        manifest_id=manifest.manifest_id,
                    )

                # Execute the protected function
                result = func(*args, **kwargs)

                # Mark seal as executed
                if seal:
                    try:
                        relay_client.mark_seal_executed(seal.seal_id)
                    except Exception:
                        # Don't fail the action if marking execution fails
                        pass

                return result

            except RelayClientError as e:
                # Gateway unavailable
                if fail_open:
                    # Allow execution without approval (graceful degradation)
                    print(f"⚠️  Relay Gateway unavailable, executing without approval: {e}")
                    return func(*args, **kwargs)
                else:
                    # Fail closed - block execution
                    raise PolicyViolationError(
                        denial_reason=f"Gateway unavailable (fail-closed): {e}",
                        manifest_id=manifest.manifest_id,
                    )

        return wrapper

    return decorator


def _get_relay_client(args: tuple) -> Optional[RelayClient]:
    """
    Extract RelayClient from function arguments.

    Checks:
    1. First argument (e.g., self.relay or self._relay)
    2. Global _relay_client variable

    Args:
        args: Function arguments

    Returns:
        RelayClient instance if found, None otherwise
    """
    # Check if first argument has relay client
    if args:
        first_arg = args[0]
        if isinstance(first_arg, RelayClient):
            return first_arg
        if hasattr(first_arg, 'relay'):
            return first_arg.relay
        if hasattr(first_arg, '_relay'):
            return first_arg._relay

    # Check global context
    import sys
    frame = sys._getframe(2)  # Go up to caller's frame
    if '_relay_client' in frame.f_globals:
        return frame.f_globals['_relay_client']

    return None
