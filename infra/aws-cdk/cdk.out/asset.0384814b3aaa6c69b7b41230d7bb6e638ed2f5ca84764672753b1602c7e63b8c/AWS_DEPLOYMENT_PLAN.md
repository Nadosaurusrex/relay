# Relay AWS Deployment Architecture

## 🏗️ AWS Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet/Agents                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     API Gateway (REST API)                        │
│  • Authentication (API Keys / IAM / Cognito)                      │
│  • Rate limiting                                                  │
│  • Request validation                                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│         Application Load Balancer (ALB)                           │
│  • HTTPS termination                                              │
│  • Health checks                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│   ECS Fargate Task 1    │  │   ECS Fargate Task 2    │
│  ┌──────────────────┐   │  │  ┌──────────────────┐   │
│  │ Relay Gateway    │   │  │  │ Relay Gateway    │   │
│  │   (FastAPI)      │   │  │  │   (FastAPI)      │   │
│  └──────────────────┘   │  │  └──────────────────┘   │
│  ┌──────────────────┐   │  │  ┌──────────────────┐   │
│  │ OPA Sidecar      │   │  │  │ OPA Sidecar      │   │
│  └──────────────────┘   │  │  └──────────────────┘   │
└─────────┬───────────────┘  └─────────┬───────────────┘
          │                            │
          └────────────┬───────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼
┌────────────┐ ┌──────────────┐ ┌──────────┐ ┌────────────┐
│ RDS        │ │ Secrets      │ │ S3       │ │ CloudWatch │
│ PostgreSQL │ │ Manager      │ │ Policies │ │ Logs       │
│            │ │              │ │          │ │            │
│ • Audit    │ │ • Ed25519    │ │ • Rego   │ │ • Metrics  │
│   Trail    │ │   Keys       │ │   Files  │ │ • Alarms   │
│ • Seals    │ │ • DB Creds   │ │          │ │            │
└────────────┘ └──────────────┘ └──────────┘ └────────────┘
```

## 📋 AWS Services Used

### Compute
- **ECS Fargate**: Run Relay Gateway containers (serverless)
- **ECS Service**: Auto-scaling, health checks, load balancing

### Storage
- **RDS PostgreSQL**: Immutable audit trail and seal storage
  - Multi-AZ for high availability
  - Automated backups
  - Encryption at rest
- **S3**: Policy files (Rego) storage
  - Versioning enabled
  - Server-side encryption

### Networking
- **VPC**: Isolated network environment
- **Private Subnets**: For ECS tasks and RDS
- **Public Subnets**: For ALB
- **NAT Gateway**: For outbound internet access from private subnets
- **Security Groups**: Network-level security

### API & Load Balancing
- **API Gateway**: External API endpoint with authentication
- **Application Load Balancer**: Routes traffic to ECS tasks

### Security
- **Secrets Manager**: Store Ed25519 keys and database credentials
- **IAM Roles**: Least-privilege access for ECS tasks
- **KMS**: Encryption keys for data at rest

### Monitoring
- **CloudWatch Logs**: Centralized logging
- **CloudWatch Metrics**: Performance monitoring
- **CloudWatch Alarms**: Alerting for failures
- **X-Ray**: Distributed tracing (optional)

### Optional Enhancements
- **DynamoDB**: Alternative to RDS for audit trail (serverless, higher scale)
- **Lambda**: For OPA policy evaluation (alternative to sidecar)
- **Cognito**: User authentication for web UI
- **WAF**: Web application firewall

## 💰 Cost Estimation (Monthly)

### Small Deployment (Development/Testing)
- ECS Fargate (0.25 vCPU, 0.5 GB RAM, 2 tasks): ~$15
- RDS PostgreSQL (db.t3.micro): ~$15
- ALB: ~$20
- NAT Gateway: ~$35
- S3 + Secrets Manager: ~$5
- CloudWatch: ~$10
**Total: ~$100/month**

### Medium Deployment (Production - 100K requests/day)
- ECS Fargate (0.5 vCPU, 1 GB RAM, 4 tasks): ~$60
- RDS PostgreSQL (db.t3.small, Multi-AZ): ~$60
- ALB: ~$20
- NAT Gateway: ~$35
- S3 + Secrets Manager: ~$10
- CloudWatch: ~$20
**Total: ~$205/month**

### Large Deployment (Scale - 1M requests/day)
- ECS Fargate (1 vCPU, 2 GB RAM, 8 tasks): ~$240
- RDS PostgreSQL (db.r5.large, Multi-AZ): ~$400
- ALB: ~$30
- NAT Gateway (2): ~$70
- S3 + Secrets Manager: ~$20
- CloudWatch: ~$50
**Total: ~$810/month**

## 🚀 Deployment Options

### Option 1: AWS CDK (Recommended)
- Infrastructure as Code in Python
- Type-safe constructs
- Easy to version control
- Automatic CloudFormation generation

### Option 2: CloudFormation
- Native AWS IaC
- YAML/JSON templates
- Good for simple deployments

### Option 3: Terraform
- Multi-cloud support
- Large community
- HCL syntax

## 📦 Deployment Steps

### Phase 1: Prepare Application
1. Update `gateway/config.py` for AWS environment variables
2. Create production Dockerfile
3. Test container locally
4. Push Docker image to ECR

### Phase 2: Deploy Infrastructure
1. Create VPC and networking
2. Provision RDS PostgreSQL
3. Set up Secrets Manager
4. Create S3 bucket for policies
5. Deploy ECS cluster and service
6. Configure ALB and API Gateway
7. Set up CloudWatch monitoring

### Phase 3: Initialize Data
1. Run database migrations
2. Upload policies to S3
3. Generate and store Ed25519 keys
4. Bootstrap OPA policies

### Phase 4: Testing
1. Health check endpoints
2. Smoke tests for each API endpoint
3. Load testing
4. Security scanning

### Phase 5: Production Cutover
1. DNS configuration
2. SSL/TLS certificates
3. Enable monitoring alerts
4. Documentation for ops team

## 🔒 Security Best Practices

### Network Security
- ✅ ECS tasks in private subnets (no direct internet access)
- ✅ RDS in private subnets
- ✅ Security groups with minimal permissions
- ✅ VPC Flow Logs enabled

### Application Security
- ✅ HTTPS only (TLS 1.2+)
- ✅ API Gateway with API keys or IAM authentication
- ✅ Secrets in AWS Secrets Manager (never in code)
- ✅ Least-privilege IAM roles
- ✅ Container image scanning (ECR)

### Data Security
- ✅ RDS encryption at rest (KMS)
- ✅ RDS encryption in transit (SSL)
- ✅ S3 bucket encryption
- ✅ Audit logs encrypted
- ✅ Automated backups with retention

### Compliance
- ✅ Immutable audit trail (database triggers)
- ✅ Cryptographic proofs (Ed25519)
- ✅ CloudTrail for AWS API auditing
- ✅ VPC Flow Logs for network auditing

## 🔧 Configuration Management

### Environment Variables (via ECS Task Definition)
```
RELAY_DB_HOST=<rds-endpoint>
RELAY_DB_PORT=5432
RELAY_DB_NAME=relay
RELAY_DB_USER=relay
RELAY_DB_PASSWORD=<from-secrets-manager>
RELAY_OPA_URL=http://localhost:8181
RELAY_PRIVATE_KEY=<from-secrets-manager>
RELAY_SEAL_TTL_MINUTES=5
RELAY_API_HOST=0.0.0.0
RELAY_API_PORT=8000
AWS_REGION=us-east-1
S3_POLICY_BUCKET=relay-policies-<account-id>
```

## 📊 Monitoring & Alerting

### CloudWatch Metrics
- Request count
- Error rate (4xx, 5xx)
- Latency (p50, p95, p99)
- Database connections
- ECS CPU/Memory utilization

### CloudWatch Alarms
- High error rate (> 5%)
- High latency (p99 > 500ms)
- Database connection pool exhausted
- ECS task failures
- RDS storage space < 20%

### Logs
- Gateway API logs → CloudWatch Logs
- OPA policy evaluation logs
- Database query logs
- ALB access logs → S3

## 🔄 CI/CD Pipeline

### GitHub Actions / GitLab CI
1. **Build**: Docker image with version tag
2. **Test**: Run unit and integration tests
3. **Push**: Upload to ECR
4. **Deploy**: Update ECS service with new image
5. **Verify**: Health checks and smoke tests

### Blue/Green Deployment
- Use ECS to run new task definitions
- Gradually shift traffic via ALB
- Rollback in seconds if needed

## 📈 Scaling Strategy

### Horizontal Scaling
- ECS Service Auto Scaling based on:
  - CPU utilization (> 70%)
  - Request count (> 1000/min)
  - Custom CloudWatch metrics

### Database Scaling
- Start with db.t3.small
- Scale up to db.r5.xlarge for high throughput
- Enable read replicas for query workloads
- Consider Aurora Serverless for variable traffic

### Caching (Future)
- ElastiCache Redis for:
  - Policy caching
  - Seal verification lookups
  - Session data

## 🌍 Multi-Region (Future)

### Active-Active
- Deploy to multiple AWS regions
- Route53 latency-based routing
- Cross-region RDS replication
- S3 cross-region replication

### Disaster Recovery
- Automated backups to S3
- Cross-region backup replication
- Recovery Time Objective (RTO): < 1 hour
- Recovery Point Objective (RPO): < 15 minutes

## 🎯 Next Steps

1. **Review this plan** - Confirm architecture meets requirements
2. **Choose deployment method** - CDK, CloudFormation, or Terraform?
3. **Set up AWS account** - Enable required services
4. **Create IaC code** - Write infrastructure code
5. **Deploy to dev** - Test deployment in development environment
6. **Deploy to prod** - Production cutover

---

**Ready to deploy?** Let's start with AWS CDK implementation!
