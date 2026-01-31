# Kubernetes Deployment for DDoS Protection Platform

This directory contains Kubernetes manifests for deploying the DDoS Protection Platform on Kubernetes.

## Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Persistent storage class available
- LoadBalancer service support (for production)

## Quick Deploy

```bash
# Apply all manifests
kubectl apply -f kubernetes/

# Check deployment status
kubectl get pods -n ddos-platform

# Get service URLs
kubectl get svc -n ddos-platform
```

## Components

- **namespace.yaml**: Creates ddos-platform namespace
- **postgres.yaml**: PostgreSQL StatefulSet with PVC
- **redis.yaml**: Redis Deployment
- **backend.yaml**: Backend API Deployment
- **frontend.yaml**: Frontend Deployment
- **services.yaml**: Service definitions
- **ingress.yaml**: Ingress for external access
- **configmap.yaml**: Configuration data
- **secrets.yaml**: Sensitive data (update before deploying!)

## Scaling

```bash
# Scale backend
kubectl scale deployment backend -n ddos-platform --replicas=3

# Scale frontend
kubectl scale deployment frontend -n ddos-platform --replicas=2
```

## Updating

```bash
# Update image
kubectl set image deployment/backend backend=your-registry/ddos-backend:v1.1 -n ddos-platform

# Rolling update
kubectl rollout status deployment/backend -n ddos-platform

# Rollback if needed
kubectl rollout undo deployment/backend -n ddos-platform
```

## Monitoring

```bash
# Check logs
kubectl logs -f deployment/backend -n ddos-platform

# Check events
kubectl get events -n ddos-platform

# Describe pod
kubectl describe pod <pod-name> -n ddos-platform
```

## Cleanup

```bash
# Delete all resources
kubectl delete namespace ddos-platform
```

## Production Considerations

1. Use proper secrets management (e.g., sealed-secrets, Vault)
2. Set resource limits and requests
3. Configure horizontal pod autoscaling
4. Use production-ready storage class
5. Enable SSL/TLS with cert-manager
6. Set up monitoring with Prometheus Operator
7. Configure network policies
8. Use separate namespaces for dev/staging/prod

For detailed Helm chart deployment, see `helm/` directory.
