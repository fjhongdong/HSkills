# 场景设定模板

## 目录

1. [场景档案结构](#场景档案结构)
2. [环境描述指南](#环境描述指南)
3. [光线设计指南](#光线设计指南)
4. [氛围关键词库](#氛围关键词库)
5. [示例场景档案](#示例场景档案)

---

## 场景档案结构

### 完整场景档案 JSON 格式

```json
{
  "scene_number": 1,
  "scene_heading": "INT. COFFEE SHOP - DAY",

  "environment": {
    "type": "interior",
    "category": "commercial/restaurant",
    "location_name": "城市咖啡厅",
    "location_en": "urban coffee shop",

    "spatial": {
      "size": "medium",
      "layout": "open floor plan with scattered tables",
      "ceiling_height": "high, exposed beams",
      "windows": "large floor-to-ceiling windows on one side"
    },

    "key_elements": [
      "espresso bar counter",
      "wooden tables and chairs",
      "exposed brick wall",
      "hanging pendant lights",
      "potted plants"
    ],

    "background_elements": [
      "other customers (blurred)",
      "barista working",
      "menu board",
      "coffee equipment"
    ]
  },

  "time": {
    "time_of_day": "morning",
    "specific_time": "around 9 AM",
    "season": "autumn",
    "weather": "overcast, light rain outside"
  },

  "lighting": {
    "type": "mixed",
    "natural_source": "diffused daylight from windows",
    "artificial_source": "warm pendant lights, ambient cafe lighting",
    "direction": "side lighting from windows",
    "intensity": "medium, soft",
    "color_temperature": "warm",
    "quality": "soft, diffused",
    "shadows": "soft shadows, low contrast"
  },

  "color_palette": {
    "dominant": "warm browns, cream",
    "accent": "forest green (plants), copper (fixtures)",
    "mood_colors": "cozy earth tones"
  },

  "atmosphere": {
    "mood": "cozy, relaxed, intimate",
    "sound_design": "soft jazz, coffee machine sounds, quiet chatter",
    "temperature_feel": "warm and inviting"
  },

  "visual_prompt": "场景视觉提示词",
  "seed_prompt": "场景一致性种子"
}
```

---

## 环境描述指南

### 室内场景类型

| 类别 | 场景类型 | 典型元素 |
|------|----------|----------|
| **居家** | 客厅 | sofa, coffee table, TV, bookshelf, rug |
| | 卧室 | bed, nightstand, wardrobe, lamp, curtains |
| | 厨房 | counter, stove, refrigerator, cabinets |
| | 浴室 | sink, mirror, bathtub/shower, tiles |
| **办公** | 办公室 | desk, computer, chair, files, window |
| | 会议室 | long table, chairs, projector, whiteboard |
| | 大厅 | reception desk, seating area, elevators |
| **商业** | 咖啡厅 | coffee bar, tables, pendant lights |
| | 餐厅 | dining tables, bar, kitchen view |
| | 酒吧 | bar counter, stools, bottles, dim lights |
| | 商场 | stores, escalators, shoppers |
| **公共** | 医院 | beds, medical equipment, white walls |
| | 学校 | desks, blackboard, windows |
| | 图书馆 | bookshelves, reading tables, quiet |

### 室外场景类型

| 类别 | 场景类型 | 典型元素 |
|------|----------|----------|
| **城市** | 街道 | buildings, cars, pedestrians, signs |
| | 广场 | open space, fountain, benches |
| | 停车场 | cars, concrete, lights |
| | 天台 | city skyline, railings, sky |
| **自然** | 公园 | trees, grass, paths, benches |
| | 海滩 | sand, waves, ocean, sky |
| | 森林 | trees, leaves, shadows, path |
| | 山区 | peaks, rocks, vegetation, clouds |
| **其他** | 校园 | buildings, students, trees |
| | 工地 | construction, machinery, workers |

### 空间描述词

**大小**：
- cramped, tiny, small, medium, spacious, vast, expansive

**布局**：
- open plan, divided, L-shaped, circular, linear, cluttered, minimal

**风格**：
- modern, contemporary, traditional, vintage, industrial, rustic, minimalist, luxurious

---

## 光线设计指南

### 自然光时段

| 时段 | 英文 | 光线特征 | 色温 | 适合氛围 |
|------|------|----------|------|----------|
| 黎明 | dawn | 柔和金色，长影 | 暖 | 希望、新开始 |
| 早晨 | morning | 明亮清新 | 中性 | 活力、清醒 |
| 正午 | midday | 强烈直射，短影 | 中性偏冷 | 高能量、紧张 |
| 下午 | afternoon | 温暖柔和 | 暖 | 轻松、日常 |
| 黄昏 | golden hour | 金橙色，长影 | 暖 | 浪漫、怀旧 |
| 傍晚 | blue hour | 蓝紫色调 | 冷 | 神秘、过渡 |
| 夜晚 | night | 人造光源 | 混合 | 多种可能 |

### 光线方向

| 方向 | 英文 | 效果 |
|------|------|------|
| 正面光 | front lighting | 平坦，减少阴影 |
| 侧光 | side lighting | 增加深度和质感 |
| 逆光 | backlighting | 轮廓光，剪影效果 |
| 顶光 | top lighting | 戏剧性阴影 |
| 底光 | under lighting | 恐怖、不自然 |
| 环境光 | ambient | 均匀柔和 |

### 光线质量

| 质量 | 英文 | 描述 |
|------|------|------|
| 硬光 | hard light | 清晰边缘阴影，高对比 |
| 软光 | soft light | 柔和渐变阴影，低对比 |
| 漫射光 | diffused | 均匀分布，无明显方向 |

### 光线提示词模板

```
[light_type] lighting, [direction] light, [quality],
[color_temperature] tones, [intensity] intensity,
[shadow_description]
```

示例：
```
natural soft lighting, side light from large windows,
warm golden tones, medium intensity,
soft shadows creating depth
```

---

## 氛围关键词库

### 情绪氛围

| 氛围 | 英文关键词 |
|------|-----------|
| 温馨 | warm, cozy, comfortable, inviting, homey |
| 浪漫 | romantic, intimate, soft, dreamy, tender |
| 紧张 | tense, suspenseful, uneasy, anxious, oppressive |
| 恐怖 | eerie, creepy, dark, unsettling, ominous |
| 悲伤 | melancholic, somber, gloomy, mournful |
| 欢乐 | cheerful, lively, vibrant, festive, bright |
| 神秘 | mysterious, enigmatic, foggy, shadowy |
| 平静 | peaceful, serene, tranquil, calm, quiet |
| 压抑 | claustrophobic, oppressive, heavy, suffocating |
| 史诗 | epic, grand, majestic, awe-inspiring |

### 视觉风格

| 风格 | 英文关键词 |
|------|-----------|
| 写实 | realistic, photorealistic, natural |
| 电影感 | cinematic, filmic, movie-like |
| 梦幻 | dreamy, ethereal, soft focus |
| 复古 | vintage, retro, nostalgic, film grain |
| 未来 | futuristic, sci-fi, high-tech |
| 黑色电影 | noir, high contrast, dramatic shadows |
| 柔和 | soft, pastel, gentle, muted |
| 鲜艳 | vibrant, saturated, bold colors |

---

## 示例场景档案

### 示例1：都市咖啡厅

```json
{
  "scene_number": 1,
  "scene_heading": "INT. 城市咖啡厅 - 早晨",

  "environment": {
    "type": "interior",
    "location_en": "modern urban coffee shop",
    "spatial": {
      "size": "medium",
      "layout": "open with counter area and seating"
    },
    "key_elements": [
      "espresso bar with copper fixtures",
      "wooden tables with plants",
      "exposed brick accent wall",
      "large street-facing windows"
    ]
  },

  "lighting": {
    "type": "mixed",
    "natural_source": "morning light through windows",
    "artificial_source": "warm pendant lights",
    "color_temperature": "warm",
    "quality": "soft, inviting"
  },

  "atmosphere": {
    "mood": "cozy, relaxed",
    "mood_keywords": ["warm", "inviting", "urban", "morning calm"]
  },

  "visual_prompt": "interior of modern urban coffee shop, morning soft light through large windows, warm pendant lighting, exposed brick wall, wooden tables with green plants, espresso bar with copper fixtures, cozy inviting atmosphere, cinematic",

  "seed_prompt": "[SCENE:咖啡厅] modern coffee shop interior, warm lighting, brick walls, wooden furniture, morning atmosphere, consistent environment"
}
```

### 示例2：夜晚街道

```json
{
  "scene_number": 5,
  "scene_heading": "EXT. 城市街道 - 夜晚",

  "environment": {
    "type": "exterior",
    "location_en": "city street at night",
    "spatial": {
      "layout": "urban street with buildings on both sides"
    },
    "key_elements": [
      "wet pavement (after rain)",
      "neon signs",
      "street lights",
      "parked cars"
    ],
    "background_elements": [
      "distant pedestrians",
      "shop windows",
      "reflections on wet ground"
    ]
  },

  "time": {
    "time_of_day": "night",
    "weather": "just stopped raining"
  },

  "lighting": {
    "type": "artificial",
    "sources": ["street lights", "neon signs", "shop windows"],
    "color_temperature": "mixed - warm street lights, cool neon",
    "quality": "hard light with soft reflections"
  },

  "atmosphere": {
    "mood": "moody, cinematic noir",
    "mood_keywords": ["urban noir", "mysterious", "reflective", "isolated"]
  },

  "visual_prompt": "city street at night after rain, wet pavement with reflections, neon signs glowing, warm street lights, urban noir atmosphere, cinematic moody lighting, empty street with distant figures, high contrast",

  "seed_prompt": "[SCENE:夜街] night city street, wet pavement, neon lights, noir mood, consistent environment"
}
```
