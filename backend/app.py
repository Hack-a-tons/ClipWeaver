import os
import base64
from openai import AzureOpenAI
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from analyzer import extract_scenes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

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
    return send_from_directory("output", filename)

@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze video and generate storyboard"""
    if "video" not in request.files:
        return jsonify({"status": "error", "error": "No video file provided"}), 400
    
    video = request.files["video"]
    if video.filename == "":
        return jsonify({"status": "error", "error": "Empty filename"}), 400
    
    # Save uploaded video
    video_path = "temp.mp4"
    video.save(video_path)

    # Extract scenes
    scene_dir = "output/scenes"
    os.makedirs(scene_dir, exist_ok=True)
    scenes = extract_scenes(video_path, scene_dir)

    # Generate storyboard with AI descriptions
    markdown = "# Storyboard\n\n"
    for i, img in enumerate(scenes, 1):
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
        except Exception as e:
            desc = f"Error generating description: {str(e)}"

        # Generate full URL for the image
        img_url = f"{BASE_URL}/{img}"
        
        markdown += f"## Scene {i}\n"
        markdown += f"![Scene {i}]({img_url})\n"
        markdown += f"- Description: {desc}\n\n"

    # Save markdown
    md_path = "output/storyboard.md"
    with open(md_path, "w") as f:
        f.write(markdown)

    return send_file(md_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 13000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    app.run(host=host, port=port, debug=True)
