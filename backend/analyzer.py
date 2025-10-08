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

def extract_scene_screenshots(video_path, output_dir, scene_start, scene_end, scene_num):
    """Extract 3 screenshots from a scene: beginning, middle, end"""
    duration = scene_end - scene_start
    
    # Adjust timestamps to avoid transition frames
    offset = min(0.5, duration * 0.1)  # 10% of scene duration or 0.5s, whichever is smaller
    
    timestamps = [
        scene_start + offset,           # Beginning (slightly forward)
        scene_start + duration / 2,     # Middle
        scene_end - offset              # End (slightly back)
    ]
    
    positions = ['beginning', 'middle', 'end']
    screenshots = []
    
    for i, (timestamp, position) in enumerate(zip(timestamps, positions)):
        filename = f"scene_{scene_num:03d}_{position}.png"
        filepath = os.path.join(output_dir, filename)
        
        cmd = [
            "ffmpeg", "-i", video_path, "-ss", str(timestamp),
            "-vframes", "1", filepath, "-y"
        ]
        
        logger.info(f"🎞️ Extracting scene {scene_num} {position} at {timestamp:.1f}s")
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if os.path.exists(filepath):
            screenshots.append(filepath)
    
    return screenshots

def extract_scenes(video_path, output_dir, scene_threshold=0.06, max_scenes=10, min_scenes=2):
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
    
    # Try scene detection first to get scene boundaries
    logger.info(f"🔍 Attempting automatic scene detection with threshold {scene_threshold}")
    cmd = [
        "ffmpeg", "-i", video_path,
        "-filter_complex", f"select='gt(scene,{scene_threshold})',metadata=print",
        "-f", "null", "-"
    ]
    
    logger.info(f"🔧 FFmpeg command: {' '.join(cmd)}")
    
    scene_times = [0]  # Start with beginning of video
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        logger.info(f"📝 FFmpeg stderr: {result.stderr[:200]}...")
        
        # Parse scene change timestamps from stderr
        for line in result.stderr.split('\n'):
            if 'pts_time:' in line and 'scene_score' in line:
                try:
                    pts_time = float(line.split('pts_time:')[1].split()[0])
                    scene_times.append(pts_time)
                except:
                    continue
        
        scene_times.append(duration)  # End with end of video
        scene_times = sorted(list(set(scene_times)))  # Remove duplicates and sort
        
        if len(scene_times) > 2 and len(scene_times) - 1 <= max_scenes:
            logger.info(f"✅ Automatic scene detection found {len(scene_times) - 1} scenes")
        else:
            logger.info(f"⚠️ Scene detection found {len(scene_times) - 1} scenes, using fallback")
            raise Exception("Using fallback")
            
    except Exception as e:
        logger.info(f"⚠️ Scene detection failed, using fallback: {e}")
        
        # Fallback: Create scene boundaries based on video length
        if duration > 15:
            min_scenes_for_long = max(3, min_scenes)
            num_scenes = min(min_scenes_for_long, max_scenes)
            logger.info(f"📐 Long video ({duration:.1f}s): creating {num_scenes} scenes")
        elif duration > 10:
            num_scenes = min(min_scenes, max_scenes)
            logger.info(f"📐 Medium video ({duration:.1f}s): creating {num_scenes} scenes")
        else:
            num_scenes = max(1, min(int(duration / 5), max_scenes))
            logger.info(f"📐 Short video ({duration:.1f}s): creating {num_scenes} scenes")
        
        # Create evenly spaced scene boundaries
        scene_times = [i * duration / num_scenes for i in range(num_scenes + 1)]
    
    # Extract 3 screenshots per scene
    all_screenshots = []
    for i in range(len(scene_times) - 1):
        scene_start = scene_times[i]
        scene_end = scene_times[i + 1]
        scene_num = i + 1
        
        logger.info(f"🎬 Processing scene {scene_num}: {scene_start:.1f}s - {scene_end:.1f}s")
        screenshots = extract_scene_screenshots(video_path, output_dir, scene_start, scene_end, scene_num)
        all_screenshots.extend(screenshots)
    
    logger.info(f"📊 Final result: {len(scene_times) - 1} scenes, {len(all_screenshots)} screenshots extracted")
    return all_screenshots
