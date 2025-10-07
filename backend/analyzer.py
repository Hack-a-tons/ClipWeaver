import os
import subprocess
import glob

def extract_scenes(video_path, output_dir):
    """
    Extract scene changes from video using ffmpeg
    
    Args:
        video_path: Path to input video file
        output_dir: Directory to save scene thumbnails
        
    Returns:
        List of paths to extracted scene images
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Detect scene changes using ffmpeg
    # gt(scene,0.4) means scenes with change > 0.4 (40% different)
    cmd = [
        "ffmpeg", "-i", video_path,
        "-filter_complex", "select='gt(scene,0.4)',metadata=print",
        "-vsync", "vfr", 
        f"{output_dir}/scene_%03d.png"
    ]
    
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e}")
        # If scene detection fails, extract frames at regular intervals
        fallback_cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", "fps=1/5",  # 1 frame every 5 seconds
            f"{output_dir}/scene_%03d.png"
        ]
        subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Get all extracted scenes
    scenes = sorted(glob.glob(f"{output_dir}/scene_*.png"))
    return scenes
