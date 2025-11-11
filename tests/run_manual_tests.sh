#!/bin/bash
# Manual Testing Script for Phase 2 Integration

set -e

echo "=========================================="
echo "Phase 2 Integration Manual Testing"
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
SKIPPED=0

# Function to run test
run_test() {
    local test_name="$1"
    local command="$2"
    local expected="$3"
    
    echo -n "Testing: $test_name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

# Function to check if API is running
check_api() {
    curl -s http://localhost:38153/ > /dev/null 2>&1
}

# Change to backend directory
cd "$(dirname "$0")/../backend" || exit 1

echo "1. Testing CLI Plugin Commands"
echo "-------------------------------"

run_test "Plugin List" "python3 cli.py plugin list" "Lists plugins"
run_test "Plugin Info" "python3 cli.py plugin info emis" "Shows plugin info"
run_test "Plugin Enable" "python3 cli.py plugin enable emis" "Enables plugin"
run_test "Plugin Disable" "python3 cli.py plugin disable emis" "Disables plugin"
python3 cli.py plugin enable emis > /dev/null 2>&1  # Re-enable

echo ""
echo "2. Testing Updated CLI Commands"
echo "--------------------------------"

run_test "List Shows Plugins" "python3 cli.py list | grep -i plugin" "Shows plugins section"
run_test "Config Shows Plugin" "python3 cli.py config emis | grep -i plugin" "Shows plugin config"
run_test "Check Credentials" "python3 cli.py check emis" "Shows credentials"

echo ""
echo "3. Testing API Endpoints"
echo "-------------------------"

if check_api; then
    run_test "GET /plugins" "curl -s http://localhost:38153/plugins | grep -q plugins" "Returns plugins"
    run_test "GET /plugins/emis" "curl -s http://localhost:38153/plugins/emis | grep -q emis" "Returns plugin info"
    run_test "POST /plugins/emis/enable" "curl -s -X POST http://localhost:38153/plugins/emis/enable | grep -q success" "Enables plugin"
    run_test "POST /plugins/emis/disable" "curl -s -X POST http://localhost:38153/plugins/emis/disable | grep -q success" "Disables plugin"
    curl -s -X POST http://localhost:38153/plugins/emis/enable > /dev/null 2>&1  # Re-enable
    run_test "GET /sites" "curl -s http://localhost:38153/sites | grep -q sites" "Returns sites"
else
    echo -e "${YELLOW}⚠ API server not running, skipping API tests${NC}"
    ((SKIPPED+=5))
fi

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed${NC}"
    exit 1
fi

