import os
import subprocess
import glob
import json
import logging

logger = logging.getLogger(__name__)

def get_video_duration(video_path):
    """Get video duration in seconds"""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json", 
        "-show_format", video_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        logger.info(f"📏 Video duration: {duration:.2f} seconds")
        return duration
    except Exception as e:
        logger.error(f"❌ Error getting video duration: {e}")
        return 0

def extract_scenes(video_path, output_dir, scene_threshold=0.4, max_scenes=10, min_scenes=2):
    """
    Extract scene changes from video using ffmpeg with intelligent fallback
    
    Args:
        video_path: Path to input video file
        output_dir: Directory to save scene thumbnails
        scene_threshold: Sensitivity for scene detection (0.1-1.0)
        max_scenes: Maximum number of scenes to extract
        min_scenes: Minimum number of scenes for longer videos
        
    Returns:
        List of paths to extracted scene images
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Get video duration
    duration = get_video_duration(video_path)
    
    # Try scene detection first
    logger.info(f"🔍 Attempting automatic scene detection with threshold {scene_threshold}")
    cmd = [
        "ffmpeg", "-i", video_path,
        "-filter_complex", f"select='gt(scene,{scene_threshold})',metadata=print",
        "-vsync", "vfr", 
        f"{output_dir}/scene_%03d.png"
    ]
    
    logger.info(f"🔧 FFmpeg command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logger.info(f"📝 FFmpeg stdout: {result.stdout.decode()[:200]}...")
        logger.info(f"📝 FFmpeg stderr: {result.stderr.decode()[:200]}...")
        scenes = sorted(glob.glob(f"{output_dir}/scene_*.png"))
        
        # If we got scenes and they're reasonable, use them
        if len(scenes) > 0 and len(scenes) <= max_scenes:
            logger.info(f"✅ Automatic scene detection found {len(scenes)} scenes")
            return scenes
        elif len(scenes) > max_scenes:
            logger.info(f"⚠️ Too many scenes detected ({len(scenes)}), using fallback")
        else:
            logger.info(f"⚠️ No scenes detected automatically, using fallback")
            
    except subprocess.CalledProcessError as e:
        logger.info(f"⚠️ Scene detection failed, using fallback: {e}")
        logger.info(f"📝 FFmpeg error stderr: {e.stderr.decode() if e.stderr else 'No stderr'}")
        logger.info(f"📝 FFmpeg error stdout: {e.stdout.decode() if e.stdout else 'No stdout'}")
    
    # Clean up any partial results
    for f in glob.glob(f"{output_dir}/scene_*.png"):
        os.remove(f)
    
    # Fallback: Extract scenes based on video length
    if duration > 0:
        # For videos longer than 15s, ensure at least 3 scenes
        if duration > 15:
            # Extract scenes at regular intervals, minimum 3 for longer videos
            min_scenes_for_long = max(3, min_scenes)
            interval = max(duration / min_scenes_for_long, 3)  # At least 3s apart
            num_scenes = min(int(duration / interval), max_scenes)
            if num_scenes < min_scenes_for_long and duration > 15:
                num_scenes = min(min_scenes_for_long, max_scenes)
            logger.info(f"📐 Long video ({duration:.1f}s): extracting {num_scenes} scenes at {duration/num_scenes:.1f}s intervals")
        elif duration > 10:
            # Extract scenes at regular intervals
            interval = max(duration / min_scenes, 3)  # At least 3s apart
            num_scenes = min(int(duration / interval), max_scenes)
            logger.info(f"📐 Medium video ({duration:.1f}s): extracting {num_scenes} scenes at {interval:.1f}s intervals")
        else:
            # For short videos, extract fewer scenes
            num_scenes = max(1, min(int(duration / 5), max_scenes))
            logger.info(f"📐 Short video ({duration:.1f}s): extracting {num_scenes} scenes")
        
        # Extract at regular intervals
        for i in range(num_scenes):
            timestamp = (i + 0.5) * duration / num_scenes  # Offset by 0.5 to avoid start/end
            cmd = [
                "ffmpeg", "-i", video_path, "-ss", str(timestamp),
                "-vframes", "1", f"{output_dir}/scene_{i+1:03d}.png"
            ]
            logger.info(f"🎞️ Extracting scene {i+1} at {timestamp:.1f}s")
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Get all extracted scenes
    scenes = sorted(glob.glob(f"{output_dir}/scene_*.png"))
    logger.info(f"📊 Final result: {len(scenes)} scenes extracted")
    return scenes
