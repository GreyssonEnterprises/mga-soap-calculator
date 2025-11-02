# MGA Soap Calculator API - Complete Reference

**Version:** 1.0.0
**Base URL:** `http://localhost:8000/api/v1`

## Table of Contents

1. [Authentication](#authentication)
2. [Calculation Endpoints](#calculation-endpoints)
3. [Health & Status](#health--status)
4. [Request/Response Examples](#requestresponse-examples)
5. [Error Handling](#error-handling)
6. [Curl Examples](#curl-examples)

---

## Authentication

All endpoints except `/health` require JWT authentication.

### Register User

**Endpoint:** `POST /auth/register`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "created_at": "2025-11-02T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid email or weak password
- `409 Conflict` - Email already registered

---

### Login & Get Token

**Endpoint:** `POST /auth/login`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials

**Token Usage:**
Include token in all subsequent requests:
```
Authorization: Bearer <access_token>
```

---

## Calculation Endpoints

### Create Calculation

**Endpoint:** `POST /calculate`

**Authentication:** Required (Bearer token)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "oils": [
    {
      "id": 1,
      "percentage": 50
    },
    {
      "id": 2,
      "percentage": 30
    },
    {
      "id": 3,
      "percentage": 20
    }
  ],
  "lye": {
    "naoh_percent": 100,
    "koh_percent": 0
  },
  "water": {
    "method": "percent_of_oils",
    "value": 38
  },
  "superfat_percent": 5,
  "additives": [
    {
      "id": 1,
      "usage_percent": 2
    }
  ]
}
```

**Request Parameters:**

**oils** (required, array)
- `id`: Oil database ID (integer)
- `percentage`: Oil percentage (0-100, sum must equal 100)

**lye** (required, object)
- `naoh_percent`: NaOH percentage (0-100)
- `koh_percent`: KOH percentage (0-100)
- Sum of NaOH + KOH must equal 100

**water** (required, object)
- `method`: Calculation method (enum)
  - `percent_of_oils`: Water as percentage of oils
  - `lye_concentration`: Water calculated from lye concentration
  - `lye_ratio`: Water calculated from water:lye ratio
- `value`: Method-specific value (float)

**superfat_percent** (required, float)
- Superfat percentage (0-100)
- Recommended range: 3-15%
- Warning generated if > 20%

**additives** (optional, array)
- `id`: Additive database ID (integer)
- `usage_percent`: Usage percentage by weight (float)

**Response (200 OK):**
```json
{
  "calculation_id": "550e8400-e29b-41d4-a716-446655440000",
  "recipe": {
    "oils": [
      {
        "id": 1,
        "name": "Olive Oil",
        "weight_g": 500.0,
        "percentage": 50.0
      }
    ],
    "lye": {
      "naoh_weight_g": 142.6,
      "koh_weight_g": 0.0,
      "total_weight_g": 142.6
    },
    "water": {
      "total_weight_g": 380.0,
      "method": "percent_of_oils"
    },
    "additives": [
      {
        "id": 1,
        "name": "Kaolin Clay",
        "weight_g": 20.0,
        "usage_percent": 2.0
      }
    ]
  },
  "results": {
    "quality_metrics": {
      "hardness": 41.5,
      "cleansing": 12.3,
      "conditioning": 51.2,
      "bubbly": 15.4,
      "creamy": 25.8,
      "longevity": 38.5,
      "stability": 42.1
    },
    "fatty_acid_profile": {
      "lauric": 0.0,
      "myristic": 0.0,
      "palmitic": 10.5,
      "stearic": 3.0,
      "ricinoleic": 0.0,
      "oleic": 71.0,
      "linoleic": 10.5,
      "linolenic": 0.5
    },
    "saturated_unsaturated_ratio": "13:85",
    "iodine_value": 80.5,
    "ins_value": 107.5
  },
  "warnings": [
    {
      "type": "HIGH_SUPERFAT",
      "message": "Superfat is high (5%). Consider 3-5% for most applications.",
      "severity": "info"
    }
  ],
  "created_at": "2025-11-02T10:30:00Z"
}
```

**Error Responses:**

| Status | Error Code | Message |
|--------|-----------|---------|
| 400 | `INVALID_OIL_PERCENTAGES` | Oil percentages must sum to 100.0% |
| 400 | `INVALID_LYE_PERCENTAGES` | Lye percentages must sum to 100.0% |
| 401 | `UNAUTHORIZED` | Missing or invalid JWT token |
| 422 | `UNKNOWN_OIL_ID` | Oil IDs [5, 99] not found in database |
| 422 | `UNKNOWN_ADDITIVE_ID` | Additive IDs [50] not found in database |

---

### Retrieve Calculation

**Endpoint:** `GET /calculate/{calculation_id}`

**Authentication:** Required (Bearer token)

**Headers:**
```
Authorization: Bearer <token>
```

**URL Parameters:**
- `calculation_id`: UUID of calculation to retrieve

**Response (200 OK):**
Returns same structure as POST /calculate response

**Error Responses:**
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Calculation belongs to different user
- `404 Not Found` - Calculation ID does not exist
- `422 Validation Error` - Invalid UUID format

---

## Health & Status

### Health Check

**Endpoint:** `GET /health`

**Authentication:** Not required

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

**Use Cases:**
- Load balancer health checks
- Container orchestration (Docker, Kubernetes)
- Uptime monitoring
- Smoke tests before running calculations

---

## Request/Response Examples

### Complete Workflow Example

#### Step 1: Register User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "soapmaker@example.com",
    "password": "MySecurePassword123!"
  }'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "soapmaker@example.com",
  "created_at": "2025-11-02T10:30:00Z"
}
```

#### Step 2: Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "soapmaker@example.com",
    "password": "MySecurePassword123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### Step 3: Create Calculation

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:8000/api/v1/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "oils": [
      {"id": 1, "percentage": 50},
      {"id": 2, "percentage": 30},
      {"id": 3, "percentage": 20}
    ],
    "lye": {"naoh_percent": 100, "koh_percent": 0},
    "water": {"method": "percent_of_oils", "value": 38},
    "superfat_percent": 5
  }'
```

#### Step 4: Retrieve Calculation

```bash
CALC_ID="550e8400-e29b-41d4-a716-446655440000"

curl -X GET http://localhost:8000/api/v1/calculate/$CALC_ID \
  -H "Authorization: Bearer $TOKEN"
```

---

## Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "error_code": "INVALID_OIL_PERCENTAGES",
  "message": "Oil percentages must sum to 100.0%",
  "details": [
    {
      "field": "oils",
      "issue": "percentages sum to 99.5%"
    }
  ]
}
```

### Error Codes Reference

| Code | HTTP Status | Description | Solution |
|------|------------|-------------|----------|
| `INVALID_OIL_PERCENTAGES` | 400 | Oil percentages don't sum to 100% | Adjust percentages to total exactly 100% |
| `INVALID_LYE_PERCENTAGES` | 400 | Lye percentages don't sum to 100% | Ensure NaOH + KOH = 100% |
| `INVALID_SUPERFAT` | 400 | Superfat outside valid range (0-100%) | Use value between 0 and 100 |
| `UNKNOWN_OIL_ID` | 422 | Oil ID not found in database | Use valid oil IDs from `/docs` |
| `UNKNOWN_ADDITIVE_ID` | 422 | Additive ID not found | Use valid additive IDs or omit |
| `UNAUTHORIZED` | 401 | Missing or invalid JWT token | Login to get valid token |
| `INVALID_CALCULATION_OWNERSHIP` | 403 | User accessing another user's calculation | Only access your own calculations |
| `CALCULATION_NOT_FOUND` | 404 | Calculation ID doesn't exist | Verify calculation UUID is correct |

---

## Curl Examples

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Register
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Pass123!"}'
```

### Login (Get Token)
```bash
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Pass123!"}' \
  | jq -r '.access_token')

echo $TOKEN
```

### Calculate (with token)
```bash
curl -X POST http://localhost:8000/api/v1/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "oils": [
      {"id": 1, "percentage": 100}
    ],
    "lye": {"naoh_percent": 100, "koh_percent": 0},
    "water": {"method": "percent_of_oils", "value": 38},
    "superfat_percent": 5
  }'
```

### Get Calculation
```bash
CALC_ID="550e8400-e29b-41d4-a716-446655440000"

curl http://localhost:8000/api/v1/calculate/$CALC_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Pretty Print JSON Response
```bash
curl -s http://localhost:8000/api/v1/calculate/$CALC_ID \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
```

---

## API Rate Limiting

Currently, no rate limiting is enforced. For production deployment, consider:

1. **IP-based rate limiting** - via nginx reverse proxy
2. **User-based rate limiting** - implement in FastAPI middleware
3. **Endpoint-specific limits** - stricter for /calculate endpoint

Example nginx rate limiting:
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;
```

---

## Interactive Documentation

Visit the following URLs for interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

---

## Support

- **Questions:** Refer to `/docs` endpoint
- **Issues:** Check application logs: `docker logs mga_soap_api`
- **Spec Details:** See `agent-os/specs/2025-11-01-core-calculation-api/spec.md`

---

**Last Updated:** 2025-11-02
**Maintained By:** MGA Automotive Development Team
