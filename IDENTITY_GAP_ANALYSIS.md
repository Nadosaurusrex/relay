# Critical Gap Analysis: Agent Identity & Provisioning

## 🚨 The Question That Exposes the Gap

**"Who gives them `gateway_url`, `agent_id`, `org_id`?"**

**Short Answer:** Nobody. Users just... make them up. **This is a critical missing piece.**

---

## 🔍 Current State (V1)

### What Happens Today

```python
# User's agent code
relay = RelayClient(
    gateway_url="http://localhost:8000",  # ❓ Where from?
    agent_id="my-agent",                   # ❓ Who decided this?
    org_id="my-company"                    # ❓ Who assigned this?
)
```

**The Reality:**
1. User deploys Relay Gateway (docker-compose)
2. User builds their agent
3. User **picks arbitrary strings** for agent_id and org_id
4. Gateway accepts ANY agent_id/org_id with **zero verification**
5. Policies can reference these values, but there's no central registry

**It's an honor system.** 🤝 (But with zero accountability)

---

## 🚫 What's Missing: The Identity Layer

### 1. **No Agent Registration**

**Problem:** Nothing prevents me from claiming to be any agent.

```python
# Malicious actor
relay = RelayClient(
    gateway_url="http://your-company-relay.com",
    agent_id="cfo-approval-bot",  # Impersonating privileged agent!
    org_id="acme-corp"
)
```

**Result:** Gateway accepts it. Policies might allow actions based on agent_id.

**Security Impact:** 🔴 **CRITICAL** - No authentication = No trust

---

### 2. **No Organization Setup**

**Problem:** Who creates organizations? How?

**Current state:**
- Organizations don't "exist" until someone uses an org_id
- No provisioning flow
- No admin UI
- No org-level policies

**Questions with no answers:**
- Who can create a new org?
- Who manages org members?
- How do you see all agents in an org?
- How do you revoke an org's access?

---

### 3. **No Agent Authentication**

**Problem:** No way to prove an agent is who it claims to be.

**What's missing:**
```python
# Should be:
relay = RelayClient(
    gateway_url="...",
    api_key="relay_sk_abc123..."  # ❌ Doesn't exist!
)
# API key proves identity
```

**Impact:**
- Any code can claim any agent_id
- No way to revoke compromised agents
- No audit trail of "who really sent this"

---

### 4. **No Multi-Tenancy Enforcement**

**Problem:** Nothing stops org_id mixing.

```python
# Organization A's agent
relay = RelayClient(org_id="org-a", agent_id="agent-1")

# Organization B can see A's audit trail!
curl http://localhost:8000/v1/audit/query?org_id=org-a
# ❌ No authentication = Anyone can query anything
```

**Impact:**
- Zero data isolation
- No privacy between orgs
- Audit trail is public

---

## 💡 What Users THINK the Flow Should Be

### Scenario: Company deploys Relay for the first time

**User's mental model:**

```
1. Deploy Relay Gateway
2. Create organization: "acme-corp"
3. Create agents:
   - Name: "payment-processor"
   - Get API key: relay_sk_xyz123...
   - Get agent_id: agent_abc123
4. Configure agent with credentials
5. Agent authenticates when connecting
```

**Reality:**

```
1. Deploy Relay Gateway
2. Pick any string for org_id: "acme-corp"
3. Pick any string for agent_id: "payment-processor"
4. Hard-code in agent
5. Hope nobody else uses same IDs
```

**Gap:** Steps 2-4 don't exist.

---

## 🏗️ What V1 Should Have (But Doesn't)

### Minimum Viable Identity Layer

#### 1. **Organization Provisioning**

```bash
# CLI or API
relay org create --name "Acme Corp" --id "acme-corp"
# Returns: org_id, admin_token
```

**Storage:** PostgreSQL table
```sql
CREATE TABLE organizations (
    org_id VARCHAR PRIMARY KEY,
    name VARCHAR,
    created_at TIMESTAMP,
    admin_token VARCHAR UNIQUE  -- For org management
);
```

#### 2. **Agent Registration**

```bash
# Create agent within org
relay agent create \
    --org-id "acme-corp" \
    --name "Payment Processor" \
    --permissions "stripe:create_payment"

# Returns:
# agent_id: agent_abc123
# api_key: relay_sk_xyz789...
```

**Storage:**
```sql
CREATE TABLE agents (
    agent_id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(org_id),
    name VARCHAR,
    api_key_hash VARCHAR,  -- Hashed API key
    permissions JSONB,
    created_at TIMESTAMP,
    revoked_at TIMESTAMP
);
```

#### 3. **Authentication Middleware**

```python
# Gateway validates API key on every request
@app.post("/v1/manifest/validate")
async def validate_manifest(
    manifest: dict,
    api_key: str = Header(..., alias="X-Relay-API-Key")
):
    # 1. Validate API key
    agent = db.get_agent_by_api_key(api_key)
    if not agent or agent.revoked:
        raise HTTPException(401, "Invalid API key")

    # 2. Verify agent_id matches
    if manifest["agent"]["agent_id"] != agent.agent_id:
        raise HTTPException(403, "Agent ID mismatch")

    # 3. Verify org_id matches
    if manifest["agent"]["org_id"] != agent.org_id:
        raise HTTPException(403, "Organization mismatch")

    # 4. Check permissions
    if not agent.has_permission(manifest["action"]["provider"]):
        raise HTTPException(403, "Insufficient permissions")

    # 5. Proceed with policy validation
    ...
```

#### 4. **SDK Changes**

```python
# Current (V1):
relay = RelayClient(
    gateway_url="http://localhost:8000",
    agent_id="my-agent",  # ❌ Just a string
    org_id="my-org"       # ❌ Just a string
)

# Should be:
relay = RelayClient(
    gateway_url="http://localhost:8000",
    api_key="relay_sk_xyz123..."  # ✅ Proves identity
)
# agent_id and org_id derived from API key
```

---

## 📊 Impact of Missing Identity Layer

### Security Risks 🔴

| Risk | Severity | Description |
|------|----------|-------------|
| **Impersonation** | CRITICAL | Any code can claim to be any agent |
| **Data leakage** | HIGH | All audit logs accessible without auth |
| **Policy bypass** | CRITICAL | Claim privileged agent_id to get approval |
| **No revocation** | HIGH | Compromised agent can't be disabled |
| **No audit integrity** | HIGH | Can't prove who really sent manifest |

### Usability Issues ⚠️

| Issue | Impact |
|-------|--------|
| **No guidance** | Users don't know what to put for agent_id/org_id |
| **Name collisions** | Two agents might use same agent_id |
| **No discovery** | Can't see list of agents in system |
| **Manual setup** | Copy-paste strings instead of API keys |
| **No secrets management** | agent_id/org_id not treated as credentials |

### Operational Gaps 🛠️

| Gap | Impact |
|-----|--------|
| **No agent lifecycle** | Can't enable/disable agents |
| **No rotation** | Can't rotate credentials |
| **No monitoring** | Can't see which agents are active |
| **No access control** | Can't restrict agent permissions |
| **No multi-tenancy** | Can't isolate organizations |

---

## 🤔 Design Questions That Need Answers

### Question 1: Self-Hosted vs. SaaS

**Self-Hosted (Current V1):**
- Single organization assumption
- Trust all agents in internal network
- agent_id/org_id just for organization/logging

**SaaS (Future V2):**
- Multiple organizations on shared infrastructure
- Zero-trust model
- API keys mandatory

**Decision needed:** Is V1 intentionally single-org/internal-only?

---

### Question 2: Who Provisions the First Agent?

**Option A: Bootstrap Admin**
```bash
# When Gateway starts, create default org
relay-gateway --bootstrap-org "acme-corp"
# Generates: admin token
# Admin can create agents via API
```

**Option B: CLI Tool**
```bash
# Use CLI to provision
relay init --gateway http://localhost:8000
# Walks through: org creation, first agent
```

**Option C: Web UI**
```
Navigate to: http://localhost:8000/setup
1. Create organization
2. Create first agent
3. Get API key
```

---

### Question 3: API Key Format

**Option A: JWT (Stateless)**
```
relay_jwt_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Claims: { agent_id, org_id, permissions }
```

**Option B: Opaque Token (Stateful)**
```
relay_sk_live_abc123def456...
Lookup in database to get agent info
```

**Option C: mTLS (Certificate-based)**
```
Each agent gets TLS client certificate
Gateway validates cert on connection
```

---

### Question 4: Permissions Model

**Option A: Agent-Level Permissions**
```json
{
  "agent_id": "agent_123",
  "allowed_providers": ["stripe", "aws"],
  "allowed_methods": ["stripe:create_payment"]
}
```
Hard deny before policy evaluation.

**Option B: Role-Based**
```json
{
  "agent_id": "agent_123",
  "roles": ["payment_processor", "support_agent"]
}
```
Policies reference roles.

**Option C: Policy-Only**
```rego
allow if {
    input.agent.agent_id == "approved-agent-123"
    input.action.provider == "stripe"
}
```
All authorization in policies (current V1).

---

## 🚀 Recommended Approach for V1.1

### Phase 1: Minimal Identity (1 week)

**Goal:** Add authentication without breaking existing usage.

**Changes:**

1. **Optional API Key Support**
```python
# Backward compatible
relay = RelayClient(
    gateway_url="...",
    agent_id="my-agent",  # Still works
    org_id="my-org"
)

# OR: New authenticated mode
relay = RelayClient(
    gateway_url="...",
    api_key="relay_sk_..."  # Extracts agent_id/org_id from key
)
```

2. **Agent Registration CLI**
```bash
# New command
relay-admin agent create \
    --name "Payment Bot" \
    --org-id "acme-corp"

# Output:
# Agent ID: agent_abc123
# API Key: relay_sk_xyz789... (save this!)
```

3. **Database Schema**
```sql
-- New tables
CREATE TABLE agents (
    agent_id VARCHAR PRIMARY KEY,
    org_id VARCHAR,
    api_key_hash VARCHAR,
    created_at TIMESTAMP
);
```

4. **Gateway Validation (Optional)**
```python
# Check X-Relay-API-Key header if provided
# If missing, allow (backward compat)
# If present, validate
```

**Result:** Existing users unaffected, new users can opt into auth.

---

### Phase 2: Enforcement (2-3 weeks)

**Goal:** Require authentication, add management.

**Changes:**

1. **Require API Keys**
```python
# Old style deprecated
relay = RelayClient(agent_id="...", org_id="...")  # ⚠️ Deprecated warning
```

2. **Admin Web UI**
```
http://localhost:8000/admin
- Create organizations
- Create/revoke agents
- View audit log (filtered by org)
```

3. **Multi-Tenancy Enforcement**
```python
# Audit API requires auth
GET /v1/audit/query
Header: X-Relay-API-Key: relay_sk_...
# Only returns logs for authenticated org
```

**Result:** Full identity layer with auth and isolation.

---

### Phase 3: Advanced Features (1-2 months)

1. **Agent Permissions**
```json
{
  "allowed_providers": ["stripe", "aws"],
  "max_amount": 10000
}
```

2. **API Key Rotation**
```bash
relay-admin agent rotate-key --agent-id agent_123
```

3. **Audit Trail for Identity**
```sql
-- Log all auth events
CREATE TABLE auth_events (
    timestamp TIMESTAMP,
    agent_id VARCHAR,
    api_key_prefix VARCHAR,
    action VARCHAR,  -- "authenticated", "auth_failed", "key_rotated"
    ip_address INET
);
```

4. **RBAC**
```yaml
roles:
  - name: payment_processor
    permissions:
      - stripe:create_payment
      - stripe:create_refund
```

---

## 💰 Cost of NOT Fixing This

### For Internal/Single-Org Use:
**Impact: Medium** ⚠️
- Still functional (everyone trusts each other)
- agent_id/org_id useful for organization
- Security relies on network isolation

**Risk:** If someone gains network access, they can impersonate any agent.

### For Multi-Org/SaaS Use:
**Impact: CRITICAL** 🔴
- **Cannot launch** without identity layer
- Zero trust boundary
- Data leakage between orgs
- No compliance (GDPR, SOC2 impossible)

### For V2 Vision (ABP - Cross-Org):
**Impact: BLOCKER** 🛑
- Cannot prove agent identity to external parties
- No cryptographic chain of custody
- Trust model breaks completely

**V2 Vision:** "Nike's agent negotiates with Salesforce's agent"
**Requirement:** Both sides must cryptographically prove agent identity

---

## 🎯 Immediate Actions (This Week)

### 1. Document Current Limitations ✅
Add to README:

```markdown
## ⚠️ Security Note: V1 Identity Model

**Current V1 behavior:**
- `agent_id` and `org_id` are self-declared strings
- No authentication or verification
- Suitable for: Internal use, single-org, trusted environments
- NOT suitable for: Multi-org, SaaS, cross-org interactions

**Roadmap:**
- V1.1: Optional API key authentication
- V1.2: Required authentication + admin UI
- V2: Cryptographic agent identity for ABP
```

### 2. Add Security Guidance
```markdown
## Security Best Practices

**If self-hosting for single organization:**
1. Deploy Gateway on internal network only
2. Use firewall to restrict access
3. Treat agent_id/org_id as trusted identifiers
4. Use policies to enforce limits

**If planning multi-org or external access:**
1. Wait for V1.1 (API key authentication)
2. Or: Implement auth proxy in front of Gateway
3. Never expose V1 Gateway to internet
```

### 3. Design V1.1 API Key Schema
```sql
CREATE TABLE agents (
    agent_id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id VARCHAR NOT NULL,
    name VARCHAR,
    api_key_hash VARCHAR NOT NULL,  -- bcrypt(api_key)
    api_key_prefix VARCHAR,  -- First 8 chars for identification
    permissions JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    revoked_at TIMESTAMP,
    last_used_at TIMESTAMP
);

CREATE INDEX idx_agents_org ON agents(org_id);
CREATE INDEX idx_agents_api_key_hash ON agents(api_key_hash);
```

### 4. Create Issue Tracker
GitHub Issues:
- [ ] V1.1: Add optional API key authentication
- [ ] V1.1: Create agent provisioning CLI
- [ ] V1.1: Add backward compatibility mode
- [ ] V1.2: Require authentication
- [ ] V1.2: Build admin web UI
- [ ] V1.2: Multi-tenancy enforcement

---

## 📝 Answers to Original Question

### "Who gives them gateway_url?"

**V1 (Current):**
- Self-hosted: User deploys Gateway, uses http://localhost:8000 or internal URL
- No SaaS option

**V1.1+:**
- Self-hosted: Same
- SaaS: https://api.relay.dev (from Relay team)

**How users know:**
- Documentation: "Start with http://localhost:8000"
- Or: Gateway admin tells them internal URL

---

### "Who gives them agent_id?"

**V1 (Current):**
- **Users make it up themselves**
- No registration, no validation
- Just pick a descriptive name: "payment-bot-prod"

**V1.1+:**
- **System generates on registration**
```bash
relay agent create --name "Payment Bot"
# Output: agent_id: agent_abc123def456
```

**How users get it:**
- From registration response
- Stored in config file: .relay/credentials

---

### "Who gives them org_id?"

**V1 (Current):**
- **Users make it up themselves**
- Convention: Company name or domain
- Examples: "acme-corp", "nike", "salesforce"

**V1.1+:**
- **Admin creates org first**
```bash
relay org create --name "Acme Corp"
# Output: org_id: org_xyz789
```

**How users get it:**
- From org creation
- Or: Org admin shares it
- Stored in config: .relay/org_id

---

## 🏁 Summary

### Current State (V1):
- ❌ No identity management
- ❌ No authentication
- ❌ No agent registration
- ❌ Users invent IDs themselves
- ✅ Works for single-org internal use
- ❌ Not production-ready for multi-org

### What's Needed:
1. **Agent provisioning flow** (CLI or UI)
2. **API key authentication** (proves identity)
3. **Organization management** (isolation)
4. **Permission model** (optional, can stay in policies)

### Priority:
- **V1.1 (3-4 weeks)**: Add optional API keys
- **V1.2 (2-3 months)**: Require authentication, admin UI
- **V2 (6+ months)**: Cryptographic identity for ABP

### Immediate Action:
1. Document limitation in README ✅
2. Add to roadmap ✅
3. Design V1.1 schema ✅
4. Create GitHub issues ✅

---

**The user's question was spot-on: This is a critical missing piece that needs addressing before V1 can be production-ready for multi-org use.**
