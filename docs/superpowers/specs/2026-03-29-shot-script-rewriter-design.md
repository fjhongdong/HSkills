# shot-script-rewriter 设计规格

## 概述

创建新 Skill `shot-script-rewriter`，接收 `video-shot-breakdown` 的输出 JSON 和用户文字描述的角色形象，对分镜脚本进行最小化改写——仅替换角色直接相关内容，尽可能保留原脚本的故事线、情绪氛围和技术参数。

## 基本信息

- **名称：** `shot-script-rewriter`
- **触发关键词：** "改写分镜"、"换角色"、"角色替换"、"复刻脚本"、"替换人物"、"改写分镜脚本"、"角色改编"
- **与 video-shot-breakdown 的区分：** 当用户已提供 video-shot-breakdown 的输出 JSON 时触发本 Skill；如果用户只上传视频还未拆解，先触发 video-shot-breakdown
- **输入：**
  - video-shot-breakdown 的完整 JSON 输出（必需）
  - 用户文字描述的角色形象（必需）
- **输出：** 与 video-shot-breakdown 完全相同的 JSON 格式
- **定位：** 独立 Skill，不挂载到协调器流程

## 改写规则

最小干预原则，三级改写策略：

### 一级：必改（角色直接相关）

- `subjects[].description` — 替换为新角色描述
- `subjects[].clothing` — 全部替换为新角色穿搭
- `subjects[].expression` — 根据新角色气质调整表情

### 二级：适配改（与新角色冲突时才改）

- `subjects[].action` — 原动作与新角色不匹配时调整（如"霸气踢门"换甜美风角色→"轻推开门"）
- `shot_description` — 镜头概述中引用原角色特征时调整
- `audio.dialogue.content` — 台词语气与角色性格冲突时调整语调
- `audio.dialogue.tone` — 替换说话语气
- `audio.narration` — 旁白风格与角色不匹配时调整

### 三级：不动

- `shot_breakdown` 的镜头数量和顺序
- `timecode` 所有时间码
- `shot_type`、`camera_movement`、`transition` 等技术参数
- `visual.scene` 场景环境（除非场景与新角色严重冲突）
- `visual.lighting`、`visual.color` 光线和色彩
- `video_analysis.emotion` 情绪基调
- `editing_analysis` 剪辑节奏
- `on_screen_presence` 中的人物数量

### 判断标准

只改"看了会出戏"的内容。如果原内容和新角色放在一起没有违和感，就不改。

## 执行流程

### 步骤1：解析原 JSON

- 提取 video_analysis 和 shot_breakdown
- 建立角色字段清单（每镜哪些字段涉及人物）

### 步骤2：提炼新角色画像

- 从文字描述中提取：性别、年龄段、气质、性格特征、穿搭风格
- 形成内部角色特征卡片（不输出，仅内部使用）

### 步骤3：逐镜头对比改写

- 对每个 shot 执行三级改写策略
- 一级字段直接替换
- 二级字段判断是否冲突，冲突则适配改写
- 三级字段跳过

### 步骤4：更新全局字段

- `video_analysis.on_screen_presence.person_details` → 替换为新角色描述
- `video_analysis.summary` → 仅当概要中提到原角色时微调
- `video_analysis.key_elements` → 仅替换其中与角色直接相关的元素（如"慵懒穿搭"→"街头酷飒"），保留场景/道具类元素
- 其他 video_analysis 字段不动

### 步骤5：输出完整 JSON

- 格式与输入完全一致
- 不增不减字段

## 多人物与边界情况

### 多人物处理

- 原视频中 `person_count > 1` 时，用户提供的角色描述替换**主要人物**（`screen_time_ratio` 最高的人）
- 次要人物保持不变
- 如果用户需要替换多个角色，应提供多段描述（按重要性排序），Skill 依次匹配

### 无人物视频

- 原视频 `has_real_person: false` 且无 `subjects[].type: "人物"` → 提示用户该视频无人物出镜，无法进行角色替换改写
- 原视频有物体类 subjects（`type: "物体"`）→ 跳过，不替换

### null 值字段

- 原始 JSON 中为 `null` 的字段（如 `audio.dialogue: null`）改写后**保持 null**，不凭空创建内容

## 错误处理

| 错误情况 | 处理方式 |
|----------|----------|
| 输入 JSON 格式错误 | 提示用户检查 JSON 格式，提供具体解析错误位置 |
| JSON 不符合 video-shot-breakdown 格式 | 提示用户确认 JSON 来源，列出缺失的必需字段 |
| 角色描述过短（少于10字） | 提示用户补充更多角色特征（性别、年龄段、气质风格等） |
| 原视频无人物出镜 | 提示无法进行角色替换改写 |

## 输入规范

### JSON 输入

必须包含 video-shot-breakdown 输出的完整结构，至少包含 `video_info`、`video_analysis`、`shot_breakdown` 三个顶层字段。

### 角色描述建议格式

用户可自由组织文字，建议包含以下维度（缺省项由 Skill 根据已有信息推断）：

- **性别**：男/女
- **年龄段**：如 20-25岁
- **气质**：如 温柔、酷飒、活泼、知性
- **穿搭风格**：如 街头潮流、日系清新、韩系精致
- **性格特征**：如 内向安静、外向开朗
- **外貌特征**（可选）：如 长发、戴眼镜

## 文件结构

```
shot-script-rewriter/
└── SKILL.md          # Skill 定义，包含完整改写规则和执行流程
```

无辅助脚本，改写过程由 AI 直接完成。

## SKILL.md 文档结构

1. **Frontmatter** — name + description（含触发关键词）
2. **核心能力** — 一句话定位 + 输入输出说明
3. **改写规则** — 三级策略详细说明 + 判断标准
4. **执行流程** — 五步流程
5. **输入规范** — JSON 输入要求 + 角色描述建议格式
6. **注意事项** — 最小干预原则、格式兼容性、质量检查
7. **示例** — 一组改写前后对比（展示一个镜头改了什么、没改什么）

## 设计决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 实现方案 | 单阶段直接改写（非两阶段） | 定位是"快速换角色复刻"，用户不需要逐步确认 |
| 角色输入方式 | 仅文字描述 | 用户明确选择文字输入，降低输入门槛 |
| 输出格式 | 与输入完全相同的 JSON | 保持下游工具兼容性，零适配成本 |
| 改写范围 | 最小干预，三级策略 | 尽可能保留原脚本精髓，只改角色相关 |
| 独立性 | 独立 Skill，非子技能 | 使用场景明确，无需挂载到协调器 |

## CLAUDE.md 更新

实现时需更新 CLAUDE.md 中的 `Skill 分类` 表，将 `shot-script-rewriter` 归入"短视频创作"分类，排在 `video-shot-breakdown` 之后。

## 改写前后对比示例

**用户角色描述：** "22岁男生，酷飒街头风，穿着黑色oversized卫衣和工装裤，性格外向开朗"

**原始镜头（video-shot-breakdown 输出片段）：**

```json
{
  "shot_id": 1,
  "subjects": [{
    "description": "年轻女性，约25岁，气质温柔文艺",
    "action": "蜷坐在窗边软垫上",
    "expression": "平静专注，嘴角微微上扬",
    "clothing": {
      "top": "米色慵懒风卫衣，宽松版型",
      "bottom": "灰色休闲裤",
      "overall_style": "慵懒家居风"
    }
  }],
  "shot_description": "女生蜷坐在洒满阳光的窗边，专注地看书，米色卫衣与温暖的光线融为一体",
  "audio": {
    "dialogue": null,
    "narration": { "content": "这样的午后，只属于我", "tone": "温柔内心独白" }
  }
}
```

**改写后：**

```json
{
  "shot_id": 1,
  "subjects": [{
    "description": "22岁男生，酷飒街头风，性格外向开朗",
    "action": "靠坐在窗边，一只脚搭在窗台上",
    "expression": "嘴角带笑，眼神明亮放松",
    "clothing": {
      "top": "黑色oversized卫衣",
      "bottom": "卡其色工装裤",
      "overall_style": "街头酷飒风"
    }
  }],
  "shot_description": "男生靠坐在洒满阳光的窗边，黑色卫衣与温暖光线形成鲜明对比",
  "audio": {
    "dialogue": null,
    "narration": { "content": "这样的午后，只属于我", "tone": "随性内心独白" }
  }
}
```

**改动清单：**
- 一级：description、clothing、expression 全部替换
- 二级：action 调整（"蜷坐"→"靠坐"，匹配男生体态）、shot_description 重写（去掉"米色卫衣"、去掉"看书"）、narration.tone 微调（"温柔"→"随性"）
- 三级：shot_id、timecode、visual、dialogue=null 不变
