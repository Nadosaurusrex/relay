# Push CI/CD Workflows to GitHub

The CI/CD workflows are committed locally but need to be pushed with proper credentials.

## Quick Fix - Push Now

```bash
# Try pushing with your credentials
git push origin main
```

## If You Get OAuth Scope Error

GitHub requires the `workflow` scope to create/update workflow files. Here are your options:

### Option 1: Use SSH (Recommended)

```bash
# Switch to SSH authentication
git remote set-url origin git@github.com:Nadosaurusrex/relay.git

# Push
git push origin main
```

### Option 2: Create Personal Access Token

1. Go to: https://github.com/settings/tokens/new
2. Select scopes:
   - ✅ `repo` (all)
   - ✅ `workflow`
3. Generate token
4. Push with token:

```bash
git push https://YOUR_TOKEN@github.com/Nadosaurusrex/relay.git main
```

### Option 3: Use GitHub CLI

```bash
# Install gh CLI if needed: brew install gh

# Authenticate
gh auth login

# Push
git push origin main
```

## After Pushing

Once pushed, you need to add AWS credentials to GitHub Secrets:

1. Go to: https://github.com/Nadosaurusrex/relay/settings/secrets/actions

2. Add these secrets:
   - `AWS_ACCESS_KEY_ID` - Your AWS access key
   - `AWS_SECRET_ACCESS_KEY` - Your AWS secret key

3. Test it:
   ```bash
   git commit --allow-empty -m "Test CI/CD deployment"
   git push origin main
   ```

4. Check deployment:
   https://github.com/Nadosaurusrex/relay/actions

## What Happens After Setup

✅ **Every push to main** → Automatic deployment to dev environment
✅ **Manual trigger** → Deploy to production (with confirmation)
✅ **Health checks** → Automatic endpoint verification
✅ **Status reports** → Deployment summaries in GitHub Actions

See `.github/SETUP_SECRETS.md` for detailed AWS credentials setup.
