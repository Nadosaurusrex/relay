"""
Automatic manifest builder.

Constructs manifests from function calls and arguments.
"""

import inspect
from typing import Any, Dict, Callable, Optional
from uuid import uuid4

from sdk.models import Manifest, AgentContext, ActionRequest, Justification


class ManifestBuilder:
    """
    Builds manifests automatically from function calls.
    """

    def __init__(
        self,
        agent_id: str,
        org_id: str,
        user_id: Optional[str] = None,
        environment: str = "production",
    ):
        self.agent_id = agent_id
        self.org_id = org_id
        self.user_id = user_id
        self.environment = environment

    def build(
        self,
        provider: str,
        method: str,
        parameters: Dict[str, Any],
        reasoning: str,
        confidence_score: Optional[float] = None,
    ) -> Manifest:
        """
        Build a manifest from action parameters.

        Args:
            provider: Service provider (e.g., "stripe")
            method: Method being called (e.g., "create_payment")
            parameters: Function parameters
            reasoning: Natural language explanation
            confidence_score: Agent's confidence (0.0 to 1.0)

        Returns:
            A complete Manifest ready for validation
        """
        agent = AgentContext(
            agent_id=self.agent_id,
            org_id=self.org_id,
            user_id=self.user_id,
        )

        action = ActionRequest(
            provider=provider,
            method=method,
            parameters=parameters,
        )

        justification = Justification(
            reasoning=reasoning,
            confidence_score=confidence_score,
        )

        return Manifest(
            manifest_id=uuid4(),
            agent=agent,
            action=action,
            justification=justification,
            environment=self.environment,
        )

    @staticmethod
    def extract_parameters(func: Callable, args: tuple, kwargs: dict) -> Dict[str, Any]:
        """
        Extract parameters from function call.

        Maps positional and keyword arguments to parameter names.

        Args:
            func: The function being called
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Dictionary of parameter name -> value
        """
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Convert to dictionary
        parameters = dict(bound_args.arguments)

        # Remove 'self' or 'cls' if present
        parameters.pop('self', None)
        parameters.pop('cls', None)

        return parameters

    @staticmethod
    def generate_reasoning(
        provider: str,
        method: str,
        parameters: Dict[str, Any],
    ) -> str:
        """
        Generate a default reasoning string.

        Can be overridden by providing explicit reasoning.

        Args:
            provider: Service provider
            method: Method being called
            parameters: Action parameters

        Returns:
            Natural language reasoning
        """
        # Extract key parameters for reasoning
        key_params = []
        for key, value in list(parameters.items())[:3]:  # First 3 params
            if isinstance(value, (str, int, float, bool)):
                key_params.append(f"{key}={value}")

        param_str = ", ".join(key_params)
        return f"Agent requesting {provider}.{method}({param_str})"
