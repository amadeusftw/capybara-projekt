# Azure Deployment Instructions

## CapybaraCorp Domain Setup

### Local Development
To access the site as `capybaracorp.local` on your machine:

**Windows:**
1. Open `C:\Windows\System32\drivers\etc\hosts` with admin rights
2. Add this line:
```
127.0.0.1       capybaracorp.local
```
3. Save and reload Flask
4. Visit: `http://capybaracorp.local:5000`

**Mac/Linux:**
```bash
sudo nano /etc/hosts
# Add: 127.0.0.1 capybaracorp.local
```

### Production (Azure)
After deployment to Azure, configure a custom domain:

```bash
source .azure-config

# Create a CNAME record with your DNS provider pointing to:
# capybaracorp-se.azurecontainerapps.io (or your container's default domain)

# Then bind it to your container app:
az containerapp hostname bind \
  --hostname capybaracorp.se \
  --name "$CA_NAME" \
  --resource-group "$RESOURCE_GROUP"
```

## Step 1: Merge Feature Branch
When GitHub Actions is complete (green checkmark), merge the feature branch to main:

```bash
git checkout main
git pull origin main
git merge feature/admin-dashboard
git push origin main
```

Wait for the main branch GitHub Actions to complete. Monitor the deployment at:
https://github.com/amadeusftw/capybara-projekt/actions

## Step 2: Set Up Azure Secrets

Before running setup-secrets.sh, make sure you have:
- Azure CLI installed: `az --version`
- Logged in to Azure: `az login`
- Your resource group and container app name configured in `.azure-config`

Then run:

```bash
bash setup-secrets.sh
```

This will:
1. Generate a secure random admin password
2. Save credentials to `.azure-config`
3. Upload secrets to Azure Container Apps
4. Update environment variables to reference the secrets

## Step 3: Verify Deployment

Monitor the container app logs to verify admin user seeding:

```bash
# Source your Azure config
source .azure-config

# Tail the logs (last 50 lines)
az containerapp logs show \
  --name "$CA_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --tail 50

# Look for output like:
# "Seeding admin user..."
# "Admin seeding complete"
```

## Step 4: Test Login

Once the container has restarted with the new secrets:

1. Navigate to: https://your-container-app-url/auth/login
2. Log in with the credentials set in Azure Secrets:
   - Username: `capybara-admin` (or custom value from .azure-config)
   - Password: Check your .azure-config file for ADMIN_PASSWORD

3. After login, you should see:
   - "Admin Panel" link in navigation
   - Access to /admin/subscribers page
   - CSV export button

## Troubleshooting

### "Admin user already exists (idempotent)" message
This is **expected and normal** if the container restarts. The entrypoint.sh script is idempotent, meaning it can run multiple times safely.

### "RuntimeError: The current Flask app is not registered with this 'SQLAlchemy' instance"
This error occurs if the app context is not properly set up. It should not happen in the Docker container since the entrypoint.sh handles initialization. If it occurs locally:
```bash
# Run the app as a module instead
python -m app.app
```

### Secrets not appearing in logs
Make sure you used the `secretref:` prefix in environment variables:
```bash
ADMIN_PASSWORD=secretref:admin-password
```

Without this prefix, Azure treats it as a literal string value, not a secret reference.
