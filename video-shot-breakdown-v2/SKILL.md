---
name: video-shot-breakdown-v2
description: 拆解视频生成详细分镜脚本，用于一比一复刻爆款视频。采用直接视频分析，完整捕捉运镜、转场、动作连续性和音频。当用户上传视频并要求"分镜拆解"、"镜头分析"、"视频拆解"、"复刻视频"、"拆解分镜"、"分析视频结构"、"视频镜头拆解"时触发此技能。即使没有明确提及，只要用户提供了视频并询问分镜、镜头、复刻相关需求，也应触发此技能。
---

# 视频分镜拆解器 V2

对用户上传的视频进行深度分析，逐镜头拆解出最详细的分镜脚本，支持一比一复刻。**采用直接视频分析，完整捕捉运镜、转场、动作连续性和音频。**

## 核心能力

- 支持**本地视频文件**输入
- **直接视频分析**：将视频直接传给多模态模型，完整捕捉运镜、转场、动作连续性、音频
- 输出**JSON格式**分镜脚本，便于程序处理和二次开发
- 包含视频**主题、概要、情绪、类型、风格**等多维度分析
- 每个镜头提供**景别、运镜、画面、台词、音效、转场**等完整信息

---

## 分析流程

### 直接视频分析

将视频直接传给多模态模型进行整体分析。

**优势：**
- 运镜判断准确（能观察镜头的推拉摇移过程）
- 转场检测精确（能直接看到画面切换效果）
- 动作连续完整（不断帧）
- 音画同步分析（台词、BGM、音效与画面对应）

**执行方式：**
1. 直接读取视频文件
2. 将完整视频传给多模态模型
3. 模型一次性分析所有维度

**分析提示词模板：**
```
请分析这段视频，逐镜头拆解出详细的分镜脚本，目标是输出可直接用于一比一复刻的 JSON 结构化数据。

## 需要识别的信息

### 一、视频整体信息
1. 主题与概要：视频主题、2-3句话概括内容
2. 情绪分析：主要情绪、次要情绪、情绪变化曲线
3. 视频类型与风格（参考字段说明中的枚举表）
4. 目标受众、关键元素
5. 真人出镜判断：是否有人物出镜、人数、露出程度

### 二、每个镜头的逐项分析
1. **时间码**：精确起止时间（HH:MM:SS）、时长
2. **景别**：大特写/特写/近景/中景/中全景/全景/远景/大远景
3. **运镜方式**：固定/推/拉/摇/俯仰/移/跟/升降/环绕/手持/组合
4. **转场**：入镜和出镜转场类型、转场时长（秒）、转场颜色

5. **镜头参数（camera_details）**：
   - 焦距估算（14-200mm范围）
   - 焦点主体、景深（浅/中/深）、焦外质量
   - 焦点转移（如有）：从哪里移到哪里、发生时间
   - 稳定方式：三脚架/稳定器/手持/肩扛/斯坦尼康
   - 机位高度：鸟瞰/高俯/微俯/平视/微仰/仰拍/虫眼
   - 拍摄角度：正面/斜侧45°/侧面/斜侧135°/背面
   - 镜头特效：暗角/光晕/畸变/呼吸感/漏光

6. **画面分析（visual）**：
   - 场景：室内外、具体位置、环境描述、场景布置细节
   - 构图：构图法则（三分法/居中/对称等）、主体位置与面积占比、人物朝向（左/右/正面/背面）、头空间、引导空间、景深层次、背景元素、框架内框架
   - 光线：光源类型、方向、色温（尽量给出K值估算）、氛围、阴影描述
   - 色彩：主色调名称+十六进制色值、色彩情绪、调色风格、对比度、饱和度、胶片颗粒感

7. **主体分析（subjects）**：
   - 人物/物体描述、画面位置
   - `person_id`：当类型为"人物"时，关联 `on_screen_presence.person_details[].person_id`，跨镜头追踪同一人物（人物须关联 person_id 与全局人物对应）
   - 身体朝向（正面/3/4侧面/侧面/背面）
   - 视线方向（看镜头/看向画面某侧/低头/闭眼/看向画面外）
   - 动作描述、运动方式、运动速度
   - 表情描述（人物）
   - 服饰详情：上装/下装/配饰/整体风格 + 颜色十六进制值
   - 手持道具

8. **文字元素**：字幕/标题/贴纸的内容、位置、样式、入场动画

9. **变速与特效（speed_effects）**：
   - 播放速度（1.0x正常/0.5x慢动作等）
   - 变速描述（如有渐变）
   - 是否有定格帧
   - 叠加效果：胶片颗粒/漏光/灰尘粒子/色彩滤镜

10. **音频分析（audio）**：
    - 台词：说话人、内容、语调
    - 旁白：内容、语调
    - 背景音乐：有无、风格、情绪、节奏
    - 音效：类型、描述、与画面的精确同步点
    - 音乐节拍同步：剪辑点是否踩在节拍上

11. **镜头整体描述**：一句话概括画面内容

### 三、服饰植入推荐（仅当有真人出镜时）
- 是否适合服饰植入及原因
- 推荐2-4种适合的服饰风格，按匹配度排序
- 每种风格给出：匹配度评分(0-1)、推荐理由、具体单品(3-4件)
- 植入方式建议

### 四、剪辑节奏分析
- 总镜头数、平均镜头时长、最长镜头时长、最短镜头时长、剪辑节奏描述、节奏快慢、剪辑风格

## 输出要求
- 严格按照 JSON 格式输出
- 不确定的字段标注"不确定"，不要编造数值
- 数值型估算字段可给范围（如焦距"35-50mm（估算）"）
- 连续镜头间的光线、场景变化应合理自然

请严格按照本技能"输出格式"章节定义的 JSON 结构输出，确保所有字段完整填充。
```

---

## 输出格式

### JSON结构定义

```json
{
  "video_analysis": {
    "title": "视频标题（如有）",
    "theme": "视频主题",
    "summary": "视频概要（2-3句话概括视频内容）",
    "emotion": {
      "primary": "主要情绪",
      "secondary": ["次要情绪1", "次要情绪2"],
      "emotion_arc": "情绪变化曲线描述"
    },
    "video_type": "视频类型",
    "video_style": "视频风格",
    "target_audience": "目标受众",
    "key_elements": ["关键元素1", "关键元素2", "关键元素3"],

    "on_screen_presence": {
      "has_real_person": true,
      "person_count": 1,
      "person_details": [
        {
          "person_id": 1,
          "description": "人物描述（性别、年龄段、外貌特征）",
          "screen_time_ratio": 0.85,
          "appearance_notes": "主要出镜人物，几乎全程出现"
        }
      ],
      "exposure_level": "高/中/低",
      "exposure_description": "角色露出程度描述（如：人物正面露出占视频80%，主要展示上半身和全身穿搭）"
    },

    "fashion_placement": {
      "suitable": true,
      "reason": "人物全程出镜，露出面积大，穿搭展示空间充足",
      "recommended_styles": [
        {
          "style": "慵懒家居风",
          "fit_score": 0.95,
          "reason": "视频场景为居家环境，氛围温馨治愈，与慵懒家居风高度契合",
          "recommended_items": ["宽松卫衣", "针织开衫", "棉质休闲裤", "亚麻拖鞋"]
        },
        {
          "style": "文艺森系风",
          "fit_score": 0.85,
          "reason": "人物气质文艺温柔，窗边/书/绿植等元素与森系风格自然搭配",
          "recommended_items": ["棉麻连衣裙", "帆布包", "编织手链", "素色围巾"]
        },
        {
          "style": "日系简约风",
          "fit_score": 0.80,
          "reason": "画面色调偏暖白和低饱和度，日系低对比度调色，适合简约穿搭植入",
          "recommended_items": ["基础款T恤", "直筒牛仔裤", "帆布鞋", "帆布托特包"]
        }
      ],
      "placement_notes": "建议植入方式：服饰作为日常穿搭自然出现，避免特写镜头，保持故事叙事为主"
    }
  },

  "shot_breakdown": [
    {
      "shot_id": 1,
      "timecode": {
        "start": "00:00:00",
        "end": "00:00:04",
        "duration_seconds": 4.0
      },
      "shot_type": "景别",
      "camera_movement": "运镜方式",
      "transition_in": {
        "type": "入镜转场类型",
        "duration_seconds": 0.5,
        "color": "黑/白/自定义色"
      },
      "transition_out": {
        "type": "出镜转场类型",
        "duration_seconds": 0.3,
        "color": "黑/白/自定义色"
      },

      "camera_details": {
        "focal_length": "35mm",
        "focus": {
          "subject": "对焦主体描述",
          "depth_of_field": "浅/中/深",
          "bokeh_quality": "柔滑/一般/硬边"
        },
        "focus_pull": {
          "has_pull": false,
          "from": null,
          "to": null,
          "timing": null
        },
        "stabilization": "三脚架/稳定器/手持/肩扛/斯坦尼康",
        "camera_height": "鸟瞰/高俯/微俯/平视/微仰/仰拍/虫眼",
        "camera_angle": "正面/斜侧45°/侧面/斜侧135°/背面",
        "lens_effect": {
          "vignette": "无/轻微/明显",
          "flare": "无/轻微/明显",
          "distortion": "无/轻微/明显",
          "breathing": "无/轻微/明显",
          "leak": "无/轻微/明显"
        }
      },

      "visual": {
        "scene": {
          "location_type": "室内/室外",
          "specific_location": "具体场景",
          "environment": "环境描述",
          "set_dressing": "场景布置细节（道具摆放、装饰元素）"
        },
        "composition": {
          "framing_rule": "三分法/居中/对称/引导线/框架构图/对角线/黄金螺旋/留白",
          "subject_position": "主体在画面中的精确位置",
          "subject_scale": "主体占画面面积比（约1/4、1/3、1/2、2/3）",
          "facing_direction": "人物在画面中的朝向（左/右/正面/背面，与 body_angle 描述角度不同）",
          "headroom": "充裕/适中/裁切",
          "lead_room": "运动方向前的留白（左/右/上/下，空间大小）",
          "depth": "景深描述",
          "background": "背景元素",
          "frame_within_frame": "框架内框架（门窗/镜子等二次构图元素）"
        },
        "lighting": {
          "type": "自然光/人工光/混合",
          "direction": "光线方向（正面/侧面/逆光/顶光/底光）",
          "color_temperature": "冷暖色调（数值如3200K或描述）",
          "mood": "光线氛围",
          "shadow": "阴影描述（硬阴影/柔阴影/无阴影）"
        },
        "color": {
          "dominant_colors": ["主色调1", "主色调2"],
          "dominant_color_hex": ["#D4C5A9", "#8B9E6B"],
          "color_mood": "色彩情绪",
          "color_grade": "调色风格",
          "contrast": "高/中/低",
          "saturation": "高/中/低/去饱和",
          "grain": "无/轻微/明显/重度"
        }
      },

      "subjects": [
        {
          "subject_id": 1,
          "type": "人物/物体",
          "person_id": 1,
          "description": "主体描述",
          "position": "画面位置",
          "body_angle": "正面/3/4侧面/侧面/背面",
          "eye_line": "看镜头/看向画面某侧/低头/闭眼/看向画面外",
          "action": "动作描述",
          "movement": "静止/向左移入/从画外走入/原地微动/转身",
          "movement_speed": "静止/缓慢/正常/快速",
          "expression": "表情描述（人物）",
          "clothing": {
            "top": "上装描述（款式、材质、颜色）",
            "bottom": "下装描述",
            "accessories": "配饰描述",
            "overall_style": "整体风格",
            "color_hex": {
              "top": "#C4B59A",
              "bottom": "#808080",
              "accessories": null
            }
          },
          "props": ["手持道具1", "手持道具2"]
        }
      ],

      "text_elements": [
        {
          "type": "字幕/标题/贴纸",
          "content": "文字内容",
          "position": "画面位置",
          "style": "字体样式",
          "animation": "入场动画（淡入/弹入/打字机/无）"
        }
      ],

      "speed_effects": {
        "playback_speed": 1.0,
        "speed_ramp": {
          "has_ramp": false,
          "description": null
        },
        "freeze_frame": {
          "has_freeze": false,
          "at_seconds": null
        },
        "overlay": {
          "film_grain": false,
          "light_leak": false,
          "dust_particles": false,
          "color_filter": null,
          "other": null
        }
      },

      "audio": {
        "dialogue": {
          "speaker": "说话人",
          "content": "台词内容",
          "tone": "语调"
        },
        "narration": {
          "content": "旁白内容",
          "tone": "旁白语调"
        },
        "music": {
          "presence": true,
          "style": "音乐风格（presence 为 false 时，style/mood/tempo 均为 null）",
          "mood": "音乐情绪",
          "tempo": "节奏快慢"
        },
        "sound_effects": [
          {
            "type": "音效类型",
            "description": "音效描述",
            "sync_point": "与画面对应的时间点（如：翻页声与画面翻页动作同步）"
          }
        ],
        "music_beat_sync": {
          "cuts_on_beat": true,
          "description": "剪辑点是否踩在音乐节拍上的描述"
        }
      },

      "shot_description": "镜头整体描述（一句话概括画面内容）"
    }
  ],

  "editing_analysis": {
    "total_shots": 2,
    "average_shot_duration": 4.0,
    "longest_shot_seconds": 4.0,
    "shortest_shot_seconds": 4.0,
    "editing_rhythm": "剪辑节奏描述",
    "pacing": "快/中/慢",
    "cut_style": "剪辑风格"
  }
}
```

---

## 字段说明

### 视频类型 (video_type)

| 类型 | 说明 |
|------|------|
| 剧情/短剧 | 有完整故事情节的叙事视频 |
| 日常Vlog | 生活记录、日常分享 |
| 知识科普 | 教程、讲解、知识分享 |
| 产品测评 | 开箱、评测、对比 |
| 美食探店 | 美食制作、餐厅探店 |
| 旅行风光 | 旅行记录、风景展示 |
| 时尚穿搭 | OOTD、穿搭展示 |
| 情感治愈 | 情感表达、治愈内容 |
| 搞笑娱乐 | 搞笑、娱乐、段子 |
| 舞蹈音乐 | 舞蹈、音乐表演 |
| 萌宠动物 | 宠物、动物相关 |
| 运动健身 | 运动、健身教程 |
| 其他 | 不属于以上类型 |

### 视频风格 (video_style)

| 风格 | 说明 |
|------|------|
| 日系清新 | 柔光、自然、干净 |
| 韩系精致 | 时尚、都市、高级感 |
| 欧美随性 | 大胆、个性、自由 |
| 国风雅致 | 诗意、含蓄、东方美 |
| 居家温馨 | 暖色、舒适、私密 |
| 都市现代 | 冷色、简约、都市感 |
| 复古怀旧 | 胶片感、怀旧色调 |
| 赛博朋克 | 霓虹、科技感、暗色调 |
| 极简主义 | 简洁、留白、高级感 |
| 电影质感 | 专业级画面、戏剧化光影 |
| 其他 | 不属于以上风格 |

### 景别分类 (shot_type)

| 景别 | 说明 | 取景范围 |
|------|------|----------|
| 大特写 | 极近距离 | 眼睛、嘴唇等局部 |
| 特写 | 近距离 | 面部或物体细节 |
| 近景 | 较近距离 | 胸部以上 |
| 中景 | 中等距离 | 腰部以上 |
| 中全景 | 中远距离 | 膝盖以上 |
| 全景 | 较远距离 | 人物全身 |
| 远景 | 远距离 | 人物+环境 |
| 大远景 | 极远距离 | 大环境为主 |

### 运镜方式 (camera_movement)

| 运镜 | 说明 |
|------|------|
| 固定镜头 | 相机固定不动 |
| 推镜头 | 相机向主体靠近 |
| 拉镜头 | 相机远离主体 |
| 摇镜头 | 相机左右旋转 |
| 俯仰 | 相机上下旋转 |
| 移镜头 | 相机横向移动 |
| 跟镜头 | 跟随主体移动 |
| 升降镜头 | 相机上下移动 |
| 环绕 | 围绕主体旋转 |
| 手持 | 手持晃动感 |
| 组合运镜 | 多种运镜组合 |

### 转场类型 (transition)

| 转场 | 说明 |
|------|------|
| 硬切 | 直接切换 |
| 淡入 | 从黑/白渐显 |
| 淡出 | 渐变到黑/白 |
| 溶解 | 画面叠加过渡 |
| 划像 | 画面滑动切换 |
| 黑场 | 黑屏过渡 |
| 闪白 | 白屏过渡 |
| 匹配剪辑 | 画面元素匹配切换 |
| 遮罩转场 | 用物体遮挡切换 |
| 缩放转场 | 放大/缩小切换 |
| 无缝转场 | 运动衔接切换 |

### 焦距估算 (focal_length)

| 焦距范围 | 视角效果 | 典型用途 |
|----------|----------|----------|
| 14-24mm | 超广角，强烈透视变形 | 夸张空间感、大全景 |
| 24-35mm | 广角，轻微透视变形 | 环境+人物、Vlog自拍 |
| 35-50mm | 标准焦距，接近人眼 | 自然视角、街拍、日常 |
| 50-85mm | 中长焦，轻度压缩 | 人像、半身特写 |
| 85-135mm | 长焦，明显压缩 | 人像特写、虚化背景 |
| 135-200mm+ | 超长焦，强压缩 | 远距拍摄、强烈虚化 |

### 机位高度 (camera_height)

| 高度 | 说明 | 视觉效果 |
|------|------|----------|
| 鸟瞰 | 正上方俯拍 | 上帝视角，展示空间布局 |
| 高俯 | 显著高于主体 | 主体渺小，环境主导 |
| 微俯 | 略高于平视 | 轻微俯视，日常感 |
| 平视 | 与主体眼睛齐平 | 平等、自然、纪录片感 |
| 微仰 | 略低于平视 | 主体略显高大 |
| 仰拍 | 显著低于主体 | 主体威严、力量感 |
| 虫眼 | 接近地面仰拍 | 极度夸张，戏剧化 |

### 拍摄角度 (camera_angle)

| 角度 | 说明 | 代入感 |
|------|------|--------|
| 正面 | 镜头正对主体面部 | 最强，直视观众 |
| 斜侧45° | 镜头与主体成45° | 强，兼顾面部和立体感 |
| 侧面 | 镜头与主体成90° | 中，展示轮廓 |
| 斜侧135° | 镜头与主体成135° | 弱，神秘感 |
| 背面 | 镜头在主体正后方 | 弱，悬念和孤独感 |

### 稳定方式 (stabilization)

| 方式 | 说明 | 画面效果 |
|------|------|----------|
| 三脚架 | 固定支架 | 完全静止，零抖动 |
| 稳定器/云台 | 机械/电子稳定 | 丝滑移动，微弱浮动 |
| 肩扛 | 摄像师肩部支撑 | 轻微呼吸感晃动 |
| 手持 | 手持拍摄 | 明显晃动，临场感 |
| 斯坦尼康 | 专业稳定器 | 平滑移动，专业电影感 |

### 构图法则 (framing_rule)

| 构图 | 说明 |
|------|------|
| 三分法 | 主体放在三分线交点 |
| 居中 | 主体在画面正中 |
| 对称 | 左右/上下对称 |
| 引导线 | 用线条引导视线到主体 |
| 框架构图 | 用门框/窗框等框住主体 |
| 对角线 | 主体沿对角线分布 |
| 黄金螺旋 | 按黄金螺旋放置主体 |
| 留白 | 大面积留白突出主体 |

### 播放速度 (playback_speed)

| 速度 | 说明 | 用途 |
|------|------|------|
| 0.25x | 极慢动作 | 强调瞬间，如水滴、表情 |
| 0.5x | 慢动作 | 强调动作美感 |
| 1.0x | 正常速度 | 标准叙事 |
| 1.5-2x | 快进 | 压缩时间、制造趣味 |
| 变速(ramp) | 速度渐变 | 转场强调，如正常→慢→正常 |

### 镜头特效 (lens_effect)

| 特效 | 说明 | 复刻方式 |
|------|------|----------|
| 暗角 | 画面边缘变暗 | 后期加暗角/光学暗角 |
| 光晕 | 光源产生光晕 | 镜头对准光源/后期叠加 |
| 畸变 | 广角桶形/长焦枕形 | 镜头自然产生 |
| 呼吸感 | 对焦时画面微缩放 | 专业电影镜头特性 |
| 漏光 | 光线漏入画面边缘 | 胶片特性/后期叠加 |

### 情绪分类 (emotion)

| 情绪类型 | 包含情绪 |
|----------|----------|
| 正向情绪 | 开心、治愈、温暖、感动、兴奋、期待、满足、希望 |
| 负向情绪 | 悲伤、愤怒、恐惧、焦虑、孤独、失落、沮丧、烦躁 |
| 中性情绪 | 平静、思考、好奇、惊讶、困惑、观望 |
| 复合情绪 | 矛盾、释然、苦笑、欣慰、怀念 |

### 真人出镜判断 (on_screen_presence)

用于判断视频中是否有真人出镜，以及角色的露出程度。

| 字段 | 说明 |
|------|------|
| has_real_person | 是否有真人出镜（true/false） |
| person_count | 出镜人数 |
| person_details | 每个人物的详细信息 |
| exposure_level | 角色露出程度：高（>70%）、中（30%-70%）、低（<30%） |
| exposure_description | 露出程度详细描述 |

**露出程度判断标准：**

| 级别 | 占比 | 说明 |
|------|------|------|
| **高** | >70% | 人物在大部分镜头中出现，且露出面积较大（半身或全身） |
| **中** | 30%-70% | 人物在部分镜头中出现，或露出面积适中 |
| **低** | <30% | 人物仅偶尔出现，或露出面积很小（如手部特写、背影等） |

### 服饰植入推荐 (fashion_placement)

仅当 `on_screen_presence.has_real_person = true` 时输出。根据视频场景、人物气质、画面风格，推荐适合植入的服饰风格。

| 字段 | 说明 |
|------|------|
| suitable | 是否适合服饰植入（true/false） |
| reason | 适合/不适合的原因 |
| recommended_styles | 推荐服饰风格列表（2-4种），按匹配度排序 |
| placement_notes | 植入方式建议 |

**recommended_styles 每项字段：**

| 字段 | 说明 |
|------|------|
| style | 服饰风格名称 |
| fit_score | 匹配度评分（0-1），综合场景、气质、色调、受众计算 |
| reason | 推荐该风格的理由 |
| recommended_items | 推荐的具体单品列表（3-4件） |

**匹配度评分维度：**

| 维度 | 权重 | 判断依据 |
|------|------|----------|
| 场景匹配 | 30% | 视频场景与服饰风格的适配度（如：居家→慵懒风，街头→潮牌） |
| 人物气质 | 30% | 出镜人物的外貌、年龄、气质与服饰受众是否一致 |
| 视觉色调 | 20% | 画面色彩与服饰风格色彩体系是否协调 |
| 受众重叠 | 20% | 视频目标受众与服饰目标消费群的重叠度 |

**常见服饰风格参考：**

| 风格 | 典型场景 | 典型单品 |
|------|----------|----------|
| 慵懒家居风 | 居家、沙发、窗边、阳台 | 宽松卫衣、针织开衫、棉裤、毛绒拖鞋 |
| 通勤职场风 | 办公室、地铁、写字楼 | 西装外套、衬衫、烟管裤、乐福鞋 |
| 文艺森系风 | 书店、咖啡馆、公园 | 棉麻衬衫、亚麻裙、帆布包、编织饰品 |
| 休闲街头风 | 街头、商场、聚会 | 潮牌T恤、工装裤、板鞋、棒球帽 |
| 优雅知性风 | 画廊、餐厅、高端场所 | 连衣裙、风衣、高跟鞋、手提包 |
| 运动活力风 | 健身房、跑步、户外 | 运动套装、瑜伽裤、跑鞋、运动手表 |
| 日系简约风 | 日常、校园、咖啡馆 | 基础款T恤、直筒裤、帆布鞋、托特包 |
| 国潮风格 | 街拍、活动现场 | 汉元素上衣、刺绣单品、国风配饰 |

### 主体分析 (subjects)

镜头内出现的人物和物体。

| 字段 | 说明 |
|------|------|
| subject_id | 镜头内主体编号（每个镜头内独立编号） |
| type | 主体类型：人物 / 物体 |
| person_id | **仅当 type 为「人物」时存在**。关联 `on_screen_presence.person_details[].person_id`，跨镜头追踪同一人物 |
| description | 主体外观描述（人物：性别、年龄段、外貌特征；物体：外观、材质等） |
| position | 主体在画面中的位置描述 |
| body_angle | 身体朝向（相对于镜头）：正面 / 3/4侧面 / 侧面 / 背面 |
| eye_line | 视线方向：看镜头 / 看向画面某侧 / 低头 / 闭眼 / 看向画面外 |
| action | 动作描述 |
| movement | 运动方式：静止 / 向左移入 / 从画外走入 / 原地微动 / 转身 等 |
| movement_speed | 运动速度：静止 / 缓慢 / 正常 / 快速 |
| expression | 表情描述（仅人物类型） |
| clothing | 服饰详情（含上装/下装/配饰/整体风格/颜色十六进制值，color_hex 含 top/bottom/accessories） |
| props | 手持道具列表 |

### 文字元素 (text_elements)

| 字段 | 说明 |
|------|------|
| type | 文字类型：字幕 / 标题 / 贴纸 |
| content | 文字内容 |
| position | 文字在画面中的位置 |
| style | 字体样式描述（字体、颜色、大小等） |
| animation | 入场动画：淡入 / 弹入 / 打字机 / 无 |

### 变速与特效 (speed_effects)

| 字段 | 说明 |
|------|------|
| playback_speed | 播放速度倍率（如 1.0x 正常、0.5x 慢动作） |
| speed_ramp.has_ramp | 是否有速度渐变效果 |
| speed_ramp.description | 渐变描述（如"正常→慢动作→正常"） |
| freeze_frame.has_freeze | 是否有定格帧 |
| freeze_frame.at_seconds | 定格帧发生的时间点（秒） |
| overlay.film_grain | 是否叠加胶片颗粒效果 |
| overlay.light_leak | 是否叠加漏光效果 |
| overlay.dust_particles | 是否叠加灰尘粒子效果 |
| overlay.color_filter | 色彩滤镜描述（如有） |
| overlay.other | 其他叠加效果描述 |

### 音频分析 (audio)

| 字段 | 说明 |
|------|------|
| dialogue | 台词信息：说话人、内容、语调。无台词时为 null |
| narration | 旁白信息：内容、语调。无旁白时为 null |
| music.presence | 是否有背景音乐（true/false） |
| music.style | 音乐风格描述（presence 为 false 时为 null） |
| music.mood | 音乐情绪（presence 为 false 时为 null） |
| music.tempo | 节奏快慢：慢速 / 中速 / 快速（presence 为 false 时为 null） |
| sound_effects | 音效列表，每项含 type（类型）、description（描述）、sync_point（与画面的同步点） |
| music_beat_sync.cuts_on_beat | 剪辑点是否踩在音乐节拍上 |
| music_beat_sync.description | 节拍同步关系的文字描述 |

### 场景分析 (scene)

| 字段 | 说明 |
|------|------|
| location_type | 场景类型：室内 / 室外 |
| specific_location | 具体场景名称（如"家中窗边角落"、"城市天台"） |
| environment | 环境整体描述（氛围、光线、空间感） |
| set_dressing | 场景布置细节（道具摆放、装饰元素、陈设风格） |

### 构图分析 (composition)

| 字段 | 说明 |
|------|------|
| framing_rule | 构图法则（见构图法则表） |
| subject_position | 主体在画面中的精确位置描述 |
| subject_scale | 主体占画面面积比（约1/4、1/3、1/2、2/3） |
| facing_direction | 人物在画面中的朝向：左 / 右 / 正面 / 背面（与 body_angle 不同，此处描述画面中的视觉方向） |
| headroom | 头空间：充裕 / 适中 / 裁切 |
| lead_room | 引导空间：运动方向前的留白（方向+空间大小） |
| depth | 景深层次描述（前景/中景/背景的虚实关系） |
| background | 背景元素描述 |
| frame_within_frame | 框架内框架（门窗/镜子等二次构图元素），无则为 null |

### 光线分析 (lighting)

| 字段 | 说明 |
|------|------|
| type | 光源类型：自然光 / 人工光 / 混合 |
| direction | 光线方向：正面光 / 侧面光 / 逆光 / 顶光 / 底光 |
| color_temperature | 色温（数值如 3200K 或描述如"暖色调"） |
| mood | 光线氛围描述 |
| shadow | 阴影类型：硬阴影 / 柔阴影 / 无阴影 |

### 色彩分析 (color)

| 字段 | 说明 |
|------|------|
| dominant_colors | 主色调名称列表（2-4个） |
| dominant_color_hex | 主色调十六进制色值列表，与 dominant_colors 一一对应 |
| color_mood | 色彩情绪描述 |
| color_grade | 调色风格描述 |
| contrast | 对比度：高 / 中 / 低 |
| saturation | 饱和度：高 / 中 / 低 / 去饱和 |
| grain | 胶片颗粒感：无 / 轻微 / 明显 / 重度 |

---

## 执行步骤

### 步骤1：执行分析

1. 将视频传给多模态模型
2. 模型同时分析画面和音频
3. 一次性获取完整的分镜信息

### 步骤2：整合分析结果

1. 提炼视频主题和概要
2. 分析情绪基调和变化
3. 判断视频类型和风格
4. 整理镜头分割和转场信息

### 步骤3：生成JSON输出

按照 JSON 结构填充分析结果。

---

## 示例输出

```json
{
  "video_analysis": {
    "title": "独居治愈日常",
    "theme": "独居生活的治愈瞬间",
    "summary": "一位女生在周末午后独自在家享受宁静时光，通过看书、喝咖啡、看窗外等日常细节，传递独居生活的美好与治愈。",
    "emotion": {
      "primary": "治愈",
      "secondary": ["温暖", "平静", "满足"],
      "emotion_arc": "平静 → 沉浸 → 满足，情绪逐渐升温但整体保持柔和"
    },
    "video_type": "情感治愈",
    "video_style": "日系清新",
    "target_audience": "20-30岁独居女性，追求生活品质的年轻人",
    "key_elements": ["阳光", "书籍", "咖啡", "窗边", "慵懒穿搭"],

    "on_screen_presence": {
      "has_real_person": true,
      "person_count": 1,
      "person_details": [
        {
          "person_id": 1,
          "description": "年轻女性，约25岁，气质温柔文艺，穿着米色慵懒风卫衣",
          "screen_time_ratio": 0.95,
          "appearance_notes": "几乎全程出镜，主要展示半身和全身，表情清晰可见"
        }
      ],
      "exposure_level": "高",
      "exposure_description": "人物正面露出占视频95%以上，主要展示半身和全身穿搭，面部表情清晰可见，适合服饰种草和人物形象展示"
    },

    "fashion_placement": {
      "suitable": true,
      "reason": "人物全程出镜，半身和全身展示空间充足，穿搭自然融入居家场景",
      "recommended_styles": [
        {
          "style": "慵懒家居风",
          "fit_score": 0.95,
          "reason": "视频为居家场景，氛围温馨治愈，与慵懒家居风高度契合",
          "recommended_items": ["宽松卫衣", "针织开衫", "棉质休闲裤", "毛绒拖鞋"]
        },
        {
          "style": "文艺森系风",
          "fit_score": 0.85,
          "reason": "人物气质温柔文艺，窗边/书/绿植等元素与森系风格自然搭配",
          "recommended_items": ["棉麻衬衫", "亚麻长裙", "帆布包", "编织手链"]
        },
        {
          "style": "日系简约风",
          "fit_score": 0.80,
          "reason": "画面日系低对比度调色，暖白色调，适合基础款简约穿搭植入",
          "recommended_items": ["基础款长袖T恤", "直筒休闲裤", "帆布鞋", "素色托特包"]
        }
      ],
      "placement_notes": "建议植入方式：服饰作为日常居家穿搭自然出现，避免特写镜头，保持治愈叙事为主"
    }
  },

  "shot_breakdown": [
    {
      "shot_id": 1,
      "timecode": {
        "start": "00:00:00",
        "end": "00:00:04",
        "duration_seconds": 4.0
      },
      "shot_type": "中景",
      "camera_movement": "固定镜头",
      "transition_in": {
        "type": "淡入",
        "duration_seconds": 0.5,
        "color": "黑"
      },
      "transition_out": {
        "type": "硬切",
        "duration_seconds": 0,
        "color": null
      },

      "camera_details": {
        "focal_length": "35mm",
        "focus": {
          "subject": "人物面部和书本",
          "depth_of_field": "中",
          "bokeh_quality": "柔滑"
        },
        "focus_pull": {
          "has_pull": false,
          "from": null,
          "to": null,
          "timing": null
        },
        "stabilization": "三脚架",
        "camera_height": "平视",
        "camera_angle": "斜侧45°",
        "lens_effect": {
          "vignette": "轻微",
          "flare": "无",
          "distortion": "无",
          "breathing": "无",
          "leak": "无"
        }
      },

      "visual": {
        "scene": {
          "location_type": "室内",
          "specific_location": "家中窗边角落",
          "environment": "阳光透过白色纱帘洒入，窗边有绿植和软垫，整体温馨",
          "set_dressing": "窗台上一盆绿萝，旁边散落两本精装书，软垫是亚麻材质米白色"
        },
        "composition": {
          "framing_rule": "三分法",
          "subject_position": "画面右侧三分线，纵向下三分之一处",
          "subject_scale": "约1/2",
          "facing_direction": "朝左",
          "headroom": "适中",
          "lead_room": "左侧留白约1/3画面",
          "depth": "前景有窗框虚化边缘，中景人物清晰，背景虚化的室内空间",
          "background": "米白色墙面、绿植、木质家具",
          "frame_within_frame": "窗框自然形成二次构图，人物在窗框内偏右"
        },
        "lighting": {
          "type": "自然光",
          "direction": "左侧逆光",
          "color_temperature": "暖色调（约3500K）",
          "mood": "柔和温暖，有圆形光斑",
          "shadow": "柔阴影，窗框在地面投射淡影"
        },
        "color": {
          "dominant_colors": ["米白色", "浅棕色", "淡绿色"],
          "dominant_color_hex": ["#F5F0E8", "#D4C5A9", "#A8C5A0"],
          "color_mood": "温暖治愈",
          "color_grade": "日系胶片感，低对比度",
          "contrast": "低",
          "saturation": "中",
          "grain": "轻微"
        }
      },

      "subjects": [
        {
          "subject_id": 1,
          "type": "人物",
          "person_id": 1,
          "description": "年轻女性，约25岁，气质温柔文艺",
          "position": "蜷坐在窗边软垫上",
          "body_angle": "3/4侧面",
          "eye_line": "低头看向大腿上的书本",
          "action": "专注看书，偶尔翻页",
          "movement": "原地微动（翻页时身体轻微起伏）",
          "movement_speed": "缓慢",
          "expression": "平静专注，嘴角微微上扬",
          "clothing": {
            "top": "米色慵懒风卫衣，宽松版型，棉质",
            "bottom": "灰色休闲裤，针织材质",
            "accessories": "无",
            "overall_style": "慵懒家居风",
            "color_hex": {
              "top": "#D4C5A9",
              "bottom": "#A0A0A0",
              "accessories": null
            }
          },
          "props": ["精装书籍（米白封面）"]
        }
      ],

      "text_elements": [],

      "speed_effects": {
        "playback_speed": 1.0,
        "speed_ramp": {
          "has_ramp": false,
          "description": null
        },
        "freeze_frame": {
          "has_freeze": false,
          "at_seconds": null
        },
        "overlay": {
          "film_grain": true,
          "light_leak": false,
          "dust_particles": false,
          "color_filter": null,
          "other": null
        }
      },

      "audio": {
        "dialogue": null,
        "narration": null,
        "music": {
          "presence": true,
          "style": "轻音乐/钢琴",
          "mood": "治愈温暖",
          "tempo": "慢速"
        },
        "sound_effects": [
          {
            "type": "环境音",
            "description": "窗外轻微鸟鸣",
            "sync_point": null
          },
          {
            "type": "动作音",
            "description": "书页翻动声",
            "sync_point": "约第3秒，与画面翻页动作同步"
          }
        ],
        "music_beat_sync": {
          "cuts_on_beat": false,
          "description": "舒缓节奏，剪辑点不在节拍上，以情绪连贯为主"
        }
      },

      "shot_description": "女生蜷坐在洒满阳光的窗边，专注地看书，米色卫衣与温暖的光线融为一体"
    },
    {
      "shot_id": 2,
      "timecode": {
        "start": "00:00:04",
        "end": "00:00:08",
        "duration_seconds": 4.0
      },
      "shot_type": "近景",
      "camera_movement": "推镜头",
      "transition_in": {
        "type": "硬切",
        "duration_seconds": 0,
        "color": null
      },
      "transition_out": {
        "type": "硬切",
        "duration_seconds": 0,
        "color": null
      },

      "camera_details": {
        "focal_length": "50mm",
        "focus": {
          "subject": "人物面部",
          "depth_of_field": "浅",
          "bokeh_quality": "柔滑"
        },
        "focus_pull": {
          "has_pull": true,
          "from": "书本",
          "to": "人物面部",
          "timing": "镜头开始时焦点在书本，约1秒后焦点转移至面部"
        },
        "stabilization": "稳定器",
        "camera_height": "平视",
        "camera_angle": "斜侧45°",
        "lens_effect": {
          "vignette": "轻微",
          "flare": "轻微（左上角逆光光晕）",
          "distortion": "无",
          "breathing": "无",
          "leak": "无"
        }
      },

      "visual": {
        "scene": {
          "location_type": "室内",
          "specific_location": "窗边（同镜头1，机位靠近）",
          "environment": "与镜头1相同位置，景别收窄至人物上半身",
          "set_dressing": "同镜头1"
        },
        "composition": {
          "framing_rule": "居中",
          "subject_position": "画面中央",
          "subject_scale": "约2/3",
          "facing_direction": "朝左",
          "headroom": "适中",
          "lead_room": "左侧留白约1/4画面",
          "depth": "浅景深，背景完全虚化为光斑",
          "background": "虚化的窗户和金色光线",
          "frame_within_frame": null
        },
        "lighting": {
          "type": "自然光",
          "direction": "左侧逆光",
          "color_temperature": "暖色调（约3200K）",
          "mood": "光影斑驳，温暖柔和",
          "shadow": "无明确阴影，逆光漫射"
        },
        "color": {
          "dominant_colors": ["金色", "米白色"],
          "dominant_color_hex": ["#E8D5A3", "#F5F0E8"],
          "color_mood": "温暖梦幻",
          "color_grade": "日系胶片感",
          "contrast": "低",
          "saturation": "中",
          "grain": "轻微"
        }
      },

      "subjects": [
        {
          "subject_id": 1,
          "type": "人物",
          "person_id": 1,
          "description": "年轻女性面部近景",
          "position": "画面中央",
          "body_angle": "3/4侧面",
          "eye_line": "闭眼感受阳光，随后缓缓睁开看向画面外",
          "action": "从看书到抬头感受阳光",
          "movement": "缓慢抬头",
          "movement_speed": "缓慢",
          "expression": "闭眼享受，嘴角浅笑",
          "clothing": {
            "top": "米色慵懒风卫衣，宽松版型，棉质（同镜头1）",
            "bottom": "不在此景别中",
            "accessories": "无",
            "overall_style": "慵懒家居风",
            "color_hex": {
              "top": "#D4C5A9",
              "bottom": null,
              "accessories": null
            }
          },
          "props": []
        }
      ],

      "text_elements": [],

      "speed_effects": {
        "playback_speed": 1.0,
        "speed_ramp": {
          "has_ramp": false,
          "description": null
        },
        "freeze_frame": {
          "has_freeze": false,
          "at_seconds": null
        },
        "overlay": {
          "film_grain": true,
          "light_leak": false,
          "dust_particles": false,
          "color_filter": null,
          "other": null
        }
      },

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
        },
        "sound_effects": [],
        "music_beat_sync": {
          "cuts_on_beat": false,
          "description": "舒缓节奏，剪辑点不在节拍上"
        }
      },

      "shot_description": "阳光洒在女生脸上，她闭上眼睛感受温暖，米色卫衣在逆光中泛着柔和光晕"
    }
  ],

  "editing_analysis": {
    "total_shots": 2,
    "average_shot_duration": 4.0,
    "longest_shot_seconds": 4.0,
    "shortest_shot_seconds": 4.0,
    "editing_rhythm": "舒缓平稳，与治愈情绪匹配",
    "pacing": "慢",
    "cut_style": "无缝衔接，注重情绪连贯"
  }
}
```

---

## 注意事项

1. **分析方式**：采用直接视频分析，完整捕捉运镜、转场、动作连续性和音频
2. **视频质量**：视频清晰度越高，分析结果越准确
3. **隐私保护**：用户上传的视频仅用于分析，不会被存储或用于其他用途
4. **分析准确性**：AI分析可能存在误差，关键信息建议人工复核

---

## 错误处理

| 错误情况 | 处理方式 |
|----------|----------|
| 视频文件损坏 | 提示用户检查文件完整性 |
| 视频过大无法处理 | 提示用户裁剪视频后重新上传 |
