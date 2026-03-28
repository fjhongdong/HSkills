# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HSkills is a collection of Claude Code Skills focused on three core domains: **short video content creation**, **fashion/apparel**, and **AI video generation**. Each skill is an independent functional unit triggered by natural language.

## Architecture

### Skill Structure

Each skill follows a standardized structure:

```
skill-name/
├── SKILL.md          # Required - Skill definition with frontmatter
├── scripts/          # Optional - Automation scripts
├── references/       # Optional - Reference documentation
├── evals/           # Recommended - Evaluation tests
└── workspace/       # Optional - Working directory for iterations
```

### SKILL.md Format

Every SKILL.md must start with YAML frontmatter:

```yaml
---
name: skill-name
description: Detailed description including trigger keywords and core functionality
---
```

The description field should include:
- Core functionality
- Trigger keywords/phrases
- When to activate the skill

### Skill Categories

| Category | Skills |
|----------|--------|
| Short Video Creation | hot-script-generator, video-shot-breakdown |
| Fashion/Apparel | clothing-analyzer, outfit-character-generator, video-fashion-placement-analyzer |
| AI Video | script-to-video |
| Utilities | music-matcher, github-repo-search |

## Development Commands

### Environment Setup

```bash
# Video processing
brew install ffmpeg

# Audio analysis (for music-matcher)
pip install librosa numpy scipy

# Document parsing (for script-to-video)
pip install python-docx pdfplumber

# HTTP requests
pip install requests
```

### Running Scripts

```bash
# Extract frames from video (video-fashion-placement-analyzer)
python video-fashion-placement-analyzer/scripts/extract_frames.py <video_path> [output_dir] [--mode basic|scene]

# Script-to-video tools
python script-to-video/scripts/parse_script.py <script_file>
python script-to-video/scripts/character_extractor.py <script_file>
python script-to-video/scripts/scene_analyzer.py <script_file>
```

## Key Design Principles

### hot-script-generator Iron Laws

1. **Seed Core (种草核心)**: No clothing close-ups; apparel only as story background
2. **Consistency (全片一致性)**: Character and clothing must be completely consistent throughout
3. **Viral Adaptation (爆款适配)**: 9:16 vertical format, strong hook in first 3 seconds, 15-30 seconds, 4-8 shots
4. **Aesthetic Compliance (审美合规)**: Follow Eastern positive aesthetic principles

### github-repo-search Workflow Constraint

**Requirements convergence is mandatory** - Before any search, must confirm with user:
- Topic (agent memory, RAG, browser automation, etc.)
- Quantity (Top 10/Top 20)
- Minimum stars (default: 100)
- Sort mode (relevance-first or stars-first)
- Target form (product/framework/documentation)

Do not skip this step even if user says "just search directly".

### Multi-dimensional Diversity Strategy

When generating scripts, use 9 dimensions to avoid homogenization:
1. Script type (drama/vlog/atmosphere/couple/seasonal/travel)
2. Opening hook (visual impact/emotional impact/suspense/conflict/surprise/contrast)
3. Narrative structure (linear/flashback/insert/montage/loop)
4. Emotional tone (healing/passionate/melancholic/humorous/quiet/reversal)
5. Visual style (Japanese/Korean/Western/Chinese/home/urban)
6. Camera language (handheld/fixed/aerial/POV/following/slow-motion)
7. Dialogue style (monologue/conversation/silent/voiceover/phone/internet-slang)
8. Pacing (slow/fast/gradual/balanced)
9. Innovation elements (reversal/contrast/symbol/time-jump/transition/frame-narrative)

### Douyin Viral Rhythm Framework (Multi-Climax Design)

For 15-30 second scripts, design 2-3 climax points:
- **0-3s**: Strong hook (visual/emotional impact)
- **3-8s**: First climax (core emotion or key moment)
- **8-15s**: Buildup/tension phase
- **15-22s**: Second climax (emotion peak or reversal)
- **22-30s**: Closing/coda (gentle landing or memorable ending)

Script generation formula: `脚本 = 热点深度分析报告 + 角色形象分析 + 9维度多样化策略 + 爆款节奏框架`

### Hotspot Analysis Report Structure (hot-script-generator)

Every hotspot analysis must include 9 parts:
1. 热点信息 (title, summary, emotion tone)
2. 情绪深度分析 (surface → deep → contradictions → outlets)
3. 主题深度挖掘 (phenomenon → issue → pain point → audience → value)
4. 推演结果 (scene, style, storyline, emotion arc, character state)
5. 标签提炼 (emotion/theme/scene/style/audience tags)
6. 关键词提炼 (core/emotion/scene/action/visual keywords)
7. 议题分析 (core issue, background, heat, demand, transformation)
8. 题材预测 (suitable script types, spread potential, viral possibility)
9. 创作建议 (recommended script/hook types, key points)

### Video Analysis Decision Logic

For video-shot-breakdown and video-fashion-placement-analyzer:

| Condition | Method | Reason |
|-----------|--------|--------|
| Duration ≤ 2min & Size ≤ 100MB | Direct video analysis | Captures camera movement, transitions, audio sync |
| Duration > 2min or Size > 100MB | Keyframe extraction | Avoids model limits |

## Skill Dependencies

| Skill | Required Tools |
|-------|---------------|
| video-shot-breakdown | ffmpeg |
| video-fashion-placement-analyzer | ffmpeg, Python 3.6+ |
| music-matcher | librosa, numpy, scipy |
| script-to-video | python-docx, pdfplumber |

## Output Formats

Most skills output structured data in two formats:
1. **Markdown**: Human-readable reports and scripts
2. **JSON**: Machine-parsable structured output (defined in each SKILL.md)

The JSON output format for video-shot-breakdown and script-to-video is particularly detailed and should be followed exactly as specified in their respective SKILL.md files.