#!/bin/bash
# Test runner script for Quid MCP

set -e

echo "🧪 Quid MCP Test Runner"
echo "======================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not found${NC}"
    echo "Install with: pip install pytest pytest-asyncio pytest-cov"
    exit 1
fi

# Parse arguments
TEST_TYPE="${1:-all}"
VERBOSE="${2:-}"

case "$TEST_TYPE" in
    unit)
        echo -e "${YELLOW}Running unit tests...${NC}"
        pytest tests/unit/ $VERBOSE
        ;;
    integration)
        echo -e "${YELLOW}Running integration tests...${NC}"
        pytest tests/integration/ -m integration $VERBOSE
        ;;
    e2e)
        echo -e "${YELLOW}Running end-to-end tests...${NC}"
        pytest tests/e2e/ -m e2e $VERBOSE
        ;;
    coverage)
        echo -e "${YELLOW}Running tests with coverage...${NC}"
        pytest --cov=backend --cov-report=html --cov-report=term tests/
        echo ""
        echo -e "${GREEN}✅ Coverage report generated: htmlcov/index.html${NC}"
        ;;
    quick)
        echo -e "${YELLOW}Running quick tests (unit only, no slow)...${NC}"
        pytest tests/unit/ -m "not slow" $VERBOSE
        ;;
    all)
        echo -e "${YELLOW}Running all tests...${NC}"
        pytest tests/ $VERBOSE
        ;;
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: ./run_tests.sh [type] [verbose]"
        echo ""
        echo "Types:"
        echo "  all          - Run all tests (default)"
        echo "  unit         - Run unit tests only"
        echo "  integration  - Run integration tests only"
        echo "  e2e          - Run end-to-end tests only"
        echo "  coverage     - Run with coverage report"
        echo "  quick        - Run quick tests (unit, no slow)"
        echo ""
        echo "Verbose flag: -v or -vv"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh                  # All tests"
        echo "  ./run_tests.sh unit             # Unit tests only"
        echo "  ./run_tests.sh unit -v          # Unit tests, verbose"
        echo "  ./run_tests.sh coverage         # With coverage"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo ""
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
