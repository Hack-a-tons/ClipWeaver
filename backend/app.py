import os
import base64
import logging
from datetime import datetime
from openai import AzureOpenAI
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from analyzer import extract_scenes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

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
    start_time = datetime.now()
    logger.info("=== VIDEO ANALYSIS STARTED ===")
    
    if "video" not in request.files:
        logger.error("No video file provided in request")
        return jsonify({"status": "error", "error": "No video file provided"}), 400
    
    video = request.files["video"]
    if video.filename == "":
        logger.error("Empty filename provided")
        return jsonify({"status": "error", "error": "Empty filename"}), 400
    
    # Log video info
    video_size = len(video.read())
    video.seek(0)  # Reset file pointer
    logger.info(f"📹 Video uploaded: {video.filename} ({video_size / (1024*1024):.2f} MB)")
    
    # Save uploaded video
    video_path = os.path.join(os.getcwd(), "temp.mp4")
    video.save(video_path)
    logger.info(f"💾 Video saved to: {video_path}")

    # Clean and prepare scenes directory
    scene_dir = "output/scenes"
    if os.path.exists(scene_dir):
        import shutil
        shutil.rmtree(scene_dir)
        logger.info(f"🧹 Cleaned old scenes directory")
    os.makedirs(scene_dir, exist_ok=True)
    
    # Get scene detection parameters
    scene_threshold = float(request.form.get('scene_threshold', 0.06))
    max_scenes = int(request.form.get('max_scenes', 10))
    logger.info(f"🎛️ Scene detection params: threshold={scene_threshold}, max_scenes={max_scenes}")
    logger.info(f"📋 API call parameters: video={video.filename}, scene_threshold={scene_threshold}, max_scenes={max_scenes}")
    
    # Extract scenes
    logger.info("🎬 Starting scene extraction...")
    scenes = extract_scenes(video_path, scene_dir, scene_threshold, max_scenes)
    logger.info(f"✅ Scene extraction complete: {len(scenes)} scenes detected")

    # Generate storyboard with AI descriptions
    logger.info("🤖 Starting AI description generation...")
    markdown = "# Storyboard\n\n"
    scene_descriptions = []
    
    # Group screenshots by scene
    scenes_dict = {}
    for screenshot_info in scenes:
        # Extract scene number from filename
        basename = os.path.basename(screenshot_info['path'])
        if 'scene_' in basename:
            scene_num = int(basename.split('_')[1])
            if scene_num not in scenes_dict:
                scenes_dict[scene_num] = []
            scenes_dict[scene_num].append(screenshot_info)
    
    # Process each scene
    for scene_num in sorted(scenes_dict.keys()):
        # Sort images by position: beginning, middle, end
        def sort_by_position(screenshot_info):
            position = screenshot_info['position']
            if position == 'beginning':
                return 0
            elif position == 'middle':
                return 1
            elif position == 'end':
                return 2
            return 3
        
        scene_screenshots = sorted(scenes_dict[scene_num], key=sort_by_position)
        logger.info(f"🔍 Processing scene {scene_num} with {len(scene_screenshots)} screenshots")
        
        # Get scene timing info
        if scene_screenshots:
            scene_start = scene_screenshots[0]['scene_start']
            scene_end = scene_screenshots[0]['scene_end']
            
            # Use all screenshots for AI description
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
                logger.info(f"📝 Scene {scene_num} description: {desc[:100]}...")
            except Exception as e:
                desc = f"Error generating description: {str(e)}"
                scene_descriptions.append(desc)
                logger.error(f"❌ Error describing scene {scene_num}: {str(e)}")

            # Generate markdown for this scene
            markdown += f"## Scene {scene_num} ({scene_start:.1f}s - {scene_end:.1f}s)\n"
            
            # Add all screenshots for this scene with timestamps
            for screenshot_info in scene_screenshots:
                img_url = f"{BASE_URL}/{screenshot_info['path']}"
                position = screenshot_info['position']
                timestamp = screenshot_info['timestamp']
                markdown += f"![Scene {scene_num} - {position} @ {timestamp:.1f}s]({img_url})\n"
            
            markdown += f"- **Timeframe**: {scene_start:.1f}s - {scene_end:.1f}s ({scene_end - scene_start:.1f}s duration)\n"
            markdown += f"- **Description**: {desc}\n\n"

    # Save markdown
    md_path = "output/storyboard.md"
    with open(md_path, "w") as f:
        f.write(markdown)
    
    # Calculate processing time
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    
    # Log analytics summary
    logger.info("=== ANALYSIS COMPLETE ===")
    logger.info(f"📊 ANALYTICS SUMMARY:")
    logger.info(f"   • Video: {video.filename} ({video_size / (1024*1024):.2f} MB)")
    logger.info(f"   • Scenes detected: {len(scenes_dict)}")
    logger.info(f"   • Screenshots extracted: {len(scenes)}")
    logger.info(f"   • Processing time: {processing_time:.2f} seconds")
    logger.info(f"   • Output: {md_path}")
    logger.info(f"📋 SCENE DESCRIPTIONS:")
    for i, desc in enumerate(scene_descriptions, 1):
        logger.info(f"   Scene {i}: {desc[:150]}{'...' if len(desc) > 150 else ''}")
    logger.info("=== END ANALYSIS ===")

    # Check if JSON format is requested
    response_format = request.form.get('format', 'markdown')
    
    if response_format == 'json':
        # Build JSON response
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
                        "url": f"{BASE_URL}/{shot['path']}"
                    }
                    for shot in scene_screenshots
                ],
                "description": scene_descriptions[scene_num - 1] if scene_num <= len(scene_descriptions) else ""
            })
        
        return jsonify({
            "status": "success",
            "video_info": {
                "filename": video.filename,
                "size_mb": round(video_size / (1024*1024), 2),
                "processing_time": round(processing_time, 2)
            },
            "scenes": json_scenes,
            "markdown_url": f"{BASE_URL}/output/storyboard.md",
            "total_scenes": len(scenes_dict)
        })
    else:
        # Default: return markdown file
        return send_file(md_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 13000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    app.run(host=host, port=port, debug=True)
