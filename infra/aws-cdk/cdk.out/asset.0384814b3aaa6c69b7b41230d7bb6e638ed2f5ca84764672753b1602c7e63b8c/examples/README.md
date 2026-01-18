# Relay Examples

This directory contains comprehensive examples demonstrating Relay's capabilities in real-world scenarios.

## 📚 Example Notebooks

### 01_getting_started.ipynb
**Quick introduction to Relay basics**
- Understanding manifests and seals
- Policy evaluation
- Testing different scenarios
- Basic payment processor example

**Time**: 15 minutes
**Level**: Beginner

---

### 02_adversarial_prompt_protection.ipynb
**The Air Gap: Protection from manipulation**
- Direct attack scenarios ("just this once")
- Vulnerable vs. protected agents
- Sophisticated social engineering attempts
- Audit trail for security incidents

**Key Demonstration**: Shows how LLMs can be convinced to violate policies, but Relay's air gap prevents execution.

**Time**: 20 minutes
**Level**: Intermediate

---

### 03_langchain_integration.ipynb
**Seamless framework integration**
- Traditional LangChain tools (unprotected)
- Adding Relay protection (3 lines of code)
- Complete agent example
- Production integration patterns

**Key Demonstration**: Shows that adding governance requires minimal code changes - just middleware.

**Time**: 25 minutes
**Level**: Intermediate

---

### 04_company_policies.ipynb
**Mapping business rules to technical constraints**
- Financial policies from CFO
- Infrastructure policies from CTO
- Data protection from Legal/Compliance
- Step-by-step translation guide
- Industry-specific policy library

**Key Demonstration**: Bridges the gap between human business rules and machine-enforceable policies.

**Time**: 30 minutes
**Level**: Intermediate to Advanced

---

### 05_real_world_scenarios.ipynb
**Production scenarios and cost-benefit analysis**
- Vendor negotiation gone wrong
- Prompt injection attacks
- Runaway automation ($50k AWS bill)
- GDPR compliance violations
- Privilege escalation attempts

**Key Demonstration**: Real incidents that cost companies millions, and how Relay prevents them.

**Time**: 35 minutes
**Level**: Advanced

---

## 🎯 Learning Paths

### Path 1: Quick Start (30 minutes)
1. `01_getting_started.ipynb` - Basics
2. `02_adversarial_prompt_protection.ipynb` - The air gap concept
3. Run your own test with `simple_demo.py`

### Path 2: Integration Focus (1 hour)
1. `01_getting_started.ipynb` - Foundation
2. `03_langchain_integration.ipynb` - Framework integration
3. `04_company_policies.ipynb` - Policy development

### Path 3: Security & Compliance (1.5 hours)
1. `02_adversarial_prompt_protection.ipynb` - Threat model
2. `04_company_policies.ipynb` - Compliance mapping
3. `05_real_world_scenarios.ipynb` - Real incidents

### Path 4: Complete Course (2+ hours)
Work through all notebooks in order for comprehensive understanding.

---

## 🚀 Running the Examples

### Prerequisites

1. **Start Relay Infrastructure**:
   ```bash
   cd ~/relay/infra
   docker-compose up -d
   ```

2. **Verify Services**:
   ```bash
   # Check OPA
   curl http://localhost:8181/health

   # Check PostgreSQL
   docker exec relay-postgres pg_isready -U relay
   ```

3. **Install Jupyter**:
   ```bash
   cd ~/relay
   source venv/bin/activate
   pip install jupyter notebook
   ```

### Running Notebooks

```bash
cd ~/relay/examples
jupyter notebook
```

This will open your browser with the notebook interface.

### Running Python Scripts

Alternatively, you can run the standalone scripts:

```bash
# Simple demo (no Jupyter required)
python simple_demo.py

# Full agent demo
python agent.py

# Visualize audit trail
python visualize.py
```

---

## 📖 Key Concepts Demonstrated

### The Air Gap
```
[LLM Reasoning]  →  [RELAY AIR GAP]  →  [Execution]
  (Can be tricked)    (Cannot be tricked)   (Only if approved)
```

The notebooks demonstrate that even if an LLM is 100% convinced to perform an unauthorized action, Relay's policy engine blocks it.

### Seamless Integration

Before Relay:
```python
result = stripe.Charge.create(amount=5000)
```

After Relay:
```python
@relay.protect(provider="stripe", method="create_payment")
def create_charge(amount):
    return stripe.Charge.create(amount=amount)
```

Just add a decorator - no refactoring required.

### Business Rules → Policies

```
"Payments over $50 require approval"
    ↓
YAML Policy
    ↓
Rego Enforcement
    ↓
Automatic Blocking
```

---

## 🎓 What You'll Learn

1. **Safety**: How to protect agents from manipulation and prompt injection
2. **Integration**: How to add Relay to existing agent frameworks (LangChain, etc.)
3. **Policy Development**: How to translate business rules to enforceable policies
4. **Real-World Value**: How Relay prevents costly incidents in production

---

## 💡 Pro Tips

### For Security Teams
- Focus on `02_adversarial_prompt_protection.ipynb` and `05_real_world_scenarios.ipynb`
- These show threat models and real attack vectors

### For Developers
- Start with `01_getting_started.ipynb` and `03_langchain_integration.ipynb`
- These show practical integration patterns

### For Compliance/Legal
- Review `04_company_policies.ipynb` and scenario 4 in `05_real_world_scenarios.ipynb`
- These demonstrate GDPR, SOC2, and regulatory compliance

### For Management
- Read `05_real_world_scenarios.ipynb` for cost-benefit analysis
- Shows ROI and incident prevention value

---

## 🔗 Additional Resources

- **Main Documentation**: `../README.md`
- **Quick Start**: `../QUICKSTART.md`
- **Project Summary**: `../PROJECT_SUMMARY.md`
- **API Reference**: See Gateway endpoints in `../gateway/`

---

## 🤝 Contributing Examples

Have a great example to share? We'd love to include it!

1. Create your notebook in this directory
2. Follow the naming convention: `XX_descriptive_name.ipynb`
3. Include clear markdown explanations
4. Add it to this README
5. Submit a pull request

---

## 📞 Support

- **Issues**: https://github.com/Nadosaurusrex/relay/issues
- **Discussions**: https://github.com/Nadosaurusrex/relay/discussions
- **Documentation**: https://github.com/Nadosaurusrex/relay/blob/main/README.md

---

**Built with ❤️ for the age of autonomous agents**
