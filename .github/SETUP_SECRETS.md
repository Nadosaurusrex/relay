# GitHub Actions Secrets Setup

To enable automatic deployments, you need to add AWS credentials to GitHub Secrets.

## Required Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

### 1. AWS_ACCESS_KEY_ID
Your AWS access key ID from IAM user credentials

### 2. AWS_SECRET_ACCESS_KEY
Your AWS secret access key from IAM user credentials

## Getting AWS Credentials

### Option 1: Use Existing IAM User (Recommended if you have one)

```bash
# Check your current credentials
aws sts get-caller-identity

# If you're using an IAM user, get your credentials:
# Go to AWS Console → IAM → Users → Your User → Security credentials
# Create access key if needed
```

### Option 2: Create New IAM User for GitHub Actions

```bash
# Create IAM user
aws iam create-user --user-name github-actions-relay

# Attach required policies
aws iam attach-user-policy \
  --user-name github-actions-relay \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess

# Create access key
aws iam create-access-key --user-name github-actions-relay
```

**Required Permissions:**
- CloudFormation (full)
- ECS (full)
- ECR (full)
- RDS (full)
- S3 (full)
- VPC (full)
- IAM (limited - role creation)
- Secrets Manager (full)
- CloudWatch (full)
- EC2 (full)

Simplest approach: Use `PowerUserAccess` policy (covers all above except IAM role creation, which CDK handles)

## Add Secrets to GitHub

1. Go to: `https://github.com/Nadosaurusrex/relay/settings/secrets/actions`

2. Click "New repository secret"

3. Add `AWS_ACCESS_KEY_ID`:
   - Name: `AWS_ACCESS_KEY_ID`
   - Value: Your access key (e.g., `AKIA...`)

4. Click "New repository secret" again

5. Add `AWS_SECRET_ACCESS_KEY`:
   - Name: `AWS_SECRET_ACCESS_KEY`
   - Value: Your secret key (long string)

## Verify Setup

After adding secrets, push any change to main:

```bash
git commit --allow-empty -m "Test deployment workflow"
git push origin main
```

Then check: `https://github.com/Nadosaurusrex/relay/actions`

## Security Best Practices

1. ✅ Use dedicated IAM user for GitHub Actions
2. ✅ Use least-privilege permissions (or PowerUserAccess)
3. ✅ Rotate access keys regularly
4. ✅ Never commit access keys to git
5. ✅ Monitor CloudTrail for unexpected API calls
6. ⚠️ Consider using OIDC instead of long-lived credentials (advanced)

## Optional: Use OIDC (More Secure)

Instead of access keys, use GitHub OIDC provider:

```bash
# Create OIDC provider (one-time setup)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# Then update the workflow to use OIDC role assumption
# (requires additional IAM role configuration)
```

## Testing

After setup, the workflow will automatically:
1. Trigger on every push to main
2. Deploy to dev environment
3. Update secrets
4. Run health checks
5. Report status in GitHub Actions tab

For production deployments:
- Go to Actions → Deploy to Production → Run workflow
- Type "deploy-to-production" to confirm
- Production requires manual approval for safety
