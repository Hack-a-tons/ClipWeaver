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
    video_path = "temp.mp4"
    video.save(video_path)
    logger.info(f"💾 Video saved to: {video_path}")

    # Clean and prepare scenes directory
    scene_dir = "output/scenes"
    if os.path.exists(scene_dir):
        import shutil
        shutil.rmtree(scene_dir)
        logger.info(f"🧹 Cleaned old scenes directory")
    os.makedirs(scene_dir, exist_ok=True)
    
    # Extract scenes
    logger.info("🎬 Starting scene extraction...")
    scenes = extract_scenes(video_path, scene_dir)
    logger.info(f"✅ Scene extraction complete: {len(scenes)} scenes detected")

    # Generate storyboard with AI descriptions
    logger.info("🤖 Starting AI description generation...")
    markdown = "# Storyboard\n\n"
    scene_descriptions = []
    
    for i, img in enumerate(scenes, 1):
        logger.info(f"🔍 Processing scene {i}/{len(scenes)}: {os.path.basename(img)}")
        prompt = "Describe the scene in this image briefly and vividly, as if for a video storyboard."
        
        try:
            # Encode image to base64 for Azure OpenAI
            with open(img, "rb") as f:
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
            logger.info(f"📝 Scene {i} description: {desc[:100]}...")
        except Exception as e:
            desc = f"Error generating description: {str(e)}"
            scene_descriptions.append(desc)
            logger.error(f"❌ Error describing scene {i}: {str(e)}")

        # Generate full URL for the image
        img_url = f"{BASE_URL}/{img}"
        
        markdown += f"## Scene {i}\n"
        markdown += f"![Scene {i}]({img_url})\n"
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
    logger.info(f"   • Scenes detected: {len(scenes)}")
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
