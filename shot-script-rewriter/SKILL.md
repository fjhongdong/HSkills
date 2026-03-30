---
name: shot-script-rewriter
description: 接收分镜脚本 JSON 和用户文字描述的角色形象，对分镜脚本进行最小化角色替换改写。当用户提供分镜JSON并要求"改写分镜"、"换角色"、"角色替换"、"复刻脚本"、"替换人物"、"改写分镜脚本"、"角色改编"、"换个角色复刻"、"用我的角色重写分镜"时触发此技能。即使没有明确提及改写，只要用户同时提供了分镜脚本 JSON 和角色描述，也应触发此技能。
---

# 分镜脚本角色改写器

接收分镜脚本 JSON，根据用户描述的新角色形象进行最小化改写——仅替换角色直接相关内容，尽可能保留原脚本的故事线、情绪氛围和技术参数。

## 核心能力

- 接收完整的分镜脚本 JSON
- 接收用户文字描述的新角色形象
- 按三级策略（必改/适配改/不动）进行最小化改写
- 输出与输入格式完全相同的 JSON

## 输入输出

**输入：**
1. 分镜脚本 JSON（必需）
2. 用户文字描述的角色形象（必需）

**输出：** 与输入格式完全相同的 JSON

---

## 改写规则

**核心原则：最小干预。** 只改"看了会出戏"的内容。如果原内容和新角色放在一起没有违和感，就不改。

### 一级：必改（角色直接相关，每个镜头必改）

| 字段 | 改写方式 | 示例 |
|------|----------|------|
| `subjects[].description` | 替换为新角色描述 | "年轻女性，约25岁，气质温柔文艺" → "22岁男生，酷飒街头风，性格外向开朗" |
| `subjects[].clothing` | 全部替换为新角色穿搭 | 米色慵懒风卫衣 → 黑色oversized卫衣 + 卡其色工装裤 |
| `subjects[].expression` | 根据新角色气质调整表情 | "平静专注，嘴角微微上扬" → "嘴角带笑，眼神明亮放松" |

### 二级：适配改（与新角色冲突时才改，不冲突则保留原样）

| 字段 | 触发条件 | 示例 |
|------|----------|------|
| `subjects[].action` | 原动作与新角色性别/气质/体型不匹配 | "蜷坐在软垫上"（温柔女生）→ "靠坐着，一只脚搭在窗台上"（酷飒男生） |
| `subjects[].position` | 姿势与角色体态/性别不匹配 | "蜷坐在窗边软垫上"（温柔女生）→ "靠坐在窗边"（酷飒男生） |
| `shot_description` | 镜头概述中引用了原角色的性别、服饰或典型动作 | "女生蜷坐在...米色卫衣与..." → "男生靠坐在...黑色卫衣与..." |
| `audio.dialogue.content` | 台词语气与角色性格严重冲突 | "哼，讨厌~"（甜美风）→ "还行吧"（酷飒风） |
| `audio.dialogue.tone` | 说话语气与角色不符 | "撒娇语气" → "随性语气" |
| `audio.narration` | 旁白风格与角色不匹配 | "温柔内心独白" → "随性内心独白" |

**二级改写判断方法：**
- 性别冲突：原动作/台词隐含的性别与新角色不同（如"她撩了一下头发"→男生角色需改）
- 气质冲突：原描述的情绪调性与新角色气质相反（如"娇羞"配酷飒角色需改）
- 体态冲突：原动作需要特定体型才能自然完成（如"蜷坐"对成年男性不自然）
- **如果不冲突，坚决不改**

### 三级：不动（无论如何都不改）

- `shot_breakdown` 的镜头数量和顺序
- `timecode` 所有时间码（起止时间、时长）
- `shot_type`、`camera_movement`、`transition_in`、`transition_out`
- `visual.scene` 场景环境（除非场景与新角色严重冲突）
- `visual.lighting`、`visual.color` 光线和色彩
- `visual.composition` 构图
- `video_analysis.emotion` 情绪基调
- `video_analysis.theme`、`video_analysis.video_type`、`video_analysis.video_style`
- `editing_analysis` 剪辑节奏
- `video_analysis.on_screen_presence.person_count` 人物数量
- `text_elements` 字幕、标题、贴纸
- 原始 JSON 中为 `null` 的字段保持 `null`

---

## 输入规范

### JSON 输入

必须包含完整的分镜脚本结构，至少包含以下三个顶层字段：
- `video_info`：视频基本信息
- `video_analysis`：视频分析结果
- `shot_breakdown`：分镜数组

如果输入 JSON 缺少以上任一字段，提示用户确认 JSON 格式是否正确。

### 角色描述

用户可自由组织文字描述角色形象，建议包含以下维度（缺省项由 Skill 根据已有信息合理推断）：

| 维度 | 必需 | 示例 |
|------|------|------|
| 性别 | 是 | 男/女 |
| 年龄段 | 是 | 20-25岁 |
| 气质 | 是 | 温柔/酷飒/活泼/知性/阳光/文艺 |
| 穿搭风格 | 是 | 街头潮流/日系清新/韩系精致/运动休闲 |
| 性格特征 | 推荐 | 内向安静/外向开朗/酷酷的/元气满满 |
| 外貌特征 | 可选 | 长发/短发/戴眼镜/高挑/娇小 |

---

## 执行流程

### 步骤1：验证输入

检查输入 JSON 是否符合分镜脚本格式：
- 必须包含 `video_info`、`video_analysis`、`shot_breakdown` 三个顶层字段
- `shot_breakdown` 必须是非空数组
- 如果 `has_real_person` 为 `false` 且无 `subjects[].type: "人物"`，提示用户无法进行角色替换改写

检查角色描述是否足够：
- 少于 10 个字 → 提示用户补充更多角色特征
- 建议至少包含：性别、年龄段、气质或穿搭风格

### 步骤2：提炼新角色画像

从用户文字描述中提取角色维度（参见"输入规范 > 角色描述"），形成内部角色特征卡片，用于后续改写判断。

### 步骤3：逐镜头改写

对 `shot_breakdown` 中的每个镜头：

1. **一级改写**：直接替换 `subjects[]` 中的 description、clothing、expression
2. **二级改写**：逐个检查 position、action、shot_description、dialogue、narration，判断是否与新角色冲突，冲突则适配
3. **三级跳过**：timecode、shot_type、visual、transition 等字段原样保留

**多人物处理：**
- `person_count > 1` 时，角色描述替换主要人物（`screen_time_ratio` 最高者）
- 次要人物保持不变
- 用户如需替换多人，应提供多段描述（按重要性排序）

### 步骤4：更新全局字段

| 字段 | 处理方式 |
|------|----------|
| `video_analysis.on_screen_presence.person_details` | 替换为新角色描述 |
| `summary` | 仅当概要中提到原角色时微调 |
| `key_elements` | 仅替换角色相关元素（如"慵懒穿搭"→"街头酷飒"），保留场景/道具元素 |
| 其他 video_analysis 字段 | 不动 |

### 步骤5：输出 JSON

输出完整的 JSON，确保：
- 格式与输入完全一致，不增不减字段
- 原始 `null` 字段保持 `null`
- JSON 语法正确，可被程序解析

---

## 错误处理

| 错误情况 | 处理方式 |
|----------|----------|
| 输入 JSON 格式错误 | 提示用户检查 JSON 格式，提供具体解析错误位置 |
| JSON 缺少必需字段 | 提示用户确认 JSON 格式，列出缺失字段 |
| 角色描述过短（<10字） | 提示用户补充性别、年龄段、气质风格等信息 |
| 原视频无人物出镜 | 提示无法进行角色替换改写 |

---

## 注意事项

1. **最小干预是第一原则**：能不改就不改。宁可保留一些不那么完美的地方，也不要过度改写导致偏离原脚本
2. **保持故事线完整**：改写后的脚本必须讲述同一个故事，只是主角换了
3. **保持情绪一致**：原脚本是治愈风，改写后也应该是治愈风，只是通过新角色来表达
4. **格式严格兼容**：输出 JSON 必须与输入格式完全一致
5. **不要凭空创造**：原始 JSON 中为 `null` 的字段（如 `dialogue: null`）改写后保持 `null`
6. **物体类 subjects 不替换**：`subjects[].type: "物体"` 的条目保持原样
7. **质量自检**：改写完成后，检查每个镜头是否仍有"出戏感"——如果有，说明改写不够彻底或改错了

---

## 示例

**用户角色描述：** "22岁男生，酷飒街头风，穿着黑色oversized卫衣和工装裤，性格外向开朗"

### 原始镜头（分镜脚本示例）

```json
{
  "shot_id": 1,
  "timecode": {
    "start": "00:00:00",
    "end": "00:00:04",
    "duration_seconds": 4.0
  },
  "shot_type": "中景",
  "camera_movement": "固定镜头",
  "transition_in": "淡入",
  "transition_out": "硬切",

  "visual": {
    "scene": {
      "location_type": "室内",
      "specific_location": "家中窗边角落",
      "environment": "阳光透过白色纱帘洒入，窗边有绿植和软垫，整体温馨"
    },
    "lighting": {
      "type": "自然光",
      "direction": "左侧逆光",
      "color_temperature": "暖色调",
      "mood": "柔和温暖，有光斑"
    },
    "color": {
      "dominant_colors": ["米白色", "浅棕色", "淡绿色"],
      "color_mood": "温暖治愈",
      "color_grade": "日系胶片感，低对比度"
    }
  },

  "subjects": [
    {
      "subject_id": 1,
      "type": "人物",
      "description": "年轻女性，约25岁，气质温柔文艺",
      "position": "蜷坐在窗边软垫上",
      "action": "专注看书，偶尔翻页",
      "expression": "平静专注，嘴角微微上扬",
      "clothing": {
        "top": "米色慵懒风卫衣，宽松版型",
        "bottom": "灰色休闲裤",
        "accessories": "无",
        "overall_style": "慵懒家居风"
      },
      "props": ["书籍"]
    }
  ],

  "audio": {
    "dialogue": null,
    "narration": {
      "content": "这样的午后，只属于我",
      "tone": "温柔内心独白"
    },
    "music": {
      "presence": true,
      "style": "轻音乐/钢琴",
      "mood": "治愈温暖",
      "tempo": "慢速"
    }
  },

  "shot_description": "女生蜷坐在洒满阳光的窗边，专注地看书，米色卫衣与温暖的光线融为一体"
}
```

### 改写后

```json
{
  "shot_id": 1,
  "timecode": {
    "start": "00:00:00",
    "end": "00:00:04",
    "duration_seconds": 4.0
  },
  "shot_type": "中景",
  "camera_movement": "固定镜头",
  "transition_in": "淡入",
  "transition_out": "硬切",

  "visual": {
    "scene": {
      "location_type": "室内",
      "specific_location": "家中窗边角落",
      "environment": "阳光透过白色纱帘洒入，窗边有绿植和软垫，整体温馨"
    },
    "lighting": {
      "type": "自然光",
      "direction": "左侧逆光",
      "color_temperature": "暖色调",
      "mood": "柔和温暖，有光斑"
    },
    "color": {
      "dominant_colors": ["米白色", "浅棕色", "淡绿色"],
      "color_mood": "温暖治愈",
      "color_grade": "日系胶片感，低对比度"
    }
  },

  "subjects": [
    {
      "subject_id": 1,
      "type": "人物",
      "description": "22岁男生，酷飒街头风，性格外向开朗",
      "position": "靠坐在窗边",
      "action": "随手翻着书，时不时望向窗外",
      "expression": "嘴角带笑，眼神明亮放松",
      "clothing": {
        "top": "黑色oversized卫衣",
        "bottom": "卡其色工装裤",
        "accessories": "无",
        "overall_style": "街头酷飒风"
      },
      "props": ["书籍"]
    }
  ],

  "audio": {
    "dialogue": null,
    "narration": {
      "content": "这样的午后，只属于我",
      "tone": "随性内心独白"
    },
    "music": {
      "presence": true,
      "style": "轻音乐/钢琴",
      "mood": "治愈温暖",
      "tempo": "慢速"
    }
  },

  "shot_description": "男生靠坐在洒满阳光的窗边，黑色卫衣与温暖光线形成鲜明对比"
}
```

### 改动清单

| 级别 | 字段 | 原值 | 新值 | 原因 |
|------|------|------|------|------|
| 一级 | subjects[0].description | "年轻女性，约25岁，气质温柔文艺" | "22岁男生，酷飒街头风，性格外向开朗" | 角色替换 |
| 一级 | subjects[0].clothing | 米色慵懒风卫衣+灰色休闲裤 | 黑色oversized卫衣+卡其色工装裤 | 穿搭替换 |
| 一级 | subjects[0].expression | "平静专注，嘴角微微上扬" | "嘴角带笑，眼神明亮放松" | 气质调整 |
| 二级 | subjects[0].position | "蜷坐在窗边软垫上" | "靠坐在窗边" | 蜷坐与酷飒男生体态不匹配 |
| 二级 | subjects[0].action | "专注看书，偶尔翻页" | "随手翻着书，时不时望向窗外" | 温柔→外向开朗的行为差异 |
| 二级 | shot_description | "女生蜷坐...米色卫衣..." | "男生靠坐...黑色卫衣..." | 包含原角色性别和服饰 |
| 二级 | narration.tone | "温柔内心独白" | "随性内心独白" | 气质冲突 |
| 三级 | timecode | — | 不变 | — |
| 三级 | visual.scene | — | 不变 | — |
| 三级 | visual.lighting | — | 不变 | — |
| 三级 | visual.color | — | 不变 | — |
| 三级 | dialogue | null | null（保持） | — |
| 三级 | music | — | 不变 | — |
