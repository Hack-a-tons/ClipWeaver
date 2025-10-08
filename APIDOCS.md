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

**Example cURL (Markdown):**
```bash
curl -X POST https://api.clip.hurated.com/analyze \
  -F "video=@sample.mp4" \
  -F "scene_threshold=0.06" \
  -F "max_scenes=10"
```

**Example cURL (JSON):**
```bash
curl -X POST https://api.clip.hurated.com/analyze \
  -F "video=@sample.mp4" \
  -F "scene_threshold=0.06" \
  -F "max_scenes=10" \
  -F "format=json"
```

#### Response

**Markdown Format (Default):**
Returns a downloadable `.md` file with the storyboard.

**JSON Format:**
```json
{
  "status": "success",
  "video_info": {
    "filename": "sample.mp4",
    "size_mb": 7.91,
    "processing_time": 27.16
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
          "url": "https://api.clip.hurated.com/output/scenes/scene_001_beginning.png"
        },
        {
          "position": "middle",
          "timestamp": 4.0,
          "url": "https://api.clip.hurated.com/output/scenes/scene_001_middle.png"
        },
        {
          "position": "end",
          "timestamp": 7.5,
          "url": "https://api.clip.hurated.com/output/scenes/scene_001_end.png"
        }
      ],
      "description": "AI-generated scene description based on all three screenshots..."
    }
  ],
  "markdown_url": "https://api.clip.hurated.com/output/storyboard.md",
  "total_scenes": 3
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

### 2. **Health Check**

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
# Get storyboard markdown
curl https://api.clip.hurated.com/output/storyboard.md

# Get scene thumbnail
curl https://api.clip.hurated.com/output/scenes/scene_001_beginning.png
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
// Analyze video and get JSON response
async function analyzeVideo(videoFile: File): Promise<AnalyzeResponse> {
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
const result = await analyzeVideo(file);
console.log(`Found ${result.total_scenes} scenes`);
result.scenes.forEach(scene => {
  console.log(`Scene ${scene.scene_number}: ${scene.timeframe.start}s-${scene.timeframe.end}s`);
  console.log(`Description: ${scene.description}`);
});
```

### Python

```python
import requests

def analyze_video_json(video_path):
    """Get JSON response with scene data"""
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
json_result = analyze_video_json('sample.mp4')
print(f"Processing time: {json_result['video_info']['processing_time']}s")

for scene in json_result['scenes']:
    print(f"Scene {scene['scene_number']}: {scene['timeframe']['start']}s-{scene['timeframe']['end']}s")
    print(f"Screenshots: {len(scene['screenshots'])}")
```

---

## 🌐 CORS

CORS is enabled for all origins in development. In production:
- Allowed Origins: `*.clip.hurated.com`, `localhost:*`
- Allowed Methods: GET, POST, OPTIONS
- Allowed Headers: Content-Type

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