import os
import base64
import logging
import time
import random
import json
import threading
import re
from datetime import datetime
from openai import AzureOpenAI
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from analyzer import extract_scenes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS with dynamic origin checking
def is_allowed_origin(origin):
    """Check if origin is allowed based on whitelist patterns"""
    if not origin:
        return False
    
    allowed_patterns = [
        r'^https://bolt\.new$',
        r'^https://.*\.bolt\.new$',
        r'^https://.*\.webcontainer-api\.io$',
        r'^http://localhost(:\d+)?$',
        r'^https://clips\.hurated\.com$'
    ]
    
    for pattern in allowed_patterns:
        if re.match(pattern, origin):
            return True
    return False

def handle_cors():
    """Handle CORS headers dynamically"""
    origin = request.headers.get('Origin')
    
    if is_allowed_origin(origin):
        return {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Client-Info, Apikey',
            'Access-Control-Max-Age': '86400'
        }
    return {}

@app.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    cors_headers = handle_cors()
    for header, value in cors_headers.items():
        response.headers[header] = value
    return response

@app.before_request
def handle_preflight():
    """Handle OPTIONS preflight requests"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        cors_headers = handle_cors()
        for header, value in cors_headers.items():
            response.headers[header] = value
        return response, 200

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base URL for the API (used for generating full URLs)
BASE_URL = os.getenv("BASE_URL", "https://api.clip.hurated.com")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# In-memory storage for request status (in production, use Redis or database)
request_status = {}
request_logs = {}

def generate_unique_folder():
    """Generate unique folder name based on timestamp, IP, and random value"""
    timestamp = int(time.time())
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
    # Clean IP for folder name (replace dots/colons with underscores)
    clean_ip = client_ip.replace('.', '_').replace(':', '_')
    random_val = random.randint(1000, 9999)
    folder_name = f"{timestamp}_{clean_ip}_{random_val}"
    return folder_name

def log_status(request_id, message, level="INFO"):
    """Log message and store for status endpoint"""
    if request_id not in request_logs:
        request_logs[request_id] = []
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message
    }
    request_logs[request_id].append(log_entry)
    
    # Also log to console
    if level == "INFO":
        logger.info(f"[{request_id}] {message}")
    elif level == "ERROR":
        logger.error(f"[{request_id}] {message}")

def process_video_async(request_id, video_path, scene_dir, scene_threshold, max_scenes, response_format, video_filename, video_size):
    """Process video asynchronously"""
    try:
        request_status[request_id] = {"status": "processing", "progress": 0}
        log_status(request_id, "🎬 Starting scene extraction...")
        
        # Extract scenes
        scenes = extract_scenes(video_path, scene_dir, scene_threshold, max_scenes)
        request_status[request_id]["progress"] = 30
        log_status(request_id, f"✅ Scene extraction complete: {len(scenes)} scenes detected")

        # Generate storyboard with AI descriptions
        log_status(request_id, "🤖 Starting AI description generation...")
        markdown = "# Storyboard\n\n"
        scene_descriptions = []
        
        # Group screenshots by scene
        scenes_dict = {}
        for screenshot_info in scenes:
            basename = os.path.basename(screenshot_info['path'])
            if 'scene_' in basename:
                scene_num = int(basename.split('_')[1])
                if scene_num not in scenes_dict:
                    scenes_dict[scene_num] = []
                scenes_dict[scene_num].append(screenshot_info)
        
        request_status[request_id]["progress"] = 40
        
        # Process each scene
        total_scenes = len(scenes_dict)
        for i, scene_num in enumerate(sorted(scenes_dict.keys())):
            progress = 40 + int((i / total_scenes) * 50)  # 40-90% for AI processing
            request_status[request_id]["progress"] = progress
            
            scene_screenshots = sorted(scenes_dict[scene_num], key=lambda x: ['beginning', 'middle', 'end'].index(x['position']))
            log_status(request_id, f"🔍 Processing scene {scene_num} with {len(scene_screenshots)} screenshots")
            
            if scene_screenshots:
                scene_start = scene_screenshots[0]['scene_start']
                scene_end = scene_screenshots[0]['scene_end']
                
                prompt = f"Describe this video scene (timeframe {scene_start:.1f}s - {scene_end:.1f}s) based on these sequential frames. Focus on the overall action, movement, and story progression."
                
                try:
                    # Encode all images to base64
                    image_contents = []
                    for screenshot_info in scene_screenshots:
                        with open(screenshot_info['path'], "rb") as f:
                            image_data = base64.b64encode(f.read()).decode('utf-8')
                            image_contents.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}})
                    
                    # Call Azure OpenAI with all images
                    messages_content = [{"type": "text", "text": prompt}] + image_contents
                    
                    response = client.chat.completions.create(
                        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that describes video scenes based on multiple frames."},
                            {"role": "user", "content": messages_content}
                        ],
                        max_tokens=300
                    )
                    desc = response.choices[0].message.content.strip()
                    scene_descriptions.append(desc)
                    log_status(request_id, f"📝 Scene {scene_num} description generated")
                except Exception as e:
                    desc = f"Error generating description: {str(e)}"
                    scene_descriptions.append(desc)
                    log_status(request_id, f"❌ Error describing scene {scene_num}: {str(e)}", "ERROR")

                # Generate markdown for this scene
                markdown += f"## Scene {scene_num} ({scene_start:.1f}s - {scene_end:.1f}s)\n"
                
                for screenshot_info in scene_screenshots:
                    relative_path = os.path.relpath(screenshot_info['path'], "output")
                    img_url = f"{BASE_URL}/output/{relative_path}"
                    position = screenshot_info['position']
                    timestamp = screenshot_info['timestamp']
                    markdown += f"![Scene {scene_num} - {position} @ {timestamp:.1f}s]({img_url})\n"
                
                markdown += f"- **Timeframe**: {scene_start:.1f}s - {scene_end:.1f}s ({scene_end - scene_start:.1f}s duration)\n"
                markdown += f"- **Description**: {desc}\n\n"

        request_status[request_id]["progress"] = 90
        
        # Save markdown
        request_dir = os.path.dirname(scene_dir)
        md_path = os.path.join(request_dir, "storyboard.md")
        with open(md_path, "w") as f:
            f.write(markdown)
        
        # Save results
        if response_format == 'json':
            json_scenes = []
            for scene_num in sorted(scenes_dict.keys()):
                scene_screenshots = sorted(scenes_dict[scene_num], key=lambda x: ['beginning', 'middle', 'end'].index(x['position']))
                scene_start = scene_screenshots[0]['scene_start']
                scene_end = scene_screenshots[0]['scene_end']
                
                json_scenes.append({
                    "scene_number": scene_num,
                    "timeframe": {
                        "start": round(scene_start, 1),
                        "end": round(scene_end, 1),
                        "duration": round(scene_end - scene_start, 1)
                    },
                    "screenshots": [
                        {
                            "position": shot['position'],
                            "timestamp": round(shot['timestamp'], 1),
                            "url": f"{BASE_URL}/output/{os.path.relpath(shot['path'], 'output')}"
                        }
                        for shot in scene_screenshots
                    ],
                    "description": scene_descriptions[scene_num - 1] if scene_num <= len(scene_descriptions) else ""
                })
            
            result = {
                "status": "success",
                "request_id": request_id,
                "video_info": {
                    "filename": video_filename,
                    "size_mb": round(video_size / (1024*1024), 2)
                },
                "scenes": json_scenes,
                "markdown_url": f"{BASE_URL}/output/{request_id}/storyboard.md",
                "total_scenes": len(scenes_dict)
            }
        else:
            result = {"markdown_path": md_path}
        
        request_status[request_id] = {
            "status": "completed", 
            "progress": 100,
            "result": result
        }
        log_status(request_id, "✅ Analysis complete!")
        
    except Exception as e:
        request_status[request_id] = {"status": "error", "error": str(e)}
        log_status(request_id, f"❌ Processing failed: {str(e)}", "ERROR")

@app.route("/status/<request_id>", methods=["GET"])
def get_status(request_id):
    """Get status and logs for a processing request"""
    if request_id not in request_status:
        return jsonify({"status": "error", "error": "Request ID not found"}), 404
    
    status_info = request_status[request_id].copy()
    logs = request_logs.get(request_id, [])
    
    # Add recent logs (last 10 entries)
    status_info["logs"] = logs[-10:]
    status_info["total_logs"] = len(logs)
    
    return jsonify(status_info)

@app.route("/result/<request_id>", methods=["GET"])
def get_result(request_id):
    """Get final result for a completed request"""
    if request_id not in request_status:
        return jsonify({"status": "error", "error": "Request ID not found"}), 404
    
    status_info = request_status[request_id]
    
    if status_info["status"] != "completed":
        return jsonify({
            "status": "error", 
            "error": f"Request not completed. Current status: {status_info['status']}"
        }), 400
    
    result = status_info["result"]
    
    # If it's a markdown result, serve the file
    if "markdown_path" in result:
        return send_file(result["markdown_path"], as_attachment=True, download_name=f"storyboard_{request_id}.md")
    else:
        # JSON result
        return jsonify(result)

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    logger.info("Health check requested")
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "scene_detection": "operational",
            "ai_description": "operational",
            "storage": "operational"
        }
    })

@app.route("/output/<path:filename>", methods=["GET"])
def serve_output(filename):
    """Serve static files from output directory"""
    logger.info(f"Serving file: {filename}")
    return send_from_directory("output", filename)

@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze video and generate storyboard"""
    # Generate unique folder for this request
    unique_folder = generate_unique_folder()
    
    if "video" not in request.files:
        return jsonify({"status": "error", "error": "No video file provided"}), 400
    
    video = request.files["video"]
    if video.filename == "":
        return jsonify({"status": "error", "error": "Empty filename"}), 400
    
    # Get processing mode
    async_mode = request.form.get('async', 'false').lower() == 'true'
    response_format = request.form.get('format', 'markdown')
    
    # Log video info
    video_size = len(video.read())
    video.seek(0)  # Reset file pointer
    
    # Create unique directories for this request
    request_dir = os.path.join("output", unique_folder)
    scene_dir = os.path.join(request_dir, "scenes")
    os.makedirs(scene_dir, exist_ok=True)
    
    # Save uploaded video in unique directory with original filename
    video_path = os.path.join(request_dir, video.filename)
    video.save(video_path)
    
    # Get scene detection parameters
    scene_threshold = float(request.form.get('scene_threshold', 0.06))
    max_scenes = int(request.form.get('max_scenes', 10))
    
    if async_mode:
        # Start async processing
        request_status[unique_folder] = {"status": "queued", "progress": 0}
        request_logs[unique_folder] = []
        log_status(unique_folder, f"📹 Video uploaded: {video.filename} ({video_size / (1024*1024):.2f} MB)")
        
        thread = threading.Thread(
            target=process_video_async,
            args=(unique_folder, video_path, scene_dir, scene_threshold, max_scenes, response_format, video.filename, video_size)
        )
        thread.start()
        
        return jsonify({
            "status": "accepted",
            "request_id": unique_folder,
            "message": "Video processing started. Use /status/{request_id} to check progress."
        }), 202
    else:
        # Synchronous processing (original behavior)
        start_time = datetime.now()
        log_status(unique_folder, f"=== VIDEO ANALYSIS STARTED (ID: {unique_folder}) ===")
        log_status(unique_folder, f"📹 Video uploaded: {video.filename} ({video_size / (1024*1024):.2f} MB)")
        
        # Process synchronously using the same function
        process_video_async(unique_folder, video_path, scene_dir, scene_threshold, max_scenes, response_format, video.filename, video_size)
        
        # Return result immediately
        if unique_folder in request_status and request_status[unique_folder]["status"] == "completed":
            result = request_status[unique_folder]["result"]
            if response_format == 'json':
                return jsonify(result)
            else:
                return send_file(result["markdown_path"], as_attachment=True, download_name=f"storyboard_{unique_folder}.md")
        else:
            error = request_status.get(unique_folder, {}).get("error", "Unknown error")
            return jsonify({"status": "error", "error": error}), 500

if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 13000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    app.run(host=host, port=port, debug=True)
