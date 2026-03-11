#!/usr/bin/env python3
"""
一致性校验器 - 检查角色和场景在不同镜头间的视觉一致性
生成一致性控制参考表
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict


@dataclass
class ConsistencyIssue:
    """一致性问题"""
    issue_type: str           # character / scene / lighting / style
    severity: str             # warning / error
    location: str             # 问题位置描述
    description: str          # 问题描述
    suggestion: str           # 建议修复方案


@dataclass
class CharacterConsistencyProfile:
    """角色一致性档案"""
    name: str
    seed_prompt: str                    # 角色种子提示词(用于保持一致)
    appearance_keywords: List[str]      # 外貌关键词
    costume_by_scene: Dict[int, str]    # 每场景服装
    first_appearance: int               # 首次出场场景
    all_appearances: List[str]          # 所有出场镜头ID
    consistency_notes: List[str]        # 一致性注意事项


@dataclass
class SceneConsistencyProfile:
    """场景一致性档案"""
    scene_number: int
    location: str
    seed_prompt: str                    # 场景种子提示词
    lighting_profile: str               # 光线档案
    color_palette: List[str]            # 色彩板
    all_shots: List[str]                # 该场景所有镜头ID
    consistency_notes: List[str]


@dataclass
class ConsistencyReport:
    """一致性报告"""
    character_profiles: List[CharacterConsistencyProfile]
    scene_profiles: List[SceneConsistencyProfile]
    issues: List[ConsistencyIssue]
    global_style_prompt: str            # 全局风格提示词
    recommendations: List[str]


class ConsistencyChecker:
    """一致性校验器"""

    def __init__(self):
        self.character_profiles: Dict[str, CharacterConsistencyProfile] = {}
        self.scene_profiles: Dict[int, SceneConsistencyProfile] = {}
        self.issues: List[ConsistencyIssue] = []

    def check_consistency(
        self,
        storyboard: Dict,
        character_data: Dict[str, Dict],
        scene_data: List[Dict]
    ) -> Dict:
        """
        执行一致性检查

        Args:
            storyboard: storyboard_generator.py 的输出
            character_data: character_extractor.py 的输出
            scene_data: scene_analyzer.py 的输出

        Returns:
            一致性报告字典
        """
        # 1. 生成角色一致性档案
        self._build_character_profiles(storyboard, character_data)

        # 2. 生成场景一致性档案
        self._build_scene_profiles(storyboard, scene_data)

        # 3. 检查问题
        self._check_character_consistency(storyboard)
        self._check_scene_consistency(storyboard)
        self._check_lighting_consistency(storyboard, scene_data)

        # 4. 生成全局风格提示词
        global_style = self._generate_global_style_prompt(scene_data)

        # 5. 生成建议
        recommendations = self._generate_recommendations()

        return self._to_dict(global_style, recommendations)

    def _build_character_profiles(self, storyboard: Dict, character_data: Dict[str, Dict]):
        """构建角色一致性档案"""
        shots = storyboard.get("shots", [])

        for char_name, char_info in character_data.items():
            # 收集角色所有出场镜头
            appearances = []
            first_appearance = None

            for shot in shots:
                if char_name in shot.get("subject", ""):
                    appearances.append(shot.get("shot_id", ""))
                    if first_appearance is None:
                        first_appearance = shot.get("scene_number", 0)

            # 生成种子提示词
            visual_keywords = char_info.get("visual_keywords", [])
            prompt_desc = char_info.get("prompt_description", "")

            seed_prompt = self._generate_character_seed(char_name, prompt_desc, visual_keywords)

            self.character_profiles[char_name] = CharacterConsistencyProfile(
                name=char_name,
                seed_prompt=seed_prompt,
                appearance_keywords=visual_keywords,
                costume_by_scene={},
                first_appearance=first_appearance or 0,
                all_appearances=appearances,
                consistency_notes=[
                    f"首次出场于场景 {first_appearance}",
                    f"共出现在 {len(appearances)} 个镜头中",
                    "保持服装、发型、配饰一致"
                ]
            )

    def _build_scene_profiles(self, storyboard: Dict, scene_data: List[Dict]):
        """构建场景一致性档案"""
        shots = storyboard.get("shots", [])

        # 按场景分组镜头
        scene_shots: Dict[int, List[str]] = defaultdict(list)
        for shot in shots:
            scene_num = shot.get("scene_number", 0)
            scene_shots[scene_num].append(shot.get("shot_id", ""))

        for scene_info in scene_data:
            scene_num = scene_info.get("scene_number", 0)
            env = scene_info.get("environment", {})

            seed_prompt = self._generate_scene_seed(scene_info)

            self.scene_profiles[scene_num] = SceneConsistencyProfile(
                scene_number=scene_num,
                location=env.get("location_type", ""),
                seed_prompt=seed_prompt,
                lighting_profile=self._describe_lighting(env.get("lighting", {})),
                color_palette=env.get("color_palette", []),
                all_shots=scene_shots.get(scene_num, []),
                consistency_notes=[
                    f"场景包含 {len(scene_shots.get(scene_num, []))} 个镜头",
                    "保持光线方向和强度一致",
                    "保持背景元素位置一致"
                ]
            )

    def _check_character_consistency(self, storyboard: Dict):
        """检查角色一致性问题"""
        shots = storyboard.get("shots", [])

        # 检查同一角色在不同镜头中的描述是否一致
        for char_name, profile in self.character_profiles.items():
            if len(profile.all_appearances) > 1:
                # 提醒保持一致性
                self.issues.append(ConsistencyIssue(
                    issue_type="character",
                    severity="warning",
                    location=f"角色 {char_name}",
                    description=f"角色在 {len(profile.all_appearances)} 个镜头中出现,需确保视觉一致",
                    suggestion=f"使用种子提示词: {profile.seed_prompt[:50]}..."
                ))

    def _check_scene_consistency(self, storyboard: Dict):
        """检查场景一致性问题"""
        for scene_num, profile in self.scene_profiles.items():
            if len(profile.all_shots) > 3:
                self.issues.append(ConsistencyIssue(
                    issue_type="scene",
                    severity="warning",
                    location=f"场景 {scene_num}",
                    description=f"场景包含 {len(profile.all_shots)} 个镜头,需确保环境一致",
                    suggestion=f"使用场景种子: {profile.seed_prompt[:50]}..."
                ))

    def _check_lighting_consistency(self, storyboard: Dict, scene_data: List[Dict]):
        """检查光线一致性"""
        scene_lighting = {
            s.get("scene_number"): s.get("environment", {}).get("lighting", {})
            for s in scene_data
        }

        shots = storyboard.get("shots", [])

        # 按场景分组检查
        current_scene = None
        current_lighting = None

        for shot in shots:
            scene_num = shot.get("scene_number")
            if scene_num != current_scene:
                current_scene = scene_num
                current_lighting = scene_lighting.get(scene_num, {})

    def _generate_character_seed(
        self,
        name: str,
        prompt_desc: str,
        keywords: List[str]
    ) -> str:
        """生成角色种子提示词"""
        parts = [prompt_desc] if prompt_desc else []
        parts.extend(keywords[:5])

        seed = ", ".join(filter(None, parts))
        return f"[CHARACTER:{name}] {seed}, consistent appearance, same person"

    def _generate_scene_seed(self, scene_info: Dict) -> str:
        """生成场景种子提示词"""
        visual_prompt = scene_info.get("visual_prompt", "")
        mood_keywords = scene_info.get("mood_keywords", [])

        seed = visual_prompt
        if mood_keywords:
            seed += ", " + ", ".join(mood_keywords[:3])

        return f"[SCENE:{scene_info.get('scene_number', 0)}] {seed}, consistent environment"

    def _describe_lighting(self, lighting: Dict) -> str:
        """描述光线设置"""
        parts = []
        if lighting.get("type"):
            parts.append(f"{lighting['type']} lighting")
        if lighting.get("color_temperature"):
            parts.append(f"{lighting['color_temperature']} tone")
        if lighting.get("intensity"):
            parts.append(f"{lighting['intensity']} intensity")
        return ", ".join(parts) if parts else "natural lighting"

    def _generate_global_style_prompt(self, scene_data: List[Dict]) -> str:
        """生成全局风格提示词"""
        # 收集所有场景的共同特征
        all_moods = []
        for scene in scene_data:
            all_moods.extend(scene.get("mood_keywords", []))

        # 选择最常见的氛围词
        from collections import Counter
        mood_counter = Counter(all_moods)
        common_moods = [m for m, _ in mood_counter.most_common(3)]

        style_prompt = "cinematic, high quality, consistent style"
        if common_moods:
            style_prompt += ", " + ", ".join(common_moods)

        return style_prompt

    def _generate_recommendations(self) -> List[str]:
        """生成一致性建议"""
        recommendations = [
            "1. 为每个角色创建参考图,并在所有相关镜头中使用相同的角色种子提示词",
            "2. 同一场景内的所有镜头应使用相同的场景种子提示词作为基础",
            "3. 注意保持光线方向的连续性,避免同一场景内光源方向突变",
            "4. 角色服装在同一场景内应保持一致,除非剧情需要换装",
            "5. 使用一致的色彩调性,可在后期统一调色",
            "6. 建议先生成关键帧确定风格,再批量生成其他镜头",
        ]

        # 根据具体问题添加建议
        char_issues = sum(1 for i in self.issues if i.issue_type == "character")
        if char_issues > 3:
            recommendations.append(
                f"7. 检测到 {char_issues} 个角色一致性提醒,建议使用 LoRA 或角色参考图"
            )

        return recommendations

    def _to_dict(self, global_style: str, recommendations: List[str]) -> Dict:
        """转换为输出字典"""
        return {
            "global_style_prompt": global_style,
            "character_profiles": [
                {
                    "name": p.name,
                    "seed_prompt": p.seed_prompt,
                    "appearance_keywords": p.appearance_keywords,
                    "first_appearance": p.first_appearance,
                    "total_appearances": len(p.all_appearances),
                    "shot_ids": p.all_appearances,
                    "consistency_notes": p.consistency_notes
                }
                for p in self.character_profiles.values()
            ],
            "scene_profiles": [
                {
                    "scene_number": p.scene_number,
                    "location": p.location,
                    "seed_prompt": p.seed_prompt,
                    "lighting_profile": p.lighting_profile,
                    "total_shots": len(p.all_shots),
                    "shot_ids": p.all_shots,
                    "consistency_notes": p.consistency_notes
                }
                for p in self.scene_profiles.values()
            ],
            "issues": [
                {
                    "type": i.issue_type,
                    "severity": i.severity,
                    "location": i.location,
                    "description": i.description,
                    "suggestion": i.suggestion
                }
                for i in self.issues
            ],
            "recommendations": recommendations
        }


def check_consistency(
    storyboard: Dict,
    character_data: Dict[str, Dict],
    scene_data: List[Dict]
) -> Dict:
    """
    一致性检查便捷函数

    Args:
        storyboard: storyboard_generator.py 的输出
        character_data: character_extractor.py 的输出
        scene_data: scene_analyzer.py 的输出

    Returns:
        一致性报告字典
    """
    checker = ConsistencyChecker()
    return checker.check_consistency(storyboard, character_data, scene_data)


if __name__ == "__main__":
    # 示例用法
    sample_storyboard = {
        "shots": [
            {"shot_id": "1-1", "scene_number": 1, "subject": "张伟"},
            {"shot_id": "1-2", "scene_number": 1, "subject": "张伟 and 李娜"},
            {"shot_id": "1-3", "scene_number": 1, "subject": "李娜"},
            {"shot_id": "2-1", "scene_number": 2, "subject": "李娜"},
        ]
    }

    sample_characters = {
        "张伟": {
            "visual_keywords": ["male", "short hair", "suit"],
            "prompt_description": "young Asian male in business suit"
        },
        "李娜": {
            "visual_keywords": ["female", "long hair", "dress"],
            "prompt_description": "young Asian female in casual dress"
        }
    }

    sample_scenes = [
        {"scene_number": 1, "visual_prompt": "office interior", "mood_keywords": ["professional"]},
        {"scene_number": 2, "visual_prompt": "cafe interior", "mood_keywords": ["relaxed"]}
    ]

    result = check_consistency(sample_storyboard, sample_characters, sample_scenes)
    print(json.dumps(result, ensure_ascii=False, indent=2))
