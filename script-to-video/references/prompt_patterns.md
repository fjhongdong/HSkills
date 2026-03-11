# 高效提示词模式库

## 目录

1. [提示词结构公式](#提示词结构公式)
2. [镜头类型模板](#镜头类型模板)
3. [情绪场景模板](#情绪场景模板)
4. [动作场景模板](#动作场景模板)
5. [特效场景模板](#特效场景模板)
6. [组合技巧](#组合技巧)

---

## 提示词结构公式

### 基础公式

```
[主体] + [动作] + [场景] + [光线] + [氛围] + [风格] + [质量]
```

### 完整公式

```
[镜头类型], [主体描述], [动作/姿态],
[场景/环境], [时间], [天气],
[光线设置], [色彩基调],
[情绪氛围], [风格关键词],
[质量增强词], [负面排除词]
```

### 权重分配（重要性排序）

1. **主体** (30%) - 最重要，决定画面核心
2. **动作/姿态** (20%) - 定义主体状态
3. **场景** (15%) - 提供上下文
4. **光线** (15%) - 影响整体氛围
5. **风格+质量** (20%) - 统一视觉效果

---

## 镜头类型模板

### 建立镜头 (Establishing Shot)

```
模板:
extreme long shot, establishing shot of [location],
[time of day], [weather/atmosphere],
[key visual elements], [lighting],
cinematic, wide angle, high quality

示例:
extreme long shot, establishing shot of modern city skyline,
golden hour sunset, warm summer evening,
tall glass buildings reflecting orange light, busy streets below,
cinematic golden hour lighting, warm tones,
epic, beautiful, high quality
```

### 人物特写 (Character Close-up)

```
模板:
close-up shot of [character description],
[expression/emotion], [eye direction],
[lighting on face], [background blur],
[mood], cinematic portrait, high quality

示例:
close-up shot of young Asian woman with long black hair,
contemplative expression, looking off-camera to the left,
soft side lighting creating gentle shadows, bokeh background,
melancholic mood, cinematic portrait, shallow depth of field, high quality
```

### 对话双人镜头 (Two-Shot Dialogue)

```
模板:
medium two-shot of [character A] and [character B],
[their positions/poses], [interaction],
[location], [lighting],
conversational scene, natural, high quality

示例:
medium two-shot of man in suit and woman in dress,
facing each other across cafe table, engaged in conversation,
cozy coffee shop interior, warm window light,
intimate conversational scene, natural performance, cinematic, high quality
```

### 过肩镜头 (Over-the-Shoulder)

```
模板:
over-the-shoulder shot from behind [character A],
focusing on [character B], [B's expression],
[setting], [lighting],
dialogue scene, cinematic framing, high quality

示例:
over-the-shoulder shot from behind man's shoulder,
focusing on woman's face, concerned expression,
office meeting room, fluorescent lighting,
tense dialogue scene, cinematic framing, shallow depth of field, high quality
```

### 跟随镜头 (Tracking Shot)

```
模板:
tracking shot following [character],
[movement direction], [action],
[through location], [lighting],
smooth motion, dynamic, cinematic, high quality

示例:
tracking shot following woman walking,
moving forward down city street,
passing shops and pedestrians, afternoon sunlight,
smooth steady motion, dynamic urban scene, cinematic, high quality
```

---

## 情绪场景模板

### 浪漫场景

```
模板:
[shot type], romantic scene of [characters],
[romantic action/pose], [intimate setting],
golden hour / candlelight / soft lighting,
warm tones, dreamy atmosphere, soft focus,
romantic, intimate, beautiful, cinematic

示例:
medium shot, romantic scene of young couple,
holding hands while walking on beach at sunset,
golden hour warm light, waves in background,
warm orange and pink tones, dreamy soft atmosphere,
romantic, intimate, beautiful, cinematic, high quality
```

### 紧张/悬疑场景

```
模板:
[shot type], tense scene of [character/situation],
[suspenseful element], [threatening environment],
low key lighting, harsh shadows,
cold desaturated tones, claustrophobic framing,
suspenseful, tense, noir, cinematic

示例:
close-up, tense scene of man looking over shoulder,
shadows moving in dark alley behind him,
single harsh street light, deep shadows,
cold blue-gray tones, tight claustrophobic framing,
suspenseful, paranoid, noir style, cinematic, high quality
```

### 悲伤场景

```
模板:
[shot type], melancholic scene of [character],
[sad action/expression], [somber setting],
overcast / dim lighting, muted colors,
blue-gray tones, heavy atmosphere,
melancholic, emotional, somber, cinematic

示例:
medium shot, melancholic scene of woman sitting alone,
looking out rain-streaked window, tears on cheek,
overcast gray day, dim interior lighting,
muted blue-gray tones, heavy somber atmosphere,
melancholic, emotional, beautiful sadness, cinematic, high quality
```

### 欢乐场景

```
模板:
[shot type], joyful scene of [characters],
[happy action], [lively setting],
bright natural lighting, vibrant colors,
warm tones, energetic atmosphere,
joyful, cheerful, dynamic, cinematic

示例:
wide shot, joyful scene of friends at outdoor party,
laughing and dancing together, colorful decorations,
bright sunny day, natural golden light,
vibrant warm colors, energetic festive atmosphere,
joyful, celebratory, dynamic, cinematic, high quality
```

---

## 动作场景模板

### 追逐场景

```
模板:
[shot type], chase scene, [pursuer] chasing [target],
[running/driving action], [through location],
dynamic camera movement, motion blur,
intense lighting, high contrast,
action, thrilling, dynamic, cinematic

示例:
tracking shot, chase scene, man in black chasing woman,
sprinting through crowded market, pushing past people,
handheld dynamic camera, slight motion blur,
harsh daylight with deep shadows, high contrast,
action thriller, intense, dynamic, cinematic, high quality
```

### 打斗场景

```
模板:
[shot type], fight scene between [fighters],
[combat action], [fighting location],
dramatic lighting, high contrast shadows,
intense atmosphere, dynamic angles,
action, martial arts / combat style, cinematic

示例:
medium shot, fight scene between two martial artists,
exchanging rapid punches and kicks, warehouse setting,
dramatic side lighting, sharp shadows,
intense focused atmosphere, dynamic low angle,
action, martial arts combat, cinematic, high quality
```

### 爆炸/灾难场景

```
模板:
[shot type], [disaster type] scene,
[destruction elements], [characters reacting],
dramatic lighting with fire/debris,
orange and black tones, chaotic atmosphere,
disaster, epic, dramatic, cinematic

示例:
wide shot, explosion scene in city,
building collapsing with fire and debris, people running,
dramatic fire lighting against dark smoke,
orange flames and black smoke, chaotic destruction,
disaster movie, epic scale, dramatic, cinematic, high quality
```

---

## 特效场景模板

### 魔法/超能力

```
模板:
[shot type], [character] using [power type],
[visual effect description], [energy colors],
magical lighting, glowing effects,
fantastical atmosphere, [style],
fantasy, magical, cinematic, high quality

示例:
medium shot, young wizard casting spell,
blue magical energy swirling from hands, runes floating,
ethereal blue glow illuminating face, dark background,
mystical fantastical atmosphere, fantasy style,
magical, beautiful effects, cinematic, high quality
```

### 科幻场景

```
模板:
[shot type], sci-fi scene of [subject],
[futuristic elements], [technology],
high-tech lighting, holographic effects,
blue and white tones, futuristic atmosphere,
sci-fi, futuristic, cinematic, high quality

示例:
wide shot, sci-fi scene of spaceship interior,
holographic displays, crew at control stations,
blue ambient lighting with orange accents, lens flares,
cool blue and white tones, high-tech atmosphere,
sci-fi, futuristic, cinematic, high quality
```

### 梦境/回忆

```
模板:
[shot type], dream sequence / flashback of [scene],
[dreamy visual elements], [memory content],
soft ethereal lighting, haze/glow,
desaturated or warm nostalgic tones,
dreamlike, surreal, cinematic, high quality

示例:
medium shot, flashback memory of childhood,
young girl playing in sunlit garden, soft edges,
dreamy overexposed lighting, slight lens haze,
warm sepia nostalgic tones, soft vignette,
dreamlike, nostalgic, beautiful, cinematic, high quality
```

---

## 组合技巧

### 层次叠加法

从基础到细节逐层添加：

```
层次1 - 核心: close-up of woman
层次2 - 动作: crying, tears streaming
层次3 - 场景: rainy window background
层次4 - 光线: cold blue light from outside
层次5 - 情绪: melancholic, heartbroken
层次6 - 风格: cinematic, emotional
层次7 - 质量: high quality, detailed

完整: close-up of woman crying, tears streaming down face,
rainy window background with water droplets, cold blue light from outside,
melancholic heartbroken mood, cinematic emotional scene,
high quality, detailed, beautiful sadness
```

### 对比强调法

通过对比元素增强效果：

```
光与暗: bright spotlight on subject, dark shadows around
冷与暖: cold blue background, warm orange light on face
动与静: blurred motion in background, sharp still subject
大与小: vast empty space, small lone figure
```

### 感官联动法

添加暗示其他感官的视觉元素：

```
声音暗示: mouth open screaming, visible shock wave
触感暗示: goosebumps on skin, wind-blown hair
温度暗示: visible breath in cold, sweat drops in heat
```

### 一致性强化法

在每个提示词中重复核心元素：

```
镜头1: ... [STYLE: cinematic noir, high contrast, rainy night]
镜头2: ... [STYLE: cinematic noir, high contrast, rainy night]
镜头3: ... [STYLE: cinematic noir, high contrast, rainy night]
```

---

## 提示词检查公式

生成前检查是否包含：

```
□ WHO - 谁（主体描述）
□ WHAT - 做什么（动作/状态）
□ WHERE - 在哪里（场景）
□ WHEN - 什么时候（时间/光线）
□ HOW - 怎样的（氛围/风格）
□ QUALITY - 质量词
```

完整的提示词应该能回答以上所有问题。
