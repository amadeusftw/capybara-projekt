#!/bin/bash
# Azure Secrets Setup Script for Capybara Newsletter App

# Source the .azure-config file
source .azure-config

echo "================================"
echo "Azure Secrets Setup"
echo "================================"

# Generate a secure random password
echo ""
echo "Generating secure admin password..."
ADMIN_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
ADMIN_USERNAME="capybara-admin"

echo "Admin Username: $ADMIN_USERNAME"
echo "Admin Password: $ADMIN_PASSWORD (save this securely!)"

# Append to .azure-config
echo "" >> .azure-config
echo "# Auto-generated admin credentials" >> .azure-config
echo "ADMIN_USERNAME=\"$ADMIN_USERNAME\"" >> .azure-config
echo "ADMIN_PASSWORD=\"$ADMIN_PASSWORD\"" >> .azure-config

echo ""
echo "Credentials saved to .azure-config"
echo ""

# Set secrets in Azure Container Apps
echo "Uploading secrets to Azure Container Apps..."
echo ""

# Create admin-username secret
echo "Creating admin-username secret..."
az containerapp secret set \
  --name "$CA_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --secrets "admin-username=$ADMIN_USERNAME"

# Create admin-password secret
echo "Creating admin-password secret..."
az containerapp secret set \
  --name "$CA_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --secrets "admin-password=$ADMIN_PASSWORD"

echo ""
echo "Setting environment variables to reference secrets..."
echo ""

# Update environment variables to use secretref
az containerapp update \
  --name "$CA_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --set-env-vars \
    "ADMIN_USERNAME=secretref:admin-username" \
    "ADMIN_PASSWORD=secretref:admin-password" \
  --output json | jq '.properties.template.containers[0].env'

echo ""
echo "================================"
echo "✅ Secrets setup complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Commit entrypoint.sh: git add entrypoint.sh && git commit -m 'Add idempotent admin seeding to entrypoint'"
echo "2. Push to GitHub: git push"
echo "3. Monitor logs: az containerapp logs show -n $CA_NAME -g $RESOURCE_GROUP --tail 50"
echo ""
