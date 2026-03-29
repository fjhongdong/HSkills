---
name: video-shot-breakdown-v2
description: 拆解短视频生成详细分镜脚本，用于一比一复刻爆款视频。长视频自动截取前2分钟后进行直接多模态分析。当用户上传视频并要求"分镜拆解"、"镜头分析"、"视频拆解"、"复刻视频"、"拆解分镜"、"分析视频结构"、"视频镜头拆解"时触发此技能。即使没有明确提及，只要用户提供了视频并询问分镜、镜头、复刻相关需求，也应触发此技能。
---

# 短视频分镜拆解器 V2

对用户上传的短视频进行深度分析，逐镜头拆解出最详细的分镜脚本，支持一比一复刻。**长视频自动截取前2分钟后分析，保留完整运镜/转场/音频信息。**

## 核心能力

- 支持**本地视频文件**和**URL链接**两种输入方式
- **长视频自动截取**：超过2分钟的视频自动截取前2分钟，再进行直接视频分析
- **直接视频分析优先**：所有场景都优先使用直接视频分析，完整捕捉运镜、转场、动作连续性、音频
- **关键帧分析降级**：仅在模型不支持视频输入或文件过大时作为降级方案
- 输出**JSON格式**分镜脚本，便于程序处理和二次开发
- 包含视频**主题、概要、情绪、类型、风格**等多维度分析
- 每个镜头提供**景别、运镜、画面、台词、音效、转场**等完整信息

---

## 分析流程

### 方案选择原则

| 视频情况 | 推荐方案 | 原因 |
|----------|----------|------|
| 时长 ≤ 2分钟 | **直接视频分析** | 完整捕捉运镜、转场、动作连续性、音频 |
| 时长 > 2分钟 | **截取前2分钟 → 直接视频分析** | 保留完整运镜/转场/音频信息，牺牲后半段内容 |
| 模型不支持视频 或 文件 >500MB | **关键帧分析（降级方案）** | 模型输入限制 |

**始终优先直接视频分析**，因为它能完整捕捉：
- 运镜方式（推/拉/摇/移/跟）
- 转场效果（硬切/淡入淡出/溶解等）
- 动作连续性和节奏
- 音频与画面的同步关系

---

### 方案一：直接视频分析（≤2分钟）

直接将视频传给多模态模型进行整体分析。

**优势：**
- 运镜判断准确（能观察镜头的推拉摇移过程）
- 转场检测精确（能直接看到画面切换效果）
- 动作连续完整（不断帧）
- 音画同步分析（台词、BGM、音效与画面对应）

**执行方式：**
1. 直接读取视频文件或URL
2. 将完整视频传给多模态模型
3. 模型一次性分析所有维度

**分析提示词模板：**
```
请分析这段短视频，逐镜头拆解出详细的分镜脚本。

需要识别的信息：
1. 视频整体：主题、概要、情绪、类型、风格
2. 每个镜头：时间码、景别、运镜方式、转场类型
3. 画面内容：场景、构图、光线、色彩、人物动作表情、服装道具
4. 音频内容：台词、旁白、背景音乐风格、音效
5. 剪辑节奏：镜头数量、平均时长、节奏快慢

请按照JSON格式输出完整的分镜脚本。
```

---

### 方案二：截取后直接分析（>2分钟）★核心方案

当视频超过2分钟时，**截取前2分钟**，再进行直接视频分析。

**为什么截取而非关键帧：**
- 关键帧分析会丢失运镜过程（只能推断，不够准确）
- 关键帧分析无法捕捉音频信息（台词、BGM、音效）
- 关键帧分析的转场检测对渐变转场（溶解/淡入淡出）效果差
- 截取后的视频仍然保留完整的运镜、转场、音频、动作连续性

**截取规则：**
- 固定截取前 **120秒（2分钟）**
- 使用 `-c copy` 避免重新编码，速度快且无损
- 截取后保留原始视频的帧率、分辨率、编码格式
- 截取后仍可能略短于120秒（取决于关键帧位置）

**ffmpeg 截取命令：**
```bash
ffmpeg -i input.mp4 -t 120 -c copy -y trimmed_output.mp4
```

**执行方式：**
1. 获取视频时长
2. 如果 > 120秒，用 ffmpeg 截取前120秒到临时文件
3. 将截取后的视频传给多模态模型
4. 模型分析截取后的视频（流程同方案一）
5. 在 JSON 输出中标注截取信息（`trimmed_info`）

---

### 方案三：关键帧分析（降级方案）

仅在以下情况使用：
- 模型不支持视频输入
- 文件超过 500MB
- ffmpeg 截取失败时的备选方案

详细说明同 V1，使用 `hybrid` 模式提取关键帧后传给模型分析图片序列。

**关键帧提取模式**

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `basic` | 按时间间隔均匀提取 | 视频节奏均匀、转场简单 |
| `scene` | 检测场景变化提取 | 转场明显的硬切视频 |
| `hybrid`（推荐） | 结合均匀间隔 + 场景变化，合并去重 | 所有场景，确保每个镜头都有代表帧 |

**关键帧提取策略**

| 视频时长 | 提取间隔 | 最大帧数 | 说明 |
|---------|---------|---------|------|
| < 15秒 | 每1秒1帧 | 15帧 | 短视频节奏快，需要密集采样 |
| 15-30秒 | 每1.5秒1帧 | 20帧 | 常见短视频时长 |
| 30-60秒 | 每2秒1帧 | 25帧 | 中等长度视频 |
| 60-120秒 | 每3秒1帧 | 30帧 | 较长视频 |
| > 120秒 | 每5秒1帧 | 40帧 | 长视频，需控制帧数 |

---

## 输出格式

### JSON结构定义

```json
{
  "video_info": {
    "file_path": "文件路径或URL",
    "duration": 30.0,
    "duration_formatted": "00:30",
    "width": 1080,
    "height": 1920,
    "resolution": "1080x1920",
    "aspect_ratio": "9:16",
    "fps": 30.0,
    "total_frames": 900,
    "rotation": 0,
    "file_size_bytes": 15728640,
    "file_size_mb": 15.0,

    "video": {
      "codec": "h264",
      "codec_long": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
      "profile": "High",
      "level": 4.0,
      "pixel_format": "yuv420p",
      "bit_depth": null,
      "color_space": "bt709",
      "color_primaries": "bt709",
      "color_transfer": "bt709",
      "bitrate_kbps": 4200
    },

    "audio": {
      "codec": "aac",
      "codec_long": "AAC (Advanced Audio Coding)",
      "sample_rate": 44100,
      "channels": 2,
      "channel_layout": "stereo",
      "bitrate_kbps": 128
    },

    "container": {
      "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
      "format_long_name": "QuickTime / MOV",
      "overall_bitrate_kbps": 4328
    },

    "trimmed_info": {
      "is_trimmed": false,
      "original_duration": null,
      "original_duration_formatted": null,
      "trimmed_duration": null,
      "trimmed_duration_formatted": null,
      "trim_note": null
    }
  },

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
      "person_count": 2,
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
        "end": "00:00:03",
        "duration_seconds": 3.0
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
        "stabilization": "三脚架/稳定器/手持/肩扛",
        "camera_height": "平视/微俯/俯拍/仰拍/鸟瞰/虫眼视角",
        "camera_angle": "正面/斜侧45°/侧面/斜侧135°/背面",
        "lens_effect": {
          "vignette": "无/轻微/明显",
          "flare": "无/轻微/明显",
          "distortion": "无/轻微/明显",
          "breathing": "无/轻微/明显"
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
          "framing_rule": "三分法/居中/对称/引导线/框架构图/对角线/黄金螺旋",
          "subject_position": "主体在画面中的精确位置",
          "subject_scale": "主体占画面面积比（约1/4、1/3、1/2、2/3）",
          "facing_direction": "朝向",
          "headroom": "充裕/适中/裁切",
          "lead_room": "运动方向前的留白（左/右/上/下，空间大小）",
          "depth": "景深描述",
          "background": "背景元素",
          "frame_within_frame": "框架内框架（门窗/镜子等二次构图元素）"
        },
        "lighting": {
          "type": "自然光/人工光/混合",
          "direction": "光线方向（正面/侧面/逆光/顶光/底光）",
          "color_temperature": "冷暖色调（数值如5500K或描述）",
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
          "description": "主体描述",
          "position": "画面位置",
          "body_angle": "正面/3/4侧面/侧面/背面",
          "eye_line": "看镜头/看向画面左侧/低头/闭眼/看向画面外",
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
              "bottom": "#808080"
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
          "style": "音乐风格",
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
    "total_shots": 8,
    "average_shot_duration": 3.5,
    "editing_rhythm": "剪辑节奏描述",
    "pacing": "快/中/慢",
    "cut_style": "剪辑风格"
  }
}
```

### video_info 子字段说明

#### video（视频流）

| 字段 | 说明 | 用途 |
|------|------|------|
| codec | 视频编码（h264/h265/vp9等） | 复刻时选择编码器 |
| codec_long | 编码全称 | 确认编码格式 |
| profile | 编码 profile（Baseline/Main/High） | 确认编码质量等级 |
| level | 编码 level | 确认兼容性要求 |
| pixel_format | 像素格式（yuv420p/yuv444p等） | 复刻时匹配色彩采样 |
| bit_depth | 位深（8/10/12） | HDR 视频需匹配 |
| color_space | 色彩空间（bt709/bt2020等） | 精确复刻色彩需要匹配 |
| color_primaries | 色域（bt709/bt2020等） | 判断 SDR/HDR |
| color_transfer | 传输特性（bt709/smpte2084等） | 判断是否为 HDR PQ/HLG |
| bitrate_kbps | 视频码率 | 复刻时控制文件大小和质量 |

#### audio（音频流）

| 字段 | 说明 | 用途 |
|------|------|------|
| codec | 音频编码（aac/opus/mp3等） | 复刻时选择音频编码器 |
| codec_long | 编码全称 | 确认编码格式 |
| sample_rate | 采样率（44100/48000等） | 音频质量匹配 |
| channels | 声道数 | 声道布局匹配 |
| channel_layout | 声道布局（stereo/mono/5.1等） | 空间音频匹配 |
| bitrate_kbps | 音频码率 | 音频质量匹配 |

#### container（容器）

| 字段 | 说明 | 用途 |
|------|------|------|
| format_name | 容器格式名 | 确认文件类型（mp4/mov/webm等） |
| format_long_name | 容器全称 | 确认封装格式 |
| overall_bitrate_kbps | 总码率 | 整体文件大小估算 |

### trimmed_info 字段说明

当视频未截取时（≤2分钟），所有字段为 `false`/`null`。

当视频已截取时（>2分钟），填充如下：

```json
"trimmed_info": {
  "is_trimmed": true,
  "original_duration": 300.0,
  "original_duration_formatted": "05:00",
  "trimmed_duration": 120.0,
  "trimmed_duration_formatted": "02:00",
  "trim_note": "原始视频 05:00，已截取前 02:00 进行分析"
}
```

| 字段 | 说明 |
|------|------|
| is_trimmed | 是否进行了截取 |
| original_duration | 原始视频时长（秒） |
| original_duration_formatted | 原始视频时长（格式化） |
| trimmed_duration | 截取后时长（秒） |
| trimmed_duration_formatted | 截取后时长（格式化） |
| trim_note | 截取说明 |

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
| 中性情绪 | 平静、思考、好奇、惊讶、困惑、期待 |
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

---

## 执行步骤

### 步骤1：获取视频信息

1. 获取视频基本信息（时长、文件大小、分辨率、帧率）
2. 判断视频是否需要截取

### 步骤2：截取（如需要）

**截取条件：** 时长 > 120秒

1. 使用 ffmpeg 截取前120秒：
   ```bash
   ffmpeg -i <原始视频> -t 120 -c copy -y <截取后视频>
   ```
2. 验证截取后的视频文件完整性和时长
3. 记录截取信息用于 JSON 输出

### 步骤3：执行分析

**优先直接视频分析：**
1. 将视频（或截取后的视频）传给多模态模型
2. 模型同时分析画面和音频
3. 一次性获取完整的分镜信息

**仅在模型不支持视频输入时降级到关键帧分析：**
1. 使用 `hybrid` 模式提取关键帧
2. 将关键帧序列传给多模态模型
3. 根据帧间差异推断运镜和转场

### 步骤4：整合分析结果

1. 提炼视频主题和概要
2. 分析情绪基调和变化
3. 判断视频类型和风格
4. 整理镜头分割和转场信息

### 步骤5：生成JSON输出

按照 JSON 结构填充分析结果。如果进行了截取，填充 `trimmed_info` 字段。

---

## 示例输出（截取场景）

```json
{
  "video_info": {
    "file_path": "/Users/xxx/Downloads/长视频.mp4",
    "duration": 120.0,
    "duration_formatted": "02:00",
    "width": 1080,
    "height": 1920,
    "resolution": "1080x1920",
    "aspect_ratio": "9:16",
    "fps": 30.0,
    "total_frames": 3600,
    "rotation": 0,
    "file_size_bytes": 31457280,
    "file_size_mb": 30.0,

    "video": {
      "codec": "h264",
      "codec_long": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
      "profile": "High",
      "level": 4.0,
      "pixel_format": "yuv420p",
      "bit_depth": null,
      "color_space": "bt709",
      "color_primaries": "bt709",
      "color_transfer": "bt709",
      "bitrate_kbps": 2000
    },

    "audio": {
      "codec": "aac",
      "codec_long": "AAC (Advanced Audio Coding)",
      "sample_rate": 44100,
      "channels": 2,
      "channel_layout": "stereo",
      "bitrate_kbps": 128
    },

    "container": {
      "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
      "format_long_name": "QuickTime / MOV",
      "overall_bitrate_kbps": 2128
    },

    "trimmed_info": {
      "is_trimmed": true,
      "original_duration": 300.0,
      "original_duration_formatted": "05:00",
      "trimmed_duration": 120.0,
      "trimmed_duration_formatted": "02:00",
      "trim_note": "原始视频 05:00，已截取前 02:00 进行分析"
    }
  },

  "video_analysis": {
    "title": "独居治愈日常",
    "theme": "独居生活的治愈瞬间",
    "summary": "一位女生在周末午后独自在家享受宁静时光，通过看书、喝咖啡、看窗外等日常细节，传递独居生活的美好与治愈。分析基于原始视频前2分钟内容。",
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
          "breathing": "无"
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
          "facing_direction": "侧脸朝左，低头看书",
          "headroom": "适中",
          "lead_room": "左侧留白约1/3画面",
          "depth": "前景有窗框虚化边缘，中景人物清晰，背景虚化的室内空间",
          "background": "米白色墙面、绿植、木质家具",
          "frame_within_frame": "窗框自然形成二次构图，人物在窗框内偏右"
        },
        "lighting": {
          "type": "自然光",
          "direction": "左侧逆光",
          "color_temperature": "暖色调（约5500K）",
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
              "bottom": "#A0A0A0"
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
    }
  ],

  "editing_analysis": {
    "total_shots": 8,
    "average_shot_duration": 4.5,
    "editing_rhythm": "舒缓平稳，与治愈情绪匹配",
    "pacing": "慢",
    "cut_style": "无缝衔接，注重情绪连贯"
  }
}
```

---

## 辅助脚本

### 视频截取

当视频超过2分钟时，使用 ffmpeg 截取前120秒：

```bash
# 基本截取（无损，不重新编码）
ffmpeg -i input.mp4 -t 120 -c copy -y trimmed.mp4

# 指定截取时长（如截取前60秒）
ffmpeg -i input.mp4 -t 60 -c copy -y trimmed.mp4
```

**说明：**
- `-t 120`：截取前120秒
- `-c copy`：直接复制音视频流，不重新编码，速度快且无损
- `-y`：覆盖已有文件

### 关键帧提取脚本（降级方案）

本技能提供关键帧提取脚本 `scripts/extract_frames.py`，仅在模型不支持视频输入时使用。

```bash
# 推荐方式：混合模式（默认）
python scripts/extract_frames.py video.mp4

# 混合模式 + 自适应阈值
python scripts/extract_frames.py video.mp4 --mode hybrid --adaptive

# 基础模式
python scripts/extract_frames.py video.mp4 --mode basic

# JSON 输出（含每帧时间码）
python scripts/extract_frames.py video.mp4 --output-json
```

---

## 注意事项

1. **截取策略**：超过2分钟的视频固定截取前2分钟，使用 `-c copy` 无损截取
2. **方案优先级**：直接视频分析 > 截取后直接分析 > 关键帧分析（降级）
3. **截取信息标注**：如果进行了截取，JSON 输出的 `trimmed_info` 必须如实填充
4. **分析精度**：
   - 直接视频分析（含截取后）：运镜、转场、动作、音频判断最准确
   - 关键帧分析（降级）：运镜和渐变转场判断可能不准确
5. **视频质量**：视频清晰度越高，分析结果越准确
6. **隐私保护**：用户上传的视频仅用于分析，不会被存储或用于其他用途
7. **分析准确性**：AI分析可能存在误差，关键信息建议人工复核
8. **截取后说明**：输出概要中应注明"分析基于原始视频前2分钟内容"

---

## 错误处理

| 错误情况 | 处理方式 |
|----------|----------|
| 视频文件损坏 | 提示用户检查文件完整性 |
| URL无法访问 | 提示用户检查链接有效性 |
| ffmpeg未安装 | 提供安装指引，建议使用浏览器方式作为备选 |
| 截取失败 | 尝试不使用 `-c copy` 重新编码截取；或回退到关键帧分析 |
| 截取后文件异常 | 验证截取文件的时长和完整性，失败则回退到关键帧分析 |
| 关键帧提取失败 | 尝试调整参数或使用浏览器截图方式 |
| 场景变化检测无结果 | 自动降低阈值重试，或切换到 basic/hybrid 模式 |
| 帧数超限截断 | 脚本输出截断警告，优先保留场景变化帧 |
