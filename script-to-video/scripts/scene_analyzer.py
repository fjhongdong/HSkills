#!/usr/bin/env python3
"""
场景分析器 - 分析剧本场景并生成场景设定提示词
包括环境、光线、氛围等视觉要素分析
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class TimeOfDay(Enum):
    """时间段"""
    DAWN = "dawn"           # 黎明
    MORNING = "morning"     # 早晨
    DAY = "day"             # 白天
    AFTERNOON = "afternoon" # 下午
    DUSK = "dusk"           # 黄昏
    EVENING = "evening"     # 傍晚
    NIGHT = "night"         # 夜晚
    MIDNIGHT = "midnight"   # 深夜


class LightingType(Enum):
    """光线类型"""
    NATURAL = "natural"           # 自然光
    ARTIFICIAL = "artificial"     # 人造光
    MIXED = "mixed"               # 混合光
    LOW_KEY = "low_key"           # 低调光
    HIGH_KEY = "high_key"         # 高调光
    DRAMATIC = "dramatic"         # 戏剧性光
    SOFT = "soft"                 # 柔光
    HARD = "hard"                 # 硬光


@dataclass
class LightingSetup:
    """光线设置"""
    type: str = "natural"
    direction: str = "front"      # front/side/back/top/bottom
    intensity: str = "medium"     # low/medium/high
    color_temperature: str = "neutral"  # warm/neutral/cool
    quality: str = "soft"         # soft/hard
    sources: List[str] = field(default_factory=list)


@dataclass
class SceneEnvironment:
    """场景环境设定"""
    location_type: str = ""       # 地点类型
    location_name: str = ""       # 具体地点名
    int_ext: str = "INT"          # 室内/室外
    time_of_day: str = "DAY"      # 时间
    weather: str = ""             # 天气
    season: str = ""              # 季节
    spatial_layout: str = ""      # 空间布局描述
    key_props: List[str] = field(default_factory=list)  # 关键道具
    background_elements: List[str] = field(default_factory=list)  # 背景元素
    lighting: LightingSetup = field(default_factory=LightingSetup)
    color_palette: List[str] = field(default_factory=list)  # 色彩基调
    mood: str = ""                # 氛围
    atmosphere_keywords: List[str] = field(default_factory=list)


@dataclass
class SceneAnalysis:
    """场景分析结果"""
    scene_number: int
    scene_heading: str
    environment: SceneEnvironment
    visual_prompt: str = ""
    mood_keywords: List[str] = field(default_factory=list)


class SceneAnalyzer:
    """场景分析器"""

    # 地点类型映射
    LOCATION_TYPES = {
        # 室内场所
        "办公室": ("office", "INT", ["desk", "computer", "chair", "documents"]),
        "卧室": ("bedroom", "INT", ["bed", "nightstand", "wardrobe", "lamp"]),
        "客厅": ("living room", "INT", ["sofa", "coffee table", "TV", "bookshelf"]),
        "厨房": ("kitchen", "INT", ["stove", "refrigerator", "counter", "cabinets"]),
        "餐厅": ("dining room", "INT", ["dining table", "chairs", "chandelier"]),
        "浴室": ("bathroom", "INT", ["sink", "mirror", "bathtub", "toilet"]),
        "教室": ("classroom", "INT", ["desks", "blackboard", "podium", "chairs"]),
        "医院": ("hospital", "INT", ["hospital bed", "medical equipment", "white walls"]),
        "咖啡厅": ("cafe", "INT", ["coffee machines", "tables", "warm lighting"]),
        "酒吧": ("bar", "INT", ["bar counter", "bottles", "dim lighting", "stools"]),
        "商场": ("mall", "INT", ["shops", "escalators", "bright lights"]),
        "电梯": ("elevator", "INT", ["metal walls", "buttons", "confined space"]),
        "走廊": ("hallway", "INT", ["doors", "fluorescent lights", "long perspective"]),

        # 室外场所
        "街道": ("street", "EXT", ["buildings", "cars", "pedestrians", "streetlights"]),
        "公园": ("park", "EXT", ["trees", "benches", "grass", "paths"]),
        "海滩": ("beach", "EXT", ["sand", "waves", "ocean", "sky"]),
        "山": ("mountain", "EXT", ["peaks", "rocks", "clouds", "vegetation"]),
        "森林": ("forest", "EXT", ["trees", "leaves", "shadows", "nature"]),
        "停车场": ("parking lot", "EXT", ["cars", "concrete", "lights"]),
        "天台": ("rooftop", "EXT", ["city view", "sky", "railings"]),
        "校园": ("campus", "EXT", ["buildings", "students", "trees", "paths"]),
    }

    # 时间到光线的映射
    TIME_TO_LIGHTING = {
        "DAWN": {
            "type": "natural",
            "color_temperature": "warm",
            "intensity": "low",
            "quality": "soft",
            "description": "golden hour, soft warm light, long shadows"
        },
        "MORNING": {
            "type": "natural",
            "color_temperature": "neutral",
            "intensity": "medium",
            "quality": "soft",
            "description": "bright morning light, fresh atmosphere"
        },
        "DAY": {
            "type": "natural",
            "color_temperature": "neutral",
            "intensity": "high",
            "quality": "hard",
            "description": "bright daylight, clear visibility"
        },
        "AFTERNOON": {
            "type": "natural",
            "color_temperature": "warm",
            "intensity": "medium",
            "quality": "soft",
            "description": "warm afternoon light, relaxed mood"
        },
        "DUSK": {
            "type": "natural",
            "color_temperature": "warm",
            "intensity": "low",
            "quality": "soft",
            "description": "golden hour, orange and pink hues, dramatic shadows"
        },
        "EVENING": {
            "type": "mixed",
            "color_temperature": "warm",
            "intensity": "low",
            "quality": "soft",
            "description": "twilight, artificial lights starting, blue hour"
        },
        "NIGHT": {
            "type": "artificial",
            "color_temperature": "cool",
            "intensity": "low",
            "quality": "hard",
            "description": "night scene, artificial lighting, dark atmosphere"
        },
    }

    # 天气关键词
    WEATHER_KEYWORDS = {
        "晴": ("sunny", ["bright", "clear sky", "sunshine"]),
        "阴": ("overcast", ["cloudy", "gray sky", "diffused light"]),
        "雨": ("rainy", ["rain", "wet surfaces", "reflections", "umbrellas"]),
        "雪": ("snowy", ["snow", "white", "cold", "winter"]),
        "雾": ("foggy", ["fog", "mist", "low visibility", "mysterious"]),
        "风": ("windy", ["wind", "movement", "flowing"]),
        "暴风雨": ("stormy", ["storm", "dark clouds", "lightning", "dramatic"]),
    }

    # 氛围关键词
    MOOD_MAPPINGS = {
        "紧张": ["tense", "suspenseful", "dark shadows", "high contrast"],
        "温馨": ["warm", "cozy", "soft lighting", "comfortable"],
        "浪漫": ["romantic", "soft focus", "warm colors", "intimate"],
        "恐怖": ["horror", "dark", "shadows", "eerie", "unsettling"],
        "悲伤": ["melancholic", "muted colors", "overcast", "somber"],
        "欢乐": ["joyful", "bright", "vibrant colors", "lively"],
        "神秘": ["mysterious", "fog", "shadows", "enigmatic"],
        "压抑": ["oppressive", "claustrophobic", "dark", "heavy"],
    }

    def __init__(self):
        self.scenes: List[SceneAnalysis] = []

    def analyze_scene(self, scene_data: Dict) -> SceneAnalysis:
        """分析单个场景"""
        scene_num = scene_data.get("number", 0)
        heading = scene_data.get("heading", "")
        location = scene_data.get("location", "")
        time_of_day = scene_data.get("time_of_day", "DAY").upper()
        int_ext = scene_data.get("int_ext", "INT.")

        # 创建环境设定
        environment = SceneEnvironment()
        environment.location_name = location
        environment.int_ext = "INT" if "INT" in int_ext.upper() else "EXT"
        environment.time_of_day = time_of_day

        # 分析地点类型
        for cn_name, (en_name, default_int_ext, props) in self.LOCATION_TYPES.items():
            if cn_name in location:
                environment.location_type = en_name
                environment.key_props = props.copy()
                break

        if not environment.location_type:
            environment.location_type = location

        # 设置光线
        lighting_info = self.TIME_TO_LIGHTING.get(time_of_day, self.TIME_TO_LIGHTING["DAY"])
        environment.lighting = LightingSetup(
            type=lighting_info["type"],
            color_temperature=lighting_info["color_temperature"],
            intensity=lighting_info["intensity"],
            quality=lighting_info["quality"]
        )

        # 生成视觉提示词
        visual_prompt = self._generate_visual_prompt(environment, lighting_info)

        # 生成氛围关键词
        mood_keywords = self._infer_mood_keywords(environment)

        return SceneAnalysis(
            scene_number=scene_num,
            scene_heading=heading,
            environment=environment,
            visual_prompt=visual_prompt,
            mood_keywords=mood_keywords
        )

    def analyze_all_scenes(self, parsed_script: Dict) -> List[Dict]:
        """分析所有场景"""
        results = []

        for scene_data in parsed_script.get("scenes", []):
            analysis = self.analyze_scene(scene_data)
            results.append(self._to_dict(analysis))

        return results

    def _generate_visual_prompt(self, env: SceneEnvironment, lighting_info: Dict) -> str:
        """生成场景视觉提示词"""
        parts = []

        # 基础场景
        if env.int_ext == "INT":
            parts.append(f"interior of {env.location_type}")
        else:
            parts.append(f"exterior {env.location_type}")

        # 光线描述
        parts.append(lighting_info.get("description", ""))

        # 关键道具
        if env.key_props:
            parts.append(f"with {', '.join(env.key_props[:3])}")

        # 天气(仅室外)
        if env.int_ext == "EXT" and env.weather:
            parts.append(env.weather)

        return ", ".join(filter(None, parts))

    def _infer_mood_keywords(self, env: SceneEnvironment) -> List[str]:
        """推断氛围关键词"""
        keywords = []

        # 根据时间推断
        time_moods = {
            "NIGHT": ["mysterious", "quiet", "dark"],
            "DAWN": ["hopeful", "fresh", "new beginning"],
            "DUSK": ["romantic", "nostalgic", "transitional"],
        }
        keywords.extend(time_moods.get(env.time_of_day, []))

        # 根据地点推断
        location_moods = {
            "hospital": ["clinical", "sterile", "tense"],
            "bar": ["relaxed", "social", "dim"],
            "beach": ["peaceful", "open", "free"],
            "forest": ["natural", "serene", "mysterious"],
        }
        keywords.extend(location_moods.get(env.location_type, []))

        return keywords[:5]  # 限制数量

    def _to_dict(self, analysis: SceneAnalysis) -> Dict:
        """转换为字典"""
        env = analysis.environment
        return {
            "scene_number": analysis.scene_number,
            "scene_heading": analysis.scene_heading,
            "environment": {
                "location_type": env.location_type,
                "location_name": env.location_name,
                "int_ext": env.int_ext,
                "time_of_day": env.time_of_day,
                "weather": env.weather,
                "season": env.season,
                "key_props": env.key_props,
                "lighting": {
                    "type": env.lighting.type,
                    "color_temperature": env.lighting.color_temperature,
                    "intensity": env.lighting.intensity,
                    "quality": env.lighting.quality,
                },
                "color_palette": env.color_palette,
                "mood": env.mood,
            },
            "visual_prompt": analysis.visual_prompt,
            "mood_keywords": analysis.mood_keywords,
        }


def analyze_scenes(parsed_script: Dict) -> List[Dict]:
    """
    分析剧本场景的便捷函数

    Args:
        parsed_script: parse_script.py 的输出结果

    Returns:
        场景分析结果列表
    """
    analyzer = SceneAnalyzer()
    return analyzer.analyze_all_scenes(parsed_script)


if __name__ == "__main__":
    # 示例用法
    sample_script = {
        "scenes": [
            {
                "number": 1,
                "heading": "INT. 办公室 - DAY",
                "location": "办公室",
                "time_of_day": "DAY",
                "int_ext": "INT."
            },
            {
                "number": 2,
                "heading": "EXT. 公园 - DUSK",
                "location": "公园",
                "time_of_day": "DUSK",
                "int_ext": "EXT."
            },
            {
                "number": 3,
                "heading": "INT. 咖啡厅 - NIGHT",
                "location": "咖啡厅",
                "time_of_day": "NIGHT",
                "int_ext": "INT."
            }
        ]
    }

    results = analyze_scenes(sample_script)
    print(json.dumps(results, ensure_ascii=False, indent=2))
