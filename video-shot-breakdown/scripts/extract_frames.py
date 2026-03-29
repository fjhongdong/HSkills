#!/usr/bin/env python3
"""
视频关键帧提取工具
用于从视频中提取关键帧图片，支持基础间隔、场景变化检测和混合模式

使用方法:
    python extract_frames.py video.mp4
    python extract_frames.py video.mp4 output_frames/
    python extract_frames.py video.mp4 --mode hybrid
    python extract_frames.py video.mp4 --mode scene --threshold 0.2
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

        file_size = float(info.get('format', {}).get('size', 0))

        return {
            'duration': duration,
            'width': width,
            'height': height,
            'fps': fps,
            'resolution': f"{width}x{height}",
            'file_size_mb': round(file_size / (1024 * 1024), 2)
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


def get_frame_timestamps(video_path, output_dir):
    """从 ffmpeg 输出中获取每帧的精确时间码"""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_entries', 'frame=pts_time,best_effort_timestamp_time',
        '-select_streams', 'v',
        video_path
    ]

    timestamps = {}
    frames = sorted([f for f in os.listdir(output_dir) if f.endswith('.jpg')])

    if not frames:
        return timestamps

    # 通过文件修改时间和视频参数推算时间码
    # 使用帧序号 * 间隔作为近似时间码
    return timestamps


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

    # 使用 show_entries 帧信息来获取时间码
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
        # showinfo 输出格式: [Parsed_showinfo_1 ...] n:0 pts:90 ... pts_time:3.000000
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
    """分析视频的场景复杂度，用于自适应阈值计算

    原理：先对视频做低频采样，计算相邻帧差异的统计分布，
    根据分布的 90 百分位来确定最优的场景变化阈值。
    """
    duration = video_info['duration']

    # 对视频以 2fps 采样，输出帧差异值
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', 'fps=2,scale=320:-1',
        '-f', 'null',
        '-'
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)

        # 尝试通过 scene 检测滤镜获取帧差异分布
        # 用多个阈值采样来估算最优阈值
        thresholds_to_test = [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
        counts = {}

        for thresh in thresholds_to_test:
            test_cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f"select='gt(scene\\,{thresh})',fps=2,scale=160:-1",
                '-vsync', 'vfr',
                '-f', 'null',
                '-'
            ]
            try:
                test_proc = subprocess.run(test_cmd, capture_output=True, text=True, check=False)
                # 从输出中计数实际处理的帧数
                match = re.search(r'(\d+) frames', test_proc.stderr)
                counts[thresh] = int(match.group(1)) if match else 0
            except Exception:
                counts[thresh] = 0

        total_possible_transitions = duration / 2  # 2fps 采样下的最大帧数

        # 找到第一个阈值：其检测到的变化数 < 总帧数的 30%
        # 这意味着该阈值能有效区分"场景变化"和"帧内微变"
        estimated_shots = max(3, int(duration / 4))  # 粗估镜头数（假设平均4秒一个镜头）

        best_threshold = 0.3  # 默认值
        for thresh in thresholds_to_test:
            if counts.get(thresh, 0) <= estimated_shots * 1.5:
                best_threshold = thresh
                break

        # 如果最低阈值检测的帧数也远超预期，说明视频内容变化极快，降低阈值
        if counts.get(0.1, 0) > estimated_shots * 3:
            best_threshold = 0.15
        # 如果最高阈值检测帧数为0，说明变化极小，降低阈值
        elif counts.get(0.5, 0) == 0:
            best_threshold = 0.15

        return best_threshold

    except Exception:
        return 0.3  # 分析失败，回退默认值


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
        # merge_tolerance: 时间差低于此值的帧视为重复
        merge_tolerance = min(interval * 0.6, 1.0)

        # 按时间码排序所有帧
        all_frames = []
        all_frames.extend(basic_data)
        all_frames.extend(scene_data)
        all_frames.sort(key=lambda x: x['timestamp'])

        # 去重：当 interval 帧和 scene 帧时间接近时，保留 scene 帧（更精准）
        merged = []
        for frame in all_frames:
            is_dup = False
            for existing in merged:
                if abs(frame['timestamp'] - existing['timestamp']) < merge_tolerance:
                    # 两者接近，优先保留 scene_change 帧
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
            # 优先保留 scene_change 帧，均匀间隔帧按均匀间隔保留
            scene_frames_merged = [f for f in merged if f['source'] == 'scene_change']
            interval_frames_merged = [f for f in merged if f['source'] == 'interval']

            if len(scene_frames_merged) >= max_frames:
                # 场景变化帧已够，均匀采样取 max_frames
                step = len(scene_frames_merged) / max_frames
                selected_indices = [int(i * step) for i in range(max_frames)]
                final_frames = [scene_frames_merged[i] for i in selected_indices]
            else:
                # 混合：全部场景变化帧 + 部分均匀间隔帧
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
        description='Extract key frames from video',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python extract_frames.py video.mp4
    python extract_frames.py video.mp4 output_frames/
    python extract_frames.py video.mp4 --mode hybrid
    python extract_frames.py video.mp4 --mode scene --threshold 0.2
    python extract_frames.py video.mp4 --mode hybrid --adaptive
    python extract_frames.py video.mp4 --output-json
        """
    )

    parser.add_argument('video_path', help='Path to the video file')
    parser.add_argument('output_dir', nargs='?', default=None,
                        help='Output directory for frames (default: frames_<video_name>/)')
    parser.add_argument('--mode', choices=['basic', 'scene', 'hybrid'], default='hybrid',
                        help='Extraction mode: basic (interval), scene (scene change), hybrid (recommended, both)')
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

    # 设置输出目录
    if args.output_dir is None:
        video_name = Path(args.video_path).stem
        args.output_dir = f"frames_{video_name}"

    # 计算默认 max_frames
    if args.max_frames is None:
        video_info = get_video_info(args.video_path)
        if video_info:
            _, args.max_frames = calculate_extraction_params(video_info['duration'])
        else:
            args.max_frames = 30

    # 根据模式提取关键帧
    if args.mode == 'basic':
        result = extract_frames_basic(
            args.video_path,
            args.output_dir,
            interval=args.interval,
            max_frames=args.max_frames
        )
    elif args.mode == 'scene':
        result = extract_frames_scene(
            args.video_path,
            args.output_dir,
            threshold=args.threshold,
            max_frames=args.max_frames
        )
    else:  # hybrid
        result = extract_frames_hybrid(
            args.video_path,
            args.output_dir,
            max_frames=args.max_frames,
            adaptive=args.adaptive,
            threshold=args.threshold
        )

    if result:
        if args.output_json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            params = result['extraction_params']
            print(f"\nExtraction complete!")
            print(f"  - Mode: {params['mode']}")
            print(f"  - Frames extracted: {params['actual_frames']}")
            if params.get('stats'):
                stats = params['stats']
                print(f"  - Interval frames: {stats['interval_frames']}")
                print(f"  - Scene frames: {stats['scene_frames']}")
                print(f"  - Duplicates removed: {stats['duplicates_removed']}")
            print(f"  - Output directory: {result['output_dir']}")
            print(f"  - Video duration: {result['video_info']['duration']:.1f}s")
            print(f"  - Resolution: {result['video_info']['resolution']}")
            if params.get('truncated'):
                print(f"  ⚠ Some frames were truncated (max_frames={params['max_frames']})")
    else:
        print("Frame extraction failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
