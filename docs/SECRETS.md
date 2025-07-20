# GitHub Actions Secrets Configuration

This document outlines all the secrets required for the EPIC V11 CI/CD pipeline.

## Required Secrets

### 🚀 Deployment Secrets

| Secret Name | Description | Example Value | Required |
|------------|-------------|---------------|----------|
| `STAGING_SSH_KEY` | Private SSH key for staging server | `-----BEGIN OPENSSH PRIVATE KEY-----...` | ✅ |
| `STAGING_USER` | SSH username for staging | `ubuntu` | ✅ |
| `STAGING_HOST` | Staging server hostname/IP | `staging.epic.pos.com` | ✅ |
| `STAGING_URL` | Full staging URL | `https://staging.epic.pos.com` | ✅ |
| `PRODUCTION_SSH_KEY` | Private SSH key for production | `-----BEGIN OPENSSH PRIVATE KEY-----...` | ✅ |
| `PRODUCTION_USER` | SSH username for production | `ubuntu` | ✅ |
| `PRODUCTION_HOST` | Production server hostname/IP | `epic.pos.com` | ✅ |
| `PRODUCTION_URL` | Full production URL | `https://epic.pos.com` | ✅ |

### 📢 Notification Secrets

| Secret Name | Description | Example Value | Required |
|------------|-------------|---------------|----------|
| `SLACK_WEBHOOK` | Slack webhook for notifications | `https://hooks.slack.com/services/...` | ❌ |

### 🔐 Optional Security Secrets

| Secret Name | Description | Example Value | Required |
|------------|-------------|---------------|----------|
| `DOCKERHUB_USERNAME` | Docker Hub username | `epicv11` | ❌ |
| `DOCKERHUB_TOKEN` | Docker Hub access token | `dckr_pat_...` | ❌ |
| `SONAR_TOKEN` | SonarCloud token | `sqp_...` | ❌ |

## Setting Up Secrets

### Via GitHub Web Interface

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret from the table above

### Via GitHub CLI

```bash
# Install GitHub CLI
brew install gh  # macOS
# or
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg

# Authenticate
gh auth login

# Add secrets
gh secret set STAGING_SSH_KEY < ~/.ssh/staging_key
gh secret set STAGING_USER -b "ubuntu"
gh secret set STAGING_HOST -b "staging.epic.pos.com"
gh secret set STAGING_URL -b "https://staging.epic.pos.com"

# List secrets
gh secret list
```

## Generating SSH Keys

### Create Deployment Keys

```bash
# Generate staging key
ssh-keygen -t ed25519 -C "epic-staging-deploy" -f ~/.ssh/epic_staging_key -N ""

# Generate production key  
ssh-keygen -t ed25519 -C "epic-production-deploy" -f ~/.ssh/epic_production_key -N ""

# Copy public keys to servers
ssh-copy-id -i ~/.ssh/epic_staging_key.pub ubuntu@staging.epic.pos.com
ssh-copy-id -i ~/.ssh/epic_production_key.pub ubuntu@epic.pos.com
```

### Add to GitHub Secrets

```bash
# Add staging key
gh secret set STAGING_SSH_KEY < ~/.ssh/epic_staging_key

# Add production key
gh secret set PRODUCTION_SSH_KEY < ~/.ssh/epic_production_key
```

## Environment-Specific Variables

### Staging Environment (.env.staging)
```bash
NODE_ENV=staging
NEXT_PUBLIC_API_URL=https://staging.epic.pos.com
DATABASE_URL=postgresql://epic_admin:password@postgres:5432/epic_v11_staging
```

### Production Environment (.env.production)
```bash
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://epic.pos.com
DATABASE_URL=postgresql://epic_admin:password@postgres:5432/epic_v11_prod
```

## Security Best Practices

### 1. SSH Key Security
- Use ED25519 keys (more secure than RSA)
- Set appropriate permissions: `chmod 600 ~/.ssh/epic_*_key`
- Use different keys for staging and production
- Rotate keys every 90 days

### 2. Secret Rotation
- Rotate deployment keys quarterly
- Update API keys when team members change
- Use expiring tokens where possible

### 3. Access Control
- Limit who can view/edit secrets
- Use GitHub environments for additional protection
- Enable required reviewers for production

### 4. Audit Trail
- Monitor secret access in GitHub audit log
- Set up alerts for secret usage
- Review deployment logs regularly

## Troubleshooting

### SSH Connection Issues
```bash
# Test SSH connection
ssh -i ~/.ssh/epic_staging_key ubuntu@staging.epic.pos.com -v

# Common fixes:
# 1. Check key permissions (600)
# 2. Verify username is correct
# 3. Ensure key is added to authorized_keys
# 4. Check firewall rules (port 22)
```

### Secret Not Found
```bash
# Verify secret exists
gh secret list

# Check secret name matches exactly (case-sensitive)
# Ensure workflow has access to secrets
# Check if using reusable workflows (need inherit)
```

### Invalid Secret Format
- SSH keys must include full header/footer
- No extra whitespace or newlines
- Use `< file` redirection, not copy/paste
- For multiline secrets, use GitHub web UI

## Emergency Procedures

### Revoke Compromised Keys
```bash
# 1. Remove from GitHub immediately
gh secret remove STAGING_SSH_KEY

# 2. Remove from server
ssh ubuntu@staging.epic.pos.com
nano ~/.ssh/authorized_keys  # Remove the key

# 3. Generate and deploy new key
ssh-keygen -t ed25519 -C "epic-staging-deploy-new" -f ~/.ssh/epic_staging_key_new
gh secret set STAGING_SSH_KEY < ~/.ssh/epic_staging_key_new
```

### Disable Deployments
```bash
# Disable all workflows
gh workflow disable "CD Pipeline"
gh workflow disable "CI Pipeline"

# Re-enable when ready
gh workflow enable "CD Pipeline"
```