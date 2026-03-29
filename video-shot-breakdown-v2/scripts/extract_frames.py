#!/usr/bin/env python3
"""
视频处理工具
支持视频截取（截取前N秒）和关键帧提取，用于短视频分镜拆解。

使用方法:
    # 截取视频前120秒（无损）
    python extract_frames.py video.mp4 --trim

    # 截取前60秒
    python extract_frames.py video.mp4 --trim --trim-duration 60

    # 截取并输出JSON
    python extract_frames.py video.mp4 --trim --output-json

    # 关键帧提取（混合模式，默认）
    python extract_frames.py video.mp4

    # 关键帧提取 + 自适应阈值
    python extract_frames.py video.mp4 --mode hybrid --adaptive

依赖:
    - Python 3.6+
    - ffmpeg (需预先安装)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def format_duration(seconds):
    """将秒数格式化为 HH:MM:SS"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def get_video_info(video_path):
    """获取视频完整技术参数，用于1:1复刻。

    返回视频流、音频流、容器的所有关键技术规格。
    """
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        video_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)

        # 查找视频流和音频流
        video_stream = None
        audio_stream = None
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'video' and video_stream is None:
                video_stream = stream
            elif stream.get('codec_type') == 'audio' and audio_stream is None:
                audio_stream = stream

        if not video_stream:
            return None

        fmt = info.get('format', {})
        duration = float(fmt.get('duration', 0))
        width = int(video_stream.get('width', 0))
        height = int(video_stream.get('height', 0))
        fps_str = video_stream.get('r_frame_rate', '30/1')

        # 解析帧率
        if '/' in fps_str:
            num, den = fps_str.split('/')
            fps = float(num) / float(den) if float(den) != 0 else 30
        else:
            fps = float(fps_str)

        file_size = float(fmt.get('size', 0))
        total_frames = int(video_stream.get('nb_frames', 0))
        if total_frames == 0 and duration > 0 and fps > 0:
            total_frames = int(duration * fps)

        # 计算宽高比
        dar = video_stream.get('display_aspect_ratio')
        if dar and dar != '0:0' and dar != 'N/A':
            aspect_ratio = dar
        else:
            from math import gcd
            g = gcd(width, height)
            aspect_ratio = f"{width // g}:{height // g}" if g > 0 else f"{width}:{height}"

        # 旋转信息
        rotation = 0
        for tag_key in ['rotation', 'rotate']:
            for source in [video_stream.get('tags', {}), video_stream.get('side_data_list', [])]:
                if isinstance(source, dict) and tag_key in source:
                    rotation = int(source[tag_key])
                    break
        # 检查 displaymatrix (新版本 ffmpeg)
        if rotation == 0:
            for sd in video_stream.get('side_data_list', []):
                if sd.get('side_data_type') == 'Display Matrix':
                    rot = sd.get('rotation')
                    if rot is not None:
                        rotation = int(rot)

        video_info = {
            'codec': video_stream.get('codec_name', 'unknown'),
            'codec_long': video_stream.get('codec_long_name', ''),
            'profile': video_stream.get('profile', ''),
            'level': video_stream.get('level'),
            'pixel_format': video_stream.get('pix_fmt', ''),
            'bit_depth': int(video_stream.get('bits_per_raw_sample', 0)) or None,
            'color_space': video_stream.get('color_space', ''),
            'color_primaries': video_stream.get('color_primaries', ''),
            'color_transfer': video_stream.get('color_transfer', ''),
            'bitrate_kbps': round(int(video_stream.get('bit_rate', 0)) / 1000) if video_stream.get('bit_rate') else None,
        }

        audio_info = None
        if audio_stream:
            channel_layout = audio_stream.get('channel_layout', '')
            if not channel_layout:
                ch_count = int(audio_stream.get('channels', 0))
                channel_map = {1: 'mono', 2: 'stereo', 6: '5.1', 8: '7.1'}
                channel_layout = channel_map.get(ch_count, f"{ch_count} channels")

            audio_info = {
                'codec': audio_stream.get('codec_name', 'unknown'),
                'codec_long': audio_stream.get('codec_long_name', ''),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': int(audio_stream.get('channels', 0)),
                'channel_layout': channel_layout,
                'bitrate_kbps': round(int(audio_stream.get('bit_rate', 0)) / 1000) if audio_stream.get('bit_rate') else None,
            }

        container_info = {
            'format_name': fmt.get('format_name', ''),
            'format_long_name': fmt.get('format_long_name', ''),
            'overall_bitrate_kbps': round(int(fmt.get('bit_rate', 0)) / 1000) if fmt.get('bit_rate') else None,
        }

        return {
            'file_path': video_path,
            'duration': round(duration, 3),
            'duration_formatted': format_duration(duration),
            'width': width,
            'height': height,
            'resolution': f"{width}x{height}",
            'aspect_ratio': aspect_ratio,
            'fps': round(fps, 3),
            'total_frames': total_frames,
            'rotation': rotation,
            'file_size_bytes': int(file_size),
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'video': video_info,
            'audio': audio_info,
            'container': container_info,
        }

    except subprocess.CalledProcessError as e:
        print(f"Error getting video info: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing video info: {e}")
        return None


def trim_video(video_path, output_path, trim_duration=120):
    """截取视频前N秒，使用流复制（无损，不重新编码）。

    Args:
        video_path: 原始视频路径
        output_path: 截取后输出路径
        trim_duration: 截取时长（秒），默认120秒

    Returns:
        dict with trim result, or None on failure
    """
    original_info = get_video_info(video_path)
    if not original_info:
        print("Error: Failed to get video info for trimming")
        return None

    original_duration = original_info['duration']

    # 如果视频不超过截取时长，无需截取
    if original_duration <= trim_duration:
        print(f"[trim] Video duration ({original_duration:.1f}s) <= {trim_duration}s, no trimming needed")
        return {
            'trimmed': False,
            'trim_duration_limit': trim_duration,
            'original': original_info,
            'trimmed': None,
            'trim_note': None
        }

    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-t', str(trim_duration),
        '-c', 'copy',
        '-y',
        output_path
    ]

    print(f"[trim] Trimming video: {original_duration:.1f}s → {trim_duration}s (first {trim_duration}s)")
    print(f"[trim] Output: {output_path}")

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)

        # 获取截取后视频的完整信息
        trimmed_info = get_video_info(output_path)
        if not trimmed_info:
            print("Warning: Could not verify trimmed video, but file was created")
            return None

        actual_duration = trimmed_info['duration']
        print(f"[trim] Success: trimmed to {actual_duration:.1f}s")

        return {
            'trimmed': True,
            'trim_duration_limit': trim_duration,
            'original': original_info,
            'trimmed_video': trimmed_info,
            'trim_note': f"原始视频 {format_duration(original_duration)}，已截取前 {format_duration(actual_duration)} 进行分析"
        }

    except subprocess.CalledProcessError as e:
        print(f"Error trimming video: {e}")
        print(f"ffmpeg stderr: {e.stderr if e.stderr else 'N/A'}")

        # 尝试降级：不使用 -c copy，而是重新编码
        print("[trim] Retrying with re-encoding...")
        fallback_cmd = [
            'ffmpeg',
            '-i', video_path,
            '-t', str(trim_duration),
            '-y',
            output_path
        ]
        try:
            subprocess.run(fallback_cmd, capture_output=True, text=True, check=True)
            trimmed_info = get_video_info(output_path)
            if not trimmed_info:
                return None

            actual_duration = trimmed_info['duration']
            print(f"[trim] Fallback success: trimmed to {actual_duration:.1f}s (re-encoded)")

            return {
                'trimmed': True,
                'trim_duration_limit': trim_duration,
                'original': original_info,
                'trimmed_video': trimmed_info,
                'trim_note': f"原始视频 {format_duration(original_duration)}，已截取前 {format_duration(actual_duration)} 进行分析（重新编码）"
            }
        except subprocess.CalledProcessError as e2:
            print(f"Error: Fallback trimming also failed: {e2}")
            return None


def calculate_extraction_params(duration):
    """根据视频时长计算提取参数"""
    if duration < 15:
        interval = 1
        max_frames = 15
    elif duration < 30:
        interval = 1.5
        max_frames = 20
    elif duration < 60:
        interval = 2
        max_frames = 25
    elif duration < 120:
        interval = 3
        max_frames = 30
    else:
        interval = 5
        max_frames = 40

    return interval, max_frames


def calculate_scale(width, height):
    """根据原始分辨率智能计算缩放尺寸，保留高清视频的细节"""
    long_edge = max(width, height)

    if long_edge >= 3840:  # 4K+
        target = 2560
    elif long_edge >= 2560:  # 2K/QHD
        target = 1920
    elif long_edge >= 1280:  # 1080p/720p
        target = 1280
    else:  # 低分辨率，保持原始尺寸
        return None  # 不缩放

    ratio = target / long_edge
    new_w = int(width * ratio)
    new_h = int(height * ratio)

    # 确保尺寸为偶数（ffmpeg 要求）
    new_w = new_w + (new_w % 2)
    new_h = new_h + (new_h % 2)

    return f"scale={new_w}:{new_h}"


def extract_frames_basic(video_path, output_dir, interval=None, max_frames=None):
    """基础模式：按时间间隔提取关键帧，保留时间码"""
    video_info = get_video_info(video_path)
    if not video_info:
        print("Failed to get video info")
        return None

    duration = video_info['duration']

    if interval is None or max_frames is None:
        interval, max_frames = calculate_extraction_params(duration)

    os.makedirs(output_dir, exist_ok=True)

    scale_filter = calculate_scale(video_info['width'], video_info['height'])
    vf_parts = [f'fps=1/{interval}']
    if scale_filter:
        vf_parts.append(scale_filter)
    vf = ','.join(vf_parts)

    output_pattern = os.path.join(output_dir, 'basic_%04d.jpg')

    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', vf,
        '-q:v', '2',
        '-frames:v', str(max_frames),
        '-y',
        output_pattern
    ]

    print(f"[basic] Extracting frames: interval={interval}s, max={max_frames}, scale={scale_filter or 'original'}")

    try:
        subprocess.run(cmd, capture_output=True, check=True)

        frames = sorted([f for f in os.listdir(output_dir) if f.startswith('basic_') and f.endswith('.jpg')])

        # 计算每帧的近似时间码
        frame_data = []
        for i, fname in enumerate(frames):
            timestamp = round(i * interval, 2)
            frame_data.append({
                'filename': fname,
                'timestamp': timestamp,
                'source': 'interval'
            })

        truncated = len(frames) >= max_frames
        if truncated:
            est_total = int(duration / interval)
            print(f"  ⚠ Truncation warning: extracted {len(frames)} frames, estimated {est_total} total (max_frames={max_frames})")

        result = {
            'success': True,
            'video_info': video_info,
            'extraction_params': {
                'mode': 'basic',
                'interval': interval,
                'max_frames': max_frames,
                'actual_frames': len(frames),
                'truncated': truncated
            },
            'output_dir': output_dir,
            'frames': frame_data
        }

        return result

    except subprocess.CalledProcessError as e:
        print(f"Error extracting frames: {e}")
        print(f"ffmpeg stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
        return None


def extract_frames_scene(video_path, output_dir, threshold=0.3, max_frames=40):
    """场景变化模式：检测场景变化提取关键帧，保留时间码"""
    video_info = get_video_info(video_path)
    if not video_info:
        print("Failed to get video info")
        return None

    os.makedirs(output_dir, exist_ok=True)

    scale_filter = calculate_scale(video_info['width'], video_info['height'])
    vf_parts = [f"select='gt(scene\\,{threshold})'"]
    if scale_filter:
        vf_parts.append(scale_filter)
    vf = ','.join(vf_parts)

    output_pattern = os.path.join(output_dir, 'scene_%04d.jpg')

    # 使用 showinfo 滤镜获取帧时间码
    info_vf = vf + ",showinfo"

    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', info_vf,
        '-vsync', 'vfr',
        '-q:v', '2',
        '-frames:v', str(max_frames),
        '-y',
        output_pattern
    ]

    print(f"[scene] Extracting frames: threshold={threshold}, max={max_frames}, scale={scale_filter or 'original'}")

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)

        frames = sorted([f for f in os.listdir(output_dir) if f.startswith('scene_') and f.endswith('.jpg')])

        # 从 ffmpeg stderr 解析 showinfo 获取精确时间码
        timestamp_map = {}
        showinfo_pattern = re.compile(r'n:(\d+).*?pts_time:([\d.]+)')
        for line in proc.stderr.split('\n'):
            match = showinfo_pattern.search(line)
            if match:
                idx = int(match.group(1))
                ts = float(match.group(2))
                timestamp_map[idx] = ts

        frame_data = []
        for i, fname in enumerate(frames):
            ts = timestamp_map.get(i, round(i * (video_info['duration'] / max(len(frames), 1)), 2))
            frame_data.append({
                'filename': fname,
                'timestamp': round(ts, 2),
                'source': 'scene_change'
            })

        truncated = len(frames) >= max_frames
        if truncated:
            print(f"  ⚠ Truncation warning: hit max_frames={max_frames} limit, some scene changes may be missed")

        result = {
            'success': True,
            'video_info': video_info,
            'extraction_params': {
                'mode': 'scene',
                'threshold': threshold,
                'max_frames': max_frames,
                'actual_frames': len(frames),
                'truncated': truncated
            },
            'output_dir': output_dir,
            'frames': frame_data
        }

        return result

    except subprocess.CalledProcessError as e:
        print(f"Error extracting frames: {e}")
        print(f"ffmpeg stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
        return None


def analyze_scene_complexity(video_path, video_info):
    """单次 ffmpeg 分析场景复杂度，自适应确定最优阈值。

    原理：用较低阈值 (0.1) 做一次场景检测，统计通过筛选的帧数，
    与预期镜头数比较。比值越高说明视频变化越密集（快剪/手持晃动），
    需要更高阈值过滤噪声；比值越低说明变化稀疏，需要更低阈值捕捉细节。
    """
    duration = video_info['duration']
    estimated_shots = max(3, int(duration / 4))

    cmd = [
        'ffmpeg', '-i', video_path,
        '-vf', "select='gt(scene\\,0.1)',showinfo",
        '-vsync', 'vfr',
        '-f', 'null', '-'
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)

        showinfo_pattern = re.compile(r'n:(\d+).*?pts_time:([\d.]+)')
        detected_count = 0
        for line in proc.stderr.split('\n'):
            if showinfo_pattern.search(line):
                detected_count += 1

        ratio = detected_count / max(estimated_shots, 1)

        if ratio <= 1.0:
            return 0.15
        elif ratio <= 2.5:
            return 0.2
        elif ratio <= 5.0:
            return 0.3
        else:
            return 0.4

    except Exception:
        return 0.3


def extract_frames_hybrid(video_path, output_dir, max_frames=40, adaptive=False, threshold=0.3):
    """混合模式：结合均匀间隔 + 场景变化检测，确保每个镜头都有代表帧

    策略：
    1. 通道 A：均匀间隔提取（保证时间段覆盖）
    2. 通道 B：场景变化检测（捕捉转场点）
    3. 合并去重：时间差 < merge_tolerance 秒的帧视为重复
    """
    video_info = get_video_info(video_path)
    if not video_info:
        print("Failed to get video info")
        return None

    duration = video_info['duration']
    interval, _ = calculate_extraction_params(duration)

    os.makedirs(output_dir, exist_ok=True)

    # 自适应阈值
    if adaptive:
        threshold = analyze_scene_complexity(video_path, video_info)
        print(f"[hybrid] Adaptive threshold: {threshold}")

    # --- 通道 A：均匀间隔 ---
    scale_filter = calculate_scale(video_info['width'], video_info['height'])
    vf_parts_a = [f'fps=1/{interval}']
    if scale_filter:
        vf_parts_a.append(scale_filter)
    vf_a = ','.join(vf_parts_a)

    basic_pattern = os.path.join(output_dir, 'basic_%04d.jpg')
    cmd_a = [
        'ffmpeg', '-i', video_path,
        '-vf', vf_a,
        '-q:v', '2',
        '-y', basic_pattern
    ]

    # --- 通道 B：场景变化 ---
    vf_parts_b = [f"select='gt(scene\\,{threshold})'"]
    if scale_filter:
        vf_parts_b.append(scale_filter)
    vf_b = ','.join(vf_parts_b) + ',showinfo'

    scene_pattern = os.path.join(output_dir, 'scene_%04d.jpg')
    cmd_b = [
        'ffmpeg', '-i', video_path,
        '-vf', vf_b,
        '-vsync', 'vfr',
        '-q:v', '2',
        '-y', scene_pattern
    ]

    print(f"[hybrid] Channel A: interval={interval}s")
    print(f"[hybrid] Channel B: scene threshold={threshold}")

    try:
        # 两个通道并行提取
        proc_a = subprocess.run(cmd_a, capture_output=True, text=True, check=True)
        proc_b = subprocess.run(cmd_b, capture_output=True, text=True, check=True)

        # 收集通道 A 帧（均匀间隔）
        basic_frames = sorted([f for f in os.listdir(output_dir) if f.startswith('basic_') and f.endswith('.jpg')])
        basic_data = []
        for i, fname in enumerate(basic_frames):
            basic_data.append({
                'filename': fname,
                'timestamp': round(i * interval, 2),
                'source': 'interval'
            })

        # 收集通道 B 帧（场景变化），解析时间码
        scene_frames = sorted([f for f in os.listdir(output_dir) if f.startswith('scene_') and f.endswith('.jpg')])
        timestamp_map = {}
        showinfo_pattern = re.compile(r'n:(\d+).*?pts_time:([\d.]+)')
        for line in proc_b.stderr.split('\n'):
            match = showinfo_pattern.search(line)
            if match:
                idx = int(match.group(1))
                ts = float(match.group(2))
                timestamp_map[idx] = ts

        scene_data = []
        for i, fname in enumerate(scene_frames):
            ts = timestamp_map.get(i, round(i * (duration / max(len(scene_frames), 1)), 2))
            scene_data.append({
                'filename': fname,
                'timestamp': round(ts, 2),
                'source': 'scene_change'
            })

        # --- 合并去重 ---
        merge_tolerance = min(interval * 0.6, 1.0)

        all_frames = []
        all_frames.extend(basic_data)
        all_frames.extend(scene_data)
        all_frames.sort(key=lambda x: x['timestamp'])

        merged = []
        for frame in all_frames:
            is_dup = False
            for existing in merged:
                if abs(frame['timestamp'] - existing['timestamp']) < merge_tolerance:
                    if frame['source'] == 'scene_change' and existing['source'] == 'interval':
                        merged.remove(existing)
                        merged.append(frame)
                    is_dup = True
                    break
            if not is_dup:
                merged.append(frame)

        merged.sort(key=lambda x: x['timestamp'])

        # 应用 max_frames 限制
        truncated = False
        if len(merged) > max_frames:
            scene_frames_merged = [f for f in merged if f['source'] == 'scene_change']
            interval_frames_merged = [f for f in merged if f['source'] == 'interval']

            if len(scene_frames_merged) >= max_frames:
                step = len(scene_frames_merged) / max_frames
                selected_indices = [int(i * step) for i in range(max_frames)]
                final_frames = [scene_frames_merged[i] for i in selected_indices]
            else:
                remaining = max_frames - len(scene_frames_merged)
                if remaining < len(interval_frames_merged):
                    step = len(interval_frames_merged) / remaining
                    selected_indices = [int(i * step) for i in range(remaining)]
                    interval_frames_merged = [interval_frames_merged[i] for i in selected_indices]
                final_frames = scene_frames_merged + interval_frames_merged

            final_frames.sort(key=lambda x: x['timestamp'])
            merged = final_frames
            truncated = True
            print(f"  ⚠ Truncation: reduced to {max_frames} frames (prioritized scene changes)")

        # 删除未被选中的帧文件
        selected_files = {f['filename'] for f in merged}
        for fname in os.listdir(output_dir):
            if fname.endswith('.jpg') and fname not in selected_files:
                os.remove(os.path.join(output_dir, fname))

        # 重新编号（统一前缀）
        for i, frame in enumerate(merged):
            old_path = os.path.join(output_dir, frame['filename'])
            new_name = f"frame_{i + 1:04d}.jpg"
            new_path = os.path.join(output_dir, new_name)
            if old_path != new_path:
                os.rename(old_path, new_path)
                frame['filename'] = new_name

        result = {
            'success': True,
            'video_info': video_info,
            'extraction_params': {
                'mode': 'hybrid',
                'interval': interval,
                'threshold': threshold,
                'max_frames': max_frames,
                'actual_frames': len(merged),
                'truncated': truncated,
                'stats': {
                    'interval_frames': len(basic_data),
                    'scene_frames': len(scene_data),
                    'merged_frames': len(merged),
                    'duplicates_removed': len(basic_data) + len(scene_data) - len(merged)
                }
            },
            'output_dir': output_dir,
            'frames': merged
        }

        return result

    except subprocess.CalledProcessError as e:
        print(f"Error extracting frames: {e}")
        print(f"ffmpeg stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Video processing tool: trim and extract key frames',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Trim video to first 2 minutes (lossless)
    python extract_frames.py video.mp4 --trim

    # Trim to first 60 seconds
    python extract_frames.py video.mp4 --trim --trim-duration 60

    # Trim and output as JSON
    python extract_frames.py video.mp4 --trim --output-json

    # Extract key frames (hybrid mode, default)
    python extract_frames.py video.mp4

    # Extract key frames with adaptive threshold
    python extract_frames.py video.mp4 --mode hybrid --adaptive

    # Extract key frames from a specific output dir
    python extract_frames.py video.mp4 output_frames/
        """
    )

    parser.add_argument('video_path', help='Path to the video file')
    parser.add_argument('output_path', nargs='?', default=None,
                        help='Output path: trimmed video file (--trim) or frame output directory (default: auto-generated)')
    parser.add_argument('--trim', action='store_true',
                        help='Trim video to first N seconds (default: 120s)')
    parser.add_argument('--trim-duration', type=int, default=120,
                        help='Trim duration in seconds (default: 120)')
    parser.add_argument('--mode', choices=['basic', 'scene', 'hybrid'], default='hybrid',
                        help='Frame extraction mode (ignored with --trim)')
    parser.add_argument('--interval', type=float, default=None,
                        help='Frame extraction interval in seconds (basic/hybrid mode)')
    parser.add_argument('--max-frames', type=int, default=None,
                        help='Maximum number of frames to extract')
    parser.add_argument('--threshold', type=float, default=0.3,
                        help='Scene change threshold (scene/hybrid mode, 0-1)')
    parser.add_argument('--adaptive', action='store_true',
                        help='Auto-detect optimal scene threshold (hybrid mode)')
    parser.add_argument('--output-json', action='store_true',
                        help='Output result as JSON')

    args = parser.parse_args()

    # 检查视频文件是否存在
    if not os.path.exists(args.video_path):
        print(f"Error: Video file not found: {args.video_path}")
        sys.exit(1)

    # --- 截取模式 ---
    if args.trim:
        if args.output_path is None:
            video_name = Path(args.video_path).stem
            ext = Path(args.video_path).suffix
            args.output_path = f"{video_name}_trimmed{ext}"

        result = trim_video(args.video_path, args.output_path, args.trim_duration)

        if result:
            if args.output_json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                if result['trimmed']:
                    orig = result['original']
                    trim_vid = result['trimmed_video']
                    print(f"\n{'='*60}")
                    print(f"  Trim Complete")
                    print(f"{'='*60}")
                    print(f"  Original:  {orig['duration_formatted']} ({orig['duration']:.1f}s)")
                    print(f"  Trimmed:   {trim_vid['duration_formatted']} ({trim_vid['duration']:.1f}s)")
                    print(f"  Output:    {trim_vid['file_path']}")
                    print(f"{'─'*60}")
                    print(f"  Video:     {orig['resolution']} @ {orig['fps']:.1f}fps, {orig['video']['codec']}")
                    if orig['video'].get('bitrate_kbps'):
                        print(f"  Bitrate:   {orig['video']['bitrate_kbps']} kbps")
                    if orig.get('audio'):
                        print(f"  Audio:     {orig['audio']['codec']} {orig['audio']['sample_rate']}Hz {orig['audio']['channel_layout']}")
                    print(f"  Size:      {trim_vid['file_size_mb']} MB")
                    print(f"{'='*60}")
                else:
                    orig = result['original']
                    print(f"\nNo trimming needed (video is {orig['duration_formatted']})")
                    print(f"  Resolution: {orig['resolution']}, FPS: {orig['fps']}, Codec: {orig['video']['codec']}")
        else:
            print("Trim failed")
            sys.exit(1)

    # --- 关键帧提取模式 ---
    else:
        if args.output_path is None:
            video_name = Path(args.video_path).stem
            args.output_path = f"frames_{video_name}"

        # 计算默认 max_frames
        if args.max_frames is None:
            video_info = get_video_info(args.video_path)
            if video_info:
                _, args.max_frames = calculate_extraction_params(video_info['duration'])
            else:
                args.max_frames = 30

        if args.mode == 'basic':
            result = extract_frames_basic(
                args.video_path,
                args.output_path,
                interval=args.interval,
                max_frames=args.max_frames
            )
        elif args.mode == 'scene':
            result = extract_frames_scene(
                args.video_path,
                args.output_path,
                threshold=args.threshold,
                max_frames=args.max_frames
            )
        else:  # hybrid
            result = extract_frames_hybrid(
                args.video_path,
                args.output_path,
                max_frames=args.max_frames,
                adaptive=args.adaptive,
                threshold=args.threshold
            )

        if result:
            if args.output_json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                vi = result['video_info']
                params = result['extraction_params']
                print(f"\n{'='*60}")
                print(f"  Extraction Complete")
                print(f"{'='*60}")
                print(f"  Mode:       {params['mode']}")
                print(f"  Frames:     {params['actual_frames']} extracted")
                if params.get('stats'):
                    stats = params['stats']
                    print(f"  Stats:      {stats['interval_frames']} interval + {stats['scene_frames']} scene → {stats['merged_frames']} merged ({stats['duplicates_removed']} duplicates removed)")
                print(f"{'─'*60}")
                print(f"  Duration:   {vi['duration_formatted']} ({vi['duration']:.1f}s)")
                print(f"  Resolution: {vi['resolution']} ({vi['aspect_ratio']})")
                print(f"  FPS:        {vi['fps']}")
                print(f"  Frames:     {vi['total_frames']} total")
                print(f"  Video:      {vi['video']['codec']}", end='')
                if vi['video'].get('profile'):
                    print(f" ({vi['video']['profile']})", end='')
                print()
                if vi.get('audio'):
                    print(f"  Audio:      {vi['audio']['codec']} {vi['audio']['sample_rate']}Hz {vi['audio']['channel_layout']}")
                print(f"  Size:       {vi['file_size_mb']} MB")
                print(f"{'─'*60}")
                print(f"  Output:     {result['output_dir']}")
                if params.get('truncated'):
                    print(f"  ⚠ Truncated at max_frames={params['max_frames']}")
                print(f"{'='*60}")
        else:
            print("Frame extraction failed")
            sys.exit(1)


if __name__ == '__main__':
    main()
