# ClipWeaver Backend

Python Flask backend for video scene analysis using Azure OpenAI.

## Local Development

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install ffmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg
```

3. Copy `.env.example` to `.env` and configure:
```bash
cp ../.env.example ../.env
```

4. Run the server:
```bash
python app.py
```

Server will start on `http://localhost:13000`

### Testing

Test the health endpoint:
```bash
curl http://localhost:13000/health
```

Test video analysis:
```bash
curl -X POST http://localhost:13000/analyze \
  -F "video=@sample.mp4"
```

## File Structure

- `app.py` - Main Flask application with Azure OpenAI integration
- `analyzer.py` - Video scene detection using ffmpeg
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `output/` - Generated storyboards and scene images

## Azure OpenAI Configuration

Required environment variables:
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_API_VERSION` - API version (e.g., 2025-01-01-preview)
- `AZURE_OPENAI_DEPLOYMENT_NAME` - Your GPT-4 Vision deployment name

## API Endpoints

### GET /health
Health check endpoint

### POST /analyze
Upload video and generate storyboard
- **Body:** `multipart/form-data` with `video` file
- **Returns:** Markdown storyboard file
