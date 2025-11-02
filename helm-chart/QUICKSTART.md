# Quick Start Guide

## Installation Steps

1. **Install the Helm chart:**
   ```bash
   helm install planner-solver ./helm-chart
   ```

2. **Wait for pods to be ready:**
   ```bash
   kubectl get pods -w
   ```

3. **Initialize MongoDB Replica Set** (required after first install):
   ```bash
   # Connect to MongoDB primary
   kubectl exec -it mongo-db-0 -- mongosh -u root -p planner_solver
   
   # Run in MongoDB shell:
   rs.initiate({
     _id: "rs0",
     members: [
       { _id: 0, host: "mongo-db-0.mongo-db:27017" },
       { _id: 1, host: "mongo-db-1.mongo-db:27017" },
       { _id: 2, host: "mongo-db-2.mongo-db:27017" }
     ]
   })
   
   # Exit with Ctrl+D
   ```

4. **Verify the deployment:**
   ```bash
   helm list
   kubectl get statefulset
   kubectl get pods
   kubectl get svc
   ```

## Access Services

- **Planner Solver API**: http://localhost:8080 (via port-forward)
  ```bash
  kubectl port-forward svc/planner-solver 8080:8080
  ```

- **RabbitMQ Management**: http://localhost:15672 (via port-forward)
  ```bash
  kubectl port-forward svc/rabbitmq 15672:15672
  ```
  Login: root / planner_solver

- **MongoDB**: Port 27017
  ```bash
  kubectl port-forward svc/mongo-db 27017:27017
  ```

## Uninstall

```bash
helm uninstall planner-solver
kubectl delete pvc -l io.kompose.service=mongo-db-data
```
