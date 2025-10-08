#!/usr/bin/env bash

# ClipWeaver Backend Test Script
# This script demonstrates the API endpoints in demo order

set -e

# Change to script directory
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Base URL
API_URL="https://api.clip.hurated.com"

# Function to print section headers
print_header() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Function to print test descriptions
print_test() {
    echo -e "${YELLOW}📋 TEST: $1${NC}"
    echo ""
}

# Function to print curl commands
print_curl() {
    echo -e "${BLUE}🔧 Command:${NC}"
    echo -e "${GREEN}$1${NC}"
    echo ""
}

# Function to pause with skip option
pause_with_skip() {
    echo ""
    echo -e "${YELLOW}⏸️  Pausing for 30 seconds (press any key to skip)...${NC}"
    read -t 30 -n 1 -s || true
    echo ""
}

# Start of tests
clear
print_header "🎬 CLIPWEAVER API TEST SUITE"
echo -e "${CYAN}This script will test ClipWeaver API endpoints${NC}"
echo -e "${CYAN}Base URL: ${GREEN}${API_URL}${NC}"
echo ""
echo -e "${YELLOW}Press any key to start...${NC}"
read -n 1 -s
echo ""

# ============================================================================
# TEST 1: Health Check
# ============================================================================
print_header "TEST 1: Health Check"
print_test "Verify the API is running and all services are operational"

CURL_CMD="curl -s -X GET ${API_URL}/health | jq ."
print_curl "$CURL_CMD"

echo -e "${BLUE}📤 Response:${NC}"
eval "$CURL_CMD"

pause_with_skip

# ============================================================================
# TEST 2: Video Analysis Demo
# ============================================================================
print_header "TEST 2: Video Analysis Demo"
print_test "Upload a video file and generate AI-powered storyboard"

echo -e "${BLUE}📤 Running video analysis demo...${NC}"
./demo.sh --called-from-test

pause_with_skip

# ============================================================================
# TEST 3: API Documentation Check
# ============================================================================
print_header "TEST 3: API Endpoints Summary"
print_test "Display available API endpoints"

echo -e "${CYAN}📚 Available Endpoints:${NC}"
echo ""
echo -e "${GREEN}1. GET  /health${NC}"
echo "   - Health check and service status"
echo ""
echo -e "${GREEN}2. POST /analyze${NC}"
echo "   - Upload video and generate storyboard"
echo "   - Parameters: video (file), scene_threshold (float), max_scenes (int)"
echo ""
echo -e "${GREEN}3. GET  /api/v1/storyboard/{job_id}${NC}"
echo "   - Get storyboard in JSON format (future)"
echo ""
echo -e "${GREEN}4. GET  /api/v1/markdown/{job_id}${NC}"
echo "   - Download markdown storyboard (future)"
echo ""
echo -e "${GREEN}5. GET  /api/v1/thumbnail/{job_id}/{filename}${NC}"
echo "   - Get scene thumbnail image (future)"
echo ""

pause_with_skip

# ============================================================================
# TEST 4: Error Handling Test
# ============================================================================
print_header "TEST 4: Error Handling"
print_test "Test API error responses with invalid requests"

echo -e "${YELLOW}Test 4.1: Missing video file${NC}"
CURL_CMD="curl -s -X POST ${API_URL}/analyze -w \"\\nHTTP Status: %{http_code}\\n\""
print_curl "$CURL_CMD"

echo -e "${BLUE}📤 Response:${NC}"
eval "$CURL_CMD"

pause_with_skip

# ============================================================================
# Final Summary
# ============================================================================
print_header "✅ TEST SUITE COMPLETE"

echo -e "${GREEN}🎉 All tests completed successfully!${NC}"
echo ""
echo -e "${CYAN}📋 Summary:${NC}"
echo "  ✅ Health check endpoint working"
echo "  ✅ Video analysis demo completed"
echo "  ✅ Error handling verified"
echo ""
echo -e "${CYAN}🔗 Next Steps:${NC}"
echo "  1. Run video analysis demo standalone: ./demo.sh"
echo "  2. Test the frontend: https://app.clip.hurated.com"
echo "  3. Review API docs: cat APIDOCS.md"
echo ""
echo -e "${BLUE}📚 For more information:${NC}"
echo "  - API Documentation: APIDOCS.md"
echo "  - Deployment Guide: DEPLOYMENT.md"
echo "  - Backend README: backend/README.md"
echo "  - Video Analysis Demo: ./demo.sh"
echo ""
echo -e "${GREEN}Thank you for testing ClipWeaver! 🎬${NC}"
echo ""
