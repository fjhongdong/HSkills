#!/usr/bin/env python3
"""
视频关键帧提取工具
用于提取视频中的关键帧，供多模态AI分析使用
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def get_video_duration(video_path):
    """获取视频时长（秒）"""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'json', video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])


def calculate_frame_interval(duration, max_frames=60):
    """根据视频时长计算帧提取间隔"""
    if duration <= 60:  # 1分钟以内
        interval = 2
        max_frames = min(30, int(duration / interval))
    elif duration <= 300:  # 1-5分钟
        interval = 5
        max_frames = min(60, int(duration / interval))
    elif duration <= 900:  # 5-15分钟
        interval = 10
        max_frames = min(90, int(duration / interval))
    else:  # 15分钟以上
        interval = 15
        max_frames = min(120, int(duration / interval))

    return interval, max_frames


def extract_frames(video_path, output_dir, interval=5, max_frames=60):
    """
    提取视频关键帧

    Args:
        video_path: 视频文件路径
        output_dir: 输出目录
        interval: 提取间隔（秒）
        max_frames: 最大帧数

    Returns:
        list: 提取的帧文件路径列表
    """
    os.makedirs(output_dir, exist_ok=True)

    # 使用ffmpeg提取帧
    output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')

    cmd = [
        'ffmpeg', '-i', video_path,
        '-vf', f'fps=1/{interval},scale=1280:-1',
        '-frames:v', str(max_frames),
        '-q:v', '2',
        '-y',  # 覆盖已存在的文件
        output_pattern
    ]

    subprocess.run(cmd, capture_output=True)

    # 获取所有提取的帧
    frames = sorted(Path(output_dir).glob('frame_*.jpg'))

    return [str(f) for f in frames]


def extract_key_frames(video_path, output_dir=None):
    """
    智能提取视频关键帧的主函数

    Args:
        video_path: 视频文件路径
        output_dir: 输出目录（可选，默认为视频同目录下的frames子目录）

    Returns:
        dict: 包含提取结果的字典
    """
    if not os.path.exists(video_path):
        return {'error': f'视频文件不存在: {video_path}'}

    # 检查ffmpeg是否可用
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
    except FileNotFoundError:
        return {'error': 'ffmpeg未安装，请先安装ffmpeg'}

    # 设置输出目录
    if output_dir is None:
        video_dir = os.path.dirname(video_path)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_dir = os.path.join(video_dir, f'{video_name}_frames')

    # 获取视频时长
    try:
        duration = get_video_duration(video_path)
    except Exception as e:
        return {'error': f'无法获取视频时长: {str(e)}'}

    # 计算提取参数
    interval, max_frames = calculate_frame_interval(duration)

    # 提取帧
    frames = extract_frames(video_path, output_dir, interval, max_frames)

    return {
        'success': True,
        'video_path': video_path,
        'duration_seconds': duration,
        'frame_interval': interval,
        'frames_extracted': len(frames),
        'frame_paths': frames,
        'output_directory': output_dir
    }


def analyze_video_for_fashion(video_path, output_dir=None):
    """
    为服饰分析提取视频帧的便捷函数

    Args:
        video_path: 视频文件路径
        output_dir: 输出目录（可选）

    Returns:
        dict: 提取结果，可直接用于多模态AI分析
    """
    result = extract_key_frames(video_path, output_dir)

    if 'error' in result:
        return result

    # 添加分析建议
    result['analysis_suggestion'] = {
        'person_detection': '分析每帧是否包含人物，统计出镜时间',
        'style_analysis': '识别人物穿搭风格，判断年龄段',
        'scene_analysis': '分析场景类型、风格和色调',
        'audience_inference': '根据内容推断目标受众'
    }

    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python extract_frames.py <视频路径> [输出目录]")
        sys.exit(1)

    video_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    result = analyze_video_for_fashion(video_path, output_dir)

    print(json.dumps(result, indent=2, ensure_ascii=False))