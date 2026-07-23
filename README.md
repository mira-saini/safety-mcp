# Deploying a Remote MCP Server with Azure Container Apps

## Overview

This guide walks through deploying a remote Model Context Protocol (MCP) server using:

- Visual Studio Code
- GitHub
- Azure Container Registry (ACR)
- Azure Container Apps (ACA)

At a high level:

```text
Local VS Code Project
          ↓
      GitHub Repo
          ↓
 GitHub Actions CI/CD
          ↓
 Azure Container Registry (ACR)
          ↓
 Azure Container Apps (ACA)
          ↓
   Public MCP Endpoint
          ↓
 Azure AI Foundry / Copilot Studio / Custom Apps
```

The end result is a publicly accessible MCP endpoint that can be consumed by Azure AI Foundry Agents, Copilot Studio Agents, or custom applications.

---

# Prerequisites

Before starting, ensure you have:

- Azure Subscription
- GitHub Account
- Visual Studio Code
- Docker installed locally
- Azure Container Apps permissions
- Azure Container Registry permissions

You will also need:

- A GitHub repository
- A working local MCP server project
- Permission to create Azure resources

---

# Recommended Project Structure

Open your project in VS Code and organize it similarly to the following:

```text
mcp-server/
│
├── server.py
├── requirements.txt
├── Dockerfile
├── .gitignore
│
├── .github/
│   └── workflows/
│       └── azure-container-app.yml
│
└── README.md
```

Example:

```text
mcp-server/
│
├── server.py
├── requirements.txt
├── Dockerfile
│
├── .github/
│   └── workflows/
│       └── azure-container-app.yml
```

---

# Step 1: Create Your GitHub Repository

Create a new GitHub repository.

Example:

```text
https://github.com/your-org/mcp-server
```

Push your project:

```bash
git init
git add .
git commit -m "Initial commit"

git remote add origin https://github.com/your-org/mcp-server.git

git push -u origin main
```

Azure will later pull code from this repository to build and deploy your container image.

---

# Step 2: Create an Azure Container Registry

Azure Container Registry (ACR) stores the Docker image that will be deployed.

Example:

```text
mymcpregistry.azurecr.io
```

Think of ACR as Azure's private Docker Hub.

Workflow:

```text
GitHub Code
      ↓
Build Docker Image
      ↓
Push to ACR
      ↓
Deploy to ACA
```

---

# Step 3: Create an Azure Container App

Create a Container App within Azure.

During creation:

- Choose your resource group
- Select your Container Apps Environment
- Connect an Azure Container Registry
- Configure ingress settings

Enable:

```text
Ingress: Enabled
Transport: HTTP
External Traffic: Enabled
```

---

# Step 4: Connect GitHub to Azure

When creating the Container App, Azure offers:

```text
Deployment Source:
GitHub Actions
```

Select:

```text
GitHub Actions
```

Azure will:

1. Connect to your repository
2. Create a GitHub workflow
3. Generate deployment configuration
4. Configure CI/CD

---

# How Azure Deploys Your Code

Many developers assume Azure Container Apps directly runs their GitHub repository.

It does not.

Instead, Azure performs:

```text
GitHub Repository
        ↓
GitHub Action Triggered
        ↓
Docker Image Build
        ↓
Push Image to ACR
        ↓
Container App Pulls Image
        ↓
Container Starts Running
```

The running application is the Docker image, not the GitHub code directly.

---

# Step 5: GitHub Secrets

GitHub Actions needs permission to access Azure resources.

This is handled through Repository Secrets.

Navigate to:

```text
GitHub Repository
→ Settings
→ Secrets and Variables
→ Actions
```

Azure may create some automatically, but you often need to verify them.

Common secrets include:

```text
AZURE_CLIENT_ID

AZURE_TENANT_ID

AZURE_SUBSCRIPTION_ID

AZURE_CLIENT_SECRET
```

Or a credential JSON:

```text
AZURE_CREDENTIALS
```

Depending on your organization's setup, Azure may use:

- Service Principal authentication
- Workload Identity Federation
- Managed Identity

---

# Step 6: Azure Creates a Workflow File

Once GitHub deployment is configured, Azure usually adds:

```text
.github/workflows/
```

Example:

```text
.github/workflows/azure-container-app.yml
```

This file controls:

- Docker build
- Container Registry push
- Container App deployment

---

# Why You Will Probably Need to Edit the Workflow

Azure-generated workflows are rarely perfect for custom MCP servers.

Common reasons for modification:

### Container Name Changes

Azure may reference:

```yaml
containerAppName: my-app
```

You may need:

```yaml
containerAppName: my-mcp-server
```

---

### Registry Name Updates

```yaml
acrName: myregistry
```

Must match your actual registry.

---

### Dockerfile Path Updates

Azure often assumes:

```yaml
appSourcePath: .
```

If your Dockerfile lives elsewhere:

```yaml
appSourcePath: ./backend
```

you must update the workflow.

---

### Branch Name Changes

Generated workflows often watch:

```yaml
branches:
  - main
```

If your repository uses:

```yaml
master
```

or another branch, modify accordingly.

---

### Custom Build Arguments

You may need to add:

```yaml
buildArguments: |
  ENV=prod
```

for more advanced deployments.

---

# Example Deployment Flow

Every push to GitHub can automatically deploy:

```text
Developer Pushes Code
          ↓
GitHub Action Starts
          ↓
Docker Image Built
          ↓
Image Stored in ACR
          ↓
Azure Container App Updated
          ↓
New MCP Version Live
```

This gives you continuous deployment without manually rebuilding containers.

---

# Step 7: Configure Your Dockerfile

A minimal Python MCP server Dockerfile might look like:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "server.py"]
```

Your workflow will build this image automatically.

---

# Step 8: Verify Container App Startup

After deployment:

Navigate to:

```text
Azure Portal
→ Container App
→ Revisions
```

Verify:

```text
Running
```

instead of:

```text
Failed
```

If deployment fails, inspect:

```text
Container App Logs
Revision Logs
System Logs
```

---

# Step 9: Obtain the Public Endpoint

Once ingress is enabled, Azure provides a URL similar to:

```text
https://my-mcp-app.westus.azurecontainerapps.io
```

For MCP servers, you may expose:

```text
https://my-mcp-app.westus.azurecontainerapps.io/mcp
```

depending on your framework and implementation.

This becomes the remote MCP endpoint.

---

# Using the Endpoint

The endpoint can then be consumed by:

### Azure AI Foundry Agents

```text
Foundry Agent
    ↓
Remote MCP Tool
```

### Copilot Studio Agents

```text
Copilot Agent
       ↓
Remote MCP Endpoint
```

### Custom Applications

```text
React App
    ↓
Foundry Agent
    ↓
MCP Server
```

---

# Common Deployment Issues

## Target Port Mismatch

Example:

```text
Container listens on 8000
Container App configured for 80
```

Result:

```text
Activation failed
TargetPort does not match listening port
```

Fix:

Make Container App target port match the server's listening port.

---

## Connection Refused

Typically means:

- Application crashed
- Wrong port
- Startup failed

Check revision logs.

---

## GitHub Action Fails

Verify:

- Secrets exist
- Service Principal permissions
- Registry permissions
- Subscription permissions

---

## ACR Authentication Failure

Verify:

```text
Container App
→ Registry Settings
```

and confirm the Container App has permission to pull images.

---

# Final Architecture

```text
VS Code
   ↓
GitHub Repository
   ↓
GitHub Actions Workflow
   ↓
Azure Container Registry
   ↓
Azure Container Apps
   ↓
Remote MCP Endpoint
   ↓
Azure AI Foundry / Copilot Studio / Apps
```

Once deployed, any update pushed to GitHub can automatically rebuild and redeploy your MCP server through the GitHub Actions workflow.