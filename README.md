# HSkills

Claude Code 自用 Skills 集合，提供一系列专业技能扩展功能。

---

## 项目简介

HSkills 是一个 Claude Code Skills 仓库，包含多个自定义技能模块，用于扩展 Claude Code 的能力。每个 Skill 都是独立的功能单元，可通过自然语言触发，帮助用户完成特定领域的复杂任务。

---

## 包含的 Skills

### script-to-video-prompts（短剧剧本转AI视频提示词生成器）

将短剧剧本文档智能拆解为可直接用于AI视频生成的完整提示词体系。

**触发词：**
- "剧本转视频提示词"
- "拆解剧本生成分镜"
- "短剧转AI视频"
- "批量生成分镜提示词"
- "剧本可视化"

---

### music-matcher（短视频脚本音乐匹配器）

自动分析短视频脚本，从本地音乐库或 API 音乐服务中匹配出最适合的背景音乐。

**触发词：**
- "帮我配音乐"
- "脚本配乐"
- "找背景音乐"
- "视频配什么音乐"
- "音乐匹配"
- "给脚本找BGM"

---

## script-to-video-prompts 详细说明

### 功能概述

这是一个专业的短剧剧本到AI视频提示词的智能转换工具，能够将剧本文档自动解析并生成：

1. **角色设定提示词** - 包含外貌、服装、性格特征的完整描述
2. **场景设定提示词** - 包含环境、光线、氛围的完整描述
3. **逐镜头分镜提示词** - 包含景别、运镜、动作的专业分镜脚本
4. **一致性校验报告** - 确保跨镜头角色和场景的视觉一致

### 支持的剧本格式

| 格式 | 说明 | 解析方式 |
|------|------|----------|
| .txt | 纯文本格式 | 直接解析 |
| .md | Markdown格式 | 直接解析 |
| .docx | Word文档 | 使用python-docx解析 |
| .pdf | PDF文档 | 使用pdfplumber解析 |
| .fdx | Final Draft格式 | XML解析 |

### 工作流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        剧本文档输入                              │
│              (Word/PDF/TXT/Markdown/Final Draft)                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: 剧本智能解析 (parse_script.py)                         │
│  ├── 自动识别剧本格式（标准编剧格式/自由格式）                    │
│  ├── 提取场次、场景描述、角色对白、动作指示                       │
│  ├── 自动生成场次时长估算                                        │
│  └── 输出结构化剧本数据                                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: 角色设定提取 (character_extractor.py)                  │
│  ├── 基础外貌（年龄、性别、体型、五官特征）                       │
│  ├── 发型发色、肤色                                              │
│  ├── 服装造型（支持多场次服装变化追踪）                           │
│  ├── 角色气质/性格的视觉化表达                                    │
│  └── 生成AI视频生成用角色描述提示词                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: 场景设定分析 (scene_analyzer.py)                       │
│  ├── 场景类型（INT./EXT.、具体地点）                             │
│  ├── 空间结构、关键道具布置                                       │
│  ├── 光线设计（光源类型、方向、强度、色温）                       │
│  ├── 色彩基调、视觉氛围                                          │
│  └── 生成场景视觉提示词                                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: 分镜提示词生成 (storyboard_generator.py)               │
│  ├── 镜头编号（场次-镜号）                                       │
│  ├── 景别选择（ECU/CU/MCU/MS/MLS/LS/ELS）                       │
│  ├── 运镜方式（推/拉/摇/移/跟/升降等）                           │
│  ├── 情绪氛围关键词                                              │
│  ├── 建议时长、转场方式                                          │
│  └── 生成完整AI视频提示词                                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: 一致性校验 (consistency_checker.py)                    │
│  ├── 角色跨镜头一致性控制                                        │
│  ├── 场景连续性检查                                              │
│  ├── 光影风格统一性校验                                          │
│  └── 生成一致性种子提示词                                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 6: 提示词优化 (prompt_optimizer.py)                       │
│  ├── 标准化中文术语为英文                                        │
│  ├── 移除冗余和负面词                                            │
│  ├── 添加质量提升关键词                                          │
│  └── 优化提示词结构                                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 7: 多格式导出 (export_utils.py)                           │
│  ├── JSON - 结构化数据                                          │
│  ├── CSV - 分镜表格                                             │
│  ├── Markdown - 文档格式                                        │
│  ├── Excel - 专业分镜表                                         │
│  └── HTML - 可视化预览                                          │
└─────────────────────────────────────────────────────────────────┘
```

### 目录结构

```
script-to-video-prompts/
├── SKILL.md                              # Skill 定义文件
│
├── scripts/                              # Python 自动化脚本
│   ├── parse_script.py                   # 剧本解析器
│   │   └── 支持 TXT/MD/DOCX/PDF/FDX 格式
│   ├── character_extractor.py            # 角色信息提取器
│   │   └── 外貌、服装、性格特征提取
│   ├── scene_analyzer.py                 # 场景分析器
│   │   └── 环境、光线、氛围分析
│   ├── storyboard_generator.py           # 分镜生成器
│   │   └── 景别、运镜、镜头生成
│   ├── consistency_checker.py            # 一致性校验器
│   │   └── 角色/场景一致性检查
│   ├── prompt_optimizer.py               # 提示词优化器
│   │   └── 标准化、优化、质量提升
│   └── export_utils.py                   # 多格式导出工具
│       └── JSON/CSV/Markdown/Excel/HTML
│
├── references/                           # 规范文档
│   ├── screenplay_format_spec.md         # 剧本格式规范
│   ├── character_template.md             # 角色设定模板
│   │   └── 外貌描述词、服装风格、提示词生成模板
│   ├── scene_template.md                 # 场景设定模板
│   │   └── 环境类型、光线设计、氛围关键词
│   ├── shot_terminology.md               # 景别/运镜术语词典
│   │   └── 8种基础景别 + 15种运镜方式
│   ├── mood_keywords_library.md          # 情绪氛围关键词库
│   │   └── 正负情绪、光线氛围、色彩情绪映射
│   ├── video_style_guide.md              # AI视频风格指南
│   ├── consistency_control.md            # 一致性控制指南
│   │   └── 种子词模板、质量检查清单
│   └── prompt_patterns.md                # 高效提示词模式库
│       └── 镜头模板、情绪场景模板、动作场景模板
│
└── assets/                               # 模板资源
    ├── storyboard_template.csv           # 分镜脚本CSV模板
    ├── export_template.html              # 可视化导出HTML模板
    ├── character_profile_template.json   # 角色档案JSON模板
    └── prompt_cheatsheet.md              # 提示词速查表
```

### 核心功能详解

#### 1. 剧本解析器 (parse_script.py)

**核心类：**
- `ScriptParser` - 主解析器类
- `ScriptElement` - 剧本元素（场景标题、动作、对白等）
- `Scene` - 场景数据结构
- `ParsedScript` - 解析后的完整剧本

**解析能力：**
- 自动识别 INT./EXT. 场景标题
- 支持中文场景格式（"场景X"、"第X场"）
- 提取角色名（全大写或中文人名）
- 识别括号内动作指示
- 自动估算场景时长

**输出示例：**
```json
{
  "title": "剧本标题",
  "metadata": {
    "scene_count": 10,
    "character_count": 5,
    "location_count": 3
  },
  "all_characters": ["张伟", "李娜", "王老师"],
  "scenes": [...]
}
```

#### 2. 角色提取器 (character_extractor.py)

**核心类：**
- `CharacterExtractor` - 角色信息提取器
- `CharacterProfile` - 完整角色档案
- `CharacterAppearance` - 外貌设定
- `CharacterCostume` - 服装设定

**提取维度：**
| 维度 | 关键词示例 |
|------|-----------|
| 年龄 | 婴儿/儿童/少年/青年/中年/老年 |
| 性别 | 男/女/男性/女性 |
| 体型 | 瘦/苗条/健壮/魁梧 |
| 发型 | 长发/短发/卷发/马尾 |
| 发色 | 黑发/金发/棕发 |
| 服装风格 | 正装/休闲/运动/制服 |

**输出示例：**
```json
{
  "张伟": {
    "name": "张伟",
    "appearance": {
      "gender": "male",
      "age_range": "25-30",
      "hair_style": "short hair",
      "hair_color": "black hair"
    },
    "visual_keywords": ["male", "short hair", "suit"],
    "prompt_description": "young Asian male, short black hair, wearing business suit"
  }
}
```

#### 3. 场景分析器 (scene_analyzer.py)

**核心类：**
- `SceneAnalyzer` - 场景分析器
- `SceneEnvironment` - 场景环境设定
- `LightingSetup` - 光线设置

**场景类型库：**
| 室内场景 | 室外场景 |
|----------|----------|
| 办公室、卧室、客厅 | 街道、公园、海滩 |
| 咖啡厅、酒吧、餐厅 | 森林、山、停车场 |
| 医院、教室、电梯 | 天台、校园 |

**光线时段映射：**
| 时段 | 光线特征 | 色温 |
|------|----------|------|
| DAWN | 柔和金色，长影 | 暖 |
| MORNING | 明亮清新 | 中性 |
| DAY | 强烈直射 | 中性偏冷 |
| DUSK | 金橙色，长影 | 暖 |
| NIGHT | 人造光源 | 冷 |

#### 4. 分镜生成器 (storyboard_generator.py)

**核心类：**
- `StoryboardGenerator` - 分镜生成器
- `Shot` - 单个镜头
- `Storyboard` - 完整分镜脚本

**景别枚举：**
```python
class ShotSize(Enum):
    ECU = "extreme close-up"   # 大特写
    CU = "close-up"            # 特写
    MCU = "medium close-up"    # 中近景
    MS = "medium shot"         # 中景
    MLS = "medium long shot"   # 中远景
    LS = "long shot"           # 远景
    ELS = "extreme long shot"  # 大远景
```

**运镜枚举：**
```python
class CameraMovement(Enum):
    STATIC = "static"      # 固定
    PAN = "pan"            # 摇
    TILT = "tilt"          # 俯仰
    PUSH = "push in"       # 推
    PULL = "pull out"      # 拉
    DOLLY = "dolly"        # 移动
    TRACK = "tracking"     # 跟踪
    CRANE = "crane"        # 升降
    HANDHELD = "handheld"  # 手持
```

**智能映射：**
- 动作→景别映射（表情→特写，对话→中近景）
- 情绪→运镜映射（紧张→手持+推，浪漫→轨道+环绕）

#### 5. 一致性校验器 (consistency_checker.py)

**核心类：**
- `ConsistencyChecker` - 一致性校验器
- `CharacterConsistencyProfile` - 角色一致性档案
- `SceneConsistencyProfile` - 场景一致性档案
- `ConsistencyIssue` - 一致性问题

**校验维度：**
1. 角色跨镜头一致性
2. 场景连续性
3. 光影风格统一性

**输出种子提示词格式：**
```
[CHARACTER:角色名] 外貌描述, consistent appearance, same person
[SCENE:场景号] 场景描述, consistent environment
```

#### 6. 提示词优化器 (prompt_optimizer.py)

**优化流程：**
1. 标准化中文术语为英文
2. 移除冗余词汇
3. 检测并移除负面词
4. 添加质量提升关键词
5. 优化提示词结构

**质量提升关键词：**
- high quality, cinematic, professional lighting
- detailed, sharp focus, 8k, masterpiece

**视频特定关键词：**
- smooth motion, natural movement, temporal coherence

#### 7. 导出工具 (export_utils.py)

**支持格式：**
| 格式 | 说明 | 特点 |
|------|------|------|
| JSON | 结构化数据 | 完整数据，便于程序处理 |
| CSV | 分镜表格 | 简洁表格，便于查看 |
| Markdown | 文档格式 | 可读性强，便于分享 |
| Excel | 专业分镜表 | 多Sheet，样式美观 |
| HTML | 可视化预览 | 浏览器打开，美观展示 |

---

### 参考文档说明

#### 景别/运镜术语词典 (shot_terminology.md)

包含完整的影视专业术语：

**8种基础景别：**
| 缩写 | 英文 | 中文 | 用途 |
|------|------|------|------|
| ECU | Extreme Close-Up | 大特写 | 强调情绪、细节 |
| CU | Close-Up | 特写 | 表情、反应 |
| MCU | Medium Close-Up | 中近景 | 对话、采访 |
| MS | Medium Shot | 中景 | 常规对话 |
| MLS | Medium Long Shot | 中远景 | 动作+环境 |
| LS | Long Shot | 远景 | 展示动作 |
| ELS | Extreme Long Shot | 大远景 | 建立场景 |

**15种运镜方式：**
- 基础：固定、推、拉、摇、俯仰、移、跟、升降、环绕
- 进阶：手持、稳定器、变焦、甩镜、滑轨、航拍

#### 情绪氛围关键词库 (mood_keywords_library.md)

**情绪分类：**
- 正面：快乐、兴奋、平静、温暖、希望、浪漫、自信
- 负面：悲伤、愤怒、恐惧、孤独、绝望、焦虑
- 复杂：神秘、怀旧、沉思、紧张、困惑

**色彩情绪映射：**
| 颜色 | 情绪关联 |
|------|----------|
| 红色 | 热情、危险、愤怒、爱 |
| 蓝色 | 冷静、悲伤、信任、冷 |
| 金色 | 奢华、温暖、怀旧 |
| 紫色 | 神秘、奢华、灵性 |

#### 角色设定模板 (character_template.md)

**角色档案结构：**
- 基础信息：年龄、性别、种族、体型
- 外貌特征：发型发色、眼睛、脸型、特征标记
- 服装设定：风格、颜色、配饰
- 性格表现：性格特征到视觉表达的映射

**提示词模板：**
```
[age] [gender] [ethnicity], [body_type] build,
[hair_color] [hair_style] hair, [eye_color] eyes,
wearing [costume_description], [expression]
```

#### 场景设定模板 (scene_template.md)

**场景档案结构：**
- 环境信息：类型、地点、空间布局
- 时间信息：时段、季节、天气
- 光线设计：光源类型、方向、强度、色温
- 氛围设定：情绪氛围、色彩基调

#### 一致性控制指南 (consistency_control.md)

**核心原理：**
1. 种子词锁定 - 固定描述作为锚点
2. 参考图控制 - 提供参考图像
3. 特征强调 - 重复强调关键特征
4. 排除变化 - 明确排除不希望的变化

**种子词模板：**
```
[CHARACTER:ID] 描述, consistent appearance, same person
[SCENE:ID] 描述, consistent environment
```

#### 高效提示词模式库 (prompt_patterns.md)

**提示词公式：**
```
[主体] + [动作] + [场景] + [光线] + [氛围] + [风格] + [质量]
```

**镜头模板示例：**
- 建立镜头模板
- 人物特写模板
- 对话双人镜头模板
- 过肩镜头模板
- 跟随镜头模板

---

### 输出结构示例

```
一、项目元数据
   - 片名、集数、总时长、场次数

二、风格总设定
   - 画面风格、色彩体系、光影风格

三、角色设定库
   [
     {
       "name": "张伟",
       "appearance": {...},
       "visual_keywords": [...],
       "prompt_description": "young Asian male...",
       "seed_prompt": "[CHARACTER:张伟] ..."
     }
   ]

四、场景设定库
   [
     {
       "scene_number": 1,
       "environment": {...},
       "visual_prompt": "interior of modern office...",
       "seed_prompt": "[SCENE:1] ..."
     }
   ]

五、完整分镜提示词
   [
     {
       "shot_id": "1-1",
       "scene_number": 1,
       "shot_size": "long shot",
       "camera_movement": "static",
       "subject": "establishing shot",
       "duration": 3.0,
       "visual_prompt": "establishing shot, interior of modern office, cinematic"
     }
   ]

六、一致性参考表
   - 角色/场景一致性种子词
   - 一致性问题列表
   - 优化建议
```

---

## music-matcher 详细说明

### 功能概述

这是一个智能短视频音乐匹配工具，能够分析视频脚本的情感需求，从音乐库中匹配出最适合的背景音乐。

**核心能力：**
1. **脚本情感分析** - 自动提取脚本的情绪基调、情节节奏、风格类型
2. **音乐库接入** - 支持本地文件夹和 API 两种方式
3. **智能匹配** - 综合情绪、节奏、风格、时长多维度评分
4. **本地音频分析** - 使用 librosa 提取 BPM、能量、调性等特征
5. **多模态 AI 分析** - 支持 Claude/OpenAI API 深度理解音乐语义

### 音乐库输入方式

#### 方式一：本地文件夹

```
【音乐库路径】
~/Music/BGM
```

**支持格式：** MP3, WAV, FLAC, AAC, M4A, OGG

**自动分析内容：**
- BPM（节奏速度）
- 能量等级（低/中/高）
- 调性（大调/小调）
- 频谱特征（亮度、丰富度）
- 情绪预测

#### 方式二：API 接口

```
【音乐API】
接口地址：https://api.example.com/music
认证方式：Bearer Token
认证信息：xxx
请求方式：GET
```

**API 响应字段映射：**
| 原始字段名 | 标准字段 |
|-----------|---------|
| title / name / song_name | title |
| duration / length / time | duration |
| bpm / tempo / beat | bpm |
| genre / style / category | genre |
| mood / emotion / feeling | mood |
| tags / labels / keywords | tags |
| audio_url / url / stream_url | audio_url |

### 工作流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      用户输入                                    │
│   视频脚本 + 音乐库路径/API配置                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: 获取音乐库                                             │
│  本地模式: 扫描目录 → 分析音频特征 → 缓存元数据                   │
│  API模式: 调用API → 解析响应 → 字段映射                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: 分析脚本                                               │
│  ├── 整体情绪基调（欢乐/悲伤/紧张/温馨/励志等）                   │
│  ├── 情绪走向（持续稳定/逐渐升温/先抑后扬）                       │
│  ├── 情节节奏（快/中/慢）                                        │
│  └── 风格类型（生活记录/剧情短片/商业广告等）                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: 综合匹配评分                                           │
│  ├── 情绪匹配 (40%)                                             │
│  ├── 节奏匹配 (30%)                                             │
│  ├── 风格匹配 (20%)                                             │
│  └── 时长适配 (10%)                                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: 输出推荐                                               │
│  推荐音乐 + 匹配度 + 推荐理由 + 使用建议                          │
└─────────────────────────────────────────────────────────────────┘
```

### 目录结构

```
music-matcher/
├── SKILL.md                    # Skill 定义文件
│   ├── 音乐库输入方式说明
│   ├── 工作流程详解
│   ├── API 调用指南
│   ├── 本地音频分析实现
│   └── 多模态 AI 分析配置
│
└── evals/                      # 评估测试
    └── evals.json              # 测试用例
        ├── 晨跑活力场景
        ├── 亲情温馨场景
        └── 科技产品发布会
```

### 匹配评分维度

| 维度 | 权重 | 匹配逻辑 |
|------|------|----------|
| 情绪匹配 | 40% | 音乐情绪与脚本情绪基调一致 |
| 节奏匹配 | 30% | BPM与叙事节奏匹配 |
| 风格匹配 | 20% | 音乐风格与内容类型协调 |
| 时长适配 | 10% | 音乐时长与脚本预估时长接近 |

**节奏匹配参考表：**
| 叙事节奏 | 推荐BPM |
|----------|---------|
| 慢节奏叙事 | 60-90 |
| 中等节奏 | 90-120 |
| 快节奏/紧张 | 120-160+ |

### 本地音频分析

**依赖安装：**
```bash
# ffmpeg（音频处理）
brew install ffmpeg  # macOS

# Python 依赖
pip install librosa numpy scipy

# 可选：专业音频分析
pip install essentia
```

**分析内容：**

| 分析项 | 工具 | 输出 |
|--------|------|------|
| 时长 | ffmpeg | 秒数 |
| BPM | librosa | 节拍数/分钟 |
| 能量 | librosa (RMS) | 低/中/高 |
| 调性 | librosa (chroma) | 大调/小调 |
| 频谱特征 | librosa | 亮度、丰富度 |
| 情绪预测 | 综合分析 | 欢快/忧伤/紧张等 |

**情绪预测逻辑：**
```python
# 欢快：快节奏 + 高能量 + 大调 + 明亮
if bpm > 100 and energy > 0.03 and mode == 'major':
    mood = '欢快'

# 忧伤：慢节奏 + 低能量 + 小调
if bpm < 90 and energy < 0.03 and mode == 'minor':
    mood = '忧伤'

# 紧张：快节奏 + 高能量 + 小调
if bpm > 120 and energy > 0.04 and mode == 'minor':
    mood = '紧张'
```

### 多模态 AI 分析

支持调用 Claude/OpenAI API 深度理解音乐语义：

**Claude API 配置：**
```
【多模态AI API】
服务提供商: Claude
接口地址: https://api.anthropic.com/v1/messages
认证方式: Header (x-api-key)
认证信息: sk-ant-xxx
模型: claude-sonnet-4-6
```

**AI 分析输出：**
```json
{
  "mood": "欢快",
  "mood_intensity": 8,
  "energy_level": "中高",
  "rhythm": "明快紧凑",
  "genre": "流行电子",
  "instruments": ["钢琴", "电子合成器", "鼓"],
  "suitable_scenes": ["清晨", "运动", "旅行", "广告"],
  "emotional_arc": "从平静开场，逐渐展开，中段达到明亮高潮",
  "keywords": ["阳光", "活力", "希望", "清新"],
  "description": "一首温暖明亮的轻音乐，传递清晨阳光般的希望感"
}
```

### 输出示例

```
## 脚本分析

**情绪基调：** 活力、积极、阳光
**情绪走向：** 逐渐升温（平静开场→活力高潮）
**情节节奏：** 中等节奏
**风格类型：** 生活记录/Vlog

**音乐需求画像：**
- 情绪需求：欢快、充满活力和希望
- BPM 需求：100-130（配合慢跑节奏）
- 能量需求：中高
- 场景标签：清晨、运动、活力

---

## 最佳背景音乐推荐

**推荐音乐：** Morning Light
**来源：** API (track_id: tr_001)
**匹配度：** 94%

### 音乐信息
- 时长：2:15
- BPM：118
- 风格：流行电子
- 情绪：欢快、充满希望
- 音频地址：https://cdn.example.com/tr_001.mp3

### 推荐理由
脚本的"清晨公园晨跑"场景与音乐的"清晨、运动"标签高度匹配。
BPM 118 完美契合慢跑节奏，情绪从平静到活力的走向与镜头节奏同步。

### 使用建议
- 建议从第 5 秒开始使用
- 结尾处做 2 秒淡出
- 音量建议 -8dB
```

---

## 使用方法

### 在 Claude Code 中使用

在 Claude Code 对话中直接使用触发词即可激活对应的 Skill：

```
用户: 帮我把这个剧本文档转成视频提示词
Claude: [自动触发 script-to-video-prompts skill]
```

### 脚本独立使用

每个脚本都可以独立运行：

```bash
# 解析剧本
python script-to-video-prompts/scripts/parse_script.py my_script.txt

# 示例输出
{
  "title": "my_script",
  "metadata": {
    "scene_count": 5,
    "character_count": 3
  },
  ...
}
```

```python
# Python 中使用
from scripts.parse_script import parse_script
from scripts.character_extractor import extract_characters
from scripts.scene_analyzer import analyze_scenes
from scripts.storyboard_generator import generate_storyboard

# 1. 解析剧本
parsed = parse_script("剧本.docx")

# 2. 提取角色
characters = extract_characters(parsed)

# 3. 分析场景
scenes = analyze_scenes(parsed)

# 4. 生成分镜
storyboard = generate_storyboard(parsed, scenes, characters)
```

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3 |
| 文档解析 | python-docx, pdfplumber |
| 数据导出 | openpyxl, csv, json |
| 数据结构 | dataclass, enum |

**依赖安装：**
```bash
pip install python-docx pdfplumber openpyxl
```

---

## 扩展计划

- [ ] 添加更多剧本格式支持（Celtx、Fade In）
- [ ] 集成主流 AI 视频平台 API（Runway、Pika、Sora）
- [ ] 添加多语言支持（英语剧本处理）
- [ ] 添加音频提示词生成（背景音乐、音效）
- [ ] 添加批量处理和队列管理

---

## 许可证

MIT License

---

## 贡献

欢迎提交 Issue 和 Pull Request。