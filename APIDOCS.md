# 🎬 ClipWeaver API Documentation

> **Base URL:** `https://api.clip.hurated.com`  
> **Version:** 1.0.0  
> **Protocol:** REST/HTTP

---

## 📋 Overview

ClipWeaver API provides video scene analysis and storyboard generation using AI-powered scene detection and description. Upload a video, and receive a structured storyboard with scene thumbnails and AI-generated descriptions in either Markdown or JSON format.

---

## 🔐 Authentication

Currently, the API does not require authentication for basic usage. Rate limiting may apply in production.

---

## 📡 Endpoints

### 1. **Analyze Video**

**POST** `/analyze`

Upload a video file to analyze scenes and generate a storyboard.

#### Request

**Headers:**
```
Content-Type: multipart/form-data
```

**Body (Form Data):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `video` | File | Yes | Video file (mp4, mov, avi, webm). Max size: 500MB |
| `scene_threshold` | Float | No | Scene detection sensitivity (0.1-0.9). Default: 0.06 |
| `max_scenes` | Integer | No | Maximum scenes to extract. Default: 10 |
| `format` | String | No | Response format: `markdown` (default) or `json` |
| `async` | Boolean | No | Enable async processing: `true` or `false` (default) |

**Example cURL (Markdown):**
```bash
curl -X POST https://api.clip.hurated.com/analyze \
  -F "video=@sample.mp4" \
  -F "scene_threshold=0.06" \
  -F "max_scenes=10"
```

**Example cURL (Async JSON):**
```bash
curl -X POST https://api.clip.hurated.com/analyze \
  -F "video=@sample.mp4" \
  -F "scene_threshold=0.06" \
  -F "max_scenes=10" \
  -F "format=json" \
  -F "async=true"
```

#### Response

**Synchronous Processing (Default):**

**Markdown Format:** Returns a downloadable `.md` file with the storyboard.

**JSON Format:**
```json
{
  "status": "success",
  "request_id": "1759906169_127_0_0_1_5242",
  "video_info": {
    "filename": "demo.mp4",
    "size_mb": 7.91
  },
  "scenes": [
    {
      "scene_number": 1,
      "timeframe": {
        "start": 0.0,
        "end": 8.0,
        "duration": 8.0
      },
      "screenshots": [
        {
          "position": "beginning",
          "timestamp": 0.5,
          "url": "https://api.clip.hurated.com/output/1759906169_127_0_0_1_5242/scenes/scene_001_beginning.png"
        },
        {
          "position": "middle",
          "timestamp": 4.0,
          "url": "https://api.clip.hurated.com/output/1759906169_127_0_0_1_5242/scenes/scene_001_middle.png"
        },
        {
          "position": "end",
          "timestamp": 7.5,
          "url": "https://api.clip.hurated.com/output/1759906169_127_0_0_1_5242/scenes/scene_001_end.png"
        }
      ],
      "description": "AI-generated scene description based on all three screenshots..."
    }
  ],
  "markdown_url": "https://api.clip.hurated.com/output/1759906169_127_0_0_1_5242/storyboard.md",
  "total_scenes": 3
}
```

**Asynchronous Processing (`async=true`):**

**Accepted (202):**
```json
{
  "status": "accepted",
  "request_id": "1759906130_127_0_0_1_2350",
  "message": "Video processing started. Use /status/{request_id} to check progress."
}
```

**Error (400 Bad Request):**
```json
{
  "status": "error",
  "error": "Invalid video format. Supported formats: mp4, mov, avi, webm"
}
```

---

### 2. **Check Processing Status**

**GET** `/status/{request_id}`

Check the status and progress of an async video analysis request.

#### Request

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `request_id` | String | Request ID from async analyze response |

**Example:**
```bash
curl https://api.clip.hurated.com/status/1759906130_127_0_0_1_2350
```

#### Response

**Processing (200 OK):**
```json
{
  "status": "processing",
  "progress": 65,
  "logs": [
    {
      "timestamp": "2025-10-08T06:30:59.256330",
      "level": "INFO",
      "message": "📹 Video uploaded: demo.mp4 (7.91 MB)"
    },
    {
      "timestamp": "2025-10-08T06:31:07.343739",
      "level": "INFO", 
      "message": "✅ Scene extraction complete: 9 scenes detected"
    },
    {
      "timestamp": "2025-10-08T06:31:07.343796",
      "level": "INFO",
      "message": "🤖 Starting AI description generation..."
    }
  ],
  "total_logs": 8
}
```

**Completed (200 OK):**
```json
{
  "status": "completed",
  "progress": 100,
  "result": {
    "status": "success",
    "request_id": "1759905059_127_0_0_1_8539",
    "scenes": [...],
    "total_scenes": 3
  },
  "logs": [...],
  "total_logs": 12
}
```

**Error (200 OK):**
```json
{
  "status": "error",
  "error": "Scene detection failed: Invalid video format",
  "logs": [...],
  "total_logs": 3
}
```

---

### 3. **Get Processing Result**

**GET** `/result/{request_id}`

Retrieve the final result of a completed async video analysis.

#### Request

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `request_id` | String | Request ID from async analyze response |

**Example:**
```bash
curl https://api.clip.hurated.com/result/1759906130_127_0_0_1_2350
```

#### Response

**Success (200 OK):**
- **JSON Format**: Returns the complete analysis result as JSON
- **Markdown Format**: Returns the storyboard file for download

**Error (400 Bad Request):**
```json
{
  "status": "error",
  "error": "Request not completed. Current status: processing"
}
```

---

### 4. **Health Check**

**GET** `/health`

Check API service status.

#### Response

**Success (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "scene_detection": "operational",
    "ai_description": "operational",
    "storage": "operational"
  }
}
```

---

### 3. **Serve Output Files**

**GET** `/output/{filename}`

Retrieve generated storyboard files and scene thumbnails.

#### Request

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | String | File path (e.g., `storyboard.md`, `scenes/scene_001_middle.png`) |

**Examples:**
```bash
# Get storyboard markdown (use actual request_id from your analysis)
curl https://api.clip.hurated.com/output/1759906130_127_0_0_1_2350/storyboard.md

# Get scene thumbnail (use actual request_id from your analysis)
curl https://api.clip.hurated.com/output/1759906130_127_0_0_1_2350/scenes/scene_001_beginning.png
```

---

## 📊 Data Models

### Scene Object (JSON Format)
```typescript
interface Scene {
  scene_number: number;
  timeframe: {
    start: number;    // Start time in seconds
    end: number;      // End time in seconds
    duration: number; // Duration in seconds
  };
  screenshots: Array<{
    position: "beginning" | "middle" | "end";
    timestamp: number; // Exact timestamp in seconds
    url: string;      // Full URL to screenshot
  }>;
  description: string; // AI-generated description
}
```

### JSON Response
```typescript
interface AnalyzeResponse {
  status: "success" | "error";
  video_info: {
    filename: string;
    size_mb: number;
    processing_time: number;
  };
  scenes: Scene[];
  markdown_url: string;
  total_scenes: number;
}
```

---

## ⚠️ Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid parameters or file format |
| 413 | Payload Too Large | Video file exceeds 500MB |
| 415 | Unsupported Media Type | Invalid video format |
| 500 | Internal Server Error | Server processing error |

---

## 💻 Client Integration Examples

### JavaScript/TypeScript

```typescript
// Analyze video and get JSON response (synchronous)
async function analyzeVideoSync(videoFile: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('video', videoFile);
  formData.append('format', 'json');
  formData.append('scene_threshold', '0.06');
  formData.append('max_scenes', '10');
  
  const response = await fetch('https://api.clip.hurated.com/analyze', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// Analyze video asynchronously with progress monitoring
async function analyzeVideoAsync(videoFile: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('video', videoFile);
  formData.append('format', 'json');
  formData.append('async', 'true');
  
  // Start processing
  const startResponse = await fetch('https://api.clip.hurated.com/analyze', {
    method: 'POST',
    body: formData
  });
  
  const { request_id } = await startResponse.json();
  
  // Poll for completion
  while (true) {
    const statusResponse = await fetch(`https://api.clip.hurated.com/status/${request_id}`);
    const status = await statusResponse.json();
    
    if (status.status === 'completed') {
      const resultResponse = await fetch(`https://api.clip.hurated.com/result/${request_id}`);
      return await resultResponse.json();
    } else if (status.status === 'error') {
      throw new Error(status.error);
    }
    
    // Show progress
    console.log(`Progress: ${status.progress}% - ${status.logs[status.logs.length - 1]?.message}`);
    
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}

// Download markdown storyboard
async function downloadMarkdown(videoFile: File): Promise<Blob> {
  const formData = new FormData();
  formData.append('video', videoFile);
  // format defaults to 'markdown'
  
  const response = await fetch('https://api.clip.hurated.com/analyze', {
    method: 'POST',
    body: formData
  });
  
  return await response.blob();
}

// Usage example
const result = await analyzeVideoSync(file);
console.log(`Found ${result.total_scenes} scenes`);
result.scenes.forEach(scene => {
  console.log(`Scene ${scene.scene_number}: ${scene.timeframe.start}s-${scene.timeframe.end}s`);
  console.log(`Description: ${scene.description}`);
});
```

### Python

```python
import requests
import time

def analyze_video_sync(video_path):
    """Get JSON response synchronously"""
    url = "https://api.clip.hurated.com/analyze"
    
    with open(video_path, 'rb') as f:
        files = {'video': f}
        data = {
            'format': 'json',
            'scene_threshold': 0.06,
            'max_scenes': 10
        }
        
        response = requests.post(url, files=files, data=data)
        return response.json()

def analyze_video_async(video_path):
    """Analyze video asynchronously with progress monitoring"""
    url = "https://api.clip.hurated.com/analyze"
    
    # Start processing
    with open(video_path, 'rb') as f:
        files = {'video': f}
        data = {
            'format': 'json',
            'async': 'true',
            'scene_threshold': 0.06,
            'max_scenes': 10
        }
        
        response = requests.post(url, files=files, data=data)
        result = response.json()
        request_id = result['request_id']
    
    # Poll for completion
    while True:
        status_response = requests.get(f"https://api.clip.hurated.com/status/{request_id}")
        status = status_response.json()
        
        if status['status'] == 'completed':
            result_response = requests.get(f"https://api.clip.hurated.com/result/{request_id}")
            return result_response.json()
        elif status['status'] == 'error':
            raise Exception(status['error'])
        
        # Show progress
        latest_log = status['logs'][-1]['message'] if status['logs'] else ''
        print(f"Progress: {status['progress']}% - {latest_log}")
        
        time.sleep(2)

def download_markdown(video_path, output_path):
    """Download markdown storyboard"""
    url = "https://api.clip.hurated.com/analyze"
    
    with open(video_path, 'rb') as f:
        files = {'video': f}
        data = {'scene_threshold': 0.06}  # format defaults to markdown
        
        response = requests.post(url, files=files, data=data)
        
        with open(output_path, 'wb') as out:
            out.write(response.content)

# Usage
json_result = analyze_video_sync('sample.mp4')
print(f"Request ID: {json_result['request_id']}")
print(f"Total scenes: {json_result['total_scenes']}")

for scene in json_result['scenes']:
    print(f"Scene {scene['scene_number']}: {scene['timeframe']['start']}s-{scene['timeframe']['end']}s")
    print(f"Screenshots: {len(scene['screenshots'])}")
```

---

## 🌐 CORS

CORS is configured with dynamic origin checking for security. Allowed origins:

- `https://bolt.new` - Bolt.new main domain
- `https://*.bolt.new` - All Bolt.new subdomains
- `https://*.webcontainer-api.io` - WebContainer preview URLs
- `http://localhost:*` - Local development (any port)
- `https://clips.hurated.com` - Production deployment

**CORS Headers:**
- `Access-Control-Allow-Origin`: Dynamic based on request origin
- `Access-Control-Allow-Methods`: GET, POST, PUT, DELETE, OPTIONS
- `Access-Control-Allow-Headers`: Content-Type, Authorization, X-Client-Info, Apikey
- `Access-Control-Max-Age`: 86400 (24 hours)

**Preflight Requests:**
- OPTIONS requests are handled automatically
- Returns 200 status with appropriate CORS headers
- Unauthorized origins receive responses without CORS headers

---

## 📝 Changelog

### v1.0.0 (2025-10-08)
- Initial API release
- Scene detection with ffmpeg and intelligent fallbacks
- Azure OpenAI GPT-4 vision integration for multi-frame analysis
- Dual format support: Markdown file download and JSON response
- Precise timestamp tracking for each screenshot
- RESTful endpoints with comprehensive error handling

---

## 🔗 Additional Resources

- **Live Demo:** https://clips.hurated.com
- **GitHub Repository:** https://github.com/dbystruev/ClipWeaver
- **Frontend Code:** Built with Bolt.new (React/Next.js)

---

## 🛠️ Bolt.new Integration

Use this prompt in Bolt.new to create a ClipWeaver client:

```
Create a video storyboard app using the ClipWeaver API at api.clip.hurated.com.

Features:
1. Video upload with drag-and-drop (max 500MB)
2. Scene detection sensitivity slider (0.1-0.9)
3. Max scenes selector (1-20)
4. Format toggle (JSON/Markdown download)
5. Display JSON results with scene thumbnails and descriptions
6. Show precise timestamps for each scene
7. Download markdown button
8. Modern UI with Tailwind CSS

API endpoint: POST /analyze
Parameters: video (file), scene_threshold (float), max_scenes (int), format (string)

Use TypeScript, React, and fetch API.
```