#!/usr/bin/env bash

# ClipWeaver Video Analysis Demo
# This script demonstrates the video analysis functionality
# Usage: ./demo.sh [json|markdown] [video_filename] [--called-from-test]

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

# Parse arguments
FORMAT="markdown"
VIDEO_FILE=""
CALLED_FROM_TEST=""

for arg in "$@"; do
    case $arg in
        json|JSON)
            FORMAT="json"
            ;;
        markdown|MARKDOWN)
            FORMAT="markdown"
            ;;
        --called-from-test)
            CALLED_FROM_TEST="--called-from-test"
            ;;
        *.mp4|*.mov|*.avi|*.webm)
            VIDEO_FILE="$arg"
            ;;
    esac
done

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
if [ "$CALLED_FROM_TEST" != "--called-from-test" ]; then
    clear
    print_header "🎬 CLIPWEAVER VIDEO ANALYSIS DEMO"
    echo -e "${CYAN}This demo will analyze a video and generate an AI-powered storyboard${NC}"
    echo -e "${CYAN}Format: ${GREEN}${FORMAT}${NC}"
    echo -e "${CYAN}Base URL: ${GREEN}${API_URL}${NC}"
    echo ""
fi

# Check for sample video file
if [ -n "$VIDEO_FILE" ]; then
    # Use provided video file
    if [ ! -f "$VIDEO_FILE" ]; then
        echo -e "${RED}❌ Video file not found: $VIDEO_FILE${NC}"
        exit 1
    fi
elif [ -f "sample.mp4" ]; then
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

# Build curl command based on format
if [ "$FORMAT" = "json" ]; then
    OUTPUT_FILE="storyboard_result.json"
    CURL_CMD="curl -s -X POST ${API_URL}/analyze \\
  -F \"video=@${VIDEO_FILE}\" \\
  -F \"format=json\" \\
  -F \"async=true\""
else
    OUTPUT_FILE="storyboard_result.md"
    CURL_CMD="curl -s -X POST ${API_URL}/analyze \\
  -F \"video=@${VIDEO_FILE}\" \\
  -F \"async=true\""
fi

print_curl "$CURL_CMD"

echo -e "${BLUE}📤 Uploading and starting async analysis...${NC}"
RESPONSE=$(eval "$CURL_CMD")

# Extract request ID from response
REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id // empty')

if [ -z "$REQUEST_ID" ]; then
    echo -e "${RED}❌ Failed to start analysis${NC}"
    echo "$RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ Analysis started! Request ID: ${REQUEST_ID}${NC}"
echo -e "${BLUE}📊 Monitoring progress...${NC}"
echo ""

# Poll status until complete
while true; do
    STATUS_RESPONSE=$(curl -s "${API_URL}/status/${REQUEST_ID}")
    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')
    PROGRESS=$(echo "$STATUS_RESPONSE" | jq -r '.progress // 0')
    
    # Show latest log message
    LATEST_LOG=$(echo "$STATUS_RESPONSE" | jq -r '.logs[-1].message // ""')
    if [ -n "$LATEST_LOG" ]; then
        echo -e "${CYAN}[${PROGRESS}%] ${LATEST_LOG}${NC}"
    fi
    
    if [ "$STATUS" = "completed" ]; then
        echo -e "${GREEN}✅ Analysis complete!${NC}"
        break
    elif [ "$STATUS" = "error" ]; then
        ERROR=$(echo "$STATUS_RESPONSE" | jq -r '.error // "Unknown error"')
        echo -e "${RED}❌ Analysis failed: ${ERROR}${NC}"
        exit 1
    fi
    
    sleep 2
done

echo ""
echo -e "${BLUE}📥 Downloading result...${NC}"

# Get final result
if [ "$FORMAT" = "json" ]; then
    curl -s "${API_URL}/result/${REQUEST_ID}" > "$OUTPUT_FILE"
else
    curl -s "${API_URL}/result/${REQUEST_ID}" -o "$OUTPUT_FILE"
fi

if [ -f "$OUTPUT_FILE" ]; then
    echo -e "${GREEN}✅ Success! Storyboard saved to: ${OUTPUT_FILE}${NC}"
    echo ""
    echo -e "${BLUE}📄 Preview:${NC}"
    echo -e "${CYAN}────────────────────────────────────────────────────────────${NC}"
    
    if [ "$FORMAT" = "json" ]; then
        # Pretty print JSON with jq if available, otherwise use cat
        if command -v jq >/dev/null 2>&1; then
            jq . "$OUTPUT_FILE"
        else
            cat "$OUTPUT_FILE"
        fi
    else
        head -50 "$OUTPUT_FILE"
    fi
    
    echo -e "${CYAN}────────────────────────────────────────────────────────────${NC}"
    
    # Count scenes
    if [ "$FORMAT" = "json" ]; then
        if command -v jq >/dev/null 2>&1; then
            SCENE_COUNT=$(jq '.total_scenes // 0' "$OUTPUT_FILE")
        else
            SCENE_COUNT=$(grep -o '"scene_number"' "$OUTPUT_FILE" | wc -l)
        fi
    else
        SCENE_COUNT=$(grep -c "^## Scene" "$OUTPUT_FILE" || echo "0")
    fi
    
    echo ""
    echo -e "${GREEN}📊 Analysis Results:${NC}"
    echo "  - Scenes detected: ${SCENE_COUNT}"
    echo "  - Output file: ${OUTPUT_FILE}"
    echo ""
    echo -e "${CYAN}🔗 Next Steps:${NC}"
    if [ "$FORMAT" = "json" ]; then
        echo "  1. Review JSON data: cat ${OUTPUT_FILE}"
        echo "  2. Parse with jq: jq '.scenes[] | .description' ${OUTPUT_FILE}"
    else
        echo "  1. Review full storyboard: cat ${OUTPUT_FILE}"
    fi
    echo "  2. Check scene thumbnails: ls output/scenes/"
    echo ""
else
    echo -e "${RED}❌ Failed to generate storyboard${NC}"
    exit 1
fi

if [ "$CALLED_FROM_TEST" != "--called-from-test" ]; then
    echo -e "${GREEN}Demo complete! 🎬${NC}"
fi
