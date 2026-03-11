#!/usr/bin/env python3
"""
提示词优化器 - 优化和精炼AI视频生成提示词
提高提示词的效果和一致性
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class OptimizedPrompt:
    """优化后的提示词"""
    original: str
    optimized: str
    added_keywords: List[str]
    removed_keywords: List[str]
    quality_score: float  # 0-1
    suggestions: List[str]


class PromptOptimizer:
    """提示词优化器"""

    # 质量提升关键词
    QUALITY_BOOSTERS = [
        "high quality",
        "cinematic",
        "professional lighting",
        "detailed",
        "sharp focus",
        "8k",
        "masterpiece",
    ]

    # 视频特定关键词
    VIDEO_KEYWORDS = [
        "smooth motion",
        "natural movement",
        "consistent lighting",
        "temporal coherence",
    ]

    # 应该避免的词
    NEGATIVE_KEYWORDS = [
        "blurry",
        "low quality",
        "distorted",
        "artifacts",
        "glitch",
        "noise",
        "grainy",
    ]

    # 冗余词检测
    REDUNDANT_PATTERNS = [
        (r'\b(very|really|extremely)\s+(very|really|extremely)\b', r'\1'),
        (r'\b(beautiful|pretty)\s+(beautiful|pretty)\b', r'\1'),
        (r'\s+', ' '),  # 多余空格
    ]

    # 景别关键词映射 (标准化)
    SHOT_SIZE_MAPPING = {
        "特写": "close-up",
        "大特写": "extreme close-up",
        "近景": "medium close-up",
        "中景": "medium shot",
        "中远景": "medium long shot",
        "远景": "long shot",
        "大远景": "extreme long shot",
        "全景": "wide shot",
    }

    # 运镜关键词映射
    CAMERA_MOVEMENT_MAPPING = {
        "推": "push in",
        "拉": "pull out",
        "摇": "pan",
        "移": "dolly",
        "跟": "tracking",
        "升": "crane up",
        "降": "crane down",
        "手持": "handheld",
        "固定": "static",
    }

    def __init__(self):
        self.optimization_history: List[OptimizedPrompt] = []

    def optimize(self, prompt: str, context: Dict = None) -> OptimizedPrompt:
        """
        优化单个提示词

        Args:
            prompt: 原始提示词
            context: 上下文信息 (场景、角色等)

        Returns:
            优化后的提示词对象
        """
        original = prompt
        optimized = prompt
        added = []
        removed = []
        suggestions = []

        # 1. 标准化中文术语
        optimized = self._standardize_terms(optimized)

        # 2. 移除冗余
        optimized = self._remove_redundancy(optimized)

        # 3. 检测并移除负面词
        optimized, removed_neg = self._remove_negative_keywords(optimized)
        removed.extend(removed_neg)

        # 4. 添加质量提升词 (如果缺少)
        optimized, added_quality = self._add_quality_boosters(optimized)
        added.extend(added_quality)

        # 5. 添加视频特定关键词 (如果是视频提示词)
        if context and context.get('type') == 'video':
            optimized, added_video = self._add_video_keywords(optimized)
            added.extend(added_video)

        # 6. 优化结构
        optimized = self._optimize_structure(optimized)

        # 7. 计算质量分数
        quality_score = self._calculate_quality_score(optimized)

        # 8. 生成建议
        suggestions = self._generate_suggestions(original, optimized, quality_score)

        result = OptimizedPrompt(
            original=original,
            optimized=optimized,
            added_keywords=added,
            removed_keywords=removed,
            quality_score=quality_score,
            suggestions=suggestions
        )

        self.optimization_history.append(result)
        return result

    def optimize_batch(self, prompts: List[str], context: Dict = None) -> List[OptimizedPrompt]:
        """批量优化提示词"""
        return [self.optimize(p, context) for p in prompts]

    def optimize_storyboard(self, storyboard: Dict) -> Dict:
        """优化整个分镜的提示词"""
        shots = storyboard.get('shots', [])

        for shot in shots:
            if 'visual_prompt' in shot:
                result = self.optimize(
                    shot['visual_prompt'],
                    context={'type': 'video', 'shot': shot}
                )
                shot['visual_prompt_original'] = result.original
                shot['visual_prompt'] = result.optimized
                shot['prompt_quality_score'] = result.quality_score

        # 添加全局风格一致性提示
        global_style = self._extract_global_style(shots)
        storyboard['global_style_prompt'] = global_style

        return storyboard

    def _standardize_terms(self, prompt: str) -> str:
        """标准化术语"""
        result = prompt

        # 标准化景别
        for cn, en in self.SHOT_SIZE_MAPPING.items():
            result = result.replace(cn, en)

        # 标准化运镜
        for cn, en in self.CAMERA_MOVEMENT_MAPPING.items():
            result = result.replace(cn, en)

        return result

    def _remove_redundancy(self, prompt: str) -> str:
        """移除冗余"""
        result = prompt

        for pattern, replacement in self.REDUNDANT_PATTERNS:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        # 移除重复的逗号
        result = re.sub(r',\s*,', ',', result)

        # 移除首尾逗号
        result = result.strip(' ,')

        return result

    def _remove_negative_keywords(self, prompt: str) -> Tuple[str, List[str]]:
        """移除负面关键词"""
        result = prompt
        removed = []

        for keyword in self.NEGATIVE_KEYWORDS:
            if keyword.lower() in result.lower():
                result = re.sub(rf'\b{keyword}\b', '', result, flags=re.IGNORECASE)
                removed.append(keyword)

        return self._remove_redundancy(result), removed

    def _add_quality_boosters(self, prompt: str) -> Tuple[str, List[str]]:
        """添加质量提升关键词"""
        added = []

        # 检查是否已包含质量词
        has_quality = any(
            kw.lower() in prompt.lower()
            for kw in self.QUALITY_BOOSTERS
        )

        if not has_quality:
            # 添加基本质量词
            boosters_to_add = ["high quality", "cinematic"]
            prompt = prompt + ", " + ", ".join(boosters_to_add)
            added.extend(boosters_to_add)

        return prompt, added

    def _add_video_keywords(self, prompt: str) -> Tuple[str, List[str]]:
        """添加视频特定关键词"""
        added = []

        has_video_kw = any(
            kw.lower() in prompt.lower()
            for kw in self.VIDEO_KEYWORDS
        )

        if not has_video_kw:
            video_kw = "smooth motion"
            prompt = prompt + f", {video_kw}"
            added.append(video_kw)

        return prompt, added

    def _optimize_structure(self, prompt: str) -> str:
        """优化提示词结构"""
        # 将提示词分割成部分
        parts = [p.strip() for p in prompt.split(',') if p.strip()]

        # 重新排序: 主体 -> 动作 -> 场景 -> 风格 -> 质量
        # (简单实现,可以更复杂)

        # 确保质量词在最后
        quality_parts = []
        other_parts = []

        for part in parts:
            is_quality = any(
                kw.lower() in part.lower()
                for kw in self.QUALITY_BOOSTERS
            )
            if is_quality:
                quality_parts.append(part)
            else:
                other_parts.append(part)

        # 重组
        all_parts = other_parts + quality_parts

        return ", ".join(all_parts)

    def _calculate_quality_score(self, prompt: str) -> float:
        """计算提示词质量分数"""
        score = 0.5  # 基础分

        # 长度检查 (50-200字符最佳)
        length = len(prompt)
        if 50 <= length <= 200:
            score += 0.1
        elif length < 30:
            score -= 0.1
        elif length > 300:
            score -= 0.05

        # 质量词检查
        quality_count = sum(
            1 for kw in self.QUALITY_BOOSTERS
            if kw.lower() in prompt.lower()
        )
        score += min(quality_count * 0.05, 0.15)

        # 负面词检查
        negative_count = sum(
            1 for kw in self.NEGATIVE_KEYWORDS
            if kw.lower() in prompt.lower()
        )
        score -= negative_count * 0.1

        # 结构检查 (逗号分隔的描述)
        comma_count = prompt.count(',')
        if 3 <= comma_count <= 10:
            score += 0.1

        return max(0, min(1, score))

    def _generate_suggestions(
        self,
        original: str,
        optimized: str,
        quality_score: float
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []

        if quality_score < 0.5:
            suggestions.append("提示词质量较低,建议添加更多描述性细节")

        if len(optimized) < 50:
            suggestions.append("提示词较短,建议添加场景、光线、氛围等描述")

        if len(optimized) > 300:
            suggestions.append("提示词较长,建议精简冗余描述")

        if "lighting" not in optimized.lower() and "光" not in optimized:
            suggestions.append("建议添加光线描述 (如 'soft lighting', 'dramatic shadows')")

        if not any(mood in optimized.lower() for mood in ["mood", "atmosphere", "氛围"]):
            suggestions.append("建议添加氛围描述 (如 'tense atmosphere', 'peaceful mood')")

        return suggestions

    def _extract_global_style(self, shots: List[Dict]) -> str:
        """从所有镜头中提取全局风格"""
        all_prompts = [s.get('visual_prompt', '') for s in shots]

        # 找出共同的关键词
        from collections import Counter

        all_words = []
        for prompt in all_prompts:
            words = [w.strip().lower() for w in prompt.split(',')]
            all_words.extend(words)

        word_counts = Counter(all_words)

        # 选择出现频率超过50%的词
        threshold = len(shots) * 0.5
        common_words = [
            word for word, count in word_counts.items()
            if count >= threshold and len(word) > 3
        ]

        if common_words:
            return ", ".join(common_words[:10])
        else:
            return "cinematic, high quality, consistent style"


def optimize_prompt(prompt: str, context: Dict = None) -> Dict:
    """
    优化提示词的便捷函数

    Args:
        prompt: 原始提示词
        context: 上下文信息

    Returns:
        优化结果字典
    """
    optimizer = PromptOptimizer()
    result = optimizer.optimize(prompt, context)

    return {
        "original": result.original,
        "optimized": result.optimized,
        "added_keywords": result.added_keywords,
        "removed_keywords": result.removed_keywords,
        "quality_score": result.quality_score,
        "suggestions": result.suggestions
    }


if __name__ == "__main__":
    # 示例用法
    test_prompts = [
        "一个女孩在咖啡厅喝咖啡",
        "close-up of man, angry expression, dark room",
        "beautiful beautiful sunset, very very nice, low quality scene"
    ]

    optimizer = PromptOptimizer()

    for prompt in test_prompts:
        result = optimizer.optimize(prompt, context={'type': 'video'})
        print(f"\n原始: {result.original}")
        print(f"优化: {result.optimized}")
        print(f"质量分: {result.quality_score:.2f}")
        print(f"建议: {result.suggestions}")
