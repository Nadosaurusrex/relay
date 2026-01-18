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

## 📖 Getting Started - Step by Step

This guide walks you through setting up Relay from scratch (~45 minutes first time).

### Prerequisites Check

Ensure you have:
- **Python 3.11+**: `python --version`
- **Docker & Docker Compose**: `docker --version && docker-compose --version`
- **Git**: For cloning the repository

### Step 1: Clone and Setup Environment (~5 minutes)

```bash
# Clone repository
git clone https://github.com/yourusername/relay.git
cd relay

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Generate Cryptographic Keys (~2 minutes)

```bash
# Generate Ed25519 keypair for signing seals
python scripts/generate_keys.py --output .env

# Verify keys were generated
grep "RELAY_PRIVATE_KEY" .env
```

**What this does**: Creates a private/public keypair for signing approved actions with Ed25519 cryptography.

### Step 3: Start Infrastructure (~30 minutes)

```bash
cd infra
docker-compose up -d

# Wait for services to be ready (first time pulls Docker images)
# PostgreSQL: ~2 minutes
# OPA: ~1 minute
# Gateway: ~1 minute
```

**Verify services are healthy:**

```bash
# Check Gateway
curl http://localhost:8000/health
# Expected: {"status": "healthy", "database": "connected", "opa": "connected"}

# Check OPA
curl http://localhost:8181/health
# Expected: {}

# Check PostgreSQL
docker exec -it relay_postgres psql -U relay -d relay -c "SELECT 1;"
# Expected: 1
```

**Troubleshooting:**
- If Gateway is unhealthy, check logs: `docker-compose logs gateway`
- If database connection fails: `docker-compose restart postgres`
- If OPA is unreachable: `docker-compose restart opa`

### Step 4: Bootstrap Policies (~5 minutes)

```bash
# Return to project root
cd ..

# Load example policies into OPA
python scripts/bootstrap_policies.py

# Verify policies loaded
curl http://localhost:8181/v1/policies
```

**What policies are loaded:**
- `policies/finance.yaml`: Spending limits for Stripe payments
- `policies/infrastructure.yaml`: AWS resource constraints

### Step 5: Test Your First API Call (~3 minutes)

**Test an approved action:**

```bash
curl -X POST http://localhost:8000/v1/manifest/validate \
  -H "Content-Type: application/json" \
  -d '{
    "manifest": {
      "agent": {
        "agent_id": "test-agent",
        "org_id": "test-org"
      },
      "action": {
        "provider": "stripe",
        "method": "create_payment",
        "parameters": {"amount": 3500, "currency": "USD"}
      },
      "justification": {
        "reasoning": "Test payment under $50 limit"
      }
    }
  }'
```

**Expected response** (approved):
```json
{
  "manifest_id": "uuid-...",
  "approved": true,
  "seal": {
    "seal_id": "seal_...",
    "signature": "...",
    "expires_at": "2026-01-18T10:35:00Z"
  }
}
```

**Test a denied action:**

```bash
curl -X POST http://localhost:8000/v1/manifest/validate \
  -H "Content-Type: application/json" \
  -d '{
    "manifest": {
      "agent": {
        "agent_id": "test-agent",
        "org_id": "test-org"
      },
      "action": {
        "provider": "stripe",
        "method": "create_payment",
        "parameters": {"amount": 7500, "currency": "USD"}
      },
      "justification": {
        "reasoning": "Test payment exceeding limit"
      }
    }
  }'
```

**Expected response** (denied):
```json
{
  "manifest_id": "uuid-...",
  "approved": false,
  "denial_reason": "Payment exceeds $50.00 limit"
}
```

### Step 6: Integrate with Your Agent (~3 minutes)

**Python SDK (recommended):**

```python
from sdk.client import RelayClient
from sdk.decorator import protect

# Initialize client
relay = RelayClient(
    gateway_url="http://localhost:8000",
    agent_id="my-agent",
    org_id="my-org"
)

# Protect any function
@protect(provider="stripe", method="create_payment")
def process_payment(amount: int, currency: str):
    # Your payment logic here
    return {"status": "success", "amount": amount}

# Use it
try:
    result = process_payment(4500, "USD")  # Approved
    print(f"✅ Payment succeeded: {result}")
except PolicyViolationError as e:
    print(f"❌ Blocked: {e.denial_reason}")
```

### Step 7: Query Audit Trail (~2 minutes)

```bash
# View all actions
curl http://localhost:8000/v1/audit/query

# View statistics
curl http://localhost:8000/v1/audit/stats
```

**You're Done!** 🎉

Next steps:
- Explore Jupyter notebooks in `examples/`
- Write custom policies in `policies/`
- Integrate with your existing agents

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

## 🌐 Framework-Agnostic Integration

Relay works with **any programming language** that can make HTTP requests. While the Python SDK provides the best developer experience, you can integrate from JavaScript, Go, Rust, or any other language.

### Python SDK (3 Lines) - Recommended

```python
from sdk.client import RelayClient
from sdk.decorator import protect

relay = RelayClient(gateway_url="http://localhost:8000", agent_id="...", org_id="...")

@protect(provider="stripe", method="create_payment")
def process_payment(amount: int):
    return stripe.Charge.create(amount=amount, currency="USD")
```

**Complexity**: Very Low - automatic manifest building, error handling, seal lifecycle

### JavaScript/TypeScript (HTTP API)

```javascript
// 1. Validate action with Relay
async function processPayment(amount) {
  const response = await fetch('http://localhost:8000/v1/manifest/validate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      manifest: {
        agent: {agent_id: "sales-agent", org_id: "acme-corp"},
        action: {
          provider: "stripe",
          method: "create_payment",
          parameters: {amount: amount, currency: "USD"}
        },
        justification: {reasoning: "Customer order #12345"}
      }
    })
  });

  const result = await response.json();

  // 2. Execute if approved
  if (result.approved) {
    const charge = await stripe.charges.create({
      amount: amount,
      currency: "USD"
    });

    // 3. Mark seal as executed (prevents replay attacks)
    await fetch(
      `http://localhost:8000/v1/seal/mark-executed?seal_id=${result.seal.seal_id}`,
      {method: 'POST'}
    );

    return charge;
  } else {
    throw new Error(`Policy denied: ${result.denial_reason}`);
  }
}

// Usage
try {
  await processPayment(4500);  // $45.00
  console.log('✅ Payment approved and executed');
} catch (error) {
  console.error('❌ Payment blocked:', error.message);
}
```

**Complexity**: Moderate - manual manifest building, error handling

### Go (HTTP API)

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

type Manifest struct {
    Agent struct {
        AgentID string `json:"agent_id"`
        OrgID   string `json:"org_id"`
    } `json:"agent"`
    Action struct {
        Provider   string                 `json:"provider"`
        Method     string                 `json:"method"`
        Parameters map[string]interface{} `json:"parameters"`
    } `json:"action"`
    Justification struct {
        Reasoning string `json:"reasoning"`
    } `json:"justification"`
}

func processPayment(amount int) error {
    // 1. Build manifest
    manifest := Manifest{}
    manifest.Agent.AgentID = "sales-agent"
    manifest.Agent.OrgID = "acme-corp"
    manifest.Action.Provider = "stripe"
    manifest.Action.Method = "create_payment"
    manifest.Action.Parameters = map[string]interface{}{
        "amount":   amount,
        "currency": "USD",
    }
    manifest.Justification.Reasoning = "Customer order #12345"

    body, _ := json.Marshal(map[string]interface{}{"manifest": manifest})

    // 2. Validate with Relay
    resp, err := http.Post(
        "http://localhost:8000/v1/manifest/validate",
        "application/json",
        bytes.NewBuffer(body),
    )
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)

    // 3. Execute if approved
    if result["approved"].(bool) {
        // Execute payment with Stripe SDK
        // ...

        // Mark seal as executed
        sealID := result["seal"].(map[string]interface{})["seal_id"].(string)
        http.Post(
            fmt.Sprintf("http://localhost:8000/v1/seal/mark-executed?seal_id=%s", sealID),
            "application/json",
            nil,
        )

        return nil
    } else {
        return fmt.Errorf("policy denied: %s", result["denial_reason"])
    }
}
```

**Complexity**: Moderate - type-safe manifest building

### LangChain Integration (Python)

```python
from langchain.agents import Tool
from sdk.decorator import protect

# Wrap any function with @protect
@protect(provider="crm", method="update_lead_score")
def update_lead_score(lead_id: str, score: int):
    crm_api.update_lead(lead_id, score)
    return f"Updated lead {lead_id} to score {score}"

# Use as LangChain tool
tools = [
    Tool(
        name="UpdateLeadScore",
        func=update_lead_score,
        description="Update lead score in CRM (protected by Relay governance)"
    )
]

# Agent will use the tool, Relay intercepts and validates
agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
agent.run("Update lead ABC123 to score 85")
```

### MCP Server Integration

```python
# Expose Relay audit trail as MCP resource
import mcp

@mcp.resource("relay://audit/recent")
def get_recent_audit():
    response = requests.get("http://localhost:8000/v1/audit/query?limit=50")
    return response.json()

# Agents can query their own audit history
audit = mcp.read_resource("relay://audit/recent?agent_id=my-agent")
```

### Comparison: SDK vs HTTP API

| Feature | Python SDK | HTTP API (any language) |
|---------|-----------|-------------------------|
| **Code changes** | 3 lines | 20-30 lines |
| **Manifest building** | Automatic | Manual |
| **Error handling** | Built-in | Manual |
| **Seal lifecycle** | Automatic | Manual |
| **Type safety** | Pydantic models | JSON validation |
| **Best for** | Python agents | Non-Python agents |

### When to Use Each Approach

**Use Python SDK when**:
- Building Python agents (LangChain, CrewAI, custom)
- Want minimal code changes
- Need automatic error handling

**Use HTTP API when**:
- Agent is written in JavaScript, Go, Rust, etc.
- Need fine-grained control over manifest building
- Integrating with existing non-Python codebases

**Both approaches provide**:
- Same policy enforcement guarantees
- Same cryptographic seals
- Same audit trail immutability
- Same fail-closed safety

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

## 📚 Complete API Reference

Relay exposes 12 REST endpoints for manifest validation, seal management, audit queries, and multi-tenancy.

### Core Workflow Endpoints

#### 1. POST `/v1/manifest/validate` - Validate Agent Actions

The heart of Relay - validates agent actions against policies, generates cryptographic seals, and writes to audit ledger.

**Request:**
```bash
curl -X POST http://localhost:8000/v1/manifest/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <optional-jwt-token>" \
  -d '{
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
        "reasoning": "Customer approved quote Q-2026-001",
        "confidence_score": 0.95
      }
    },
    "dry_run": false
  }'
```

**Response (Approved):**
```json
{
  "manifest_id": "550e8400-e29b-41d4-a716-446655440000",
  "approved": true,
  "seal": {
    "seal_id": "seal_1705491000_abc123",
    "signature": "kZXJ0aWZpY2F0ZSBm...",
    "public_key": "MCowBQYDK2VwAyEA...",
    "issued_at": "2026-01-18T10:30:05Z",
    "expires_at": "2026-01-18T10:35:05Z"
  },
  "policy_version": "v1.2.3"
}
```

**Response (Denied):**
```json
{
  "manifest_id": "550e8400-e29b-41d4-a716-446655440000",
  "approved": false,
  "denial_reason": "Payment exceeds $50.00 limit",
  "policy_version": "v1.2.3"
}
```

**Parameters:**
- `dry_run` (optional, boolean): If true, validates without writing to audit trail

**Authentication:** Optional JWT token (if `RELAY_REQUIRE_JWT=true`)

---

#### 2. POST `/v1/seal/mark-executed` - Prevent Replay Attacks

Called after action execution to mark seal as one-time-use.

**Request:**
```bash
curl -X POST "http://localhost:8000/v1/seal/mark-executed?seal_id=seal_1705491000_abc123"
```

**Response:**
```json
{
  "seal_id": "seal_1705491000_abc123",
  "marked_executed": true,
  "executed_at": "2026-01-18T10:31:00Z"
}
```

**Use Case:** Prevents the same seal from being used multiple times (replay attack prevention).

---

#### 3. GET `/v1/seal/verify` - Verify Seal Authenticity

Downstream services can independently verify seal cryptographic signatures.

**Request:**
```bash
curl "http://localhost:8000/v1/seal/verify?seal_id=seal_1705491000_abc123"
```

**Response:**
```json
{
  "seal_id": "seal_1705491000_abc123",
  "valid": true,
  "approved": true,
  "expired": false,
  "already_executed": false,
  "manifest_id": "550e8400-e29b-41d4-a716-446655440000",
  "issued_at": "2026-01-18T10:30:05Z",
  "expires_at": "2026-01-18T10:35:05Z"
}
```

**Fields:**
- `valid`: Signature verification result
- `expired`: Whether seal has passed TTL
- `already_executed`: Whether seal was marked as used

**Use Case:** Stripe/AWS/Salesforce can verify seals without calling back to Relay.

---

### Audit & Compliance Endpoints

#### 4. GET `/v1/audit/query` - Query Audit Trail

Retrieve audit records with flexible filtering and pagination.

**Request:**
```bash
# All actions
curl "http://localhost:8000/v1/audit/query"

# Filter by organization
curl "http://localhost:8000/v1/audit/query?org_id=acme-corp"

# Filter by agent
curl "http://localhost:8000/v1/audit/query?agent_id=sales-agent-001"

# Filter by provider
curl "http://localhost:8000/v1/audit/query?provider=stripe"

# Only denied actions
curl "http://localhost:8000/v1/audit/query?approved_only=false"

# Pagination
curl "http://localhost:8000/v1/audit/query?limit=50&offset=100"
```

**Response:**
```json
{
  "total": 1523,
  "limit": 100,
  "offset": 0,
  "records": [
    {
      "manifest_id": "550e8400-e29b-41d4-a716-446655440000",
      "agent_id": "sales-agent-001",
      "org_id": "acme-corp",
      "provider": "stripe",
      "method": "create_payment",
      "parameters": {"amount": 4500, "currency": "USD"},
      "approved": true,
      "denial_reason": null,
      "seal_signature": "kZXJ0aWZpY2F0ZSBm...",
      "created_at": "2026-01-18T10:30:05Z",
      "policy_version": "v1.2.3"
    }
  ]
}
```

**Query Parameters:**
- `org_id` (optional): Filter by organization
- `agent_id` (optional): Filter by agent
- `provider` (optional): Filter by provider (e.g., "stripe", "aws")
- `approved_only` (optional, boolean): Show only approved or denied actions
- `limit` (default: 100): Maximum results per page
- `offset` (default: 0): Pagination offset

---

#### 5. GET `/v1/audit/stats` - Analytics & Metrics

Aggregate statistics for compliance reporting.

**Request:**
```bash
# Global stats
curl "http://localhost:8000/v1/audit/stats"

# Per-org stats
curl "http://localhost:8000/v1/audit/stats?org_id=acme-corp"

# Per-agent stats
curl "http://localhost:8000/v1/audit/stats?agent_id=sales-agent-001"
```

**Response:**
```json
{
  "total_manifests": 15234,
  "approved_count": 14890,
  "denied_count": 344,
  "approval_rate": 0.977,
  "executed_count": 14102,
  "execution_rate": 0.947,
  "top_agents": [
    {"agent_id": "sales-agent-001", "count": 523},
    {"agent_id": "procurement-agent", "count": 412}
  ],
  "top_providers": [
    {"provider": "stripe", "count": 8234},
    {"provider": "aws", "count": 4123}
  ],
  "denials_by_reason": [
    {"reason": "Payment exceeds limit", "count": 234},
    {"reason": "Unapproved vendor", "count": 110}
  ]
}
```

**Use Case:** Compliance reports, anomaly detection, agent behavior analysis.

---

### Multi-Tenancy Endpoints

#### 6. POST `/v1/orgs/register` - Bootstrap Organization

Create a new organization and initial admin agent. **Public endpoint** (no auth required).

**Request:**
```bash
curl -X POST http://localhost:8000/v1/orgs/register \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "acme-corp",
    "org_name": "Acme Corporation",
    "admin_agent_id": "admin-agent-001"
  }'
```

**Response:**
```json
{
  "org_id": "acme-corp",
  "org_name": "Acme Corporation",
  "admin_agent": {
    "agent_id": "admin-agent-001",
    "org_id": "acme-corp",
    "created_at": "2026-01-18T10:00:00Z"
  },
  "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Use Case:** First-time setup for new organizations.

---

#### 7. GET `/v1/orgs/{org_id}` - Organization Details

Retrieve organization information. **Requires JWT authentication.**

**Request:**
```bash
curl http://localhost:8000/v1/orgs/acme-corp \
  -H "Authorization: Bearer <jwt-token>"
```

**Response:**
```json
{
  "org_id": "acme-corp",
  "org_name": "Acme Corporation",
  "created_at": "2026-01-18T10:00:00Z",
  "agent_count": 12,
  "total_manifests": 1523
}
```

**Authentication:** JWT token scoped to the organization.

---

#### 8. POST `/v1/agents/register` - Create Agent

Register a new agent within an organization. **Requires JWT authentication.**

**Request:**
```bash
curl -X POST http://localhost:8000/v1/agents/register \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "sales-agent-001",
    "agent_name": "Sales Automation Agent",
    "agent_type": "langchain"
  }'
```

**Response:**
```json
{
  "agent_id": "sales-agent-001",
  "org_id": "acme-corp",
  "agent_name": "Sales Automation Agent",
  "agent_type": "langchain",
  "created_at": "2026-01-18T10:15:00Z",
  "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Use Case:** Generate agent-specific JWT tokens for authentication.

---

#### 9. GET `/v1/agents` - List Agents

Retrieve all agents for authenticated organization. **Requires JWT authentication.**

**Request:**
```bash
curl http://localhost:8000/v1/agents \
  -H "Authorization: Bearer <jwt-token>"
```

**Response:**
```json
{
  "org_id": "acme-corp",
  "agents": [
    {
      "agent_id": "sales-agent-001",
      "agent_name": "Sales Automation Agent",
      "agent_type": "langchain",
      "created_at": "2026-01-18T10:15:00Z"
    },
    {
      "agent_id": "procurement-agent",
      "agent_name": "Procurement Agent",
      "agent_type": "crewai",
      "created_at": "2026-01-18T09:00:00Z"
    }
  ]
}
```

---

### Health & Discovery Endpoints

#### 10. GET `/health` - Global Health Check

Check Gateway, database, and OPA connectivity. **Public endpoint.**

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "opa": "connected",
  "version": "1.0.0"
}
```

**Use Case:** Kubernetes liveness/readiness probes, monitoring systems.

---

#### 11. GET `/v1/manifest/health` - Manifest Service Health

Check OPA availability and current policy version. **Public endpoint.**

**Request:**
```bash
curl http://localhost:8000/v1/manifest/health
```

**Response:**
```json
{
  "status": "healthy",
  "opa_available": true,
  "policy_version": "v1.2.3",
  "policy_loaded": true
}
```

---

#### 12. GET `/` - Service Info

Discover available endpoints and service version. **Public endpoint.**

**Request:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "service": "relay-gateway",
  "version": "1.0.0",
  "description": "Agent Governance System - The Air Gap for Autonomous Actions",
  "endpoints": {
    "manifest_validation": "/v1/manifest/validate",
    "audit_query": "/v1/audit/query",
    "seal_verify": "/v1/seal/verify",
    "health": "/health"
  },
  "documentation": "https://github.com/yourusername/relay"
}
```

---

### Authentication Summary

| Endpoint | Auth Required | Token Type |
|----------|--------------|------------|
| `POST /v1/manifest/validate` | Optional* | JWT Bearer |
| `POST /v1/seal/mark-executed` | No | - |
| `GET /v1/seal/verify` | No | - |
| `GET /v1/audit/query` | No** | - |
| `GET /v1/audit/stats` | No** | - |
| `POST /v1/orgs/register` | No | - |
| `GET /v1/orgs/{id}` | Yes | JWT Bearer |
| `POST /v1/agents/register` | Yes | JWT Bearer |
| `GET /v1/agents` | Yes | JWT Bearer |
| `GET /health` | No | - |
| `GET /v1/manifest/health` | No | - |
| `GET /` | No | - |

*Optional if `RELAY_REQUIRE_JWT=false` (default for local development)
**May be restricted in production deployments

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
