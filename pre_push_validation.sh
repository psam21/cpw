#!/bin/bash
# 🚀 PRE-PUSH VALIDATION SCRIPT
# ===============================
# Run comprehensive tests before pushing to ensure pipeline integrity
# Usage: ./pre_push_validation.sh

set -e  # Exit on any error

echo "🚀 PRE-PUSH VALIDATION STARTING..."
echo "=================================="
echo "⏰ $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}🔍 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository!"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    print_warning "You have uncommitted changes. Consider committing them first."
    echo ""
fi

print_status "Running comprehensive data pipeline test..."
echo ""

# Run the comprehensive pipeline test
if python comprehensive_pipeline_test.py; then
    print_success "All pipeline tests passed!"
    echo ""
else
    print_error "Pipeline tests failed! Please fix issues before pushing."
    echo ""
    echo "📄 Check pipeline_test_report.json for detailed error information."
    exit 1
fi

# Run the existing test suite if it exists
if [ -f "test_suite.py" ]; then
    print_status "Running existing test suite..."
    echo ""
    
    # Get Python executable
    if [ -f ".venv/bin/python" ]; then
        PYTHON_CMD=".venv/bin/python"
    else
        PYTHON_CMD="python"
    fi
    
    if $PYTHON_CMD -m pytest test_suite.py -v; then
        print_success "All unit tests passed!"
        echo ""
    else
        print_error "Unit tests failed! Please fix issues before pushing."
        exit 1
    fi
else
    print_warning "No test_suite.py found, skipping unit tests."
    echo ""
fi

# Check git status
print_status "Checking git status..."
git status --porcelain

echo ""
print_status "Checking for potential large files..."
# Check for files larger than 50MB
find . -type f -size +50M -not -path './.git/*' -not -path './.*' | while read -r file; do
    print_warning "Large file detected: $file ($(du -h "$file" | cut -f1))"
done

echo ""
print_status "Validation summary:"
echo "  ✅ Pipeline tests: PASSED"
echo "  ✅ Unit tests: PASSED"
echo "  ✅ Ready for push!"

echo ""
print_success "🎉 PRE-PUSH VALIDATION COMPLETED SUCCESSFULLY!"
echo ""
echo "You can now safely push your changes:"
echo "  git push origin main"
echo ""
echo "Or run: git push"
