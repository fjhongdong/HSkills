# shot-script-rewriter 设计规格

## 概述

创建新 Skill `shot-script-rewriter`，接收 `video-shot-breakdown` 的输出 JSON 和用户文字描述的角色形象，对分镜脚本进行最小化改写——仅替换角色直接相关内容，尽可能保留原脚本的故事线、情绪氛围和技术参数。

## 基本信息

- **名称：** `shot-script-rewriter`
- **触发关键词：** "改写分镜"、"换角色"、"角色替换"、"复刻脚本"、"替换人物"、"改写分镜脚本"、"角色改编"
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
- 其他 video_analysis 字段不动

### 步骤5：输出完整 JSON

- 格式与输入完全一致
- 不增不减字段

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
