#!/usr/bin/env bash

# ClipWeaver Video Analysis Demo
# This script demonstrates the video analysis functionality

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

# Function to print curl commands
print_curl() {
    echo -e "${BLUE}🔧 Command:${NC}"
    echo -e "${GREEN}$1${NC}"
    echo ""
}

# Start demo
if [ "$1" != "--called-from-test" ]; then
    clear
    print_header "🎬 CLIPWEAVER VIDEO ANALYSIS DEMO"
    echo -e "${CYAN}This demo will analyze a video and generate an AI-powered storyboard${NC}"
    echo -e "${CYAN}Base URL: ${GREEN}${API_URL}${NC}"
    echo ""
fi

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
    read -p "Enter video file path: " VIDEO_FILE
    
    if [ -z "$VIDEO_FILE" ] || [ ! -f "$VIDEO_FILE" ]; then
        echo -e "${RED}❌ File not found or not provided${NC}"
        exit 1
    fi
fi

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
  -o storyboard_result.md"

print_curl "$CURL_CMD"

echo -e "${BLUE}📤 Uploading and analyzing video...${NC}"
eval "$CURL_CMD"

if [ -f "storyboard_result.md" ]; then
    echo -e "${GREEN}✅ Success! Storyboard saved to: storyboard_result.md${NC}"
    echo ""
    echo -e "${BLUE}📄 Preview:${NC}"
    echo -e "${CYAN}────────────────────────────────────────────────────────────${NC}"
    head -50 storyboard_result.md
    echo -e "${CYAN}────────────────────────────────────────────────────────────${NC}"
    
    # Count scenes
    SCENE_COUNT=$(grep -c "^## Scene" storyboard_result.md || echo "0")
    echo ""
    echo -e "${GREEN}📊 Analysis Results:${NC}"
    echo "  - Scenes detected: ${SCENE_COUNT}"
    echo "  - Output file: storyboard_result.md"
    echo ""
    echo -e "${CYAN}🔗 Next Steps:${NC}"
    echo "  1. Review full storyboard: cat storyboard_result.md"
    echo "  2. Check scene thumbnails: ls output/scenes/"
    echo ""
else
    echo -e "${RED}❌ Failed to generate storyboard${NC}"
    exit 1
fi

if [ "$1" != "--called-from-test" ]; then
    echo -e "${GREEN}Demo complete! 🎬${NC}"
fi
