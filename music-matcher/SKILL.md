---
name: music-matcher
description: 自动匹配短视频脚本与音乐库，找出最适合的背景音乐。当用户说"帮我配音乐"、"脚本配乐"、"找背景音乐"、"视频配什么音乐"、"音乐匹配"、"给脚本找BGM"时触发此skill。即使没有明确说"配音乐"，只要用户提供了脚本并询问音乐相关建议，也应使用此skill。
---

# 音乐匹配器 (Music Matcher)

自动分析短视频脚本，从本地音乐库或 API 音乐服务中匹配出最适合的背景音乐。

## 音乐库输入方式

支持两种音乐库输入方式：

### 方式一：本地文件夹

用户提供本地音乐库路径，如：
- `~/Music/BGM`
- `/Users/xxx/Music/背景音乐`

系统将自动对本地音频文件进行深度分析，提取 BPM、能量、调性、情绪等特征。详见【本地音频分析】章节。

### 方式二：API 接口

用户提供音乐 API 信息，格式如下：

```
【音乐API】
接口地址：https://api.example.com/music
认证方式：Bearer Token / API Key / 无需认证
认证信息：xxx（可选）
请求方式：GET / POST
```

**API 响应要求：**

API 应返回音乐列表，每首音乐包含以下字段（字段名可自定义）：

```json
{
  "music_list": [
    {
      "id": "music_001",
      "title": "歌曲名称",
      "artist": "艺术家",
      "duration": 180,
      "bpm": 120,
      "genre": "流行",
      "mood": "欢快",
      "tags": ["活力", "清晨", "运动"],
      "audio_url": "https://cdn.example.com/music.mp3"
    }
  ],
  "total": 100
}
```

**必需字段：**
- `title` 或 `name` - 音乐名称
- `id` - 音乐唯一标识

**推荐字段（用于匹配）：**
- `duration` - 时长（秒）
- `bpm` - 每分钟节拍数
- `genre` 或 `style` - 风格
- `mood` 或 `emotion` - 情绪
- `tags` - 标签数组
- `audio_url` 或 `url` - 音频流/下载地址

---

## 工作流程

### 第一步：获取音乐库

根据用户提供的输入类型，获取音乐库数据：

**本地文件夹模式：**
1. 扫描指定目录
2. 支持格式：MP3, WAV, FLAC, AAC, M4A, OGG
3. 自动分析或从文件名推断元数据

**API 模式：**
1. 调用用户提供的 API 接口
2. 解析响应数据，提取音乐列表
3. 自动映射字段名到标准格式

```
字段映射规则：
- 名称：title / name / song_name / track → title
- 时长：duration / length / time → duration
- 节奏：bpm / tempo / beat → bpm
- 风格：genre / style / category → genre
- 情绪：mood / emotion / feeling → mood
- 标签：tags / labels / keywords → tags
- 音频地址：audio_url / url / stream_url / download_url → audio_url
```

### 第二步：分析脚本

仔细阅读用户提供的短视频脚本，提取以下信息：

1. **整体情绪基调**
   - 主要情感：欢乐/悲伤/紧张/温馨/励志/悬疑/浪漫/幽默等
   - 情绪走向：持续稳定/逐渐升温/先抑后扬/高潮迭起

2. **情节节奏**
   - 叙事节奏：快节奏/中等节奏/慢节奏
   - 高潮位置：开头/中间/结尾/无明确高潮
   - 紧张程度：轻松/中等/紧张刺激

3. **风格类型**
   - 内容类型：生活记录/剧情短片/商业广告/教育科普/情感故事等
   - 视觉风格：现代都市/复古怀旧/自然清新/科技感等
   - 目标受众：年轻人/家庭/商业客户/儿童等

将分析结果整理为结构化的"音乐需求画像"。

### 第三步：综合匹配

根据脚本的音乐需求画像，对每首音乐进行评分：

**评分维度（权重可调整）：**

| 维度 | 权重 | 匹配逻辑 |
|------|------|----------|
| 情绪匹配 | 40% | 音乐情绪与脚本情绪基调一致 |
| 节奏匹配 | 30% | BPM与叙事节奏匹配 |
| 风格匹配 | 20% | 音乐风格与内容类型协调 |
| 时长适配 | 10% | 音乐时长与脚本预估时长接近 |

**节奏匹配参考表：**
- 慢节奏叙事：BPM 60-90
- 中等节奏：BPM 90-120
- 快节奏/紧张：BPM 120-160+

### 第四步：输出推荐

输出格式如下：

```
## 最佳背景音乐推荐

**推荐音乐：** [音乐名称]
**来源：** [本地路径 或 API来源]
**匹配度：** [X%]

### 音乐信息
- 时长：[X:XX]
- BPM：[XX]
- 风格：[风格标签]
- 情绪：[情绪标签]
- 音频地址：[audio_url，仅API模式]

### 推荐理由
[详细解释为什么这首歌最适合，包括情绪契合点、节奏配合、风格协调等]

### 使用建议
- [建议从音乐的哪个时间点开始使用]
- [是否需要调整音量或做淡入淡出处理]
- [脚本高潮部分与音乐高潮的配合建议]
```

---

## 输入格式

### 基础输入

```
【视频脚本】
标题：[视频标题]
时长：[预估时长，可选]

[脚本内容，可以是分镜头描述、对话、旁白等形式]
```

### 完整输入示例（API 模式）

```
帮我给这个短视频配背景音乐：

【视频脚本】
标题：周末晨跑
时长：15秒

镜头1：（全景）清晨的公园，阳光透过树叶洒下
镜头2：（中景）主角系好跑鞋鞋带，深呼吸
镜头3：（跟拍）主角开始慢跑，节奏轻快
镜头4：（特写）额头的汗水，自信的笑容
镜头5：（全景）主角跑向远方，融入晨光中

【音乐API】
接口地址：https://api.mymusic.com/v1/tracks
认证方式：Bearer Token
认证信息：eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
请求方式：GET
```

### 完整输入示例（本地模式）

```
帮我给这个短视频配背景音乐：

【视频脚本】
标题：深夜加班的温暖
时长：30秒

镜头1：（近景）办公室，深夜，只有一个工位亮着灯
镜头2：（特写）手机屏幕亮起，妈妈发来消息
镜头3：（中景）小美微笑，拿起桌上的便当盒
镜头4：（特写）便当里是精心准备的饭菜
镜头5：（全景）小美走向窗边，表情变得温暖

【音乐库路径】
/Users/xxx/Music/BGM
```

---

## API 调用指南

### 标准 API 调用流程

1. **构建请求**
   - 根据 API 文档设置请求头（认证信息）
   - 设置查询参数（如分页、筛选条件）

2. **发送请求**
   - 使用 curl 或 HTTP 客户端发送请求
   - 处理分页获取完整音乐列表

3. **解析响应**
   - 解析 JSON 响应
   - 自动映射字段名

4. **缓存结果**
   - 将音乐列表缓存到临时文件
   - 避免重复请求 API

### API 调用示例

```bash
# GET 请求示例
curl -X GET "https://api.mymusic.com/v1/tracks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# POST 请求示例
curl -X POST "https://api.mymusic.com/v1/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mood": "happy", "bpm_min": 100, "bpm_max": 130}'
```

### 搜索优化

如果 API 支持搜索功能，可根据脚本分析结果预筛选：

```json
{
  "mood": "欢快",
  "genre": "流行",
  "bpm_min": 100,
  "bpm_max": 130,
  "duration_min": 60,
  "tags": ["活力", "运动"]
}
```

---

## 示例输出

**输入：**
```
帮我配个BGM，脚本如下：

标题：产品发布会
时长：20秒

0-5秒：黑屏倒计时，充满悬念
5-12秒：产品轮廓显现，科技感十足
12-18秒：功能展示，节奏加快
18-20秒：品牌LOGO定格

【音乐API】
接口地址：https://api.music.com/tracks
认证方式：API Key
认证信息：sk-xxx
```

**输出：**
```
## 脚本分析

**情绪基调：** 紧张、期待、震撼
**情绪走向：** 逐渐升温（悬念→展示→高潮）
**情节节奏：** 快节奏，层层递进
**风格类型：** 商业科技类

**音乐需求画像：**
- BPM 建议 120-140，配合快节奏展示
- 适合电子/科技风格，有冲击力
- 需要有明显的节奏变化，配合倒计时和产品揭晓

## 最佳背景音乐推荐

**推荐音乐：** TechReveal
**来源：** API (https://api.music.com/tracks/tr_001)
**匹配度：** 94%

### 音乐信息
- 时长：2:15
- BPM：132
- 风格：电子/科技
- 情绪：紧张、震撼、未来感
- 音频地址：https://cdn.music.com/tracks/tr_001.mp3

### 推荐理由
这首歌以低沉的电子音效开场（配合倒计时的悬念感），中段加入强烈的合成器节奏（配合产品轮廓显现），高潮部分有明显的能量爆发（配合LOGO定格），完美契合发布会的节奏设计。

### 使用建议
- 从第 5 秒开始使用，配合倒计时结束
- 第 18-20 秒做渐强处理，突出LOGO出现
- 可在第 20 秒后截断或淡出
```

---

## 本地音频分析

对本地音乐文件进行深度分析，提取音乐特征用于精准匹配。

### 依赖安装

首次使用本地分析功能，需要安装以下依赖：

```bash
# 1. 安装 ffmpeg（基础音频处理）
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (使用 scoop 或 choco)
scoop install ffmpeg
# 或
choco install ffmpeg

# 2. 安装 Python 依赖（音频特征分析）
pip install librosa numpy scipy

# 可选：安装 essentia（更专业的音频分析）
pip install essentia
```

### 分析流程

对每首音频文件执行以下分析：

```
音频文件 → 基础信息 → 音频特征 → 情绪预测 → 元数据缓存
```

### 分析内容

#### 1. 基础信息（使用 ffmpeg）

```bash
# 获取时长、采样率、声道等信息
ffprobe -v quiet -print_format json -show_format -show_streams audio.mp3
```

输出字段：
- `duration` - 时长（秒）
- `sample_rate` - 采样率
- `channels` - 声道数
- `bit_rate` - 比特率

#### 2. BPM 节奏分析（使用 librosa）

```python
import librosa

def analyze_bpm(file_path):
    y, sr = librosa.load(file_path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return round(tempo)
```

BPM 分类：
| BPM 范围 | 节奏类型 | 适用场景 |
|----------|----------|----------|
| 60-80 | 慢节奏 | 抒情、情感类 |
| 80-100 | 中慢节奏 | 温馨、治愈类 |
| 100-120 | 中等节奏 | 日常、生活类 |
| 120-140 | 快节奏 | 活力、运动类 |
| 140+ | 极快节奏 | 紧张、刺激类 |

#### 3. 能量分析（使用 librosa）

```python
import librosa
import numpy as np

def analyze_energy(file_path):
    y, sr = librosa.load(file_path)

    # 计算 RMS 能量
    rms = librosa.feature.rms(y=y)[0]

    # 平均能量
    energy_mean = np.mean(rms)

    # 能量变化（动态范围）
    energy_std = np.std(rms)

    # 能量分布（低/中/高能量段落）
    energy_distribution = np.percentile(rms, [25, 50, 75])

    return {
        "energy_mean": float(energy_mean),
        "energy_std": float(energy_std),
        "energy_low": float(energy_distribution[0]),
        "energy_mid": float(energy_distribution[1]),
        "energy_high": float(energy_distribution[2])
    }
```

能量分类：
| 能量值 | 等级 | 适用场景 |
|--------|------|----------|
| < 0.02 | 低能量 | 安静、沉思、悲伤 |
| 0.02-0.05 | 中能量 | 日常、温馨、轻松 |
| 0.05-0.10 | 高能量 | 活力、激情、励志 |
| > 0.10 | 极高能量 | 紧张、震撼、冲击 |

#### 4. 调性分析（使用 librosa）

```python
import librosa

def analyze_key(file_path):
    y, sr = librosa.load(file_path)

    # 检测调性
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    key_index = np.argmax(np.mean(chroma, axis=1))

    # 调名映射
    key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # 判断大调/小调（简化判断）
    mode = 'major' if key_index in [0, 2, 4, 5, 7, 9, 11] else 'minor'

    return {
        "key": key_names[key_index],
        "mode": mode,  # major=明亮/欢快, minor=忧伤/深沉
        "key_full": f"{key_names[key_index]} {'大调' if mode == 'major' else '小调'}"
    }
```

调性与情绪对应：
| 调性 | 情绪特征 |
|------|----------|
| 大调 | 明亮、欢快、积极、阳光 |
| 小调 | 忧伤、深沉、神秘、感伤 |

#### 5. 频谱特征分析

```python
import librosa
import numpy as np

def analyze_spectral(file_path):
    y, sr = librosa.load(file_path)

    # 频谱质心（亮度）
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    brightness = np.mean(spectral_centroid)

    # 频谱带宽（丰富度）
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    richness = np.mean(spectral_bandwidth)

    # 频谱对比度（清晰度）
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    clarity = np.mean(spectral_contrast)

    return {
        "brightness": float(brightness),    # 高频成分多=明亮
        "richness": float(richness),        # 频带宽度大=丰富
        "clarity": float(clarity)           # 对比度高=清晰
    }
```

#### 6. 情绪预测（综合分析）

基于以上特征，推断音乐情绪：

```python
def predict_mood(bpm, energy, key_mode, brightness):
    """
    综合音乐特征预测情绪标签
    """
    mood_scores = {}

    # 欢快：快节奏 + 高能量 + 大调 + 明亮
    if bpm > 100 and energy > 0.03 and key_mode == 'major':
        mood_scores['欢快'] = 0.8

    # 温馨：中等节奏 + 中能量 + 大调
    if 70 < bpm < 110 and 0.01 < energy < 0.05 and key_mode == 'major':
        mood_scores['温馨'] = 0.7

    # 忧伤：慢节奏 + 低能量 + 小调
    if bpm < 90 and energy < 0.03 and key_mode == 'minor':
        mood_scores['忧伤'] = 0.8

    # 紧张：快节奏 + 高能量 + 小调
    if bpm > 120 and energy > 0.04 and key_mode == 'minor':
        mood_scores['紧张'] = 0.75

    # 励志：中快节奏 + 中高能量 + 大调
    if 90 < bpm < 130 and energy > 0.03 and key_mode == 'major':
        mood_scores['励志'] = 0.7

    # 神秘：中等节奏 + 低中能量 + 小调
    if 80 < bpm < 110 and energy < 0.04 and key_mode == 'minor':
        mood_scores['神秘'] = 0.65

    # 返回得分最高的情绪
    if mood_scores:
        return max(mood_scores, key=mood_scores.get)
    return '中性'
```

### 完整分析脚本

创建分析脚本 `analyze_music.py`：

```python
#!/usr/bin/env python3
"""
音乐文件分析脚本
用法: python analyze_music.py <音乐文件或目录>
"""

import os
import sys
import json
import librosa
import numpy as np

def analyze_audio(file_path):
    """分析单个音频文件"""
    try:
        # 加载音频
        y, sr = librosa.load(file_path, duration=60)  # 最多分析前60秒

        # 1. 时长
        duration = librosa.get_duration(y=y, sr=sr)

        # 2. BPM
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = round(float(tempo))

        # 3. 能量
        rms = librosa.feature.rms(y=y)[0]
        energy = float(np.mean(rms))
        energy_std = float(np.std(rms))

        # 4. 调性
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        key_idx = np.argmax(np.mean(chroma, axis=1))
        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = key_names[key_idx]
        mode = 'major' if np.mean(chroma[key_idx]) > 0.5 else 'minor'

        # 5. 频谱特征
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        brightness = float(np.mean(spectral_centroid))

        # 6. 情绪预测
        mood = predict_mood(bpm, energy, mode, brightness)

        return {
            "file": file_path,
            "duration": round(duration, 2),
            "bpm": bpm,
            "energy": round(energy, 4),
            "energy_variation": round(energy_std, 4),
            "key": key,
            "mode": mode,
            "brightness": round(brightness, 0),
            "mood": mood
        }
    except Exception as e:
        return {"file": file_path, "error": str(e)}

def predict_mood(bpm, energy, mode, brightness):
    """预测情绪"""
    if bpm > 100 and energy > 0.03 and mode == 'major':
        return '欢快'
    if 70 < bpm < 110 and 0.01 < energy < 0.05 and mode == 'major':
        return '温馨'
    if bpm < 90 and energy < 0.03 and mode == 'minor':
        return '忧伤'
    if bpm > 120 and energy > 0.04 and mode == 'minor':
        return '紧张'
    if 90 < bpm < 130 and energy > 0.03 and mode == 'major':
        return '励志'
    if 80 < bpm < 110 and energy < 0.04 and mode == 'minor':
        return '神秘'
    return '中性'

def analyze_directory(dir_path):
    """分析目录下所有音频文件"""
    audio_exts = ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg']
    results = []

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in audio_exts):
                file_path = os.path.join(root, file)
                print(f"分析中: {file}")
                result = analyze_audio(file_path)
                results.append(result)

    return results

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python analyze_music.py <音乐文件或目录>")
        sys.exit(1)

    target = sys.argv[1]

    if os.path.isfile(target):
        results = [analyze_audio(target)]
    elif os.path.isdir(target):
        results = analyze_directory(target)
    else:
        print(f"错误: {target} 不是有效的文件或目录")
        sys.exit(1)

    # 输出 JSON 结果
    print(json.dumps(results, ensure_ascii=False, indent=2))
```

### 元数据缓存

分析结果自动缓存到 JSON 文件，避免重复分析：

```
音乐库目录/
├── song1.mp3
├── song2.mp3
└── .music_metadata.json    ← 缓存文件
```

缓存文件格式：
```json
{
  "version": "1.0",
  "analyzed_at": "2024-01-15T10:30:00",
  "music_list": [
    {
      "file": "song1.mp3",
      "duration": 180.5,
      "bpm": 120,
      "energy": 0.0423,
      "key": "C",
      "mode": "major",
      "mood": "欢快",
      "brightness": 2500
    }
  ]
}
```

### 分析时机

- **首次分析**：扫描音乐库时，检测 `.music_metadata.json` 是否存在
- **增量更新**：对比文件修改时间，仅分析新增或修改的文件
- **强制重新分析**：用户可指定 `--reanalyze` 参数

---

## 多模态 AI 分析（API 模式）

通过 API 调用多模态 AI 服务，实现深度音乐理解和智能匹配。

### 为什么使用多模态 AI API？

| 传统方法 | 多模态 AI API |
|----------|---------------|
| 仅分析信号特征（BPM、能量） | AI 理解音乐的语义和情感 |
| 基于规则的简单情绪分类 | 深度理解音乐内容 |
| 标签匹配可能不准确 | 语义相似度匹配更精准 |
| 无法理解复杂情感 | 识别细腻的情感层次 |
| 需要本地部署模型 | API 调用，无需本地资源 |

---

### 多模态 AI API 配置

用户需提供多模态 AI API 配置信息：

```
【多模态AI API】
服务提供商: Claude / OpenAI / 自定义
接口地址: https://api.anthropic.com/v1/messages
认证方式: Bearer Token / API Key / Header
认证信息: sk-xxx
模型: claude-sonnet-4-6 / gpt-4o / 自定义模型
请求方式: POST
```

**配置示例：**

```
【多模态AI API】
服务提供商: Claude
接口地址: https://api.anthropic.com/v1/messages
认证方式: Header (x-api-key)
认证信息: sk-ant-xxx
模型: claude-sonnet-4-6
请求方式: POST
```

---

### API 调用方式

#### 方式一：Claude API（推荐）

Claude 原生支持音频输入，可直接分析音乐：

**请求格式：**

```bash
curl -X POST "https://api.anthropic.com/v1/messages" \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-sonnet-4-6",
    "max_tokens": 1024,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "请分析这段音频的音乐特征和情绪，以JSON格式返回：{\"mood\":\"情绪\",\"mood_intensity\":数字1-10,\"energy_level\":\"低/中/高\",\"rhythm\":\"节奏特征\",\"genre\":\"风格\",\"instruments\":[\"乐器\"],\"suitable_scenes\":[\"适用场景\"],\"emotional_arc\":\"情感走向\",\"keywords\":[\"关键词\"],\"description\":\"一句话描述\"}"
          },
          {
            "type": "audio",
            "source": {
              "type": "base64",
              "media_type": "audio/mpeg",
              "data": "BASE64_ENCODED_AUDIO"
            }
          }
        ]
      }
    ]
  }'
```

**响应示例：**

```json
{
  "content": [
    {
      "type": "text",
      "text": {
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
    }
  ]
}
```

#### 方式二：OpenAI GPT-4o API

GPT-4o 支持音频输入：

**请求格式：**

```bash
curl -X POST "https://api.openai.com/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-audio-preview",
    "modalities": ["text"],
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "分析这段音频的音乐特征..."
          },
          {
            "type": "input_audio",
            "input_audio": {
              "data": "BASE64_ENCODED_AUDIO",
              "format": "mp3"
            }
          }
        ]
      }
    ]
  }'
```

#### 方式三：自定义 API 服务

支持用户自定义的多模态 AI API：

**配置格式：**

```
【多模态AI API】
服务提供商: 自定义
接口地址: https://your-api.com/v1/analyze-audio
认证方式: Bearer Token
认证信息: your-token
模型: your-model-name
请求方式: POST
请求格式: {
  "audio": "{{base64_audio}}",
  "prompt": "{{analysis_prompt}}"
}
响应格式: {
  "mood": "{{mood}}",
  "energy": "{{energy}}",
  ...
}
```

---

### API 调用实现

#### 统一 API 调用接口

```python
import requests
import base64
import json

class MultimodalAudioAnalyzer:
    """多模态音频分析器 - API 模式"""

    def __init__(self, config):
        """
        初始化分析器

        config = {
            "provider": "claude",  # claude / openai / custom
            "api_url": "https://api.anthropic.com/v1/messages",
            "auth_type": "header",  # header / bearer
            "auth_key": "x-api-key",
            "auth_value": "sk-xxx",
            "model": "claude-sonnet-4-6"
        }
        """
        self.config = config

    def analyze_audio(self, audio_path):
        """分析音频文件"""

        # 1. 读取并编码音频
        with open(audio_path, 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode()

        # 2. 根据服务商构建请求
        if self.config['provider'] == 'claude':
            return self._call_claude_api(audio_data)
        elif self.config['provider'] == 'openai':
            return self._call_openai_api(audio_data)
        else:
            return self._call_custom_api(audio_data)

    def _call_claude_api(self, audio_base64):
        """调用 Claude API"""

        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            self.config['auth_key']: self.config['auth_value']
        }

        payload = {
            "model": self.config['model'],
            "max_tokens": 1024,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": self._get_analysis_prompt()
                    },
                    {
                        "type": "audio",
                        "source": {
                            "type": "base64",
                            "media_type": "audio/mpeg",
                            "data": audio_base64
                        }
                    }
                ]
            }]
        }

        response = requests.post(
            self.config['api_url'],
            headers=headers,
            json=payload
        )

        return self._parse_response(response.json())

    def _call_openai_api(self, audio_base64):
        """调用 OpenAI API"""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config['auth_value']}"
        }

        payload = {
            "model": self.config['model'],
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": self._get_analysis_prompt()
                    },
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_base64,
                            "format": "mp3"
                        }
                    }
                ]
            }]
        }

        response = requests.post(
            self.config['api_url'],
            headers=headers,
            json=payload
        )

        return self._parse_response(response.json())

    def _call_custom_api(self, audio_base64):
        """调用自定义 API"""

        headers = {
            "Content-Type": "application/json"
        }

        # 根据认证类型设置请求头
        if self.config['auth_type'] == 'bearer':
            headers["Authorization"] = f"Bearer {self.config['auth_value']}"
        elif self.config['auth_type'] == 'header':
            headers[self.config['auth_key']] = self.config['auth_value']

        payload = {
            "audio": audio_base64,
            "prompt": self._get_analysis_prompt(),
            "model": self.config.get('model')
        }

        response = requests.post(
            self.config['api_url'],
            headers=headers,
            json=payload
        )

        return response.json()

    def _get_analysis_prompt(self):
        """获取分析提示词"""
        return """请分析这段音频的音乐特征，以JSON格式返回以下信息：
{
  "mood": "主要情绪（欢快/忧伤/紧张/温馨/励志/神秘等）",
  "mood_intensity": "情绪强度（1-10的数字）",
  "energy_level": "能量等级（低/中/高）",
  "rhythm": "节奏特征（舒缓/中等/紧凑/激烈）",
  "bpm_estimate": "预估BPM",
  "genre": "音乐风格",
  "instruments": ["主要乐器列表"],
  "suitable_scenes": ["适合的场景列表"],
  "emotional_arc": "情感走向描述",
  "keywords": ["关键词标签"],
  "description": "一句话描述这首音乐的感觉"
}"""

    def _parse_response(self, response):
        """解析API响应"""
        # 根据不同API格式解析
        if 'content' in response:
            # Claude 格式
            text = response['content'][0]['text']
            return json.loads(text)
        elif 'choices' in response:
            # OpenAI 格式
            text = response['choices'][0]['message']['content']
            return json.loads(text)
        else:
            # 自定义格式
            return response
```

---

### 语义匹配 API

#### 文本-音频语义相似度 API

用于计算脚本描述与音乐的语义相似度：

```
【语义匹配API】
接口地址: https://api.example.com/v1/semantic-match
认证方式: Bearer Token
认证信息: your-token
请求方式: POST

请求格式:
{
  "text": "脚本情感描述文本",
  "audio_url": "音频URL或base64"
}

响应格式:
{
  "similarity": 0.89,
  "matched_features": ["情绪匹配", "节奏匹配"],
  "confidence": 0.92
}
```

#### 语义匹配实现

```python
class SemanticMatcher:
    """语义匹配器 - API 模式"""

    def __init__(self, config):
        self.config = config
        self.api_url = config.get('semantic_api_url')
        self.auth_value = config.get('semantic_api_key')

    def calculate_similarity(self, script_description, audio_analysis):
        """
        计算脚本与音乐的语义相似度

        script_description: 脚本的情感需求描述
        audio_analysis: AI 分析返回的音乐特征
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_value}"
        }

        payload = {
            "text": script_description,
            "audio_features": audio_analysis
        }

        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload
        )

        result = response.json()
        return result.get('similarity', 0)
```

---

### 完整匹配流程

```
┌─────────────────┐     ┌─────────────────┐
│   视频脚本      │     │   音乐库        │
│   (文本)        │     │   (音频/API)    │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  脚本语义分析   │     │  多模态AI分析   │
│    (API调用)    │     │    (API调用)    │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  情感需求画像   │     │  音乐语义特征   │
│  (结构化JSON)   │     │  (结构化JSON)   │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
         ┌─────────────────────┐
         │   语义相似度计算     │
         │   (API/本地计算)    │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │   综合评分排序       │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │   输出推荐结果       │
         └─────────────────────┘
```

---

### 综合匹配实现

```python
class MultimodalMusicMatcher:
    """多模态音乐匹配器 - 全 API 模式"""

    def __init__(self, ai_config, music_api_config=None, semantic_config=None):
        """
        ai_config: 多模态AI API配置
        music_api_config: 音乐库API配置（可选）
        semantic_config: 语义匹配API配置（可选）
        """
        self.audio_analyzer = MultimodalAudioAnalyzer(ai_config)
        self.semantic_matcher = SemanticMatcher(semantic_config) if semantic_config else None
        self.music_api_config = music_api_config

    def match_music(self, script_text, music_list):
        """
        匹配最合适的音乐

        script_text: 视频脚本文本
        music_list: 音乐列表（本地路径或API返回的列表）
        """
        # 1. 分析脚本情感需求
        script_profile = self._analyze_script(script_text)

        # 2. 分析每首音乐
        music_analyses = []
        for music in music_list:
            if isinstance(music, str):
                # 本地文件路径
                analysis = self.audio_analyzer.analyze_audio(music)
                analysis['source'] = music
            else:
                # API返回的音乐对象
                if 'analysis' in music:
                    analysis = music['analysis']
                else:
                    # 需要调用API分析
                    analysis = self._analyze_from_api(music)
                analysis['source'] = music
            music_analyses.append(analysis)

        # 3. 计算匹配度
        matches = []
        for analysis in music_analyses:
            score = self._calculate_match_score(script_profile, analysis)
            matches.append({
                'music': analysis,
                'score': score,
                'source': analysis['source']
            })

        # 4. 排序返回
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[0] if matches else None

    def _analyze_script(self, script_text):
        """分析脚本，生成音乐需求画像"""
        # 可调用AI API分析脚本
        # 这里返回结构化的需求画像
        return {
            "mood_requirement": "...",
            "rhythm_requirement": {"min": 90, "max": 120},
            "energy_requirement": "中",
            "style_keywords": ["流行", "轻音乐"],
            "scene_tags": ["清晨", "运动"]
        }

    def _calculate_match_score(self, script_profile, music_analysis):
        """计算匹配分数"""
        score = 0

        # 情绪匹配 (40%)
        if self.semantic_matcher:
            semantic_score = self.semantic_matcher.calculate_similarity(
                script_profile['mood_requirement'],
                music_analysis
            )
            score += semantic_score * 0.4
        else:
            # 本地计算情绪匹配
            mood_match = self._match_mood(
                script_profile['mood_requirement'],
                music_analysis.get('mood', '')
            )
            score += mood_match * 0.4

        # BPM匹配 (25%)
        bpm_score = self._match_bpm(
            music_analysis.get('bpm_estimate', 0),
            script_profile['rhythm_requirement']
        )
        score += bpm_score * 0.25

        # 能量匹配 (20%)
        energy_score = self._match_energy(
            music_analysis.get('energy_level', ''),
            script_profile.get('energy_requirement', '')
        )
        score += energy_score * 0.2

        # 场景匹配 (15%)
        scene_score = self._match_scenes(
            music_analysis.get('suitable_scenes', []),
            script_profile.get('scene_tags', [])
        )
        score += scene_score * 0.15

        return score

    def _match_mood(self, required, actual):
        """情绪匹配"""
        mood_map = {
            '欢快': ['欢快', '活力', '阳光', '积极'],
            '忧伤': ['忧伤', '悲伤', '感伤', '忧郁'],
            '温馨': ['温馨', '温暖', '治愈', '感动'],
            '紧张': ['紧张', '悬疑', '激烈', '震撼'],
            '励志': ['励志', '希望', '力量', '振奋']
        }
        # 匹配逻辑...
        return 0.8

    def _match_bpm(self, actual_bpm, requirement):
        """BPM匹配"""
        min_bpm = requirement.get('min', 60)
        max_bpm = requirement.get('max', 180)
        if min_bpm <= actual_bpm <= max_bpm:
            return 1.0
        # 越接近范围分数越高
        return max(0, 1 - abs(actual_bpm - (min_bpm + max_bpm) / 2) / 50)

    def _match_energy(self, actual, required):
        """能量匹配"""
        energy_levels = {'低': 1, '中低': 2, '中': 3, '中高': 4, '高': 5}
        actual_val = energy_levels.get(actual, 3)
        required_val = energy_levels.get(required, 3)
        return max(0, 1 - abs(actual_val - required_val) / 4)

    def _match_scenes(self, actual_scenes, required_scenes):
        """场景匹配"""
        if not required_scenes:
            return 0.5
        matches = len(set(actual_scenes) & set(required_scenes))
        return matches / len(required_scenes)
```

---

### 使用示例

**输入：**

```
帮我给这个短视频配背景音乐：

【视频脚本】
标题：周末晨跑
时长：15秒

镜头1：（全景）清晨的公园，阳光透过树叶洒下
镜头2：（中景）主角系好跑鞋鞋带，深呼吸
镜头3：（跟拍）主角开始慢跑，节奏轻快
镜头4：（特写）额头的汗水，自信的笑容
镜头5：（全景）主角跑向远方，融入晨光中

【音乐库API】
接口地址: https://api.mymusic.com/v1/tracks
认证方式: Bearer Token
认证信息: token-xxx

【多模态AI API】
服务提供商: Claude
接口地址: https://api.anthropic.com/v1/messages
认证方式: Header (x-api-key)
认证信息: sk-ant-xxx
模型: claude-sonnet-4-6
```

**输出：**

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

### AI 语义分析
- **情绪识别**：欢快、充满希望
- **情绪强度**：8/10
- **能量等级**：中高
- **预估BPM**：118
- **主要乐器**：钢琴、电子合成器、鼓
- **适合场景**：清晨、运动、旅行、新开始
- **情感走向**：从平静开场，中段达到明亮高潮
- **AI 描述**：一首温暖明亮的轻音乐，传递清晨阳光般的希望感

### 推荐理由
脚本的"清晨公园晨跑"场景与音乐的"清晨、运动"标签高度匹配。BPM 118 完美契合慢跑节奏，情绪从平静到活力的走向与镜头节奏同步。

### 使用建议
- 建议从第 5 秒开始使用
- 结尾处做 2 秒淡出
- 音量建议 -8dB

---

### API 依赖安装

```bash
# HTTP 请求
pip install requests

# 可选：音频编码
pip install pydub
```

---

## 注意事项

1. **API 认证**：妥善保管 API Token，不要在公开场合泄露
2. **分页处理**：大型音乐库可能需要分页获取
3. **元数据缓存**：建议缓存 API 响应，避免重复请求
4. **主观判断**：音乐匹配有主观性，推荐时说明理由
5. **版权提醒**：提醒用户注意音乐版权问题