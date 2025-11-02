# Portainer Application Grouping

## Overview

This Helm chart has been configured to ensure all resources appear as a single application in Portainer, similar to how Passbolt and other properly-configured Helm charts behave.

## How It Works

Portainer groups Kubernetes resources into applications based on standard Kubernetes labels. The key labels are:

- `app.kubernetes.io/name`: The name of the application (e.g., "planner-solver")
- `app.kubernetes.io/instance`: The release name (e.g., the name you give when running `helm install`)
- `app.kubernetes.io/managed-by`: The tool managing the deployment (e.g., "Helm")
- `app.kubernetes.io/component`: The component type (e.g., "api", "worker", "database", "messaging")

## What Changed

### 1. Added `_helpers.tpl`

Created a standard Helm helpers file ([templates/_helpers.tpl](templates/_helpers.tpl)) with label templates that ensure consistent labeling across all resources.

### 2. Updated All Resources

All Kubernetes resources now use the standard labels:

**Before (Kompose default):**
```yaml
metadata:
  labels:
    io.kompose.service: mongo-db
  name: mongo-db
```

**After (Helm best practices):**
```yaml
metadata:
  name: {{ include "planner-solver.fullname" . }}-mongodb
  labels:
    helm.sh/chart: planner-solver-0.1.0
    app.kubernetes.io/name: planner-solver
    app.kubernetes.io/instance: release-name
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: database
```

### 3. Resource Naming Convention

All resources now follow a consistent naming pattern:
- MongoDB: `<release-name>-planner-solver-mongodb`
- RabbitMQ: `<release-name>-planner-solver-rabbitmq`
- API: `<release-name>-planner-solver-api`
- Workers: `<release-name>-planner-solver-runner`

### 4. Converted Pods to Deployments

Changed bare Pod resources to Deployments for:
- Better management and scaling capabilities
- Automatic restart on failure
- Rolling updates support
- ReplicaSet management

## Portainer View

When you install this Helm chart, Portainer will:

1. **Group all resources** under a single application named after the chart release
2. **Show components** by the `app.kubernetes.io/component` label:
   - `api`: The planner-solver API server
   - `worker`: The planner-solver runner workers
   - `database`: MongoDB StatefulSet
   - `messaging`: RabbitMQ deployment

3. **Display metadata**:
   - Application name: `planner-solver`
   - Instance: Your release name
   - Managed by: Helm

## Installation Example

```bash
# Install with release name "planner-solver"
helm install planner-solver ./helm-chart

# In Portainer, you'll see one application called "planner-solver" containing:
# - 1 StatefulSet (mongodb - 3 replicas)
# - 3 Deployments (api, runner, rabbitmq)
# - 3 Services (mongodb, api, rabbitmq)
# - 4 ConfigMaps (configs and modules for api and runner)
# - 1 PVC (rabbitmq-data)
# - 3 PVCs (auto-created by MongoDB StatefulSet)
```

## Verifying Labels

You can verify the labels are correctly applied:

```bash
# Check labels on a specific resource
kubectl get deployment -l app.kubernetes.io/name=planner-solver -o yaml

# List all resources belonging to the application
kubectl get all -l app.kubernetes.io/instance=planner-solver

# Filter by component
kubectl get all -l app.kubernetes.io/component=database
```

## Comparison with Passbolt

Like Passbolt's Helm chart, this chart now:
- Uses standard Kubernetes recommended labels
- Groups all resources under a single Helm release
- Provides component-level organization
- Follows Helm best practices for templating
- Uses Deployments/StatefulSets instead of bare Pods

This ensures Portainer correctly identifies and groups all resources as a single application.
