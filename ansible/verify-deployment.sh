#!/bin/bash
# Deployment Verification Script
# Tests deployed mga-soap-calculator API on grimm-lin

set -e

echo "=========================================="
echo "MGA Soap Calculator - Deployment Verification"
echo "Target: grimm-lin:8000"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0
TOTAL=0

# Function to run a test
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"

    TOTAL=$((TOTAL + 1))
    echo -n "[$TOTAL] Testing $name... "

    # Make request and capture status
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}PASS${NC} (HTTP $status)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC} (HTTP $status, expected $expected_status)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Function to test JSON response
test_json() {
    local name="$1"
    local url="$2"
    local jq_filter="$3"
    local expected="$4"

    TOTAL=$((TOTAL + 1))
    echo -n "[$TOTAL] Testing $name... "

    # Make request and parse JSON
    result=$(curl -s "$url" | jq -r "$jq_filter" 2>/dev/null || echo "ERROR")

    if [ "$result" = "$expected" ]; then
        echo -e "${GREEN}PASS${NC} ($result)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC} (got: $result, expected: $expected)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Function to test SSH command
test_ssh_command() {
    local name="$1"
    local command="$2"
    local expected="$3"

    TOTAL=$((TOTAL + 1))
    echo -n "[$TOTAL] Testing $name... "

    # Execute SSH command
    result=$(ssh grimm-lin "$command" 2>&1 || echo "ERROR")

    if echo "$result" | grep -q "$expected"; then
        echo -e "${GREEN}PASS${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Output: $result"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "=== HTTP Endpoint Tests ==="
echo ""

# Test health endpoint
test_endpoint "Health Endpoint" "http://grimm-lin:8000/api/v1/health" 200
test_json "Health Status" "http://grimm-lin:8000/api/v1/health" ".status" "healthy"
test_json "Database Connection" "http://grimm-lin:8000/api/v1/health" ".database" "connected"

# Test data endpoints
test_endpoint "Oils Endpoint" "http://grimm-lin:8000/api/v1/oils" 200
test_endpoint "Additives Endpoint" "http://grimm-lin:8000/api/v1/additives" 200

# Test invalid endpoint
test_endpoint "Invalid Endpoint (404 expected)" "http://grimm-lin:8000/api/v1/invalid" 404

echo ""
echo "=== Service Status Tests ==="
echo ""

# Test systemd service
test_ssh_command "Systemd Service Running" \
    "systemctl --user is-active soap-calculator-api.service" \
    "active"

# Test container running
test_ssh_command "Container Running" \
    "podman ps --filter name=soap-api --format '{{.Status}}'" \
    "Up"

# Test migration status
test_ssh_command "Migration at HEAD" \
    "podman exec soap-api alembic current 2>&1" \
    "003 (head)"

echo ""
echo "=== Image Verification ==="
echo ""

# Test image exists
test_ssh_command "Image Loaded" \
    "podman images localhost/mga-soap-calculator:latest --format '{{.Repository}}'" \
    "mga-soap-calculator"

# Test rollback image exists
test_ssh_command "Rollback Image Available" \
    "podman images localhost/mga-soap-calculator:rollback --format '{{.Repository}}'" \
    "mga-soap-calculator"

echo ""
echo "=========================================="
echo "Test Results"
echo "=========================================="
echo -e "Total:  $TOTAL"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Deployment verification: SUCCESS"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Deployment verification: PARTIAL"
    echo "Review failures above for details"
    exit 1
fi
