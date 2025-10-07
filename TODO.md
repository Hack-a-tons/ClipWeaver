Your goal is to show:

“ClipWeaver can understand a video, extract scenes, and generate a Markdown storyboard with AI descriptions and thumbnails.”

Below is a step-by-step 2-hour implementation plan, with minimal commands, architecture, and short code snippets you can paste into Windsurf IDE or Docker on your Ubuntu server.

⸻

## ⚡️ CLIPWEAVER LITE — 2-HOUR MVP PLAN

### 🕒 Time Breakdown
```
Time	Task	Description
0:00–0:10	Setup	Prepare repo, environment, and install dependencies
0:10–0:40	Scene Detection	Split video into scenes + extract 3 thumbnails per scene
0:40–1:10	AI Scene Descriptions	Generate Markdown from screenshots using GPT
1:10–1:40	Frontend UI	Simple upload + display storyboard in Bolt.new
1:40–2:00	Polish + Demo	Add titles, logo, short presentation pitch
```

⸻

### 🧱 1. PROJECT STRUCTURE

Create your project folder:
```
clipweaver-lite/
├── backend/
│   ├── app.py
│   ├── analyzer.py
│   ├── requirements.txt
│   └── output/
│       ├── scenes/
│       └── storyboard.md
├── frontend/
│   └── (Bolt.new project)
└── sample.mp4  (for testing)
```

⸻

### 🧰 2. BACKEND SETUP

Requirements

Create requirements.txt:
```
flask
openai
moviepy
python-dotenv
```
Install with:
```bash
pip install -r requirements.txt
sudo apt install ffmpeg
```
Create .env and add:
```
OPENAI_API_KEY=sk-...
```

⸻

### 🧩 3. SCENE DETECTION (analyzer.py)
```python
import os, subprocess, glob
from moviepy.editor import VideoFileClip

def extract_scenes(video_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    # Detect scene changes using ffmpeg
    cmd = [
        "ffmpeg", "-i", video_path,
        "-filter_complex", "select='gt(scene,0.4)',metadata=print",
        "-vsync", "vfr", f"{output_dir}/scene_%03d.png"
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    scenes = sorted(glob.glob(f"{output_dir}/scene_*.png"))
    return scenes
```
✅ Output: output/scenes/scene_001.png, etc.

⸻

### 🧠 4. AI DESCRIPTIONS → MARKDOWN (app.py)
```python
import os, openai
from flask import Flask, request, jsonify, send_file
from analyzer import extract_scenes

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/analyze", methods=["POST"])
def analyze():
    video = request.files["video"]
    video_path = "temp.mp4"
    video.save(video_path)

    scene_dir = "output/scenes"
    scenes = extract_scenes(video_path, scene_dir)

    markdown = "# Storyboard\n\n"
    for i, img in enumerate(scenes, 1):
        prompt = f"Describe the scene in this image briefly and vividly, as if for a video storyboard."
        with open(img, "rb") as f:
            desc = openai.images.generate_description(f, prompt)  # Pseudo; see below note

        markdown += f"## Scene {i}\n"
        markdown += f"![Scene {i}]({img})\n"
        markdown += f"- Description: {desc}\n\n"

    md_path = "output/storyboard.md"
    with open(md_path, "w") as f: f.write(markdown)

    return send_file(md_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
```

#### 🧩 Note:
For image description, since OpenAI doesn’t yet expose direct images.generate_description(), use GPT-4-vision style call via API:
```python
resp = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that describes video scenes."},
        {"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": f"file://{os.path.abspath(img)}"}
        ]}
    ]
)
desc = resp.choices[0].message.content.strip()
```
⸻

### 🎨 5. FRONTEND (Bolt.new)

Use Bolt.new to make a simple 1-page web app:
	•	Upload video
	•	Button “Analyze”
	•	Show Markdown output as cards.

You can scaffold this with:

import { useState } from "react";

export default function App() {
  const [file, setFile] = useState(null);
  const [markdown, setMarkdown] = useState("");

  const uploadAndAnalyze = async () => {
    const formData = new FormData();
    formData.append("video", file);
    const res = await fetch("http://localhost:5000/analyze", {
      method: "POST",
      body: formData
    });
    const text = await res.text();
    setMarkdown(text);
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4">🎬 ClipWeaver Lite</h1>
      <input type="file" accept="video/mp4" onChange={(e)=>setFile(e.target.files[0])}/>
      <button onClick={uploadAndAnalyze} className="mt-2 bg-purple-500 text-white p-2 rounded">
        Analyze Video
      </button>
      <pre className="bg-gray-100 p-4 mt-4 rounded">{markdown}</pre>
    </div>
  );
}


⸻

### 🧪 6. TEST

Run:
```bash
python backend/app.py
```

Then in Bolt.new’s dev mode (or npm run dev), upload a short video and watch the Markdown populate with scenes + captions.

⸻

### ✨ 7. Demo Script (for Hackathon Presentation)
	1.	“AI video generators are great — but they give you hundreds of short clips.”
	2.	“We built ClipWeaver — it automatically analyzes those clips and builds a storyboard you can actually use.”
	3.	(Upload a video) “Let’s run this through ClipWeaver Lite.”
	4.	“Here’s the generated storyboard — scenes detected, AI descriptions — ready for the next creative step.”

⸻

### 🏁 Stretch Goal (if time remains)
	•	Add “Generate JSON” button that converts Markdown into:
```json
{
  "story": [
    {"scene": 1, "file": "scene_001.png", "description": "..."},
    {"scene": 2, "file": "scene_002.png", "description": "..."}
  ]
}
```
	•	Show JSON in a neat card view.

⸻

### 🚀 Final Hackathon Motto (Short Version)

ClipWeaver — the AI storyboarder for AI videos.
Helps creators turn raw generative clips into structured storyboards using automatic scene detection and AI descriptions.
