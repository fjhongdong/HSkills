#!/usr/bin/env python3
"""
视频关键帧提取工具
用于从视频中提取关键帧图片，支持按时间间隔和场景变化两种模式

使用方法:
    python extract_frames.py <视频路径> [输出目录] [--mode <basic|scene>]

依赖:
    - Python 3.6+
    - ffmpeg (需预先安装)
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def get_video_info(video_path):
    """获取视频基本信息"""
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

        # 查找视频流
        video_stream = None
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break

        if not video_stream:
            return None

        duration = float(info.get('format', {}).get('duration', 0))
        width = int(video_stream.get('width', 0))
        height = int(video_stream.get('height', 0))
        fps_str = video_stream.get('r_frame_rate', '30/1')

        # 解析帧率
        if '/' in fps_str:
            num, den = fps_str.split('/')
            fps = float(num) / float(den) if float(den) != 0 else 30
        else:
            fps = float(fps_str)

        return {
            'duration': duration,
            'width': width,
            'height': height,
            'fps': fps,
            'resolution': f"{width}x{height}"
        }

    except subprocess.CalledProcessError as e:
        print(f"Error getting video info: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing video info: {e}")
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


def extract_frames_basic(video_path, output_dir, interval=None, max_frames=None):
    """基础模式：按时间间隔提取关键帧"""
    # 获取视频信息
    video_info = get_video_info(video_path)
    if not video_info:
        print("Failed to get video info")
        return None

    duration = video_info['duration']

    # 计算提取参数
    if interval is None or max_frames is None:
        interval, max_frames = calculate_extraction_params(duration)

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 构建ffmpeg命令
    # fps=1/interval 表示每interval秒提取一帧
    output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')

    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f'fps=1/{interval},scale=1280:-1',
        '-q:v', '2',
        '-frames:v', str(max_frames),
        '-y',  # 覆盖已存在的文件
        output_pattern
    ]

    print(f"Extracting frames with interval: {interval}s, max frames: {max_frames}")
    print(f"Command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, capture_output=True, check=True)

        # 获取提取的帧列表
        frames = sorted([f for f in os.listdir(output_dir) if f.endswith('.jpg')])

        result = {
            'success': True,
            'video_info': video_info,
            'extraction_params': {
                'mode': 'basic',
                'interval': interval,
                'max_frames': max_frames,
                'actual_frames': len(frames)
            },
            'output_dir': output_dir,
            'frames': frames
        }

        return result

    except subprocess.CalledProcessError as e:
        print(f"Error extracting frames: {e}")
        print(f"ffmpeg stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
        return None


def extract_frames_scene(video_path, output_dir, threshold=0.3, max_frames=40):
    """场景变化模式：检测场景变化提取关键帧"""
    # 获取视频信息
    video_info = get_video_info(video_path)
    if not video_info:
        print("Failed to get video info")
        return None

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')

    # 使用select滤镜检测场景变化
    # gt(scene,threshold) 表示场景变化超过阈值时提取帧
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"select='gt(scene\\,{threshold})',scale=1280:-1",
        '-vsync', 'vfr',  # 可变帧率
        '-q:v', '2',
        '-frames:v', str(max_frames),
        '-y',
        output_pattern
    ]

    print(f"Extracting frames with scene detection (threshold: {threshold})")
    print(f"Command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, capture_output=True, check=True)

        # 获取提取的帧列表
        frames = sorted([f for f in os.listdir(output_dir) if f.endswith('.jpg')])

        result = {
            'success': True,
            'video_info': video_info,
            'extraction_params': {
                'mode': 'scene',
                'threshold': threshold,
                'max_frames': max_frames,
                'actual_frames': len(frames)
            },
            'output_dir': output_dir,
            'frames': frames
        }

        return result

    except subprocess.CalledProcessError as e:
        print(f"Error extracting frames: {e}")
        print(f"ffmpeg stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Extract key frames from video',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python extract_frames.py video.mp4
    python extract_frames.py video.mp4 output_frames/
    python extract_frames.py video.mp4 output_frames/ --mode scene
    python extract_frames.py video.mp4 output_frames/ --mode basic --interval 2
        """
    )

    parser.add_argument('video_path', help='Path to the video file')
    parser.add_argument('output_dir', nargs='?', default=None,
                        help='Output directory for frames (default: frames_<video_name>/)')
    parser.add_argument('--mode', choices=['basic', 'scene'], default='basic',
                        help='Extraction mode: basic (interval) or scene (scene change detection)')
    parser.add_argument('--interval', type=float, default=None,
                        help='Frame extraction interval in seconds (basic mode only)')
    parser.add_argument('--max-frames', type=int, default=None,
                        help='Maximum number of frames to extract')
    parser.add_argument('--threshold', type=float, default=0.3,
                        help='Scene change threshold (scene mode only, 0-1)')
    parser.add_argument('--output-json', action='store_true',
                        help='Output result as JSON')

    args = parser.parse_args()

    # 检查视频文件是否存在
    if not os.path.exists(args.video_path):
        print(f"Error: Video file not found: {args.video_path}")
        sys.exit(1)

    # 设置输出目录
    if args.output_dir is None:
        video_name = Path(args.video_path).stem
        args.output_dir = f"frames_{video_name}"

    # 根据模式提取关键帧
    if args.mode == 'basic':
        result = extract_frames_basic(
            args.video_path,
            args.output_dir,
            interval=args.interval,
            max_frames=args.max_frames
        )
    else:
        result = extract_frames_scene(
            args.video_path,
            args.output_dir,
            threshold=args.threshold,
            max_frames=args.max_frames
        )

    if result:
        if args.output_json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\nExtraction complete!")
            print(f"  - Frames extracted: {result['extraction_params']['actual_frames']}")
            print(f"  - Output directory: {result['output_dir']}")
            print(f"  - Video duration: {result['video_info']['duration']:.1f}s")
            print(f"  - Resolution: {result['video_info']['resolution']}")
    else:
        print("Frame extraction failed")
        sys.exit(1)


if __name__ == '__main__':
    main()