# 角色设定模板

## 目录

1. [角色档案结构](#角色档案结构)
2. [外貌描述指南](#外貌描述指南)
3. [服装设定指南](#服装设定指南)
4. [提示词生成模板](#提示词生成模板)
5. [示例角色档案](#示例角色档案)

---

## 角色档案结构

### 完整角色档案 JSON 格式

```json
{
  "name": "角色名",
  "name_en": "英文名（用于提示词）",
  "role": "主角/配角/龙套",

  "appearance": {
    "age": "25-30",
    "gender": "female",
    "ethnicity": "Asian",
    "height": "165cm / average",
    "body_type": "slim",
    "face_shape": "oval",
    "skin_tone": "fair",
    "hair": {
      "style": "long, wavy",
      "color": "black",
      "length": "shoulder-length"
    },
    "eyes": {
      "shape": "almond",
      "color": "dark brown"
    },
    "distinguishing_features": ["small mole on left cheek", "dimples"]
  },

  "personality": {
    "traits": ["confident", "determined", "warm"],
    "visual_expression": ["direct gaze", "slight smile", "head held high"]
  },

  "costumes": [
    {
      "scene_range": "1-5",
      "description": "White blouse, black pencil skirt, nude heels",
      "style": "business formal",
      "colors": ["white", "black", "beige"],
      "accessories": ["pearl earrings", "silver watch"]
    }
  ],

  "props": ["smartphone", "leather briefcase"],

  "visual_prompt": "生成用提示词",
  "seed_prompt": "一致性种子提示词"
}
```

---

## 外貌描述指南

### 年龄描述词

| 年龄段 | 中文 | 英文提示词 |
|--------|------|-----------|
| 0-2 | 婴儿 | baby, infant |
| 3-6 | 幼儿 | toddler, young child |
| 7-12 | 儿童 | child, kid |
| 13-17 | 少年/青少年 | teenager, teen, adolescent |
| 18-25 | 青年 | young adult, early twenties |
| 26-35 | 青年 | late twenties, early thirties |
| 36-50 | 中年 | middle-aged, mature |
| 51-65 | 中老年 | senior, older adult |
| 65+ | 老年 | elderly, old |

### 体型描述词

| 中文 | 英文 | 视觉特征 |
|------|------|----------|
| 纤瘦 | thin, slender | 骨感明显 |
| 苗条 | slim, lean | 匀称偏瘦 |
| 匀称 | average, fit | 标准体型 |
| 健美 | athletic, toned | 肌肉线条 |
| 健壮 | muscular, strong | 明显肌肉 |
| 魁梧 | burly, broad | 大块头 |
| 微胖 | slightly chubby | 圆润 |
| 丰满 | curvy, full-figured | 曲线明显 |

### 发型描述词

| 类别 | 选项 |
|------|------|
| 长度 | bald, buzz cut, short, medium, shoulder-length, long, very long |
| 质地 | straight, wavy, curly, coily, kinky |
| 造型 | ponytail, bun, braids, pigtails, bob, bangs, side-swept, slicked-back |
| 发色 | black, brown, blonde, red, auburn, gray, white, dyed (pink/blue/etc) |

### 五官描述词

**眼睛**：
- 形状：round, almond, hooded, monolid, deep-set, wide-set
- 颜色：black, dark brown, light brown, hazel, green, blue, gray

**脸型**：
- oval, round, square, heart-shaped, oblong, diamond

**特征**：
- freckles, moles, scars, wrinkles, dimples, glasses, beard, mustache

---

## 服装设定指南

### 服装风格分类

| 风格 | 英文 | 典型搭配 |
|------|------|----------|
| 正装商务 | formal business | suit, blazer, dress shirt, tie |
| 商务休闲 | business casual | blouse, chinos, loafers |
| 休闲 | casual | t-shirt, jeans, sneakers |
| 运动 | sporty/athletic | hoodie, joggers, trainers |
| 街头 | streetwear | oversized hoodie, cargo pants |
| 优雅 | elegant | dress, heels, jewelry |
| 波西米亚 | bohemian | flowing dress, layered jewelry |
| 朋克 | punk | leather jacket, ripped jeans, boots |
| 复古 | vintage/retro | 50s dress, 70s bell-bottoms |

### 颜色描述

使用具体颜色而非模糊描述：
- ✅ navy blue blazer
- ❌ dark jacket

常用颜色词：
- 白色系：white, cream, ivory, off-white
- 黑色系：black, charcoal, jet black
- 灰色系：gray, silver, slate
- 蓝色系：navy, royal blue, sky blue, teal
- 红色系：red, burgundy, maroon, coral
- 绿色系：forest green, olive, mint, sage
- 棕色系：brown, tan, beige, caramel

---

## 提示词生成模板

### 基础角色提示词模板

```
[age] [gender] [ethnicity], [body_type] build,
[hair_color] [hair_style] hair, [eye_color] eyes,
[face_shape] face, [distinguishing_features],
wearing [costume_description],
[personality_expression], [pose/action]
```

### 示例输出

```
25 year old Asian female, slim build,
black long wavy hair, dark brown almond eyes,
oval face with small dimples,
wearing white silk blouse and black pencil skirt,
confident expression with slight smile,
standing with arms crossed
```

### 一致性种子模板

```
[CHARACTER:角色名] [基础外貌关键词], consistent appearance, same person,
[发型发色], [服装风格], [标志特征]
```

---

## 示例角色档案

### 示例1：都市白领女主

```json
{
  "name": "林晓薇",
  "name_en": "Xiaowei",
  "role": "主角",

  "appearance": {
    "age": "28",
    "gender": "female",
    "ethnicity": "Asian Chinese",
    "height": "168cm",
    "body_type": "slim",
    "face_shape": "oval",
    "skin_tone": "fair porcelain",
    "hair": {
      "style": "long, slightly wavy, side-parted",
      "color": "dark brown, almost black",
      "length": "mid-back"
    },
    "eyes": {
      "shape": "large almond",
      "color": "dark brown"
    },
    "distinguishing_features": ["beauty mark near left eye", "dimples when smiling"]
  },

  "costumes": [
    {
      "scene_range": "1-5",
      "name": "职场装",
      "description": "Tailored white blazer, cream silk camisole, high-waisted black trousers, nude pointed heels",
      "colors": ["white", "cream", "black", "nude"],
      "accessories": ["delicate gold necklace", "small hoop earrings", "leather tote bag"]
    },
    {
      "scene_range": "6-10",
      "name": "约会装",
      "description": "Burgundy wrap dress, black strappy heels",
      "colors": ["burgundy", "black"],
      "accessories": ["drop earrings", "clutch purse"]
    }
  ],

  "visual_prompt": "28 year old Asian Chinese female, slim elegant build, long dark brown slightly wavy hair with side part, large almond dark brown eyes, oval face with fair porcelain skin, beauty mark near left eye, dimples, confident gentle expression",

  "seed_prompt": "[CHARACTER:林晓薇] Asian female late twenties, slim, long dark wavy hair, large eyes, beauty mark left eye, dimples, elegant style, consistent appearance, same person"
}
```

### 示例2：成熟商务男配

```json
{
  "name": "陈建国",
  "name_en": "Jianguo",
  "role": "配角",

  "appearance": {
    "age": "45",
    "gender": "male",
    "ethnicity": "Asian Chinese",
    "height": "178cm",
    "body_type": "average, slightly stocky",
    "face_shape": "square",
    "skin_tone": "medium tan",
    "hair": {
      "style": "short, neat, receding hairline",
      "color": "black with gray at temples",
      "length": "short"
    },
    "eyes": {
      "shape": "deep-set",
      "color": "dark brown"
    },
    "distinguishing_features": ["prominent brow", "slight wrinkles", "stern resting face"]
  },

  "costumes": [
    {
      "scene_range": "all",
      "description": "Charcoal gray three-piece suit, white dress shirt, burgundy tie, black oxford shoes",
      "colors": ["charcoal", "white", "burgundy", "black"],
      "accessories": ["silver cufflinks", "luxury watch", "reading glasses (sometimes)"]
    }
  ],

  "visual_prompt": "45 year old Asian Chinese male, average slightly stocky build, short black hair graying at temples with receding hairline, deep-set dark brown eyes, square face with prominent brow, medium tan skin, slight wrinkles, stern authoritative expression, wearing charcoal three-piece suit with burgundy tie",

  "seed_prompt": "[CHARACTER:陈建国] Asian male mid-forties, stocky, graying temples, receding hairline, stern face, business suit, consistent appearance, same person"
}
```
