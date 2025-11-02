# Step-by-Step Guide: Converting Docker Compose to Helm Chart using Kompose

This document explains how this Helm chart was created from the `compose.yaml` file and how to use it.

## Prerequisites

- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl configured
- Helm 3.x installed
- Kompose installed

## Step-by-Step Conversion Process

### Step 1: Install Kompose

If you don't have Kompose installed, install it:

```bash
# Linux
curl -L https://github.com/kubernetes/kompose/releases/download/v1.36.0/kompose-linux-amd64 -o kompose
chmod +x kompose
sudo mv ./kompose /usr/local/bin/kompose

# macOS
brew install kompose

# Windows
choco install kubernetes-kompose
```

### Step 2: Create Output Directory

```bash
mkdir -p helm-chart
```

### Step 3: Convert Docker Compose to Helm Chart

Run Kompose with the `-c` flag to generate a Helm chart:

```bash
kompose convert -c -f compose.yaml -o helm-chart
```

This command:
- `-c`: Generates a Helm chart instead of plain Kubernetes manifests
- `-f compose.yaml`: Specifies the input Docker Compose file
- `-o helm-chart`: Specifies the output directory

### Step 4: Convert MongoDB Deployment to StatefulSet

The default conversion creates a Deployment for MongoDB. For production use with replicas, we need a StatefulSet:

1. Delete the generated Deployment:
   ```bash
   rm helm-chart/templates/mongo-db-deployment.yaml
   rm helm-chart/templates/mongo-db-data-persistentvolumeclaim.yaml
   ```

2. Create `helm-chart/templates/mongo-db-statefulset.yaml` with StatefulSet configuration including:
   - `serviceName: mongo-db` (required for StatefulSet)
   - `replicas: {{ .Values.mongodb.replicas }}` for configurable replicas
   - `volumeClaimTemplates` for automatic PVC creation per replica
   - MongoDB replica set arguments: `--replSet {{ .Values.mongodb.replicaSetName }}`

3. Update the MongoDB service to be headless (required for StatefulSet):
   - Add `clusterIP: None` to the service spec

### Step 5: Create values.yaml

Create a comprehensive `values.yaml` file with configurable parameters:

```yaml
mongodb:
  enabled: true
  image: mongo
  tag: noble
  replicas: 3
  replicaSetName: rs0
  rootUsername: root
  rootPassword: planner_solver
  database: planner_solver
  storage: 1Gi

rabbitmq:
  enabled: true
  replicas: 1
  # ... other RabbitMQ settings

plannerSolver:
  enabled: true
  replicas: 1
  port: 8080

plannerSolverRunner:
  enabled: true
  replicas: 2
```

### Step 6: Update Chart.yaml

Update the Chart.yaml with proper metadata:

```yaml
name: planner-solver
description: A Helm Chart for planner-solver application with MongoDB, RabbitMQ, and workers
version: 0.1.0
apiVersion: v2
keywords:
  - planner-solver
  - mongodb
  - rabbitmq
```

### Step 7: Validate the Helm Chart

```bash
# Lint the chart
helm lint helm-chart

# Test rendering templates
helm template test-release helm-chart --dry-run

# Verify the structure
tree helm-chart
```

## How to Deploy the Helm Chart

### Install the chart

```bash
helm install planner-solver ./helm-chart
```

### Install with custom values

```bash
# Create a custom values file
cat > custom-values.yaml <<EOF
mongodb:
  replicas: 3
  storage: 5Gi
plannerSolverRunner:
  replicas: 5
EOF

# Install with custom values
helm install planner-solver ./helm-chart -f custom-values.yaml
```

### Verify deployment

```bash
# Check Helm release
helm list

# Check pods
kubectl get pods

# Check StatefulSet
kubectl get statefulset mongo-db

# Check PVCs (one per MongoDB replica)
kubectl get pvc
```

### Initialize MongoDB Replica Set

After the MongoDB StatefulSet is running, you need to initialize the replica set:

```bash
# Connect to the first MongoDB pod
kubectl exec -it mongo-db-0 -- mongosh -u root -p planner_solver

# In the MongoDB shell, initialize the replica set:
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo-db-0.mongo-db:27017" },
    { _id: 1, host: "mongo-db-1.mongo-db:27017" },
    { _id: 2, host: "mongo-db-2.mongo-db:27017" }
  ]
})

# Check replica set status
rs.status()
```

### Upgrade the deployment

```bash
helm upgrade planner-solver ./helm-chart
```

### Uninstall the deployment

```bash
helm uninstall planner-solver

# Clean up PVCs if needed
kubectl delete pvc -l io.kompose.service=mongo-db-data
```

## Key Features of This Helm Chart

1. **Single Application**: All services (planner-solver API, workers, MongoDB, RabbitMQ) are deployed as a cohesive application under one Helm release
   - Uses standard Kubernetes labels (`app.kubernetes.io/name`, `app.kubernetes.io/instance`, `app.kubernetes.io/managed-by`)
   - Portainer automatically groups all resources under a single application based on these labels
   - Each component has an `app.kubernetes.io/component` label (api, worker, database, messaging) for easy filtering

2. **MongoDB StatefulSet**:
   - Configured as a StatefulSet with 3 replicas by default
   - Each replica gets its own PersistentVolumeClaim
   - Headless service for stable network identities
   - Supports MongoDB replica set configuration

3. **Scalable Workers**: The planner-solver-runner can be scaled independently using the `plannerSolverRunner.replicas` value

4. **Configurable**: All key parameters are externalized in values.yaml

5. **Production-Ready**: Includes health checks, proper volume management, and resource isolation

6. **Proper Kubernetes Resources**: Uses Deployments instead of bare Pods for better management and scaling

## Customization Options

You can customize the deployment by modifying `values.yaml`:

- **MongoDB replicas**: Change `mongodb.replicas` (default: 3)
- **Worker count**: Change `plannerSolverRunner.replicas` (default: 2)
- **Storage size**: Change `mongodb.storage` and `rabbitmq.storage`
- **Image tags**: Update `*.tag` values for specific versions
- **Credentials**: Update passwords and usernames (use Kubernetes secrets in production)

## Production Considerations

For production deployments:

1. **Use Kubernetes Secrets** for sensitive data instead of plain text in values.yaml
2. **Configure resource limits** and requests for all containers
3. **Set up monitoring** and logging
4. **Use a StorageClass** that supports your cloud provider
5. **Enable backup** for MongoDB data
6. **Use ingress** instead of NodePort for external access
7. **Enable TLS/SSL** for MongoDB and RabbitMQ connections
