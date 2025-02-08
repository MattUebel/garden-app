# Azure Deployment Guide

This guide provides detailed instructions for deploying the Garden App to different Azure services.

## Prerequisites

1. Install Azure CLI
2. Azure subscription
3. Azure CLI login:
```bash
az login
```

## Option 1: Azure App Service (Recommended)

### Step 1: Create Resource Group
```bash
az group create --name garden-app-rg --location eastus
```

### Step 2: Create Azure Database for PostgreSQL
```bash
az postgres flexible-server create \
  --resource-group garden-app-rg \
  --name garden-db-server \
  --location eastus \
  --admin-user garden_admin \
  --admin-password <your-secure-password> \
  --sku-name Standard_B1ms
```

### Step 3: Create Storage Account
```bash
az storage account create \
  --name gardenappstore \
  --resource-group garden-app-rg \
  --location eastus \
  --sku Standard_LRS
```

### Step 4: Deploy to App Service
```bash
# Create App Service Plan
az appservice plan create \
  --name garden-app-plan \
  --resource-group garden-app-rg \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group garden-app-rg \
  --plan garden-app-plan \
  --name your-garden-app \
  --runtime "PYTHON:3.11" \
  --deployment-source-url https://github.com/YourUsername/garden-app.git
```

### Step 5: Configure Environment Variables
```bash
az webapp config appsettings set \
  --resource-group garden-app-rg \
  --name your-garden-app \
  --settings \
    DATABASE_URL="postgresql://garden_admin:<password>@garden-db-server.postgres.database.azure.com:5432/garden_db" \
    AZURE_STORAGE_CONNECTION_STRING="<connection-string-from-storage-account>"
```

## Option 2: Azure Container Apps

### Step 1: Create Azure Container Registry
```bash
az acr create \
  --resource-group garden-app-rg \
  --name gardenappregistry \
  --sku Basic

# Log in to ACR
az acr login --name gardenappregistry
```

### Step 2: Build and Push Container
```bash
# Build the image
docker build -t gardenappregistry.azurecr.io/garden-app:latest .

# Push to ACR
docker push gardenappregistry.azurecr.io/garden-app:latest
```

### Step 3: Create Container App
```bash
az containerapp create \
  --resource-group garden-app-rg \
  --name garden-app \
  --image gardenappregistry.azurecr.io/garden-app:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    DATABASE_URL="postgresql://garden_admin:<password>@garden-db-server.postgres.database.azure.com:5432/garden_db" \
    AZURE_STORAGE_CONNECTION_STRING="<connection-string>"
```

## Option 3: Azure Kubernetes Service (AKS)

### Step 1: Create AKS Cluster
```bash
az aks create \
  --resource-group garden-app-rg \
  --name garden-app-aks \
  --node-count 1 \
  --enable-addons monitoring \
  --generate-ssh-keys
```

### Step 2: Get Credentials
```bash
az aks get-credentials \
  --resource-group garden-app-rg \
  --name garden-app-aks
```

### Step 3: Deploy Using Kubernetes
```bash
# Create Kubernetes secrets
kubectl create secret generic garden-app-secrets \
  --from-literal=DATABASE_URL="postgresql://garden_admin:<password>@garden-db-server.postgres.database.azure.com:5432/garden_db" \
  --from-literal=AZURE_STORAGE_CONNECTION_STRING="<connection-string>"

# Apply Kubernetes manifests
kubectl apply -f k8s/
```

## Monitoring and Maintenance

### Enable Application Insights
```bash
az monitor app-insights component create \
  --app garden-app-insights \
  --location eastus \
  --resource-group garden-app-rg
```

### Set Up Continuous Deployment
1. Navigate to Azure Portal
2. Go to your App Service
3. Select "Deployment Center"
4. Configure GitHub Actions or Azure DevOps pipelines

### Backup and Recovery
- Enable geo-redundant backups for PostgreSQL
- Set up automated database backups
- Configure storage account redundancy

## Cost Optimization
- Use B1 tier for development/testing
- Scale up to P1V2 for production
- Enable auto-scaling rules
- Monitor resource usage

## Security Best Practices
1. Enable Azure AD authentication
2. Configure SSL/TLS certificates
3. Set up network security groups
4. Implement role-based access control (RBAC)
5. Enable Azure Security Center