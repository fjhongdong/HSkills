# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指导。

## 项目概述

HSkills 是一组 Claude Code Skills，专注于三大核心领域：**短视频内容创作**、**服饰/时尚**、**AI 视频生成**。每个 Skill 都是独立的功能单元，通过自然语言触发。

## 架构

### Skill 结构

每个 Skill 遵循标准化结构：

```
skill-name/
├── SKILL.md          # 必需 - 包含 frontmatter 的 Skill 定义
├── scripts/          # 可选 - 自动化脚本
├── references/       # 可选 - 参考文档
├── evals/           # 推荐 - 评估测试
└── workspace/       # 可选 - 迭代工作目录
```

### SKILL.md 格式

每个 SKILL.md 必须以 YAML frontmatter 开头：

```yaml
---
name: skill-name
description: 详细描述，包含触发关键词和核心功能
---
```

description 字段应包含：
- 核心功能
- 触发关键词/短语
- Skill 激活时机

### Skill 分类

| 分类 | Skills |
|------|--------|
| 短视频创作 | hot-script-generator, video-shot-breakdown |
| 服饰/时尚 | clothing-analyzer, outfit-character-generator, video-fashion-placement-analyzer |
| AI 视频 | script-to-video |
| 工具类 | music-matcher, github-repo-search |

## 开发命令

### 环境配置

```bash
# 视频处理
brew install ffmpeg

# 音频分析（music-matcher 使用）
pip install librosa numpy scipy

# 文档解析（script-to-video 使用）
pip install python-docx pdfplumber

# HTTP 请求
pip install requests
```

### 运行脚本

```bash
# 从视频提取帧（video-fashion-placement-analyzer）
python video-fashion-placement-analyzer/scripts/extract_frames.py <video_path> [output_dir] [--mode basic|scene]

# 剧本转视频工具
python script-to-video/scripts/parse_script.py <script_file>
python script-to-video/scripts/character_extractor.py <script_file>
python script-to-video/scripts/scene_analyzer.py <script_file>
```

## 关键设计原则

### hot-script-generator 铁律

1. **种草核心**: 无服饰特写；服饰仅作为故事背景
2. **全片一致性**: 角色与服饰全片完全一致
3. **爆款适配**: 9:16 竖屏格式，前 3 秒强钩子，15-30 秒时长，4-8 个镜头
4. **审美合规**: 遵循东方正向审美原则

### github-repo-search 工作流约束

**需求收敛是强制性的** - 任何搜索前，必须与用户确认：
- 主题（agent memory、RAG、browser automation 等）
- 数量（Top 10/Top 20）
- 最低星数（默认：100）
- 排序方式（相关性优先或星数优先）
- 目标形式（产品/框架/文档）

即使用户说"直接搜索"，也不可跳过此步骤。

### 多维多样化策略

生成脚本时，使用 9 个维度避免同质化：
1. 脚本类型（剧情/vlog/氛围/情侣/季节/旅行）
2. 开场钩子（视觉冲击/情感冲击/悬念/冲突/惊喜/对比）
3. 叙事结构（线性/倒叙/插叙/蒙太奇/循环）
4. 情绪基调（治愈/热烈/忧郁/幽默/静谧/反转）
5. 视觉风格（日系/韩系/西式/中式/家居/都市）
6. 镜头语言（手持/固定/航拍/POV/跟拍/慢动作）
7. 对话风格（独白/对话/默片/旁白/电话/网感）
8. 节奏（慢/快/渐变/平衡）
9. 创新元素（反转/对比/象征/时间跳跃/转场/套层叙事）

### 抖音爆款节奏框架（多高潮设计）

对于 15-30 秒脚本，设计 2-3 个高潮点：
- **0-3秒**: 强钩子（视觉/情感冲击）
- **3-8秒**: 第一高潮（核心情绪或关键时刻）
- **8-15秒**: 铺垫/张力阶段
- **15-22秒**: 第二高潮（情绪峰值或反转）
- **22-30秒**: 收尾/尾声（温和落地或难忘结尾）

脚本生成公式：`脚本 = 热点深度分析报告 + 角色形象分析 + 9维度多样化策略 + 爆款节奏框架`

### 热点分析报告结构（hot-script-generator）

每个热点分析必须包含 9 个部分：
1. 热点信息（标题、摘要、情绪基调）
2. 情绪深度分析（表层 → 深层 → 矛盾点 → 出口）
3. 主题深度挖掘（现象 → 议题 → 痛点 → 受众 → 价值）
4. 推演结果（场景、风格、故事线、情绪曲线、角色状态）
5. 标签提炼（情绪/主题/场景/风格/受众标签）
6. 关键词提炼（核心/情绪/场景/动作/视觉关键词）
7. 议题分析（核心议题、背景、热度、需求、转化）
8. 颜材预测（适合脚本类型、传播潜力、爆款可能性）
9. 创作建议（推荐脚本/钩子类型、关键要点）

### 视频分析决策逻辑

对于 video-shot-breakdown 和 video-fashion-placement-analyzer：

| 条件 | 方法 | 原因 |
|------|------|------|
| 时长 ≤ 2分钟 & 大小 ≤ 100MB | 直接视频分析 | 捕捉镜头运动、转场、音画同步 |
| 时长 > 2分钟 或 大小 > 100MB | 关键帧提取 | 避免超出模型限制 |

## Skill 依赖

| Skill | 必需工具 |
|-------|----------|
| video-shot-breakdown | ffmpeg |
| video-fashion-placement-analyzer | ffmpeg, Python 3.6+ |
| music-matcher | librosa, numpy, scipy |
| script-to-video | python-docx, pdfplumber |

## 输出格式

大多数 Skill 输出两种格式的结构化数据：
1. **Markdown**: 人类可读的报告和脚本
2. **JSON**: 机器可解析的结构化输出（在各 SKILL.md 中定义）

video-shot-breakdown 和 script-to-video 的 JSON 输出格式特别详细，应严格遵循各自 SKILL.md 中的规定。