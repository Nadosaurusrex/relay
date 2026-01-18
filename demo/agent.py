#!/usr/bin/env python3
"""
Relay Demo Agent

Demonstrates approval and denial scenarios with the Relay SDK.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sdk.client import RelayClient
from sdk.decorator import protect
from sdk.models import PolicyViolationError


class SalesAgent:
    """
    Demo sales agent that processes payments.

    Uses Relay to ensure all payments are policy-compliant.
    """

    def __init__(self, relay_client: RelayClient):
        self.relay = relay_client

    @protect(provider="stripe", method="create_payment")
    def create_payment(self, amount: int, currency: str = "USD", customer_id: str = None):
        """
        Create a payment charge.

        This function is protected by Relay policies.
        """
        # Simulate Stripe API call
        print(f"      💳 Executing Stripe payment: ${amount / 100:.2f} {currency}")
        time.sleep(0.5)  # Simulate API call

        # In real implementation, this would call Stripe API
        charge_id = f"ch_{int(time.time())}"

        return {
            "id": charge_id,
            "amount": amount,
            "currency": currency,
            "customer": customer_id,
            "status": "succeeded",
        }

    @protect(provider="stripe", method="create_refund")
    def create_refund(self, charge_id: str, amount: int):
        """
        Create a refund.

        This function is also protected by Relay policies.
        """
        print(f"      💰 Executing Stripe refund: ${amount / 100:.2f}")
        time.sleep(0.5)

        refund_id = f"re_{int(time.time())}"

        return {
            "id": refund_id,
            "amount": amount,
            "charge": charge_id,
            "status": "succeeded",
        }


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_scenario(number: int, description: str):
    """Print scenario header."""
    print(f"\n{'─' * 70}")
    print(f"🎬 Scenario {number}: {description}")
    print(f"{'─' * 70}\n")


def run_demo():
    """Run the demo scenarios."""
    print_header("🚀 Relay Demo - Agent Governance in Action")

    # Initialize Relay client
    print("📡 Initializing Relay client...")
    relay_client = RelayClient(
        gateway_url="http://localhost:8000",
        agent_id="sales-agent-001",
        org_id="acme-corp",
        user_id="demo@acme.com",
        environment="production",
    )

    # Check Gateway health
    if not relay_client.health_check():
        print("❌ Relay Gateway is not available")
        print("   Make sure the Gateway is running: docker-compose up")
        sys.exit(1)

    print("✅ Connected to Relay Gateway\n")

    # Create agent
    agent = SalesAgent(relay_client)

    # Scenario 1: Approved payment ($40)
    print_scenario(1, "Small Payment - Should be APPROVED ✅")
    try:
        print(f"   [{datetime.now().strftime('%H:%M:%S')}] Building manifest...")
        print(f"   [{datetime.now().strftime('%H:%M:%S')}] Requesting validation from Gateway...")

        result = agent.create_payment(
            amount=4000,  # $40.00
            currency="USD",
            customer_id="cus_demo123"
        )

        print(f"\n   ✅ PAYMENT APPROVED")
        print(f"   ├─ Charge ID: {result['id']}")
        print(f"   ├─ Amount: ${result['amount'] / 100:.2f}")
        print(f"   └─ Status: {result['status']}")

    except PolicyViolationError as e:
        print(f"\n   ❌ PAYMENT DENIED")
        print(f"   └─ Reason: {e.denial_reason}")

    time.sleep(1)

    # Scenario 2: Denied payment ($60)
    print_scenario(2, "Large Payment - Should be DENIED ❌")
    try:
        print(f"   [{datetime.now().strftime('%H:%M:%S')}] Building manifest...")
        print(f"   [{datetime.now().strftime('%H:%M:%S')}] Requesting validation from Gateway...")

        result = agent.create_payment(
            amount=6000,  # $60.00 - exceeds $50 limit
            currency="USD",
            customer_id="cus_demo456"
        )

        print(f"\n   ✅ PAYMENT APPROVED")
        print(f"   └─ Charge ID: {result['id']}")

    except PolicyViolationError as e:
        print(f"\n   ❌ PAYMENT DENIED")
        print(f"   ├─ Reason: {e.denial_reason}")
        print(f"   └─ Manifest ID: {e.manifest_id}")

    time.sleep(1)

    # Scenario 3: Approved payment at the limit ($50)
    print_scenario(3, "Limit Payment - Should be APPROVED ✅")
    try:
        print(f"   [{datetime.now().strftime('%H:%M:%S')}] Building manifest...")
        print(f"   [{datetime.now().strftime('%H:%M:%S')}] Requesting validation from Gateway...")

        result = agent.create_payment(
            amount=5000,  # $50.00 - exactly at limit
            currency="USD",
            customer_id="cus_demo789"
        )

        print(f"\n   ✅ PAYMENT APPROVED")
        print(f"   ├─ Charge ID: {result['id']}")
        print(f"   ├─ Amount: ${result['amount'] / 100:.2f}")
        print(f"   └─ Status: {result['status']}")

    except PolicyViolationError as e:
        print(f"\n   ❌ PAYMENT DENIED")
        print(f"   └─ Reason: {e.denial_reason}")

    time.sleep(1)

    # Scenario 4: Refund (approved)
    print_scenario(4, "Small Refund - Should be APPROVED ✅")
    try:
        print(f"   [{datetime.now().strftime('%H:%M:%S')}] Building manifest...")
        print(f"   [{datetime.now().strftime('%H:%M:%S')}] Requesting validation from Gateway...")

        result = agent.create_refund(
            charge_id="ch_existing",
            amount=3000,  # $30.00 refund
        )

        print(f"\n   ✅ REFUND APPROVED")
        print(f"   ├─ Refund ID: {result['id']}")
        print(f"   ├─ Amount: ${result['amount'] / 100:.2f}")
        print(f"   └─ Status: {result['status']}")

    except PolicyViolationError as e:
        print(f"\n   ❌ REFUND DENIED")
        print(f"   └─ Reason: {e.denial_reason}")

    # Summary
    print_header("📊 Demo Complete")
    print("✅ All scenarios executed successfully")
    print("\n📝 Next steps:")
    print("   1. View audit trail: python demo/visualize.py")
    print("   2. Query API directly: curl http://localhost:8000/v1/audit/query")
    print("   3. Check OPA policies: curl http://localhost:8181/v1/data/relay/policies/main")
    print()


if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
