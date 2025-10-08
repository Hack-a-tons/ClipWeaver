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
    for img in scenes:
        # Extract scene number from filename (e.g., scene_001_beginning.png)
        basename = os.path.basename(img)
        if 'scene_' in basename:
            scene_num = int(basename.split('_')[1])
            if scene_num not in scenes_dict:
                scenes_dict[scene_num] = []
            scenes_dict[scene_num].append(img)
    
    # Process each scene
    for scene_num in sorted(scenes_dict.keys()):
        # Sort images by position: beginning, middle, end
        def sort_by_position(img):
            basename = os.path.basename(img)
            if 'beginning' in basename:
                return 0
            elif 'middle' in basename:
                return 1
            elif 'end' in basename:
                return 2
            return 3
        
        scene_images = sorted(scenes_dict[scene_num], key=sort_by_position)
        logger.info(f"🔍 Processing scene {scene_num} with {len(scene_images)} screenshots")
        
        # Use the middle screenshot for AI description
        middle_img = None
        for img in scene_images:
            if 'middle' in os.path.basename(img):
                middle_img = img
                break
        
        if not middle_img and scene_images:
            middle_img = scene_images[0]  # Fallback to first image
        
        if middle_img:
            prompt = "Describe the scene in this image briefly and vividly, as if for a video storyboard."
            
            try:
                # Encode image to base64 for Azure OpenAI
                with open(middle_img, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                
                # Call Azure OpenAI with vision
                response = client.chat.completions.create(
                    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that describes video scenes."},
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                        ]}
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
            markdown += f"## Scene {scene_num}\n"
            
            # Add all screenshots for this scene
            for img in scene_images:
                img_url = f"{BASE_URL}/{img}"
                position = os.path.basename(img).split('_')[2].split('.')[0]  # Extract position (beginning/middle/end)
                markdown += f"![Scene {scene_num} - {position}]({img_url})\n"
            
            markdown += f"- Description: {desc}\n\n"

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

    return send_file(md_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 13000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    app.run(host=host, port=port, debug=True)
