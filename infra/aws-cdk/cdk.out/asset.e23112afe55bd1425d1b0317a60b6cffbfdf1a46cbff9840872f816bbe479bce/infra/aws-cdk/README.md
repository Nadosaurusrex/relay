# Relay AWS CDK Deployment

This directory contains AWS CDK Infrastructure-as-Code for deploying Relay to AWS.

## 📋 Prerequisites

1. **AWS CLI** installed and configured
2. **AWS CDK** installed: `npm install -g aws-cdk`
3. **Python 3.11+** installed
4. **Docker** installed (for building container images)

## 🚀 Quick Start

### 1. Install CDK Dependencies

```bash
cd infra/aws-cdk
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Bootstrap CDK (First Time Only)

```bash
cdk bootstrap aws://002259668161/us-east-1
```

### 3. Generate Ed25519 Keys

```bash
cd ../..  # Go to repo root
python scripts/generate_keys.py
```

Save the generated private key - you'll need it after deployment.

### 4. Deploy to AWS

#### Development Environment
```bash
cd infra/aws-cdk
cdk deploy --context env=dev
```

#### Production Environment
```bash
cdk deploy --context env=prod
```

### 5. Store Ed25519 Key in Secrets Manager

After deployment, update the secret with your actual Ed25519 key:

```bash
# Get the secret ARN from CDK output
aws secretsmanager update-secret \
  --secret-id relay/ed25519-key-dev \
  --secret-string '{"private_key":"YOUR_BASE64_ENCODED_KEY"}'
```

### 6. Initialize Database

Connect to the RDS instance and run migrations:

```bash
# Get database endpoint from CDK output
# Get credentials from Secrets Manager
aws secretsmanager get-secret-value --secret-id relay/db-credentials-dev

# Run migrations (from a bastion host or via AWS Systems Manager)
psql -h <db-endpoint> -U relay -d relay -f gateway/db/migrations/versions/001_initial_schema.sql
```

### 7. Upload Policies to S3

```bash
# Compile policies
python policy-compiler/compiler.py policies/finance.yaml policies/compiled/finance.rego

# Upload to S3
aws s3 cp policies/compiled/finance.rego s3://relay-policies-002259668161-dev/finance.rego
```

### 8. Test Deployment

```bash
# Get the Load Balancer URL from CDK output
curl https://<alb-dns-name>/health

# Test manifest validation
curl -X POST https://<alb-dns-name>/v1/manifest/validate \
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
        "parameters": {"amount": 4500, "currency": "USD"}
      },
      "justification": {
        "reasoning": "Test transaction"
      }
    }
  }'
```

## 📚 CDK Commands

- `cdk ls` - List all stacks
- `cdk synth` - Generate CloudFormation template
- `cdk diff` - Show differences with deployed stack
- `cdk deploy` - Deploy stack to AWS
- `cdk destroy` - Delete stack from AWS
- `cdk doctor` - Check for CDK issues

## 🏗️ Architecture

The CDK stack creates:

- **VPC** with public, private, and isolated subnets
- **RDS PostgreSQL** in isolated subnet
- **ECS Fargate** service with:
  - Gateway container (FastAPI)
  - OPA sidecar container
- **Application Load Balancer** with HTTPS
- **S3 bucket** for policy storage
- **Secrets Manager** for keys and credentials
- **CloudWatch** logs, metrics, and alarms

## 💰 Cost Optimization

### Development (Low Cost)
```bash
cdk deploy --context env=dev
```
- Single AZ
- t3.micro RDS
- 1 Fargate task (0.25 vCPU, 0.5 GB)
- 1 NAT Gateway
- Estimated: ~$100/month

### Production (High Availability)
```bash
cdk deploy --context env=prod
```
- Multi-AZ
- t3.small RDS with backups
- 2+ Fargate tasks (0.5 vCPU, 1 GB)
- 2 NAT Gateways
- Estimated: ~$300-500/month

## 🔒 Security

### Network Security
- RDS in isolated subnet (no internet access)
- ECS in private subnet (egress via NAT)
- ALB in public subnet (HTTPS only)
- Security groups with minimal permissions

### Data Security
- RDS encryption at rest (KMS)
- S3 encryption at rest
- Secrets Manager for sensitive data
- TLS in transit

### IAM Roles
- Task execution role: Pull images, write logs
- Task role: Access RDS, S3, Secrets Manager
- Least-privilege access

## 🔧 Customization

### Environment Variables

Edit `stacks/relay_stack.py` to modify:

```python
environment={
    "RELAY_SEAL_TTL_MINUTES": "5",
    "CUSTOM_VAR": "value",
}
```

### Resource Sizing

Modify instance types, task sizes, and counts:

```python
# Database size
instance_type=ec2.InstanceType.of(
    ec2.InstanceClass.BURSTABLE3,
    ec2.InstanceSize.LARGE,  # Change here
)

# ECS task size
memory_limit_mib=2048,  # Change here
cpu=1024,  # Change here
```

### Auto-scaling

Adjust scaling thresholds:

```python
scaling.scale_on_cpu_utilization(
    "CpuScaling",
    target_utilization_percent=80,  # Change here
)
```

## 📊 Monitoring

### CloudWatch Dashboard

Access at: AWS Console → CloudWatch → Dashboards → Relay-{env}

Includes:
- Request count
- Response time
- Error rates
- Database connections

### Alarms

Pre-configured alarms:
- High 5xx error rate (> 10 errors)
- High response time (> 1 second)

### Logs

View logs at: AWS Console → CloudWatch → Log Groups → /ecs/relay-gateway-{env}

```bash
# Stream logs via CLI
aws logs tail /ecs/relay-gateway-dev --follow
```

## 🧹 Cleanup

To delete all resources:

```bash
cdk destroy --context env=dev
```

**Warning**: This will delete:
- All ECS tasks
- RDS database (with backups if prod)
- S3 bucket (if empty)
- All CloudWatch logs

## 🔄 CI/CD Integration

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install CDK
        run: npm install -g aws-cdk
      - name: Install dependencies
        run: |
          cd infra/aws-cdk
          pip install -r requirements.txt
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Deploy
        run: |
          cd infra/aws-cdk
          cdk deploy --require-approval never
```

## 🐛 Troubleshooting

### Issue: CDK Bootstrap Failed

```bash
# Ensure you have admin permissions
aws sts get-caller-identity

# Try bootstrap again
cdk bootstrap aws://002259668161/us-east-1 --verbose
```

### Issue: Docker Build Failed

```bash
# Ensure Docker is running
docker ps

# Build manually to debug
cd ../..
docker build -f infra/Dockerfile.gateway -t relay-gateway .
```

### Issue: Health Check Failing

```bash
# Check ECS logs
aws logs tail /ecs/relay-gateway-dev --follow

# Check if Gateway can connect to OPA
# Check if Gateway can connect to RDS
```

### Issue: RDS Connection Failed

```bash
# Verify security group rules
# Ensure ECS tasks are in the correct subnet
# Check database credentials in Secrets Manager
```

## 📞 Support

For issues, please check:
1. CloudWatch logs for error messages
2. CDK diff to see what changed
3. AWS Console → CloudFormation for stack events

---

**Built with AWS CDK for the age of autonomous agents**
