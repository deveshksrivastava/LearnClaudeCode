// ─────────────────────────────────────────────────────────────────────────────
// WHAT IS THIS FILE?
// This is the main Azure Bicep infrastructure file.
// Bicep is Azure's declarative language for provisioning cloud resources.
// Instead of clicking through the Azure portal, you describe what you want
// in code, and Azure creates it for you. This is "Infrastructure as Code" (IaC).
//
// RESOURCES CREATED:
//   1. Log Analytics Workspace — centralised logging for all Azure resources
//   2. Azure Container Registry (ACR) — stores your Docker images
//   3. Container Apps Environment — the compute environment for Container Apps
//   4. User-assigned Managed Identity — secure, credential-free authentication
// ─────────────────────────────────────────────────────────────────────────────

// Parameters are variables you pass in when running `azd up`
// They allow the same template to deploy to dev, staging, and production
param location string = resourceGroup().location
param environmentName string
param containerAppName string = 'llm-chatbot'
param containerRegistryName string = 'acrllmchatbot${uniqueString(resourceGroup().id)}'
param logAnalyticsName string = 'log-llm-chatbot'
param containerAppsEnvName string = 'cae-llm-chatbot'

// ── Log Analytics Workspace ────────────────────────────────────────────────
// Collects logs from all Azure resources. Essential for debugging on Azure.
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'   // Pay-per-GB pricing tier
    }
    retentionInDays: 30   // Keep logs for 30 days
  }
}

// ── Azure Container Registry ───────────────────────────────────────────────
// Stores the Docker images built by `azd up`.
// Azure Container Apps pulls images directly from ACR (no DockerHub needed).
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: containerRegistryName
  location: location
  sku: {
    name: 'Basic'   // Basic tier is cheapest — upgrade to Standard for geo-replication
  }
  properties: {
    adminUserEnabled: false   // Disable admin user — use Managed Identity instead (more secure)
  }
}

// ── User-Assigned Managed Identity ────────────────────────────────────────
// Managed Identity = Azure's way to give resources permission to other resources
// WITHOUT storing credentials (no API keys in config for internal Azure services).
// Our Container App uses this identity to pull images from ACR.
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-llm-chatbot'
  location: location
}

// ── ACR Pull Role Assignment ────────────────────────────────────────────────
// Grants the Managed Identity permission to pull images from ACR.
// "AcrPull" is a built-in Azure role ID.
resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(containerRegistry.id, managedIdentity.id, 'acrpull')
  scope: containerRegistry
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '7f951dda-4ed3-4680-a7ca-43fe172d538d'  // AcrPull role ID (this is a well-known Azure GUID)
    )
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// ── Container Apps Environment ─────────────────────────────────────────────
// The environment is the shared compute infrastructure for Container Apps.
// Multiple apps can run in one environment and share networking + logging.
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: containerAppsEnvName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// ── Outputs ────────────────────────────────────────────────────────────────
// Outputs expose values that other Bicep modules or `azd` can use.
output containerRegistryLoginServer string = containerRegistry.properties.loginServer
output containerAppsEnvironmentId string = containerAppsEnvironment.id
output managedIdentityId string = managedIdentity.id
output managedIdentityClientId string = managedIdentity.properties.clientId
