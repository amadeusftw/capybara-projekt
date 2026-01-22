#!/bin/bash
# Detta script demonstrerar hur Azure-infrastrukturen byggs automatiskt.
RG="rg-cmcorp-system"
LOC="westeurope"
PLAN="plan-cmcorp-free"
APP="cm-corp-web-$(date +%s)"

echo "Creating Resource Group: $RG"
az group create --name $RG --location $LOC

echo "Creating App Service Plan (Free Tier)"
az appservice plan create --name $PLAN --resource-group $RG --sku F1 --is-linux

echo "Creating Web App"
az webapp create --resource-group $RG --plan $PLAN --name $APP --runtime "PYTHON|3.9"

echo "Infrastructure Ready!"
