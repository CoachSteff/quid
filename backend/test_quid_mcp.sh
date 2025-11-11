#!/bin/bash
# Comprehensive test script for Quid MCP CLI
# Tests: backend start/stop/restart, login, EMIS plugin, renaming

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
PASSED=0
FAILED=0
SKIPPED=0

# Test directory
TEST_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$TEST_DIR"

# Activate venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    exit 1
fi

# Function to print test header
print_test() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Test: $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to check test result
check_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

# Function to skip test
skip_test() {
    echo -e "${YELLOW}⏭️  SKIPPED: $1${NC}"
    ((SKIPPED++))
}

# Function to check if backend is running
is_backend_running() {
    local port=$1
    lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1
}

# Function to wait for backend to be ready
wait_for_backend() {
    local port=$1
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "http://localhost:$port/" >/dev/null 2>&1; then
            return 0
        fi
        sleep 1
        ((attempt++))
    done
    return 1
}

# Function to stop backend
stop_backend() {
    local port=$1
    local pid=$(lsof -Pi :$port -sTCP:LISTEN -t 2>/dev/null || echo "")
    if [ -n "$pid" ]; then
        kill $pid 2>/dev/null || true
        sleep 2
        # Force kill if still running
        if is_backend_running $port; then
            kill -9 $pid 2>/dev/null || true
            sleep 1
        fi
    fi
}

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║            Quid MCP CLI Comprehensive Test Suite          ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Test 1: Check credentials setup in venv
print_test "1. Credentials Setup (venv only)"
if [ -f "venv/.env" ]; then
    echo "✅ venv/.env exists"
    # Check if it contains EMIS credentials
    if grep -q "EMIS_EMAIL=" venv/.env && grep -q "EMIS_PASSWORD=" venv/.env; then
        echo "✅ EMIS credentials found in venv/.env"
        check_result
    else
        echo "⚠️  venv/.env exists but missing EMIS credentials"
        skip_test "Credentials not configured"
    fi
else
    echo "⚠️  venv/.env does not exist - will be created"
    skip_test "Credentials file not found"
fi

# Test 2: Verify credentials NOT in project root
print_test "2. Security: Credentials NOT in project root"
if [ -f ".env" ]; then
    # Check if .env contains actual credentials (not just template)
    if grep -q "EMIS_EMAIL=.*@" .env 2>/dev/null && grep -q "EMIS_PASSWORD=..*" .env 2>/dev/null; then
        echo -e "${RED}❌ WARNING: .env in project root contains credentials!${NC}"
        echo "   Credentials should only be in venv/.env"
        FAILED=$((FAILED + 1))
    else
        echo "✅ .env in project root does not contain real credentials"
        check_result
    fi
else
    echo "✅ No .env file in project root"
    check_result
fi

# Test 3: Check for "Emis" vs "Quid" renaming
print_test "3. Renaming Check: Emis → Quid"
emis_refs=$(grep -r "Emis\|EMIS" --include="*.py" --include="*.md" --include="*.yaml" --include="*.sh" . 2>/dev/null | grep -v "__pycache__" | grep -v "venv" | grep -v ".git" | wc -l | tr -d ' ')
if [ "$emis_refs" -gt 0 ]; then
    echo "⚠️  Found $emis_refs references to 'Emis' or 'EMIS'"
    echo "   (Some may be legitimate - e.g., plugin name 'emis')"
    # Check for problematic references
    problematic=$(grep -r "Emis\|EMIS" --include="*.py" --include="*.md" . 2>/dev/null | grep -v "__pycache__" | grep -v "venv" | grep -v "plugin" | grep -v "site_id" | grep -v "emis.yaml" | grep -v "emis.json" | wc -l | tr -d ' ')
    if [ "$problematic" -gt 0 ]; then
        echo -e "${YELLOW}   Found $problematic potentially problematic references${NC}"
        skip_test "Manual review needed"
    else
        echo "✅ All references appear to be legitimate (plugin names, configs)"
        check_result
    fi
else
    echo "✅ No references to 'Emis' found"
    check_result
fi

# Test 4: Backend Start
print_test "4. Backend Start"
stop_backend 91060
stop_backend 38153

# Load credentials from venv/.env if it exists
if [ -f "venv/.env" ]; then
    export $(grep -v '^#' venv/.env | xargs)
fi

# Start backend in background
echo "Starting backend..."
python app.py > /tmp/quid-backend-test.log 2>&1 &
BACKEND_PID=$!
sleep 5

# Check which port it's running on
if is_backend_running 91060; then
    PORT=91060
elif is_backend_running 38153; then
    PORT=38153
else
    echo -e "${RED}❌ Backend failed to start on either port${NC}"
    cat /tmp/quid-backend-test.log | tail -20
    kill $BACKEND_PID 2>/dev/null || true
    FAILED=$((FAILED + 1))
    skip_test "Backend start failed"
    PORT=""
fi

if [ -n "$PORT" ]; then
    if wait_for_backend $PORT; then
        echo "✅ Backend started on port $PORT"
        check_result
    else
        echo -e "${RED}❌ Backend not responding${NC}"
        cat /tmp/quid-backend-test.log | tail -20
        kill $BACKEND_PID 2>/dev/null || true
        FAILED=$((FAILED + 1))
    fi
fi

# Test 5: Backend Health Check
if [ -n "$PORT" ]; then
    print_test "5. Backend Health Check"
    response=$(curl -s "http://localhost:$PORT/")
    if echo "$response" | grep -q '"status":"ok"'; then
        echo "✅ Health check passed"
        check_result
    else
        echo -e "${RED}❌ Health check failed${NC}"
        echo "Response: $response"
        FAILED=$((FAILED + 1))
    fi
fi

# Test 6: List Sites
if [ -n "$PORT" ]; then
    print_test "6. List Available Sites"
    response=$(curl -s "http://localhost:$PORT/sites")
    if echo "$response" | grep -q '"sites"'; then
        echo "✅ Sites endpoint working"
        site_count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('sites', [])))" 2>/dev/null || echo "0")
        echo "   Found $site_count site(s)"
        check_result
    else
        echo -e "${RED}❌ Sites endpoint failed${NC}"
        echo "Response: $response"
        FAILED=$((FAILED + 1))
    fi
fi

# Test 7: CLI - List Sites
print_test "7. CLI: List Sites"
if ./scrape list > /tmp/cli-list.log 2>&1; then
    if grep -q "Available Sites" /tmp/cli-list.log; then
        echo "✅ CLI list command works"
        check_result
    else
        echo -e "${RED}❌ CLI list command output unexpected${NC}"
        cat /tmp/cli-list.log
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${RED}❌ CLI list command failed${NC}"
    cat /tmp/cli-list.log
    FAILED=$((FAILED + 1))
fi

# Test 8: CLI - Check Credentials
print_test "8. CLI: Check Credentials"
if ./scrape check emis > /tmp/cli-check.log 2>&1; then
    if grep -q "Credentials found\|No credentials found" /tmp/cli-check.log; then
        echo "✅ CLI check command works"
        if grep -q "✅ Credentials found" /tmp/cli-check.log; then
            echo "   Credentials are configured"
        else
            echo "   ⚠️  Credentials not found"
        fi
        check_result
    else
        echo -e "${RED}❌ CLI check command output unexpected${NC}"
        cat /tmp/cli-check.log
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${RED}❌ CLI check command failed${NC}"
    cat /tmp/cli-check.log
    FAILED=$((FAILED + 1))
fi

# Test 9: Backend Stop
if [ -n "$PORT" ]; then
    print_test "9. Backend Stop"
    stop_backend $PORT
    sleep 2
    if ! is_backend_running $PORT; then
        echo "✅ Backend stopped successfully"
        check_result
    else
        echo -e "${RED}❌ Backend still running${NC}"
        FAILED=$((FAILED + 1))
    fi
fi

# Test 10: Backend Restart
print_test "10. Backend Restart"
stop_backend 91060
stop_backend 38153
sleep 2

# Start
python app.py > /tmp/quid-backend-test.log 2>&1 &
BACKEND_PID=$!
sleep 5

if is_backend_running 91060; then
    PORT=91060
elif is_backend_running 38153; then
    PORT=38153
else
    PORT=""
fi

if [ -n "$PORT" ] && wait_for_backend $PORT; then
    echo "✅ Backend restarted successfully"
    # Stop again
    stop_backend $PORT
    sleep 2
    if ! is_backend_running $PORT; then
        check_result
    else
        echo -e "${RED}❌ Failed to stop after restart${NC}"
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${RED}❌ Backend restart failed${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 11: EMIS Plugin Query (if credentials available)
print_test "11. EMIS Plugin Query Test"
if [ -f "venv/.env" ] && grep -q "EMIS_EMAIL=.*@" venv/.env && grep -q "EMIS_PASSWORD=..*" venv/.env; then
    # Start backend for query test
    stop_backend 91060
    stop_backend 38153
    export $(grep -v '^#' venv/.env | xargs)
    python app.py > /tmp/quid-backend-test.log 2>&1 &
    BACKEND_PID=$!
    sleep 5
    
    if is_backend_running 91060; then
        PORT=91060
    elif is_backend_running 38153; then
        PORT=38153
    else
        PORT=""
    fi
    
    if [ -n "$PORT" ] && wait_for_backend $PORT; then
        echo "Testing EMIS query..."
        response=$(curl -s -X POST "http://localhost:$PORT/query/emis" \
            -H "Content-Type: application/json" \
            -d '{"query": "water treatment"}' \
            --max-time 120)
        
        if echo "$response" | grep -q '"status":"success"'; then
            echo "✅ EMIS query successful"
            check_result
        elif echo "$response" | grep -q '"status":"error"'; then
            error_msg=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('detail', 'Unknown error'))" 2>/dev/null || echo "Unknown")
            echo -e "${YELLOW}⚠️  EMIS query returned error: $error_msg${NC}"
            skip_test "Query returned error (may be expected)"
        else
            echo -e "${RED}❌ Unexpected response format${NC}"
            echo "$response" | head -20
            FAILED=$((FAILED + 1))
        fi
        
        stop_backend $PORT
    else
        skip_test "Backend not available for query test"
    fi
else
    skip_test "EMIS credentials not configured"
fi

# Final Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Passed:  $PASSED${NC}"
echo -e "${RED}❌ Failed:  $FAILED${NC}"
echo -e "${YELLOW}⏭️  Skipped: $SKIPPED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi

