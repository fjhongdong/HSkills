---
name: script-to-video
description: 短剧剧本转AI视频提示词生成器。将用户上传的短剧剧本文档智能拆解为可直接用于AI视频生成的完整提示词体系。输出包括：角色设定提示词、场景设定提示词、逐镜头分镜提示词。支持批量处理、多格式导出、一致性校验。当用户说"剧本转视频提示词"、"拆解剧本生成分镜"、"短剧转AI视频"、"批量生成分镜提示词"、"剧本可视化"时触发。
---

# 短剧剧本转视频提示词生成器

将短剧剧本文档智能拆解为可直接用于AI视频生成的完整提示词体系，支持自动化批量处理。

## 用户输入

- 短剧剧本文档（Word/PDF/TXT/Markdown/Final Draft .fdx）
- 可选：风格参考图片、角色参考图片、已有角色设定表

## 工作流程

### 1. 剧本智能解析

使用 `scripts/parse_script.py` 解析剧本：
- 自动识别剧本格式（标准编剧格式/自由格式）
- 提取场次(Scene)、场景描述(Action)、角色对白(Dialogue)、动作指示(Parenthetical)
- NLP分析：情绪曲线、节奏变化、画面密度
- 自动生成场次时长估算

### 2. 角色设定提取

使用 `scripts/character_extractor.py` 提取角色信息：
- 基础外貌（年龄、性别、体型、五官特征）
- 发型发色、肤色
- 服装造型（支持多场次服装变化追踪）
- 角色气质/性格的视觉化表达
- 标志性道具/配饰

输出格式参考 [references/character_template.md](references/character_template.md)

### 3. 场景设定分析

使用 `scripts/scene_analyzer.py` 分析场景：
- 场景类型（INT./EXT.、具体地点）
- 空间结构、关键道具布置
- 光线设计（光源类型、方向、强度、色温）
- 色彩基调、视觉氛围
- 天气/时间/季节

输出格式参考 [references/scene_template.md](references/scene_template.md)

### 4. 分镜提示词生成

使用 `scripts/storyboard_generator.py` 生成分镜：
- 镜头编号（场次-镜号）
- 景别（ECU/CU/MCU/MS/MLS/LS/ELS），详见 [references/shot_terminology.md](references/shot_terminology.md)
- 画面构图（三分法位置、视线引导）
- 角色动作、表情、站位
- 运镜方式，详见 [references/shot_terminology.md](references/shot_terminology.md)
- 情绪氛围关键词，详见 [references/mood_keywords_library.md](references/mood_keywords_library.md)
- 建议时长（秒）
- 转场方式

### 5. 一致性校验

使用 `scripts/consistency_checker.py` 校验：
- 角色跨镜头一致性控制
- 场景连续性检查
- 光影风格统一性校验
- 详见 [references/consistency_control.md](references/consistency_control.md)

### 6. 导出

使用 `scripts/export_utils.py` 导出：
- 支持格式：Markdown/JSON/CSV/Excel
- 支持按场次/角色/场景分类导出
- 可生成可视化分镜脚本

## 输出结构

```
一、项目元数据
   - 片名、集数、总时长、场次数

二、风格总设定
   - 画面风格、色彩体系、光影风格

三、角色设定库
   - JSON结构化数据 + 自然语言描述

四、场景设定库
   - JSON结构化数据 + 自然语言描述

五、完整分镜提示词
   - 按场次顺序排列

六、一致性参考表
   - 角色/场景一致性种子词
```

## 参考文件

### scripts/（自动化脚本）
- `parse_script.py` - 剧本解析器
- `character_extractor.py` - 角色信息提取
- `scene_analyzer.py` - 场景分析
- `storyboard_generator.py` - 分镜生成
- `consistency_checker.py` - 一致性校验
- `export_utils.py` - 多格式导出
- `prompt_optimizer.py` - 提示词优化

### references/（规范文档）
- `screenplay_format_spec.md` - 剧本格式规范
- `character_template.md` - 角色设定模板
- `scene_template.md` - 场景设定模板
- `shot_terminology.md` - 景别/运镜术语词典
- `mood_keywords_library.md` - 情绪氛围关键词库
- `video_style_guide.md` - AI视频风格指南
- `consistency_control.md` - 一致性控制指南
- `prompt_patterns.md` - 高效提示词模式库

### assets/（模板资源）
- `storyboard_template.xlsx` - 分镜脚本Excel模板
- `export_template.html` - 可视化导出HTML模板
