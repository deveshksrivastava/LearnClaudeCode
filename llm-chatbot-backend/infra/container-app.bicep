// ─────────────────────────────────────────────────────────────────────────────
// WHAT IS THIS FILE?
// This Bicep file defines the Azure Container App — the actual running service.
// It specifies the Docker image to run, resource limits, environment variables,
// scaling rules, and the health check configuration.
// ─────────────────────────────────────────────────────────────────────────────

param location string = resourceGroup().location
param containerAppName string
param containerAppsEnvironmentId string
param containerRegistryLoginServer string
param managedIdentityId string
param managedIdentityClientId string
param imageName string     // Full image reference e.g. myacr.azurecr.io/llm-chatbot:latest

// Secrets — these come from azd environment variables, NOT hardcoded here
@secure()
param openaiApiKey string = ''

@secure()
param azureOpenaiApiKey string = ''
param azureOpenaiEndpoint string = ''
param azureOpenaiDeploymentName string = 'gpt-4o'
param llmProvider string = 'openai'

// ── Azure Container App ────────────────────────────────────────────────────
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}   // Give this app the managed identity
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      // Allow external traffic (public endpoint)
      ingress: {
        external: true
        targetPort: 8000      // Must match Dockerfile EXPOSE and uvicorn port
        transport: 'http'
        // Azure automatically provides HTTPS — your users always see https://
      }
      // Tell Container Apps how to pull from our private ACR
      registries: [
        {
          server: containerRegistryLoginServer
          identity: managedIdentityId   // Use Managed Identity — no password needed!
        }
      ]
      // Secrets are stored securely in Azure — not visible in logs or config
      secrets: [
        {
          name: 'openai-api-key'
          value: openaiApiKey
        }
        {
          name: 'azure-openai-api-key'
          value: azureOpenaiApiKey
        }
      ]
    }
    template: {
      containers: [
        {
          name: containerAppName
          image: imageName
          // Environment variables for the container
          // secretRef links to the secrets defined above
          env: [
            { name: 'LLM_PROVIDER', value: llmProvider }
            { name: 'OPENAI_API_KEY', secretRef: 'openai-api-key' }
            { name: 'AZURE_OPENAI_API_KEY', secretRef: 'azure-openai-api-key' }
            { name: 'AZURE_OPENAI_ENDPOINT', value: azureOpenaiEndpoint }
            { name: 'AZURE_OPENAI_DEPLOYMENT_NAME', value: azureOpenaiDeploymentName }
            { name: 'CHROMA_PERSIST_PATH', value: '/app/chroma_data' }
            { name: 'CHROMA_COLLECTION_NAME', value: 'chatbot_docs' }
            { name: 'LLM_TEMPERATURE', value: '0.7' }
            { name: 'LLM_MAX_TOKENS', value: '1024' }
            { name: 'LOG_LEVEL', value: 'INFO' }
            { name: 'APP_VERSION', value: '1.0.0' }
          ]
          // Resource limits — adjust based on your Azure plan
          resources: {
            cpu: json('0.5')    // 0.5 vCPU
            memory: '1Gi'       // 1 GB RAM
          }
          // Liveness probe — Azure restarts the container if this fails 3 times
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/api/v1/health'
                port: 8000
              }
              initialDelaySeconds: 30   // Wait 30s before first check (startup time)
              periodSeconds: 30
              failureThreshold: 3
            }
          ]
        }
      ]
      // Scaling rules — automatically add/remove containers based on traffic
      scale: {
        minReplicas: 1    // Always keep at least 1 running (no cold starts)
        maxReplicas: 5    // Scale up to 5 containers under load
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '10'   // Add a container when >10 concurrent requests
              }
            }
          }
        ]
      }
    }
  }
}

// Output the URL where the app is accessible
output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
