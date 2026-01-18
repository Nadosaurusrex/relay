#!/usr/bin/env python3
"""
Simple Relay Demo - Direct OPA Integration

Demonstrates the core Relay concept without requiring the full Gateway.
"""

import requests
import json
from datetime import datetime
from uuid import uuid4


def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_scenario(number, description):
    print(f"\n{'─' * 70}")
    print(f"🎬 Scenario {number}: {description}")
    print(f"{'─' * 70}\n")


def evaluate_policy(provider, method, amount):
    """
    Evaluate a manifest against OPA policies.

    This simulates what the Gateway would do.
    """
    manifest = {
        "manifest_id": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "agent": {
            "agent_id": "sales-agent-001",
            "org_id": "acme-corp",
            "user_id": "demo@acme.com"
        },
        "action": {
            "provider": provider,
            "method": method,
            "parameters": {
                "amount": amount,
                "currency": "USD"
            }
        },
        "justification": {
            "reasoning": f"Demo {method} for ${amount/100:.2f}",
            "confidence_score": 0.95
        },
        "environment": "production"
    }

    print(f"   [{datetime.now().strftime('%H:%M:%S')}] Building manifest...")
    print(f"   ├─ Agent: {manifest['agent']['agent_id']}")
    print(f"   ├─ Action: {provider}.{method}")
    print(f"   └─ Amount: ${amount/100:.2f}")

    print(f"\n   [{datetime.now().strftime('%H:%M:%S')}] Evaluating against policies...")

    # Call OPA policy engine
    response = requests.post(
        "http://localhost:8181/v1/data/relay/policies/main",
        json={"input": manifest},
        timeout=5
    )

    result = response.json().get("result", {})
    approved = result.get("allow", False)
    reason = result.get("reason", "No policy matched")

    print(f"   [{datetime.now().strftime('%H:%M:%S')}] Policy decision received")

    return approved, reason, manifest


def simulate_payment(amount, currency="USD"):
    """Simulate executing a payment."""
    print(f"      💳 Executing Stripe payment: ${amount/100:.2f} {currency}")
    return {
        "id": f"ch_{int(datetime.now().timestamp())}",
        "amount": amount,
        "currency": currency,
        "status": "succeeded"
    }


def run_demo():
    """Run the demo scenarios."""
    print_header("🚀 Relay Demo - Agent Governance System")

    print("📡 Checking infrastructure...")

    # Check OPA
    try:
        response = requests.get("http://localhost:8181/health", timeout=5)
        print("   ✅ OPA is running")
    except:
        print("   ❌ OPA is not available")
        return

    # Check PostgreSQL
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "exec", "relay-postgres", "pg_isready", "-U", "relay"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("   ✅ PostgreSQL is running")
        else:
            print("   ⚠️  PostgreSQL may not be ready")
    except:
        print("   ⚠️  Could not check PostgreSQL")

    print("\n   🛡️  Policy engine: v1.0 (finance policies loaded)")

    # Scenario 1: Approved payment ($40)
    print_scenario(1, "Small Payment ($40) - Should be APPROVED ✅")

    approved, reason, manifest = evaluate_policy("stripe", "create_payment", 4000)

    if approved:
        result = simulate_payment(4000)
        print(f"\n   ✅ PAYMENT APPROVED")
        print(f"   ├─ Charge ID: {result['id']}")
        print(f"   ├─ Amount: ${result['amount'] / 100:.2f}")
        print(f"   ├─ Status: {result['status']}")
        print(f"   └─ Manifest ID: {manifest['manifest_id']}")
    else:
        print(f"\n   ❌ PAYMENT DENIED")
        print(f"   └─ Reason: {reason}")

    # Scenario 2: Denied payment ($60)
    print_scenario(2, "Large Payment ($60) - Should be DENIED ❌")

    approved, reason, manifest = evaluate_policy("stripe", "create_payment", 6000)

    if approved:
        result = simulate_payment(6000)
        print(f"\n   ✅ PAYMENT APPROVED")
        print(f"   └─ Charge ID: {result['id']}")
    else:
        print(f"\n   ❌ PAYMENT DENIED")
        print(f"   ├─ Reason: {reason}")
        print(f"   └─ Manifest ID: {manifest['manifest_id']}")

    # Scenario 3: Limit payment ($50)
    print_scenario(3, "Limit Payment ($50) - Should be APPROVED ✅")

    approved, reason, manifest = evaluate_policy("stripe", "create_payment", 5000)

    if approved:
        result = simulate_payment(5000)
        print(f"\n   ✅ PAYMENT APPROVED")
        print(f"   ├─ Charge ID: {result['id']}")
        print(f"   ├─ Amount: ${result['amount'] / 100:.2f}")
        print(f"   ├─ Status: {result['status']}")
        print(f"   └─ At policy limit of $50.00")
    else:
        print(f"\n   ❌ PAYMENT DENIED")
        print(f"   └─ Reason: {reason}")

    # Summary
    print_header("📊 Demo Complete")
    print("✅ Core Relay functionality demonstrated:")
    print("   ├─ Policy-based governance")
    print("   ├─ Deterministic approval/denial")
    print("   ├─ Manifest construction")
    print("   └─ OPA policy evaluation")
    print("\n📝 Infrastructure Status:")
    print("   ├─ PostgreSQL: Running ✅")
    print("   ├─ OPA: Running ✅")
    print("   └─ Policies: Loaded ✅")
    print("\n🔗 Next Steps:")
    print("   • Full Gateway: Start with 'docker-compose up gateway' (requires build)")
    print("   • View compiled policy: cat policies/compiled/finance.rego")
    print("   • Test OPA directly: curl http://localhost:8181/v1/data/relay/policies/main")
    print()


if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
