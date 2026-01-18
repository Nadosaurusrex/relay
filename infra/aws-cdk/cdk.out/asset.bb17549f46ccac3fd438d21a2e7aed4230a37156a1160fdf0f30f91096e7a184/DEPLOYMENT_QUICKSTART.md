# Relay AWS Deployment - Quick Start Guide

🎉 **Congratulations!** Your AWS deployment infrastructure is ready!

## What Was Created

### 1. AWS CDK Infrastructure Code
Located in `infra/aws-cdk/`:

- **`app.py`**: Main CDK application
- **`stacks/relay_stack.py`**: Complete infrastructure stack
  - VPC with public, private, and isolated subnets
  - RDS PostgreSQL database
  - ECS Fargate service (Gateway + OPA sidecar)
  - Application Load Balancer
  - S3 bucket for policies
  - Secrets Manager for keys
  - CloudWatch monitoring
- **`deploy.sh`**: Automated deployment script
- **`README.md`**: Detailed documentation

### 2. Architecture Diagram
See `AWS_DEPLOYMENT_PLAN.md` for the complete architecture.

## 🚀 Deploy to AWS (3 Options)

### Option 1: Automated Deployment (Recommended)

```bash
cd infra/aws-cdk
./deploy.sh dev
```

This script will:
1. ✅ Check all prerequisites
2. ✅ Install dependencies
3. ✅ Bootstrap CDK (if needed)
4. ✅ Generate Ed25519 keys
5. ✅ Deploy infrastructure
6. ✅ Show next steps

### Option 2: Manual Step-by-Step

```bash
# 1. Go to CDK directory
cd infra/aws-cdk

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Bootstrap CDK (first time only)
cdk bootstrap aws://002259668161/us-east-1

# 5. Deploy
cdk deploy --context env=dev
```

### Option 3: Review First (Dry Run)

```bash
cd infra/aws-cdk
source .venv/bin/activate || python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Generate CloudFormation template (no deployment)
cdk synth --context env=dev

# Show what will change
cdk diff --context env=dev
```

## 📋 Prerequisites (Already Installed ✓)

- ✅ AWS CLI configured with credentials
- ✅ AWS CDK installed
- ✅ Python 3.11+
- ✅ Docker
- ✅ Node.js & npm

## 💰 Cost Estimate

### Development Environment (`env=dev`)
- **Monthly Cost**: ~$100-150
- Includes:
  - 1 ECS Fargate task (0.25 vCPU, 0.5 GB RAM)
  - RDS db.t3.micro (single AZ)
  - Application Load Balancer
  - 1 NAT Gateway
  - S3, Secrets Manager, CloudWatch

### Production Environment (`env=prod`)
- **Monthly Cost**: ~$300-500
- Includes:
  - 2+ ECS Fargate tasks (0.5 vCPU, 1 GB RAM)
  - RDS db.t3.small (Multi-AZ)
  - Application Load Balancer
  - 2 NAT Gateways
  - Enhanced monitoring

## 🔒 Security Features

Your deployment includes:

- ✅ **Network Isolation**: RDS in isolated subnet, ECS in private subnet
- ✅ **Encryption**: Data at rest (RDS, S3) and in transit (HTTPS)
- ✅ **Secrets Management**: Keys stored in AWS Secrets Manager
- ✅ **IAM Roles**: Least-privilege access
- ✅ **VPC Flow Logs**: Network activity monitoring
- ✅ **CloudWatch Alarms**: Automatic alerting

## 📝 Post-Deployment Steps

After deployment completes, you'll need to:

### 1. Update Ed25519 Secret

```bash
# Load your generated key
source .env

# Update the secret in AWS
aws secretsmanager update-secret \
  --secret-id relay/ed25519-key-dev \
  --secret-string "{\"private_key\":\"$RELAY_PRIVATE_KEY\"}"
```

### 2. Initialize Database

```bash
# Get database credentials
DB_SECRET=$(aws secretsmanager get-secret-value \
  --secret-id relay/db-credentials-dev \
  --query SecretString --output text)

DB_PASSWORD=$(echo $DB_SECRET | jq -r .password)
DB_HOST=$(echo $DB_SECRET | jq -r .host)

# Connect and run migrations (requires network access to RDS)
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U relay -d relay \
  -f ../../gateway/db/migrations/versions/001_initial_schema.sql
```

### 3. Upload Policies to S3

```bash
# Compile policies
python policy-compiler/compiler.py \
  policies/finance.yaml \
  policies/compiled/finance.rego

# Upload to S3
aws s3 cp policies/compiled/finance.rego \
  s3://relay-policies-002259668161-dev/
```

### 4. Test Deployment

```bash
# Get the load balancer URL from CloudFormation outputs
ALB_URL=$(aws cloudformation describe-stacks \
  --stack-name RelayStack-dev \
  --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerURL'].OutputValue" \
  --output text)

# Test health endpoint
curl $ALB_URL/health

# Test manifest validation
curl -X POST $ALB_URL/v1/manifest/validate \
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

## 📊 Monitoring

### CloudWatch Dashboard
```bash
# Open in browser
open "https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=Relay-dev"
```

### View Logs
```bash
# Stream Gateway logs
aws logs tail /ecs/relay-gateway-dev --follow

# View recent logs
aws logs tail /ecs/relay-gateway-dev --since 1h
```

### Check Alarms
```bash
aws cloudwatch describe-alarms --alarm-name-prefix Relay
```

## 🧹 Cleanup

To delete all AWS resources:

```bash
cd infra/aws-cdk
cdk destroy --context env=dev
```

**Warning**: This will permanently delete:
- All ECS tasks and containers
- RDS database (including backups)
- S3 bucket (if empty)
- All CloudWatch logs and metrics
- Load balancers and network resources

## 🔄 CI/CD Integration

To automate deployments from GitHub:

1. Add AWS credentials to GitHub Secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

2. Create `.github/workflows/deploy.yml` (example in CDK README)

3. Push to main branch to trigger deployment

## 🐛 Troubleshooting

### Issue: CDK Bootstrap Failed
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Re-run bootstrap with verbose output
cdk bootstrap aws://002259668161/us-east-1 --verbose
```

### Issue: Deployment Stuck
```bash
# Check CloudFormation events
aws cloudformation describe-stack-events \
  --stack-name RelayStack-dev --max-items 20

# Check ECS task status
aws ecs list-tasks --cluster RelayStack-dev-RelayCluster
```

### Issue: Health Check Failing
```bash
# Check logs
aws logs tail /ecs/relay-gateway-dev --follow

# Check if Gateway can reach OPA
# Check if Gateway can connect to RDS
# Verify security group rules
```

## 📚 Additional Resources

- **Full Architecture**: See `AWS_DEPLOYMENT_PLAN.md`
- **CDK Documentation**: See `infra/aws-cdk/README.md`
- **AWS CDK Docs**: https://docs.aws.amazon.com/cdk/
- **Relay Documentation**: See main `README.md`

## 🎯 Next Steps

Choose your path:

### Path 1: Deploy Now
```bash
cd infra/aws-cdk
./deploy.sh dev
```

### Path 2: Test Locally First
```bash
# Start local infrastructure
cd infra
docker-compose up -d

# Run examples
python examples/simple_demo.py
```

### Path 3: Customize First
Edit `infra/aws-cdk/stacks/relay_stack.py` to:
- Change instance sizes
- Modify auto-scaling rules
- Add custom environment variables
- Configure different retention policies

---

## 🚨 Important Notes

1. **Database Initialization**: You must manually run database migrations after first deployment
2. **Ed25519 Keys**: Update the secret with your actual key (deployment creates a placeholder)
3. **SSL Certificate**: The ALB will use a default AWS certificate. For production, use ACM with your domain
4. **NAT Gateway**: Costs ~$32/month. Consider alternatives for dev environments
5. **Backups**: Production deployments enable automatic RDS backups (7-day retention)

## ✅ Deployment Checklist

Before going to production:

- [ ] Review and adjust instance sizes
- [ ] Configure custom domain with Route53
- [ ] Set up SSL certificate in ACM
- [ ] Configure CloudWatch alarms and notifications
- [ ] Set up backup and disaster recovery procedures
- [ ] Review security groups and network ACLs
- [ ] Enable AWS WAF for additional protection
- [ ] Configure log retention policies
- [ ] Set up cost budgets and alerts
- [ ] Document operational procedures
- [ ] Test failover scenarios
- [ ] Load test the deployment

---

**Ready to deploy?** Run: `cd infra/aws-cdk && ./deploy.sh dev`

**Need help?** Check the troubleshooting section or review CloudWatch logs.

🚀 **Happy Deploying!**
