# Relay - Agent Governance System

> **"Docusign for Machine-to-Machine Reasoning"**

Relay is an agent governance system that creates an "air gap" between autonomous agents and critical actions. It intercepts agent tool calls, validates them against deterministic policies (OPA/Rego), issues cryptographic proofs (Ed25519), and maintains an immutable audit trail (PostgreSQL).

## 🎯 Core Value Proposition

**Solve the "Manager-to-Agent" trust problem** by making agent actions:
- ✅ **Auditable**: Every action logged in an immutable ledger
- ✅ **Policy-controlled**: Deterministic OPA/Rego policies
- ✅ **Tamper-proof**: Ed25519 cryptographic seals
- ✅ **Fail-safe**: Fail-closed by default for critical actions

## 🏗️ Architecture

```
Agent Runtime          Relay Gateway (FastAPI)         Target Service
     │                         │                              │
     │  @relay.protect()       │                              │
     │  intercepts function    │                              │
     │                         │                              │
     │  POST /v1/manifest/     │                              │
     │       validate          │                              │
     ├────────────────────────>│                              │
     │                         │  1. Validate schema          │
     │                         │  2. Call OPA policy engine   │
     │                         │  3. Generate Ed25519 seal    │
     │                         │  4. Write to audit ledger    │
     │                         │                              │
     │  Return sealed approval │                              │
     │<────────────────────────┤                              │
     │                         │                              │
     │  Execute with seal      │                              │
     ├─────────────────────────┼─────────────────────────────>│
```

## 🚀 Quick Start

### 1. Generate Cryptographic Keys

```bash
cd ~/relay
python scripts/generate_keys.py --output .env
```

### 2. Start Infrastructure

```bash
cd infra
docker-compose up -d
```

This starts:
- PostgreSQL (audit ledger)
- OPA (policy engine)
- Relay Gateway (FastAPI service)

### 3. Bootstrap Policies

```bash
python scripts/bootstrap_policies.py
```

### 4. Run Examples

```bash
# Quick demo
python examples/simple_demo.py

# Or explore Jupyter notebooks
cd examples && jupyter notebook
```

### 5. View Audit Trail

```bash
python examples/visualize.py
```

## 📦 Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15

### Install Dependencies

```bash
cd ~/relay
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🔧 Configuration

Configure via environment variables (or `.env` file):

```bash
# Database
RELAY_DB_HOST=localhost
RELAY_DB_PORT=5432
RELAY_DB_NAME=relay
RELAY_DB_USER=relay
RELAY_DB_PASSWORD=relay_password

# OPA Policy Engine
RELAY_OPA_URL=http://localhost:8181
RELAY_POLICY_PATH=relay/policies/main

# Cryptography
RELAY_PRIVATE_KEY=<your-ed25519-private-key>
RELAY_SEAL_TTL_MINUTES=5

# API
RELAY_API_HOST=0.0.0.0
RELAY_API_PORT=8000
```

## 📚 Examples & Tutorials

The `examples/` directory contains comprehensive Jupyter notebooks demonstrating Relay's capabilities:

### Core Examples

1. **01_getting_started.ipynb** - Quick introduction to Relay basics
2. **02_adversarial_prompt_protection.ipynb** - The "Air Gap" concept: protection from LLM manipulation
3. **03_langchain_integration.ipynb** - Seamless integration with LangChain (3 lines of code)
4. **04_company_policies.ipynb** - Mapping business rules to technical constraints
5. **05_real_world_scenarios.ipynb** - Production scenarios with cost-benefit analysis

### Key Demonstrations

- 🛡️ **Safety**: Even if an LLM is convinced by adversarial prompts, Relay blocks unauthorized actions
- 🔌 **Integration**: Add governance to existing frameworks with minimal code changes
- 📋 **Policy Mapping**: Translate CFO/CTO rules into enforceable YAML policies
- 💰 **ROI**: Real incidents that cost millions, and how Relay prevents them

See `examples/README.md` for detailed learning paths and guides.

## 💻 SDK Usage

### Basic Example

```python
from sdk.client import RelayClient
from sdk.decorator import protect
from sdk.models import PolicyViolationError

# Initialize Relay client
relay = RelayClient(
    gateway_url="http://localhost:8000",
    agent_id="sales-agent-001",
    org_id="acme-corp",
)

# Protect a function with policy enforcement
@protect(provider="stripe", method="create_payment")
def create_payment(amount: int, currency: str):
    """This function is now protected by Relay policies."""
    return stripe.Charge.create(amount=amount, currency=currency)

# Use the protected function
try:
    result = create_payment(amount=4500, currency="USD")
    print(f"✅ Payment succeeded: {result['id']}")
except PolicyViolationError as e:
    print(f"❌ Blocked: {e.denial_reason}")
```

### Class-based Example

```python
class SalesAgent:
    def __init__(self):
        self.relay = RelayClient(
            gateway_url="http://localhost:8000",
            agent_id="sales-agent-001",
            org_id="acme-corp",
        )

    @protect(provider="stripe", method="create_payment")
    def process_payment(self, amount: int):
        # Protected by Relay
        return stripe.Charge.create(amount=amount, currency="USD")
```

## 📝 Policy Management

### YAML Policy Format

Create human-readable policies in YAML:

```yaml
# policies/finance.yaml
version: "1.0"
package: "relay.policies.main"

policies:
  - name: "spending_limits"
    rules:
      - id: "small_payments_allowed"
        condition:
          provider: "stripe"
          method: "create_payment"
          parameter_constraints:
            amount:
              max: 5000  # $50.00 in cents
        action: "allow"

      - id: "large_payments_denied"
        condition:
          provider: "stripe"
          method: "create_payment"
          parameter_constraints:
            amount:
              min: 5000
        action: "deny"
        reason: "Payment exceeds $50.00 limit"
```

### Compile and Load Policies

```bash
# Compile YAML to Rego
python policy-compiler/compiler.py policies/finance.yaml policies/compiled/finance.rego

# Load into OPA
python scripts/bootstrap_policies.py
```

## 🔐 Security

### Cryptographic Seals

Every approved action receives an Ed25519 signature:

```python
{
  "seal_id": "seal_1705491000_abc123",
  "manifest_id": "uuid-123",
  "approved": true,
  "signature": "kZXJ0aWZpY2F0ZSBm...",
  "public_key": "MCowBQYDK2VwAyEA...",
  "issued_at": "2026-01-17T10:30:05Z",
  "expires_at": "2026-01-17T10:35:05Z"
}
```

### Immutable Audit Trail

Database triggers prevent modifications:

```sql
CREATE TRIGGER immutable_manifests
BEFORE UPDATE OR DELETE ON manifests
FOR EACH ROW EXECUTE FUNCTION prevent_modification();
```

### Fail-Closed by Default

Critical actions fail if Gateway is unavailable:

```python
@protect(provider="stripe", method="charge", fail_open=False)  # Default
def critical_action(): pass

@protect(provider="analytics", method="log", fail_open=True)  # Graceful
def non_critical(): pass
```

## 📊 Audit & Compliance

### Query Audit Trail

```bash
# Get all actions
curl http://localhost:8000/v1/audit/query

# Filter by organization
curl http://localhost:8000/v1/audit/query?org_id=acme-corp

# Show only denied actions
curl http://localhost:8000/v1/audit/query?approved_only=false

# Get statistics
curl http://localhost:8000/v1/audit/stats
```

### Visualize in Terminal

```bash
python demo/visualize.py
```

Output:
```
╔══════════════════════════════════════════════════════════╗
║                   Relay Audit Trail                      ║
╠═══════════╦═══════════════╦════════╦═════════╦══════════╣
║ Timestamp ║ Action        ║ Amount ║ Status  ║ Policy   ║
╠═══════════╬═══════════════╬════════╬═════════╬══════════╣
║ 10:30:00  ║ stripe.charge ║ $40.00 ║ ✅ PASS ║ v1.2.3   ║
║ 10:31:00  ║ stripe.charge ║ $60.00 ║ ❌ DENY ║ v1.2.3   ║
╚═══════════╩═══════════════╩════════╩═════════╩══════════╝
```

## 🧪 Testing

### Run Unit Tests

```bash
pytest gateway/tests/
pytest sdk/tests/
```

### Run End-to-End Tests

```bash
# Start infrastructure
docker-compose up -d

# Run E2E tests
pytest tests/e2e/
```

### Load Testing

```bash
locust -f tests/load/locustfile.py
```

Target: 1000 requests/second with <100ms p99 latency

## 📚 API Reference

### POST /v1/manifest/validate

Validate a manifest against policies.

**Request:**
```json
{
  "manifest": {
    "agent": {
      "agent_id": "sales-agent-001",
      "org_id": "acme-corp"
    },
    "action": {
      "provider": "stripe",
      "method": "create_payment",
      "parameters": {"amount": 4500, "currency": "USD"}
    },
    "justification": {
      "reasoning": "Customer approved quote Q-2026-001"
    }
  }
}
```

**Response (Approved):**
```json
{
  "manifest_id": "uuid-123",
  "approved": true,
  "seal": {
    "seal_id": "seal_1705491000_abc123",
    "signature": "kZXJ0aWZpY2F0ZSBm...",
    "expires_at": "2026-01-17T10:35:05Z"
  },
  "policy_version": "v1.2.3"
}
```

**Response (Denied):**
```json
{
  "manifest_id": "uuid-123",
  "approved": false,
  "denial_reason": "Payment exceeds $50.00 limit",
  "policy_version": "v1.2.3"
}
```

### GET /v1/seal/verify

Verify a seal's authenticity.

**Request:**
```
GET /v1/seal/verify?seal_id=seal_1705491000_abc123
```

**Response:**
```json
{
  "seal_id": "seal_1705491000_abc123",
  "valid": true,
  "approved": true,
  "expired": false,
  "already_executed": false
}
```

### GET /v1/audit/query

Query the audit ledger.

**Parameters:**
- `org_id` (optional): Filter by organization
- `agent_id` (optional): Filter by agent
- `provider` (optional): Filter by provider
- `approved_only` (optional): Filter by approval status
- `limit` (default: 100): Maximum results
- `offset` (default: 0): Pagination offset

## 🗺️ Roadmap

### V1.1 - V1.3
- TypeScript SDK for Node.js agents
- Policy simulator (web UI)
- Webhook notifications (Slack/PagerDuty)
- Time-based policies (e.g., "no payments after 6pm")
- Approval workflows (human-in-the-loop)

### V2+
- Blockchain ledger (Ethereum/Hyperledger)
- Cross-organization policies (ABP protocol)
- ML-based anomaly detection
- Zero-knowledge proofs

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Open Policy Agent](https://www.openpolicyagent.org/) - Policy engine
- [PyNaCl](https://github.com/pyca/pynacl) - Ed25519 cryptography
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for the age of autonomous agents**
