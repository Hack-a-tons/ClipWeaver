# 🎬 ClipWeaver API Documentation

> **Base URL:** `https://api.clip.hurated.com`  
> **Version:** 1.0.0  
> **Protocol:** REST/HTTP

---

## 📋 Overview

ClipWeaver API provides video scene analysis and storyboard generation using AI-powered scene detection and description. Upload a video, and receive a structured Markdown storyboard with scene thumbnails and AI-generated descriptions.

---

## 🔐 Authentication

Currently, the API does not require authentication for basic usage. Rate limiting may apply in production.

---

## 📡 Endpoints

### 1. **Analyze Video**

**POST** `/api/v1/analyze`

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
| `scene_threshold` | Float | No | Scene detection sensitivity (0.1-1.0). Default: 0.4 |
| `max_scenes` | Integer | No | Maximum scenes to extract. Default: 20 |

**Example cURL:**
```bash
curl -X POST https://api.clip.hurated.com/api/v1/analyze \
  -F "video=@sample.mp4" \
  -F "scene_threshold=0.4" \
  -F "max_scenes=10"
```

#### Response

**Success (200 OK):**
```json
{
  "status": "success",
  "job_id": "abc123-def456-ghi789",
  "video_duration": 45.5,
  "scenes_count": 8,
  "storyboard_url": "https://api.clip.hurated.com/api/v1/storyboard/abc123-def456-ghi789",
  "download_url": "https://api.clip.hurated.com/api/v1/download/abc123-def456-ghi789"
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

### 2. **Get Storyboard**

**GET** `/api/v1/storyboard/{job_id}`

Retrieve the generated storyboard in JSON format.

#### Request

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id` | String | Job ID from analyze response |

**Example:**
```bash
curl https://api.clip.hurated.com/api/v1/storyboard/abc123-def456-ghi789
```

#### Response

**Success (200 OK):**
```json
{
  "job_id": "abc123-def456-ghi789",
  "video_info": {
    "filename": "sample.mp4",
    "duration": 45.5,
    "resolution": "1920x1080",
    "fps": 30
  },
  "scenes": [
    {
      "scene_number": 1,
      "timestamp": 0.0,
      "thumbnail_url": "https://api.clip.hurated.com/api/v1/thumbnail/abc123-def456-ghi789/scene_001.png",
      "description": "A person walks through a neon-lit alley, camera slowly pans left.",
      "duration": 5.2
    },
    {
      "scene_number": 2,
      "timestamp": 5.2,
      "thumbnail_url": "https://api.clip.hurated.com/api/v1/thumbnail/abc123-def456-ghi789/scene_002.png",
      "description": "The same character stops under a flickering sign, looking up as rain starts to fall.",
      "duration": 6.8
    }
  ],
  "markdown_url": "https://api.clip.hurated.com/api/v1/markdown/abc123-def456-ghi789"
}
```

---

### 3. **Download Markdown Storyboard**

**GET** `/api/v1/markdown/{job_id}`

Download the storyboard as a Markdown file.

#### Request

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id` | String | Job ID from analyze response |

**Example:**
```bash
curl -O https://api.clip.hurated.com/api/v1/markdown/abc123-def456-ghi789
```

#### Response

**Success (200 OK):**
```
Content-Type: text/markdown
Content-Disposition: attachment; filename="storyboard_abc123.md"

# Storyboard

## Scene 1
![Scene 1](https://api.clip.hurated.com/api/v1/thumbnail/abc123-def456-ghi789/scene_001.png)
- **Timestamp:** 00:00 - 00:05
- **Description:** A person walks through a neon-lit alley, camera slowly pans left.

## Scene 2
![Scene 2](https://api.clip.hurated.com/api/v1/thumbnail/abc123-def456-ghi789/scene_002.png)
- **Timestamp:** 00:05 - 00:12
- **Description:** The same character stops under a flickering sign, looking up as rain starts to fall.
```

---

### 4. **Get Thumbnail**

**GET** `/api/v1/thumbnail/{job_id}/{filename}`

Retrieve a specific scene thumbnail.

#### Request

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id` | String | Job ID from analyze response |
| `filename` | String | Thumbnail filename (e.g., scene_001.png) |

**Example:**
```bash
curl https://api.clip.hurated.com/api/v1/thumbnail/abc123-def456-ghi789/scene_001.png
```

#### Response

**Success (200 OK):**
```
Content-Type: image/png
[Binary image data]
```

---

### 5. **Health Check**

**GET** `/api/v1/health`

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
  },
  "timestamp": "2025-10-07T15:38:30Z"
}
```

---

## 📊 Data Models

### Scene Object
```typescript
interface Scene {
  scene_number: number;
  timestamp: number;
  thumbnail_url: string;
  description: string;
  duration: number;
}
```

### Storyboard Response
```typescript
interface StoryboardResponse {
  job_id: string;
  video_info: {
    filename: string;
    duration: number;
    resolution: string;
    fps: number;
  };
  scenes: Scene[];
  markdown_url: string;
}
```

---

## ⚠️ Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid parameters or file format |
| 404 | Not Found | Job ID not found |
| 413 | Payload Too Large | Video file exceeds 500MB |
| 415 | Unsupported Media Type | Invalid video format |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server processing error |
| 503 | Service Unavailable | AI service temporarily unavailable |

---

## 🚀 Rate Limits

- **Free Tier:** 10 requests per hour
- **Video Processing:** Maximum 500MB per file
- **Concurrent Jobs:** 3 simultaneous video analyses

---

## 💻 Client Integration Example

### JavaScript/TypeScript (Bolt.new)

```typescript
// Upload and analyze video
async function analyzeVideo(videoFile: File) {
  const formData = new FormData();
  formData.append('video', videoFile);
  formData.append('scene_threshold', '0.4');
  
  const response = await fetch('https://api.clip.hurated.com/api/v1/analyze', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  return result.job_id;
}

// Get storyboard results
async function getStoryboard(jobId: string) {
  const response = await fetch(`https://api.clip.hurated.com/api/v1/storyboard/${jobId}`);
  const storyboard = await response.json();
  return storyboard;
}

// Complete workflow
async function processVideo(file: File) {
  try {
    const jobId = await analyzeVideo(file);
    
    // Poll for completion (or use webhooks)
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    const storyboard = await getStoryboard(jobId);
    console.log('Scenes:', storyboard.scenes);
    
    return storyboard;
  } catch (error) {
    console.error('Processing failed:', error);
  }
}
```

### Python

```python
import requests

def analyze_video(video_path):
    url = "https://api.clip.hurated.com/api/v1/analyze"
    
    with open(video_path, 'rb') as f:
        files = {'video': f}
        data = {'scene_threshold': 0.4, 'max_scenes': 10}
        
        response = requests.post(url, files=files, data=data)
        return response.json()

def get_storyboard(job_id):
    url = f"https://api.clip.hurated.com/api/v1/storyboard/{job_id}"
    response = requests.get(url)
    return response.json()

# Usage
result = analyze_video('sample.mp4')
storyboard = get_storyboard(result['job_id'])
print(f"Found {len(storyboard['scenes'])} scenes")
```

---

## 🌐 CORS

CORS is enabled for all origins in development. In production:
- Allowed Origins: `*.clip.hurated.com`, `localhost:*`
- Allowed Methods: GET, POST, OPTIONS
- Allowed Headers: Content-Type, Authorization

---

## 📝 Changelog

### v1.0.0 (2025-10-07)
- Initial API release
- Scene detection with ffmpeg
- Azure OpenAI GPT-4 vision integration
- Markdown and JSON storyboard export
- RESTful endpoints

---

## 🔗 Additional Resources

- **Frontend Demo:** https://app.clip.hurated.com
- **GitHub Repository:** https://github.com/dbystruev/ClipWeaver
- **Support:** support@hurated.com

---

## 🛠️ Bolt.new Quick Start

Use this prompt in Bolt.new to generate a client:

```
Create a video storyboard app that integrates with the ClipWeaver API at api.clip.hurated.com.

Features needed:
1. Video upload with drag-and-drop (max 500MB)
2. Progress indicator during analysis
3. Display storyboard with scene thumbnails and AI descriptions
4. Download markdown button
5. Modern UI with Tailwind CSS and shadcn/ui components

API endpoints:
- POST /api/v1/analyze (upload video)
- GET /api/v1/storyboard/{job_id} (get results)
- GET /api/v1/markdown/{job_id} (download markdown)

Use TypeScript, React, and the fetch API for requests.
```
