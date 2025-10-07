# 🎬 ClipWeaver

> **AI Storyboarder for AI Videos**  
> Helping creators turn fragmented AI-generated clips into cohesive stories.

---

## 🚀 Overview

**ClipWeaver** is an AI-assisted video composition tool that bridges the gap between **AI video generation** (like Pika, Runway, or Veo) and **actual storytelling**.

Instead of generating new clips, ClipWeaver **analyzes**, **organizes**, and **weaves** existing clips into structured narratives. It detects scenes, describes them with AI, and generates storyboards or even final composite videos.

This project was prototyped during **#SFTechWeek — [Vibe Space Hackathon](https://partiful.com/e/DHxYqtnTfGg5O0IXn5L4)** as a 2-hour demo, and is now expanding into a full-featured AI storytelling framework.

---

## 🌟 Motto

> **My app ClipWeaver is an AI-assisted video composer that helps creators turn short AI-generated clips into cohesive stories using automated scene analysis, narrative structuring, and smart editing guidance.**

---

## 🧩 Problem

AI video tools like **Pika**, **Runway**, or **Veo** are incredible — but they leave you with **dozens of disconnected 3–8 second clips**.  
Turning those into a meaningful video story still takes hours of manual editing.

---

## 💡 Solution

ClipWeaver automates post-generation storytelling in four steps:

1. **Analyze Clips** — detect scenes, extract screenshots, transcribe voice (if any).
2. **Describe in Markdown** — summarize each scene with AI-generated text and image previews.
3. **Generate Scenario JSON** — define sequence, transitions, and optional audio plan.
4. **Compose Final Video** — use `ffmpeg` or compatible editor to merge chosen parts.

---

## 🧠 Secret Sauce

Unlike AI video generators, ClipWeaver doesn’t make new content.  
It **understands** and **curates** what’s already generated — turning chaos into story structure.

---

## 🧱 Tech Stack

| Component | Description | Tools |
|------------|--------------|--------|
| **Backend** | Scene detection, AI captioning | Python, Flask, ffmpeg, OpenAI API |
| **Frontend** | Upload, display storyboard | Bolt.new (React/Next.js) |
| **Optional Server** | For video composition | Ubuntu + Docker |
| **AI** | Scene understanding & text generation | GPT-4/5 (vision mode) |
| **File Format** | Scene catalog | Markdown + JSON |

---

## ⚡ Hackathon MVP: *ClipWeaver Lite*

A 2-hour demo built for **[Vibe Space](https://partiful.com/e/DHxYqtnTfGg5O0IXn5L4) @ #SFTechWeek**  
> “From raw clip to AI-generated storyboard — in one click.”

### 🎯 MVP Goals
- Upload a short video
- Auto-detect scene cuts with `ffmpeg`
- Generate keyframe thumbnails
- Use GPT to describe each scene
- Export to a readable Markdown storyboard

### 🧩 Features Implemented
✅ Scene detection  
✅ Screenshot extraction  
✅ AI text description  
✅ Markdown export  
✅ Simple Bolt.new UI  

### 🖥️ Folder Structure
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
└── sample.mp4
```

### 🛠️ Setup Instructions

#### Backend
```bash
cd backend
pip install -r requirements.txt
sudo apt install ffmpeg
export OPENAI_API_KEY="your_key_here"
python app.py

Frontend (Bolt.new)
	•	Create a new Bolt project.
	•	Use the provided App.jsx snippet to connect to the backend.
	•	Upload a video → click Analyze Video → view generated Markdown.

⸻

🧩 Example Output

Input: sample.mp4 (10-second AI-generated clip)
Output: storyboard.md

# Storyboard

## Scene 1
![Scene 1](scene_001.png)
- Description: A person walks through a neon-lit alley, camera slowly pans left.

## Scene 2
![Scene 2](scene_002.png)
- Description: The same character stops under a flickering sign, looking up as rain starts to fall.


⸻

🌍 Full Project Vision

ClipWeaver (Full Version) is a modular platform that takes multiple clips, catalogs them into structured Markdown, and then automatically builds cohesive stories with optional narration and soundtrack.

🧩 Full Workflow

Step	Description	Output
1️⃣	Scene Analysis	Markdown with image + transcript
2️⃣	Scenario Generation	JSON defining clip order, timing, audio
3️⃣	Storyboard Visualization	Interactive editor in web UI
4️⃣	Final Composition	Rendered .mp4 video assembled via ffmpeg


⸻

🧩 Future Roadmap

Phase	Feature	Status
MVP	Scene detection + Markdown output	✅ Done
v0.2	Whisper-based voice transcription	🕓 Planned
v0.3	JSON-based scenario editor	🕓 Planned
v0.4	FFMPEG-based final video generation	🕓 Planned
v1.0	Full AI-assisted story composer (public launch)	🔜 Coming soon


⸻

🧠 Potential Integrations
	•	Input sources: Runway, Pika, Veo, Kling, YouTube shorts
	•	Output targets: CapCut, DaVinci Resolve, Premiere Pro XML
	•	Plugins: “Send to ClipWeaver” browser extension

⸻

🎯 Elevator Pitch

“We built ClipWeaver, an AI-assisted video composer that helps creators turn fragmented AI-generated clips into cohesive stories.
Instead of making new videos, ClipWeaver understands and organizes what you already have — automatically detecting scenes, describing them, and building storyboards you can actually use.”

⸻

🧭 Motto (Short Version)

ClipWeaver — the AI Storyboarder for AI Videos.

⸻

👤 Authors

Denis Bystruev, Valerii Egorov
Built during #SFTechWeek — [Vibe Space Hackathon](https://partiful.com/e/DHxYqtnTfGg5O0IXn5L4)
Location: Frontier Tower, San Francisco
Date: October 7, 2025

⸻

📜 License

MIT License © 2025 Denis Bystruev, Valerii Egorov
You’re free to fork, remix, or integrate this idea into your AI video tools.