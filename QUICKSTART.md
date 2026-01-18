# Relay Quick Start Guide

Get Relay up and running in 5 minutes.

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- 10 minutes

## Option 1: Automated Setup (Recommended)

```bash
cd ~/relay
./setup.sh
```

This script will:
1. Create a Python virtual environment
2. Install dependencies
3. Generate Ed25519 keys
4. Start Docker infrastructure (PostgreSQL + OPA + Gateway)
5. Compile and load policies

Then run the demo:

```bash
python demo/agent.py
python demo/visualize.py
```

## Option 2: Manual Setup

### 1. Install Dependencies

```bash
cd ~/relay
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Generate Keys

```bash
python scripts/generate_keys.py --output .env
```

### 3. Start Infrastructure

```bash
cd infra
docker-compose up -d
cd ..
```

Wait ~30 seconds for services to start.

### 4. Bootstrap Policies

```bash
python scripts/bootstrap_policies.py
```

### 5. Run Demo

```bash
python demo/agent.py
```

### 6. View Audit Trail

```bash
python demo/visualize.py
```

## Verify Installation

Check that all services are healthy:

```bash
# Check Gateway
curl http://localhost:8000/health

# Check OPA
curl http://localhost:8181/health

# Check PostgreSQL
docker exec relay-postgres pg_isready -U relay -d relay
```

## Demo Scenarios

The demo runs 4 scenarios:

1. **$40 payment** → ✅ APPROVED (under $50 limit)
2. **$60 payment** → ❌ DENIED (exceeds $50 limit)
3. **$50 payment** → ✅ APPROVED (at limit)
4. **$30 refund** → ✅ APPROVED (under $100 limit)

## Next Steps

1. **Modify policies**: Edit `policies/finance.yaml` and re-run bootstrap
2. **Create your own agent**: See `demo/agent.py` for example
3. **Query audit trail**: `curl http://localhost:8000/v1/audit/query`
4. **Read docs**: See `README.md` for full documentation

## Troubleshooting

### Gateway won't start

Check that ports are available:
```bash
lsof -i :8000  # Gateway
lsof -i :8181  # OPA
lsof -i :5432  # PostgreSQL
```

### OPA not loading policies

Check OPA logs:
```bash
docker logs relay-opa
```

Manually load a policy:
```bash
curl -X PUT http://localhost:8181/v1/policies/finance \
  --data-binary @policies/compiled/finance.rego
```

### Database connection errors

Check PostgreSQL logs:
```bash
docker logs relay-postgres
```

Recreate database:
```bash
docker-compose down -v
docker-compose up -d
```

## Clean Up

To stop and remove everything:

```bash
cd infra
docker-compose down -v
cd ..
rm -rf venv .env
```

## Support

- 📖 Full docs: See `README.md`
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/relay/issues)
- 💬 Questions: Open a discussion

---

**Happy governing! 🚀**
