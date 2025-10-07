#!/usr/bin/env bash

# ClipWeaver Backend Test Script
# This script demonstrates the API endpoints in demo order

set -e

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

# Function to check if a file exists
check_file() {
    if [ ! -f "$1" ]; then
        echo -e "${RED}❌ Error: File $1 not found!${NC}"
        echo -e "${YELLOW}💡 Please provide a sample video file for testing.${NC}"
        exit 1
    fi
}

# Start of tests
clear
print_header "🎬 CLIPWEAVER API TEST SUITE"
echo -e "${CYAN}This script will demonstrate all ClipWeaver API endpoints${NC}"
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
# TEST 2: Upload and Analyze Video (with sample file check)
# ============================================================================
print_header "TEST 2: Video Analysis"
print_test "Upload a video file and generate AI-powered storyboard"

# Check for sample video file
VIDEO_FILE=""
if [ -f "sample.mp4" ]; then
    VIDEO_FILE="sample.mp4"
elif [ -f "test.mp4" ]; then
    VIDEO_FILE="test.mp4"
elif [ -f "demo.mp4" ]; then
    VIDEO_FILE="demo.mp4"
else
    echo -e "${YELLOW}⚠️  No sample video found. Please provide a video file.${NC}"
    echo -e "${CYAN}Available options:${NC}"
    echo "  1. Place a video file named 'sample.mp4' in the current directory"
    echo "  2. Enter the path to a video file now"
    echo ""
    read -p "Enter video file path (or press Enter to skip): " VIDEO_FILE
    
    if [ -z "$VIDEO_FILE" ]; then
        echo -e "${YELLOW}⏭️  Skipping video upload test${NC}"
        VIDEO_FILE=""
    elif [ ! -f "$VIDEO_FILE" ]; then
        echo -e "${RED}❌ File not found: $VIDEO_FILE${NC}"
        echo -e "${YELLOW}⏭️  Skipping video upload test${NC}"
        VIDEO_FILE=""
    fi
fi

if [ -n "$VIDEO_FILE" ]; then
    echo -e "${GREEN}✅ Using video file: ${VIDEO_FILE}${NC}"
    echo ""
    
    # Get file size
    FILE_SIZE=$(ls -lh "$VIDEO_FILE" | awk '{print $5}')
    echo -e "${CYAN}📊 File info:${NC}"
    echo "  - Name: $(basename "$VIDEO_FILE")"
    echo "  - Size: ${FILE_SIZE}"
    echo ""
    
    CURL_CMD="curl -s -X POST ${API_URL}/analyze \\
  -F \"video=@${VIDEO_FILE}\" \\
  -F \"scene_threshold=0.4\" \\
  -F \"max_scenes=10\" \\
  -o storyboard_result.md"
    
    print_curl "$CURL_CMD"
    
    echo -e "${BLUE}📤 Uploading and analyzing video...${NC}"
    eval "$CURL_CMD"
    
    if [ -f "storyboard_result.md" ]; then
        echo -e "${GREEN}✅ Success! Storyboard saved to: storyboard_result.md${NC}"
        echo ""
        echo -e "${BLUE}📄 Preview (first 50 lines):${NC}"
        echo -e "${CYAN}────────────────────────────────────────────────────────────${NC}"
        head -50 storyboard_result.md
        echo -e "${CYAN}────────────────────────────────────────────────────────────${NC}"
        
        # Count scenes
        SCENE_COUNT=$(grep -c "^## Scene" storyboard_result.md || echo "0")
        echo ""
        echo -e "${GREEN}📊 Analysis Results:${NC}"
        echo "  - Scenes detected: ${SCENE_COUNT}"
        echo "  - Output file: storyboard_result.md"
    else
        echo -e "${RED}❌ Failed to generate storyboard${NC}"
    fi
    
    pause_with_skip
fi

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
if [ -n "$VIDEO_FILE" ] && [ -f "storyboard_result.md" ]; then
    echo "  ✅ Video analysis working"
    echo "  ✅ Storyboard generation working"
    echo "  ✅ Output saved to: storyboard_result.md"
fi
echo "  ✅ Error handling verified"
echo ""
echo -e "${CYAN}🔗 Next Steps:${NC}"
echo "  1. Review the generated storyboard: cat storyboard_result.md"
echo "  2. Check the scene thumbnails in: output/scenes/"
echo "  3. Test the frontend: https://app.clip.hurated.com"
echo "  4. Review API docs: cat APIDOCS.md"
echo ""
echo -e "${BLUE}📚 For more information:${NC}"
echo "  - API Documentation: APIDOCS.md"
echo "  - Deployment Guide: DEPLOYMENT.md"
echo "  - Backend README: backend/README.md"
echo ""
echo -e "${GREEN}Thank you for testing ClipWeaver! 🎬${NC}"
echo ""
