# OpenShift Manifests — MGA Soap Calculator

Target: OpenShift SNO at `api.sno.greysson.com:6443`, project `mga-soap-calculator`.

## Files

| File | Purpose |
|------|---------|
| `namespace.yaml` | Namespace declaration |
| `postgresql-statefulset.yaml` | PostgreSQL 15 StatefulSet + headless Service + PVC (lvms-vg1) |
| `api-deployment.yaml` | FastAPI Deployment + ClusterIP Service |
| `route.yaml` | TLS edge Route at `mga-soap-calculator.apps.sno.greysson.com` |
| `secret-instructions.md` | How to create the required secrets (values never committed) |

## Deploy sequence

```fish
# 1. Create project (one-time)
oc new-project mga-soap-calculator

# 2. Create secrets (see secret-instructions.md — values not committed)
# ... follow secret-instructions.md ...

# 3. Apply infrastructure
oc apply -f openshift/namespace.yaml
oc apply -f openshift/postgresql-statefulset.yaml

# 4. Build and push image
set VERSION 1.5.0
podman build --platform linux/amd64 \
  -t default-route-openshift-image-registry.apps.sno.greysson.com/mga-soap-calculator/mga-soap-calculator:$VERSION \
  .
podman push default-route-openshift-image-registry.apps.sno.greysson.com/mga-soap-calculator/mga-soap-calculator:$VERSION

# 5. Apply app manifests
oc apply -f openshift/api-deployment.yaml
oc apply -f openshift/route.yaml

# 6. Set the correct image tag
oc set image deployment/mga-soap-calculator \
  mga-soap-calculator=image-registry.openshift-image-registry.svc:5000/mga-soap-calculator/mga-soap-calculator:$VERSION \
  -n mga-soap-calculator

# 7. Watch rollout
oc rollout status deployment/mga-soap-calculator -n mga-soap-calculator

# 8. Verify health
curl https://mga-soap-calculator.apps.sno.greysson.com/api/v1/health
```

## Rollback

```fish
oc rollout undo deployment/mga-soap-calculator -n mga-soap-calculator
```

## Notes

- `DATABASE_URL_SYNC` is required until Phase 2 (CI-04) derives it automatically
- PostgreSQL image: `registry.access.redhat.com/rhel9/postgresql-15:latest` (UBI9, matches app base)
- Storage: `lvms-vg1` is the default StorageClass on this SNO cluster (confirmed 2026-04-18)
- The internal registry svc URL (`image-registry.openshift-image-registry.svc:5000`) is used in Deployment specs; the external route is used for `podman push`
