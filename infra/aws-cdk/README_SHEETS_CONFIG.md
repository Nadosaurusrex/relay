# Google Sheets Waitlist Configuration for AWS Deployment

## Overview

The Google Sheets URL for the waitlist form is configured in the AWS infrastructure and baked into the frontend build during Docker image creation.

## How It Works

1. **Secret Storage**: The Google Sheets URL is stored in AWS Secrets Manager as `relay/sheets-url-{env_name}`
2. **Build Time Injection**: During Docker build, the URL is passed as a build argument `VITE_SHEETS_URL`
3. **Frontend Build**: Vite uses the `VITE_SHEETS_URL` environment variable to embed it in the compiled frontend code
4. **Static Serving**: The backend serves the pre-built frontend with the baked-in configuration

## Current Configuration

The URL is currently hardcoded in two places:

1. **CDK Stack** (`stacks/relay_stack.py`):
   ```python
   build_args={
       "VITE_SHEETS_URL": "https://script.google.com/macros/s/AKfycbx.../exec",
   }
   ```

2. **Secrets Manager** (`_create_sheets_url_secret()` method):
   ```python
   secret_string_value=secretsmanager.SecretStringValueBeta1.from_token(
       json.dumps({
           "sheets_url": "https://script.google.com/macros/s/AKfycbx.../exec"
       })
   )
   ```

## Updating the Google Sheets URL

### Option 1: Update and Redeploy (Recommended)

1. **Update the CDK code** in `stacks/relay_stack.py`:
   ```python
   build_args={
       "VITE_SHEETS_URL": "YOUR_NEW_URL_HERE",
   }
   ```

2. **Update the secret creation method** in `stacks/relay_stack.py`:
   ```python
   secret_string_value=secretsmanager.SecretStringValueBeta1.from_token(
       json.dumps({
           "sheets_url": "YOUR_NEW_URL_HERE"
       })
   )
   ```

3. **Redeploy the stack**:
   ```bash
   cd infra/aws-cdk
   cdk deploy
   ```

This will:
- Rebuild the Docker image with the new URL
- Update the secret in Secrets Manager
- Deploy the new container to ECS

### Option 2: Update Secret Only (Manual)

If you only want to update the secret without redeploying:

```bash
# Update the secret value
aws secretsmanager update-secret \
  --secret-id relay/sheets-url-prod \
  --secret-string '{"sheets_url":"YOUR_NEW_URL_HERE"}'
```

⚠️ **Note**: This updates the secret but does NOT rebuild the frontend. The old URL will still be in the deployed frontend code. You must redeploy to update the frontend.

## Accessing the Secret Programmatically

If you need to read the sheets URL from your backend:

```python
import boto3
import json

# Get the secret
client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='relay/sheets-url-prod')
secret = json.loads(response['SecretString'])
sheets_url = secret['sheets_url']
```

## Why Build-Time vs Runtime?

The URL is injected at **build time** (not runtime) because:

1. **Vite Requirement**: Vite embeds environment variables starting with `VITE_` into the compiled JavaScript bundle at build time
2. **Static Frontend**: The frontend is compiled to static HTML/JS/CSS and served by the backend
3. **No Runtime Config**: The frontend doesn't make an API call to get config - it's all baked in

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    CDK Deploy                           │
│                                                          │
│  1. Read VITE_SHEETS_URL from CDK code                 │
│  2. Pass as Docker build argument                       │
│     ↓                                                    │
│  3. Docker Build Stage 1 (Frontend)                    │
│     - Set ENV VITE_SHEETS_URL                          │
│     - npm run build (Vite embeds URL)                  │
│     - Produces: /dist with baked-in config             │
│     ↓                                                    │
│  4. Docker Build Stage 2 (Backend)                     │
│     - Copy /dist → /gateway/static                     │
│     - Backend serves static files                       │
│     ↓                                                    │
│  5. Push image to ECR                                  │
│  6. Deploy to ECS Fargate                              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  User Visits Site                       │
│                                                          │
│  Browser → ALB → ECS (Backend) → Serve /static/index.html
│                                                          │
│  Frontend JS has VITE_SHEETS_URL embedded               │
│  Form submits to: https://script.google.com/.../exec   │
└─────────────────────────────────────────────────────────┘
```

## Security Notes

- The Google Sheets URL is **not sensitive** (it's a public webhook endpoint)
- Anyone can POST to the URL, but only authorized Google accounts can view the sheet data
- The URL is visible in the frontend JavaScript (by design)
- If you need to rotate the URL:
  1. Create a new Google Apps Script deployment
  2. Update the CDK code with the new URL
  3. Redeploy the infrastructure

## Deployment Checklist

When deploying to a new environment:

- [ ] Deploy Google Apps Script and get the web app URL
- [ ] Update `VITE_SHEETS_URL` in `stacks/relay_stack.py` (build_args)
- [ ] Update `VITE_SHEETS_URL` in `_create_sheets_url_secret()` method
- [ ] Deploy CDK stack: `cdk deploy`
- [ ] Test the waitlist form on the deployed site
- [ ] Verify data appears in Google Sheets

## Environment-Specific Configuration

For multiple environments (dev, staging, prod):

```python
# In relay_stack.py
def _get_sheets_url(self) -> str:
    """Get environment-specific Google Sheets URL"""
    sheets_urls = {
        "dev": "https://script.google.com/.../exec-dev",
        "staging": "https://script.google.com/.../exec-staging",
        "prod": "https://script.google.com/.../exec-prod",
    }
    return sheets_urls.get(self.env_name, sheets_urls["dev"])

# Then use in build_args:
build_args={
    "VITE_SHEETS_URL": self._get_sheets_url(),
}
```

This allows you to have separate Google Sheets for each environment.

---

**Last Updated**: 2026-01-19
**Stack Version**: V1 (Internal Gateway Phase)
