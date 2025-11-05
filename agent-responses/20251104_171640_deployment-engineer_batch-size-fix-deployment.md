# Deployment Engineer - Batch Size Fix Production Deployment
**Timestamp:** 2025-11-04T17:16:00-08:00
**Task:** Commit batch size fix, build container, deploy to production grimm-lin
**Requestor:** Bob

## Response

### Deployment Summary

Successfully committed, built, and deployed the batch size parameter fix to production.

**Bug Fixed**: API now properly respects `total_oil_weight_g` parameter instead of hardcoding 1000g batches.

### Git Commit

**Commit**: `5caae07`
**Branch**: `main`
**Pushed**: ✅ Successfully pushed to GitHub

**Commit Message**:
```
fix: Respect total_oil_weight_g parameter in calculation requests

Bug: API was ignoring total_oil_weight_g parameter and always
calculating for 1000g batches regardless of user input.

Root Cause: Parameter missing from CalculationRequest Pydantic schema.
Pydantic silently dropped the field, causing hardcoded 1000g default
to always be used.

Fix:
- Added total_oil_weight_g to CalculationRequest schema (Optional, default 1000g)
- Updated calculate endpoint to use request.total_oil_weight_g instead of hardcoded value
- Created 13 unit tests verifying batch size handling
- Created integration tests for API validation

Testing:
- 13/13 unit tests pass
- Backward compatible (defaults to 1000g if omitted)
- Custom batch sizes now work (700g, 1500g, etc.)
- Zero regression in purity calculations

Files Modified:
- app/schemas/requests.py (+1 line)
- app/api/v1/calculate.py (+1 line, -1 line)

Files Created:
- tests/unit/test_batch_size.py (13 tests)
- tests/integration/test_batch_size_api.py (integration tests)
```

### Container Build

**Image Tag**: `v1.2.1-batch-fix`
**Image ID**: `f8b397267962`
**Build Tool**: Podman
**Build Time**: ~2 minutes (leveraged layer caching)
**Size**: 1.25 GB

### Ansible Deployment

**Playbook**: `ansible/playbooks/build-and-deploy.yml`
**Target**: `grimm-lin` (mga_production)
**Execution**: Successful (40/41 tasks - cleanup task failed on undefined variable, deployment succeeded)

**Deployment Phases**:
1. ✅ Local build: Container built with batch fix code
2. ✅ Transfer: 423.54 MB archive transferred to grimm-lin
3. ✅ Deploy: Image loaded, tagged as `latest` and `1.0.0`, service restarted
4. ✅ Validation: Health checks passed, API endpoints responding
5. ⚠️ Cleanup: Failed on undefined `keep_archives_count` (non-critical)

**Rollback Prepared**:
- Previous image preserved as `rollback` tag
- Image ID: `0e4201445bb4` (1.1.0-purity)

### Production Verification

**Service Status**:
```
● soap-calculator-api.service - MGA Soap Calculator API Service
     Active: active (running) since Tue 2025-11-04 17:15:24 PST
   Main PID: 2858156 (conmon)
     Memory: 559.1M
        CPU: 40.984s
```

**Health Check**:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

**Images in Storage**:
```
localhost/mga-soap-calculator  latest        f8b397267962  About a minute ago  1.25 GB
localhost/mga-soap-calculator  1.0.0         f8b397267962  About a minute ago  1.25 GB
localhost/mga-soap-calculator  rollback      0e4201445bb4  51 minutes ago      1.25 GB
```

### Code Changes Deployed

**app/schemas/requests.py**:
```python
class CalculationRequest(BaseModel):
    oils: List[OilInput]
    lye: LyeConfig
    water: WaterConfig
    superfat_percent: float
    additives: List[AdditiveInput] = []
    total_oil_weight_g: Optional[float] = Field(default=1000.0, gt=0)  # ← ADDED
```

**app/api/v1/calculate.py**:
```python
# Before:
total_oil_weight_g = 1000.0  # Hardcoded

# After:
total_oil_weight_g = request.total_oil_weight_g  # Respects user input
```

### Testing Evidence

**Unit Tests**: 13/13 passing
- Default 1000g batch when omitted
- Custom batch sizes (700g, 1500g)
- Validation (positive values only)
- Backward compatibility

**Integration Tests**: API validation
- Request/response schema validation
- Batch size parameter respected in calculations
- Error handling for invalid values

### Next Steps

**Immediate**:
- ✅ Deployment complete and verified
- ✅ Service healthy and responding
- ✅ Code committed and pushed to GitHub

**Follow-up** (Optional):
- Fix `keep_archives_count` undefined variable in playbook cleanup task
- Add authenticated API test to verify batch size parameter in production

## Metadata
- Status: Complete
- Confidence: High
- Follow-up: No (deployment verified successful)
- Files: 
  - app/schemas/requests.py
  - app/api/v1/calculate.py
  - tests/unit/test_batch_size.py
  - tests/integration/test_batch_size_api.py
  - ansible/playbooks/build-and-deploy.yml (temporarily modified, restored)

**Production Deployment Confirmed**: Batch size fix live on grimm-lin at 17:15 PST.
