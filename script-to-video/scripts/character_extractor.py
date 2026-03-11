#!/usr/bin/env python3
"""
角色信息提取器 - 从剧本中提取角色设定信息
自动分析角色的外貌、服装、性格等视觉特征
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from collections import defaultdict


@dataclass
class CharacterAppearance:
    """角色外貌设定"""
    age_range: str = ""           # 年龄范围
    gender: str = ""              # 性别
    body_type: str = ""           # 体型
    height: str = ""              # 身高
    facial_features: List[str] = field(default_factory=list)  # 五官特征
    hair_style: str = ""          # 发型
    hair_color: str = ""          # 发色
    skin_tone: str = ""           # 肤色
    distinguishing_marks: List[str] = field(default_factory=list)  # 特征标记


@dataclass
class CharacterCostume:
    """角色服装设定"""
    scene_number: int
    outfit_description: str
    colors: List[str] = field(default_factory=list)
    accessories: List[str] = field(default_factory=list)
    style: str = ""  # 风格: 正式/休闲/运动等


@dataclass
class CharacterProfile:
    """完整角色档案"""
    name: str
    appearance: CharacterAppearance = field(default_factory=CharacterAppearance)
    personality_traits: List[str] = field(default_factory=list)
    costumes: List[CharacterCostume] = field(default_factory=list)
    props: List[str] = field(default_factory=list)  # 标志性道具
    dialogue_count: int = 0
    scene_appearances: List[int] = field(default_factory=list)
    character_arc: str = ""  # 角色弧光描述
    visual_keywords: List[str] = field(default_factory=list)  # 视觉关键词


class CharacterExtractor:
    """角色信息提取器"""

    # 年龄相关关键词
    AGE_KEYWORDS = {
        "婴儿": ("0-1", ["baby", "infant"]),
        "幼儿": ("2-5", ["toddler", "young child"]),
        "儿童": ("6-12", ["child", "kid"]),
        "少年": ("13-17", ["teenager", "teen", "adolescent"]),
        "青年": ("18-30", ["young adult", "youth"]),
        "中年": ("35-50", ["middle-aged", "mature"]),
        "老年": ("60+", ["elderly", "senior", "old"]),
        "20多岁": ("20-29", ["twenties", "20s"]),
        "30多岁": ("30-39", ["thirties", "30s"]),
        "40多岁": ("40-49", ["forties", "40s"]),
        "50多岁": ("50-59", ["fifties", "50s"]),
    }

    # 性别关键词
    GENDER_KEYWORDS = {
        "男": "male",
        "女": "female",
        "男性": "male",
        "女性": "female",
        "男人": "male",
        "女人": "female",
        "男孩": "male",
        "女孩": "female",
        "先生": "male",
        "女士": "female",
        "小姐": "female",
    }

    # 体型关键词
    BODY_TYPE_KEYWORDS = {
        "瘦": "slim",
        "苗条": "slender",
        "纤细": "thin",
        "匀称": "athletic",
        "健壮": "muscular",
        "魁梧": "burly",
        "肥胖": "overweight",
        "微胖": "slightly chubby",
        "矮": "short",
        "高": "tall",
        "高大": "tall and strong",
    }

    # 发型关键词
    HAIR_STYLE_KEYWORDS = {
        "长发": "long hair",
        "短发": "short hair",
        "卷发": "curly hair",
        "直发": "straight hair",
        "马尾": "ponytail",
        "丸子头": "bun",
        "披肩发": "shoulder-length hair",
        "寸头": "buzz cut",
        "平头": "crew cut",
        "光头": "bald",
        "辫子": "braids",
        "刘海": "bangs",
    }

    # 发色关键词
    HAIR_COLOR_KEYWORDS = {
        "黑发": "black hair",
        "金发": "blonde hair",
        "棕发": "brown hair",
        "红发": "red hair",
        "白发": "white hair",
        "灰发": "gray hair",
        "染发": "dyed hair",
    }

    # 服装风格关键词
    COSTUME_STYLE_KEYWORDS = {
        "正装": "formal",
        "西装": "suit",
        "休闲": "casual",
        "运动": "sporty",
        "睡衣": "sleepwear",
        "制服": "uniform",
        "礼服": "formal dress",
        "牛仔": "denim",
        "复古": "vintage",
        "时尚": "fashionable",
    }

    # 性格关键词到视觉表现的映射
    PERSONALITY_TO_VISUAL = {
        "温柔": ["soft expression", "gentle eyes", "warm smile"],
        "冷酷": ["stern expression", "sharp eyes", "stoic face"],
        "活泼": ["bright eyes", "energetic pose", "cheerful expression"],
        "内向": ["downcast eyes", "reserved posture", "subtle expressions"],
        "自信": ["head held high", "direct gaze", "confident stance"],
        "紧张": ["fidgeting", "avoiding eye contact", "tense shoulders"],
        "愤怒": ["furrowed brows", "clenched jaw", "intense stare"],
        "悲伤": ["teary eyes", "drooping shoulders", "melancholic expression"],
    }

    def __init__(self):
        self.characters: Dict[str, CharacterProfile] = {}

    def extract_from_parsed_script(self, parsed_script: Dict) -> Dict[str, Dict]:
        """从解析后的剧本中提取角色信息"""

        # 初始化所有角色
        for char_name in parsed_script.get("all_characters", []):
            self.characters[char_name] = CharacterProfile(name=char_name)

        # 遍历场景提取信息
        for scene in parsed_script.get("scenes", []):
            scene_num = scene.get("number", 0)

            # 记录角色出场
            for char_name in scene.get("characters", []):
                if char_name in self.characters:
                    if scene_num not in self.characters[char_name].scene_appearances:
                        self.characters[char_name].scene_appearances.append(scene_num)

        return self._generate_output()

    def extract_from_text(self, script_text: str, character_names: List[str]) -> Dict[str, Dict]:
        """从剧本文本中提取角色信息"""

        # 初始化角色
        for name in character_names:
            self.characters[name] = CharacterProfile(name=name)

        lines = script_text.split('\n')

        for name in character_names:
            # 查找包含角色名的描述行
            for line in lines:
                if name in line:
                    self._analyze_line_for_character(name, line)

        # 生成视觉关键词
        for char in self.characters.values():
            char.visual_keywords = self._generate_visual_keywords(char)

        return self._generate_output()

    def _analyze_line_for_character(self, char_name: str, line: str):
        """分析包含角色的行,提取特征"""
        char = self.characters[char_name]

        # 提取年龄
        for cn_keyword, (age_range, _) in self.AGE_KEYWORDS.items():
            if cn_keyword in line:
                char.appearance.age_range = age_range
                break

        # 提取性别
        for cn_keyword, gender in self.GENDER_KEYWORDS.items():
            if cn_keyword in line:
                char.appearance.gender = gender
                break

        # 提取体型
        for cn_keyword, body_type in self.BODY_TYPE_KEYWORDS.items():
            if cn_keyword in line:
                char.appearance.body_type = body_type
                break

        # 提取发型
        for cn_keyword, hair_style in self.HAIR_STYLE_KEYWORDS.items():
            if cn_keyword in line:
                char.appearance.hair_style = hair_style
                break

        # 提取发色
        for cn_keyword, hair_color in self.HAIR_COLOR_KEYWORDS.items():
            if cn_keyword in line:
                char.appearance.hair_color = hair_color
                break

    def _generate_visual_keywords(self, char: CharacterProfile) -> List[str]:
        """根据角色档案生成视觉关键词"""
        keywords = []

        app = char.appearance
        if app.gender:
            keywords.append(app.gender)
        if app.age_range:
            keywords.append(f"{app.age_range} years old")
        if app.body_type:
            keywords.append(app.body_type)
        if app.hair_style:
            keywords.append(app.hair_style)
        if app.hair_color:
            keywords.append(app.hair_color)
        if app.facial_features:
            keywords.extend(app.facial_features)

        # 添加性格相关的视觉表现
        for trait in char.personality_traits:
            if trait in self.PERSONALITY_TO_VISUAL:
                keywords.extend(self.PERSONALITY_TO_VISUAL[trait])

        return keywords

    def _generate_output(self) -> Dict[str, Dict]:
        """生成输出结果"""
        output = {}

        for name, char in self.characters.items():
            output[name] = {
                "name": name,
                "appearance": {
                    "age_range": char.appearance.age_range or "unspecified",
                    "gender": char.appearance.gender or "unspecified",
                    "body_type": char.appearance.body_type or "average",
                    "height": char.appearance.height or "average",
                    "hair_style": char.appearance.hair_style or "unspecified",
                    "hair_color": char.appearance.hair_color or "black hair",
                    "skin_tone": char.appearance.skin_tone or "natural",
                    "facial_features": char.appearance.facial_features,
                    "distinguishing_marks": char.appearance.distinguishing_marks,
                },
                "personality_traits": char.personality_traits,
                "costumes": [
                    {
                        "scene": c.scene_number,
                        "description": c.outfit_description,
                        "colors": c.colors,
                        "accessories": c.accessories,
                        "style": c.style
                    }
                    for c in char.costumes
                ],
                "props": char.props,
                "scene_appearances": char.scene_appearances,
                "visual_keywords": char.visual_keywords,
                "prompt_description": self._generate_prompt_description(char)
            }

        return output

    def _generate_prompt_description(self, char: CharacterProfile) -> str:
        """生成用于AI生成的角色描述提示词"""
        parts = []

        app = char.appearance

        # 基础描述
        if app.gender and app.age_range:
            parts.append(f"{app.age_range} year old {app.gender}")
        elif app.gender:
            parts.append(app.gender)

        # 体型
        if app.body_type:
            parts.append(app.body_type)

        # 发型发色
        hair_desc = []
        if app.hair_color:
            hair_desc.append(app.hair_color)
        if app.hair_style:
            hair_desc.append(app.hair_style)
        if hair_desc:
            parts.append(", ".join(hair_desc))

        # 五官特征
        if app.facial_features:
            parts.append(", ".join(app.facial_features))

        # 组合
        if parts:
            return ", ".join(parts)
        else:
            return f"character named {char.name}"


def extract_characters(parsed_script: Dict) -> Dict[str, Dict]:
    """
    从解析后的剧本提取角色信息的便捷函数

    Args:
        parsed_script: parse_script.py 的输出结果

    Returns:
        角色信息字典
    """
    extractor = CharacterExtractor()
    return extractor.extract_from_parsed_script(parsed_script)


if __name__ == "__main__":
    import sys

    # 示例用法
    sample_script = {
        "title": "示例剧本",
        "all_characters": ["张伟", "李娜", "王老师"],
        "scenes": [
            {"number": 1, "characters": ["张伟", "李娜"]},
            {"number": 2, "characters": ["李娜", "王老师"]},
            {"number": 3, "characters": ["张伟", "李娜", "王老师"]},
        ]
    }

    result = extract_characters(sample_script)
    print(json.dumps(result, ensure_ascii=False, indent=2))
