#!/usr/bin/env python3
"""
分镜提示词生成器 - 根据剧本自动生成逐镜头的AI视频提示词
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ShotSize(Enum):
    """景别"""
    ECU = "extreme close-up"      # 大特写
    CU = "close-up"               # 特写
    MCU = "medium close-up"       # 中近景
    MS = "medium shot"            # 中景
    MLS = "medium long shot"      # 中远景
    LS = "long shot"              # 远景
    ELS = "extreme long shot"     # 大远景
    OTS = "over-the-shoulder"     # 过肩镜头
    POV = "point of view"         # 主观镜头
    TWO_SHOT = "two shot"         # 双人镜头
    GROUP = "group shot"          # 群戏镜头


class CameraMovement(Enum):
    """运镜方式"""
    STATIC = "static"             # 固定
    PAN = "pan"                   # 摇(左右)
    TILT = "tilt"                 # 俯仰
    PUSH = "push in"              # 推
    PULL = "pull out"             # 拉
    DOLLY = "dolly"               # 移动
    TRACK = "tracking"            # 跟踪
    CRANE = "crane"               # 升降
    HANDHELD = "handheld"         # 手持
    STEADICAM = "steadicam"       # 稳定器
    ZOOM = "zoom"                 # 变焦
    WHIP_PAN = "whip pan"         # 甩镜
    ORBIT = "orbit"               # 环绕


class Transition(Enum):
    """转场方式"""
    CUT = "cut"                   # 硬切
    FADE = "fade"                 # 淡入淡出
    DISSOLVE = "dissolve"         # 叠化
    WIPE = "wipe"                 # 划变
    MATCH_CUT = "match cut"       # 匹配剪辑
    JUMP_CUT = "jump cut"         # 跳切
    L_CUT = "L-cut"               # L型剪辑
    J_CUT = "J-cut"               # J型剪辑
    SMASH_CUT = "smash cut"       # 碰撞剪辑


@dataclass
class Shot:
    """单个镜头"""
    shot_id: str                  # 镜头编号 (如 "1-3" 表示第1场第3镜)
    scene_number: int
    shot_number: int
    shot_size: str                # 景别
    camera_movement: str          # 运镜
    subject: str                  # 拍摄主体
    action: str                   # 动作描述
    dialogue: str = ""            # 对白(如有)
    mood: str = ""                # 情绪氛围
    duration: float = 3.0         # 建议时长(秒)
    transition: str = "cut"       # 转场方式
    composition_notes: str = ""   # 构图说明
    lighting_notes: str = ""      # 光线说明
    audio_notes: str = ""         # 音效说明
    visual_prompt: str = ""       # AI生成用视觉提示词


@dataclass
class Storyboard:
    """分镜脚本"""
    title: str
    shots: List[Shot] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class StoryboardGenerator:
    """分镜生成器"""

    # 动作到景别的推荐映射
    ACTION_TO_SHOT_SIZE = {
        # 表情相关 -> 特写
        "表情": ShotSize.CU,
        "眼神": ShotSize.ECU,
        "微笑": ShotSize.CU,
        "流泪": ShotSize.ECU,
        "皱眉": ShotSize.CU,

        # 对话相关 -> 中近景
        "说": ShotSize.MCU,
        "对话": ShotSize.TWO_SHOT,
        "交谈": ShotSize.TWO_SHOT,
        "问": ShotSize.MCU,
        "答": ShotSize.MCU,

        # 动作相关 -> 中景/中远景
        "走": ShotSize.MLS,
        "跑": ShotSize.LS,
        "坐": ShotSize.MS,
        "站": ShotSize.MS,
        "转身": ShotSize.MS,
        "打斗": ShotSize.MLS,

        # 环境相关 -> 远景
        "进入": ShotSize.LS,
        "离开": ShotSize.LS,
        "全景": ShotSize.ELS,
        "环境": ShotSize.ELS,
    }

    # 情绪到运镜的推荐映射
    MOOD_TO_MOVEMENT = {
        "紧张": [CameraMovement.HANDHELD, CameraMovement.PUSH],
        "平静": [CameraMovement.STATIC, CameraMovement.DOLLY],
        "追逐": [CameraMovement.TRACK, CameraMovement.HANDHELD],
        "浪漫": [CameraMovement.DOLLY, CameraMovement.ORBIT],
        "惊讶": [CameraMovement.WHIP_PAN, CameraMovement.PUSH],
        "悲伤": [CameraMovement.STATIC, CameraMovement.PULL],
        "神秘": [CameraMovement.DOLLY, CameraMovement.CRANE],
        "震撼": [CameraMovement.CRANE, CameraMovement.PUSH],
    }

    # 场景类型到开场镜头的映射
    SCENE_OPENING_SHOTS = {
        "INT": ShotSize.MS,     # 室内通常中景开场
        "EXT": ShotSize.LS,     # 室外通常远景开场
    }

    def __init__(self):
        self.shots: List[Shot] = []
        self.shot_counter: Dict[int, int] = {}  # scene_num -> shot_count

    def generate_from_parsed_script(
        self,
        parsed_script: Dict,
        scene_analyses: List[Dict],
        character_profiles: Dict[str, Dict]
    ) -> Storyboard:
        """
        从解析后的剧本生成分镜

        Args:
            parsed_script: parse_script.py 的输出
            scene_analyses: scene_analyzer.py 的输出
            character_profiles: character_extractor.py 的输出
        """
        title = parsed_script.get("title", "Untitled")

        # 创建场景分析的快速查找
        scene_analysis_map = {
            sa["scene_number"]: sa for sa in scene_analyses
        }

        for scene in parsed_script.get("scenes", []):
            scene_num = scene.get("number", 0)
            scene_analysis = scene_analysis_map.get(scene_num, {})

            self._generate_scene_shots(
                scene=scene,
                scene_analysis=scene_analysis,
                character_profiles=character_profiles
            )

        return Storyboard(
            title=title,
            shots=self.shots,
            metadata={
                "total_shots": len(self.shots),
                "total_scenes": len(parsed_script.get("scenes", [])),
                "estimated_duration": sum(s.duration for s in self.shots)
            }
        )

    def _generate_scene_shots(
        self,
        scene: Dict,
        scene_analysis: Dict,
        character_profiles: Dict[str, Dict]
    ):
        """为单个场景生成镜头"""
        scene_num = scene.get("number", 0)
        characters = scene.get("characters", [])

        # 初始化场景的镜头计数
        if scene_num not in self.shot_counter:
            self.shot_counter[scene_num] = 0

        # 获取场景视觉信息
        env = scene_analysis.get("environment", {})
        visual_prompt_base = scene_analysis.get("visual_prompt", "")
        mood_keywords = scene_analysis.get("mood_keywords", [])

        # 1. 场景建立镜头 (Establishing Shot)
        self._add_shot(
            scene_num=scene_num,
            shot_size=ShotSize.LS.value if env.get("int_ext") == "EXT" else ShotSize.MLS.value,
            camera_movement=CameraMovement.STATIC.value,
            subject=f"establishing shot of {env.get('location_type', 'location')}",
            action="场景建立",
            mood=", ".join(mood_keywords[:2]) if mood_keywords else "",
            duration=3.0,
            visual_prompt=f"establishing shot, {visual_prompt_base}, cinematic"
        )

        # 2. 根据场景中的角色生成角色入场镜头
        for char_name in characters[:2]:  # 限制前两个主要角色
            char_profile = character_profiles.get(char_name, {})
            char_visual = char_profile.get("prompt_description", char_name)

            self._add_shot(
                scene_num=scene_num,
                shot_size=ShotSize.MS.value,
                camera_movement=CameraMovement.STATIC.value,
                subject=char_name,
                action=f"{char_name} 出场",
                mood="",
                duration=2.0,
                visual_prompt=f"medium shot of {char_visual}, {visual_prompt_base}"
            )

        # 3. 如果有多个角色,添加对话镜头
        if len(characters) >= 2:
            self._add_shot(
                scene_num=scene_num,
                shot_size=ShotSize.TWO_SHOT.value,
                camera_movement=CameraMovement.STATIC.value,
                subject=f"{characters[0]} and {characters[1]}",
                action="对话",
                mood="",
                duration=4.0,
                visual_prompt=f"two shot, conversation scene, {visual_prompt_base}"
            )

        # 4. 添加反应镜头
        if characters:
            self._add_shot(
                scene_num=scene_num,
                shot_size=ShotSize.CU.value,
                camera_movement=CameraMovement.STATIC.value,
                subject=characters[0],
                action="反应镜头",
                mood="",
                duration=2.0,
                visual_prompt=f"close-up reaction shot, expressive, {visual_prompt_base}"
            )

    def _add_shot(
        self,
        scene_num: int,
        shot_size: str,
        camera_movement: str,
        subject: str,
        action: str,
        mood: str,
        duration: float,
        visual_prompt: str,
        dialogue: str = "",
        transition: str = "cut"
    ):
        """添加一个镜头"""
        self.shot_counter[scene_num] = self.shot_counter.get(scene_num, 0) + 1
        shot_num = self.shot_counter[scene_num]

        shot = Shot(
            shot_id=f"{scene_num}-{shot_num}",
            scene_number=scene_num,
            shot_number=shot_num,
            shot_size=shot_size,
            camera_movement=camera_movement,
            subject=subject,
            action=action,
            dialogue=dialogue,
            mood=mood,
            duration=duration,
            transition=transition,
            visual_prompt=visual_prompt
        )

        self.shots.append(shot)

    def to_dict(self, storyboard: Storyboard) -> Dict:
        """转换为字典输出"""
        return {
            "title": storyboard.title,
            "metadata": storyboard.metadata,
            "shots": [
                {
                    "shot_id": s.shot_id,
                    "scene_number": s.scene_number,
                    "shot_number": s.shot_number,
                    "shot_size": s.shot_size,
                    "camera_movement": s.camera_movement,
                    "subject": s.subject,
                    "action": s.action,
                    "dialogue": s.dialogue,
                    "mood": s.mood,
                    "duration": s.duration,
                    "transition": s.transition,
                    "composition_notes": s.composition_notes,
                    "lighting_notes": s.lighting_notes,
                    "audio_notes": s.audio_notes,
                    "visual_prompt": s.visual_prompt
                }
                for s in storyboard.shots
            ]
        }


def generate_storyboard(
    parsed_script: Dict,
    scene_analyses: List[Dict],
    character_profiles: Dict[str, Dict]
) -> Dict:
    """
    生成分镜的便捷函数

    Args:
        parsed_script: parse_script.py 的输出
        scene_analyses: scene_analyzer.py 的输出
        character_profiles: character_extractor.py 的输出

    Returns:
        分镜数据字典
    """
    generator = StoryboardGenerator()
    storyboard = generator.generate_from_parsed_script(
        parsed_script, scene_analyses, character_profiles
    )
    return generator.to_dict(storyboard)


if __name__ == "__main__":
    # 示例用法
    sample_script = {
        "title": "示例短剧",
        "scenes": [
            {"number": 1, "characters": ["张伟", "李娜"]},
            {"number": 2, "characters": ["李娜"]},
        ]
    }

    sample_scenes = [
        {
            "scene_number": 1,
            "environment": {"location_type": "office", "int_ext": "INT"},
            "visual_prompt": "modern office interior, bright daylight",
            "mood_keywords": ["professional", "busy"]
        },
        {
            "scene_number": 2,
            "environment": {"location_type": "cafe", "int_ext": "INT"},
            "visual_prompt": "cozy cafe interior, warm lighting",
            "mood_keywords": ["relaxed", "intimate"]
        }
    ]

    sample_characters = {
        "张伟": {"prompt_description": "young Asian male, short black hair, wearing suit"},
        "李娜": {"prompt_description": "young Asian female, long black hair, casual dress"}
    }

    result = generate_storyboard(sample_script, sample_scenes, sample_characters)
    print(json.dumps(result, ensure_ascii=False, indent=2))
