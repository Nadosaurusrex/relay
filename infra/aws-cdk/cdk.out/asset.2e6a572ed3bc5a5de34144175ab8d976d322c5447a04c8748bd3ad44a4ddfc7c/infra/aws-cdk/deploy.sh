#!/bin/bash

# Relay AWS Deployment Script
# This script automates the deployment of Relay to AWS

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENV="${1:-dev}"
ACCOUNT_ID="002259668161"
REGION="us-east-1"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Relay AWS Deployment Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Environment: $ENV"
echo "AWS Account: $ACCOUNT_ID"
echo "AWS Region: $REGION"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

if ! command -v cdk &> /dev/null; then
    echo -e "${RED}AWS CDK not found. Installing...${NC}"
    npm install -g aws-cdk
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found. Please install it first.${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 not found. Please install it first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Verify AWS credentials
echo -e "${YELLOW}Verifying AWS credentials...${NC}"
aws sts get-caller-identity > /dev/null 2>&1 || {
    echo -e "${RED}AWS credentials not configured. Run 'aws configure' first.${NC}"
    exit 1
}
echo -e "${GREEN}✓ AWS credentials verified${NC}"
echo ""

# Install CDK dependencies
echo -e "${YELLOW}Installing CDK dependencies...${NC}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt
echo -e "${GREEN}✓ CDK dependencies installed${NC}"
echo ""

# Bootstrap CDK (if needed)
echo -e "${YELLOW}Checking CDK bootstrap...${NC}"
if ! aws cloudformation describe-stacks --stack-name CDKToolkit --region $REGION &> /dev/null; then
    echo "Bootstrapping CDK..."
    cdk bootstrap aws://$ACCOUNT_ID/$REGION
else
    echo -e "${GREEN}✓ CDK already bootstrapped${NC}"
fi
echo ""

# Generate Ed25519 keys (if not exists)
echo -e "${YELLOW}Checking Ed25519 keys...${NC}"
if [ ! -f "../../.env" ]; then
    echo "Generating Ed25519 keys..."
    cd ../..
    python scripts/generate_keys.py --output .env
    cd infra/aws-cdk
    echo -e "${GREEN}✓ Ed25519 keys generated${NC}"
else
    echo -e "${GREEN}✓ Ed25519 keys already exist${NC}"
fi
echo ""

# Synth CDK
echo -e "${YELLOW}Synthesizing CloudFormation template...${NC}"
cdk synth --context env=$ENV --context account=$ACCOUNT_ID --context region=$REGION
echo -e "${GREEN}✓ CloudFormation template generated${NC}"
echo ""

# Show diff
echo -e "${YELLOW}Showing deployment changes...${NC}"
cdk diff --context env=$ENV --context account=$ACCOUNT_ID --context region=$REGION || true
echo ""

# Confirm deployment
read -p "Do you want to proceed with deployment? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Deploy
echo -e "${YELLOW}Deploying to AWS...${NC}"
cdk deploy --context env=$ENV --context account=$ACCOUNT_ID --context region=$REGION --require-approval never

echo ""
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo ""

# Get outputs
echo -e "${YELLOW}Fetching stack outputs...${NC}"
STACK_NAME="RelayStack-${ENV}"

ALB_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerURL'].OutputValue" \
    --output text \
    --region $REGION)

DB_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='DatabaseEndpoint'].OutputValue" \
    --output text \
    --region $REGION)

POLICY_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='PolicyBucketName'].OutputValue" \
    --output text \
    --region $REGION)

ED25519_SECRET_ARN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='Ed25519SecretARN'].OutputValue" \
    --output text \
    --region $REGION)

DB_SECRET_ARN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='DatabaseSecretARN'].OutputValue" \
    --output text \
    --region $REGION)

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Information${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Load Balancer URL: $ALB_URL"
echo "Database Endpoint: $DB_ENDPOINT"
echo "Policy Bucket: $POLICY_BUCKET"
echo "Ed25519 Secret ARN: $ED25519_SECRET_ARN"
echo "Database Secret ARN: $DB_SECRET_ARN"
echo ""

# Post-deployment instructions
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Next Steps${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "1. Update Ed25519 secret with your actual key:"
echo "   source ../../.env"
echo "   aws secretsmanager update-secret \\"
echo "     --secret-id $ED25519_SECRET_ARN \\"
echo "     --secret-string '{\"private_key\":\"'\$RELAY_PRIVATE_KEY'\"}'"
echo ""
echo "2. Run database migrations:"
echo "   # Get DB credentials"
echo "   aws secretsmanager get-secret-value --secret-id $DB_SECRET_ARN"
echo "   # Run migrations (from bastion or Systems Manager)"
echo "   psql -h $DB_ENDPOINT -U relay -d relay -f ../../gateway/db/migrations/versions/001_initial_schema.sql"
echo ""
echo "3. Upload policies to S3:"
echo "   python ../../policy-compiler/compiler.py ../../policies/finance.yaml ../../policies/compiled/finance.rego"
echo "   aws s3 cp ../../policies/compiled/finance.rego s3://$POLICY_BUCKET/finance.rego"
echo ""
echo "4. Test deployment:"
echo "   curl $ALB_URL/health"
echo ""
echo -e "${GREEN}Deployment complete!${NC}"
