# Quickstart Guide: INCI Label Generator API

**Feature**: 003-inci-label-generator
**API Version**: v1
**Last Updated**: 2025-11-05

## Overview

The INCI Label Generator API provides professional ingredient labels in three formats (raw oils, saponified salts, common names) with regulatory-compliant percentage-based sorting.

**Key Features**:
- Three label formats: Raw INCI, Saponified INCI, Common Names
- Percentage-based sorting (descending order)
- Detailed ingredient breakdown with categories
- <100ms response time
- JWT authentication required

## Quick Start

### 1. Authentication

All INCI label endpoints require JWT authentication.

```bash
# Obtain JWT token (use your auth endpoint)
TOKEN=$(curl -X POST https://api.mga-soap-calculator.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "your-password"}' \
  | jq -r '.access_token')

# Verify token
echo $TOKEN
```

### 2. Basic Usage

**Get all label formats** (default):

```bash
curl -X GET https://api.mga-soap-calculator.com/api/v1/recipes/recipe-123-abc/inci-label \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

**Response**:
```json
{
  "recipe_id": "recipe-123-abc",
  "recipe_name": "MGA Signature Bar",
  "generated_at": "2025-11-05T14:30:00Z",
  "labels": {
    "raw_inci": "Aqua, Cocos Nucifera Oil, Olea Europaea Fruit Oil, Butyrospermum Parkii Butter, Sodium Hydroxide, Glycerin, Lavandula Angustifolia Oil, Mica",
    "saponified_inci": "Aqua, Sodium Cocoate, Sodium Olivate, Sodium Shea Butterate, Glycerin, Lavandula Angustifolia Oil, Mica",
    "common_names": "Water, Coconut Oil, Olive Oil, Shea Butter, Sodium Hydroxide, Glycerin, Lavender Essential Oil, Mica"
  },
  "ingredients_breakdown": [
    {
      "name": "Aqua",
      "percentage": 30.5,
      "category": "water",
      "notes": null
    },
    {
      "name": "Cocos Nucifera Oil",
      "percentage": 25.0,
      "category": "oil",
      "notes": "Saponifies to Sodium Cocoate"
    }
  ],
  "metadata": {
    "total_ingredients": 8,
    "calculation_method": "percentage_by_weight",
    "lye_type": "naoh",
    "superfat_percentage": 5.0
  }
}
```

## Format Options

### Get Specific Format Only

**Saponified INCI only**:
```bash
curl -X GET "https://api.mga-soap-calculator.com/api/v1/recipes/recipe-123-abc/inci-label?format=saponified_inci" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.labels.saponified_inci'

# Output: "Aqua, Sodium Cocoate, Sodium Olivate, Glycerin"
```

**Raw INCI only**:
```bash
curl -X GET "https://api.mga-soap-calculator.com/api/v1/recipes/recipe-123-abc/inci-label?format=raw_inci" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.labels.raw_inci'

# Output: "Aqua, Cocos Nucifera Oil, Olea Europaea Fruit Oil, Sodium Hydroxide, Glycerin"
```

**Common names only**:
```bash
curl -X GET "https://api.mga-soap-calculator.com/api/v1/recipes/recipe-123-abc/inci-label?format=common_names" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.labels.common_names'

# Output: "Water, Coconut Oil, Olive Oil, Sodium Hydroxide, Glycerin"
```

## Advanced Options

### Include Percentages in Label

```bash
curl -X GET "https://api.mga-soap-calculator.com/api/v1/recipes/recipe-123-abc/inci-label?include_percentages=true" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.labels.saponified_inci'

# Output: "Aqua (30.5%), Sodium Cocoate (28.1%), Sodium Olivate (22.4%), Glycerin (2.0%)"
```

### Line-by-Line Format

```bash
curl -X GET "https://api.mga-soap-calculator.com/api/v1/recipes/recipe-123-abc/inci-label?line_by_line=true" \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.labels.saponified_inci'

# Output:
# Aqua
# Sodium Cocoate
# Sodium Olivate
# Glycerin
```

### Combined Options

```bash
curl -X GET "https://api.mga-soap-calculator.com/api/v1/recipes/recipe-123-abc/inci-label?format=saponified_inci&include_percentages=true&line_by_line=true" \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.labels.saponified_inci'

# Output:
# Aqua (30.5%)
# Sodium Cocoate (28.1%)
# Sodium Olivate (22.4%)
# Glycerin (2.0%)
```

## Working with Ingredient Breakdown

### Extract Specific Categories

**Get all oils**:
```bash
curl -X GET "https://api.mga-soap-calculator.com/api/v1/recipes/recipe-123-abc/inci-label" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.ingredients_breakdown[] | select(.category == "oil")'
```

**Get ingredients above 5%**:
```bash
curl -X GET "https://api.mga-soap-calculator.com/api/v1/recipes/recipe-123-abc/inci-label" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.ingredients_breakdown[] | select(.percentage > 5.0)'
```

**Calculate total oil percentage**:
```bash
curl -X GET "https://api.mga-soap-calculator.com/api/v1/recipes/recipe-123-abc/inci-label" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '[.ingredients_breakdown[] | select(.category == "oil") | .percentage] | add'

# Output: 60.0
```

## Python Integration

### Using `httpx` (Async)

```python
import httpx
import asyncio

async def get_inci_label(recipe_id: str, token: str) -> dict:
    """
    Fetch INCI label for recipe (async)

    Args:
        recipe_id: Recipe identifier
        token: JWT access token

    Returns:
        INCI label response dictionary
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mga-soap-calculator.com/api/v1/recipes/{recipe_id}/inci-label",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()


async def main():
    token = "your-jwt-token"
    recipe_id = "recipe-123-abc"

    label_data = await get_inci_label(recipe_id, token)

    print("Saponified INCI Label:")
    print(label_data['labels']['saponified_inci'])

    print("\nIngredient Breakdown:")
    for ingredient in label_data['ingredients_breakdown']:
        print(f"  {ingredient['name']}: {ingredient['percentage']}%")


if __name__ == "__main__":
    asyncio.run(main())
```

### Using `requests` (Sync)

```python
import requests

def get_inci_label(recipe_id: str, token: str, format_type: str = "all") -> dict:
    """
    Fetch INCI label for recipe (sync)

    Args:
        recipe_id: Recipe identifier
        token: JWT access token
        format_type: Label format ("all", "raw_inci", "saponified_inci", "common_names")

    Returns:
        INCI label response dictionary
    """
    response = requests.get(
        f"https://api.mga-soap-calculator.com/api/v1/recipes/{recipe_id}/inci-label",
        headers={"Authorization": f"Bearer {token}"},
        params={"format": format_type}
    )
    response.raise_for_status()
    return response.json()


# Example usage
token = "your-jwt-token"
recipe_id = "recipe-123-abc"

# Get saponified INCI only
label_data = get_inci_label(recipe_id, token, format_type="saponified_inci")
print(label_data['labels']['saponified_inci'])

# Get all formats with percentages
label_data_full = get_inci_label(
    recipe_id,
    token,
    format_type="all"
)

# Copy-paste ready label
saponified_label = label_data_full['labels']['saponified_inci']
print(f"\nCopy this for product label:\n{saponified_label}")
```

## JavaScript/TypeScript Integration

### Using `fetch` API

```typescript
interface InciLabelResponse {
  recipe_id: string;
  recipe_name: string;
  generated_at: string;
  labels: {
    raw_inci?: string;
    saponified_inci?: string;
    common_names?: string;
  };
  ingredients_breakdown: Array<{
    name: string;
    percentage: number;
    category: string;
    notes: string | null;
  }>;
  metadata: {
    total_ingredients: number;
    calculation_method: string;
    lye_type: string;
    superfat_percentage: number;
    warnings?: string[];
  };
}

async function getInciLabel(
  recipeId: string,
  token: string,
  format: string = "all"
): Promise<InciLabelResponse> {
  const response = await fetch(
    `https://api.mga-soap-calculator.com/api/v1/recipes/${recipeId}/inci-label?format=${format}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error(`INCI label generation failed: ${response.statusText}`);
  }

  return response.json();
}

// Example usage
const token = "your-jwt-token";
const recipeId = "recipe-123-abc";

getInciLabel(recipeId, token, "saponified_inci")
  .then((data) => {
    console.log("Saponified INCI Label:");
    console.log(data.labels.saponified_inci);

    console.log("\nTop 5 Ingredients:");
    data.ingredients_breakdown.slice(0, 5).forEach((ingredient) => {
      console.log(`  ${ingredient.name}: ${ingredient.percentage}%`);
    });
  })
  .catch((error) => {
    console.error("Error fetching INCI label:", error);
  });
```

## Error Handling

### Common Errors

**401 Unauthorized**:
```bash
curl -X GET "https://api.mga-soap-calculator.com/api/v1/recipes/recipe-123-abc/inci-label" \
  # Missing Authorization header

# Response:
{
  "error": "unauthorized",
  "message": "Authentication required. Provide valid JWT token in Authorization header."
}
```

**404 Not Found**:
```bash
curl -X GET "https://api.mga-soap-calculator.com/api/v1/recipes/nonexistent/inci-label" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "error": "not_found",
  "message": "Recipe with ID 'nonexistent' not found or you do not have access to it."
}
```

**422 Validation Error**:
```bash
curl -X GET "https://api.mga-soap-calculator.com/api/v1/recipes/recipe-123-abc/inci-label?format=invalid" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "error": "validation_error",
  "message": "Invalid format parameter value",
  "details": {
    "field": "format",
    "provided": "invalid",
    "allowed": ["all", "raw_inci", "saponified_inci", "common_names"]
  }
}
```

### Error Handling in Python

```python
import httpx

async def get_inci_label_safe(recipe_id: str, token: str) -> dict | None:
    """
    Fetch INCI label with error handling

    Returns:
        Label data or None if error occurred
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.mga-soap-calculator.com/api/v1/recipes/{recipe_id}/inci-label",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(f"Recipe {recipe_id} not found")
        elif e.response.status_code == 401:
            print("Authentication failed - check token")
        else:
            print(f"HTTP error: {e.response.status_code}")
        return None

    except httpx.RequestError as e:
        print(f"Network error: {e}")
        return None
```

## Use Cases

### 1. Product Label Generation

**Scenario**: Generate copy-paste ready label for product packaging

```python
async def generate_product_label(recipe_id: str, token: str) -> str:
    """Generate saponified INCI label for product packaging"""
    label_data = await get_inci_label(recipe_id, token)

    # Use saponified format for final product label
    return label_data['labels']['saponified_inci']

# Usage
label = await generate_product_label("recipe-123-abc", token)
print(f"Product Label:\n{label}")

# Output: "Aqua, Sodium Cocoate, Sodium Olivate, Glycerin, Lavandula Angustifolia Oil"
```

### 2. Regulatory Compliance Verification

**Scenario**: Verify ingredients sorted by percentage (descending order)

```python
async def verify_sorting(recipe_id: str, token: str) -> bool:
    """Verify ingredients properly sorted by percentage"""
    label_data = await get_inci_label(recipe_id, token)

    # Check descending order
    percentages = [item['percentage'] for item in label_data['ingredients_breakdown']]
    is_sorted = all(percentages[i] >= percentages[i+1] for i in range(len(percentages)-1))

    return is_sorted

# Usage
is_compliant = await verify_sorting("recipe-123-abc", token)
print(f"Regulatory compliant sorting: {is_compliant}")
```

### 3. Multi-Format Label Sheet

**Scenario**: Generate label sheet with all three formats for internal documentation

```python
async def generate_label_sheet(recipe_id: str, token: str) -> str:
    """Generate formatted label sheet with all formats"""
    label_data = await get_inci_label(recipe_id, token)

    sheet = f"""
INCI Label Sheet
Recipe: {label_data['recipe_name']} ({label_data['recipe_id']})
Generated: {label_data['generated_at']}
Lye Type: {label_data['metadata']['lye_type'].upper()}
Superfat: {label_data['metadata']['superfat_percentage']}%

=== RAW INCI (Pre-Saponification) ===
{label_data['labels']['raw_inci']}

=== SAPONIFIED INCI (Post-Saponification) ===
{label_data['labels']['saponified_inci']}

=== COMMON NAMES (Consumer-Friendly) ===
{label_data['labels']['common_names']}

=== INGREDIENT BREAKDOWN ===
"""
    for ingredient in label_data['ingredients_breakdown']:
        notes = f" - {ingredient['notes']}" if ingredient['notes'] else ""
        sheet += f"{ingredient['name']}: {ingredient['percentage']}% ({ingredient['category']}){notes}\n"

    return sheet

# Usage
sheet = await generate_label_sheet("recipe-123-abc", token)
print(sheet)
```

## Performance Considerations

**Response Time**: <100ms p95 latency under normal load

**Best Practices**:
- Cache label data if recipe unchanged (check `generated_at` timestamp)
- Use specific format parameter when only one format needed
- Batch requests for multiple recipes using async/concurrent requests
- Set appropriate timeout (2-5 seconds recommended)

**Example with timeout**:
```python
async with httpx.AsyncClient(timeout=5.0) as client:
    response = await client.get(url, headers=headers)
```

## Rate Limiting

**Current Limits**: Per global API rate limits (check API documentation)

**Handling rate limits**:
```python
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
async def get_inci_label_with_retry(recipe_id: str, token: str) -> dict:
    """Fetch INCI label with automatic retry on rate limit"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mga-soap-calculator.com/api/v1/recipes/{recipe_id}/inci-label",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 429:  # Rate limit
            raise httpx.HTTPStatusError("Rate limited", request=None, response=response)

        response.raise_for_status()
        return response.json()
```

## Support and Documentation

**API Documentation**: https://api.mga-soap-calculator.com/docs (FastAPI auto-generated)

**OpenAPI Spec**: See `contracts/inci-label.yaml` for complete specification

**Issues**: Report via GitHub issues or contact MGA support

## Next Steps

1. **Test Integration**: Use development server (localhost:8000) for testing
2. **Error Handling**: Implement robust error handling for production use
3. **Caching**: Consider caching strategies for frequently accessed recipes
4. **UI Integration**: Build user-facing label generator UI using this API

## Changelog

**v1.0.0** (2025-11-05):
- Initial release
- Three label formats (raw, saponified, common names)
- Percentage-based sorting
- Detailed ingredient breakdown
- <100ms response time
