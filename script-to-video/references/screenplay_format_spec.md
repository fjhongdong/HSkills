# 剧本格式规范

## 目录

1. [标准编剧格式](#标准编剧格式)
2. [中文剧本格式](#中文剧本格式)
3. [Final Draft 兼容格式](#final-draft-兼容格式)
4. [元素识别规则](#元素识别规则)

---

## 标准编剧格式

### 场景标题 (Scene Heading / Slugline)

```
INT. COFFEE SHOP - DAY
EXT. CITY STREET - NIGHT
INT./EXT. CAR - CONTINUOUS
```

**格式规则**：
- 全大写
- 以 `INT.`（室内）或 `EXT.`（室外）开头
- 中间为地点名称
- 末尾为时间（DAY/NIGHT/DAWN/DUSK/CONTINUOUS）
- 用 ` - ` 分隔各部分

**时间选项**：
| 英文 | 含义 |
|------|------|
| DAY | 白天 |
| NIGHT | 夜晚 |
| DAWN | 黎明 |
| DUSK | 黄昏 |
| MORNING | 早晨 |
| AFTERNOON | 下午 |
| EVENING | 傍晚 |
| CONTINUOUS | 连续（紧接上场） |
| LATER | 稍后 |
| MOMENTS LATER | 片刻后 |

---

### 动作描述 (Action)

```
The COFFEE SHOP is bustling with morning customers.
SARAH (28, sharp-eyed, wearing a wrinkled blazer)
sits alone at a corner table, staring at her phone.
```

**格式规则**：
- 正常大小写
- 角色首次出场时名字大写
- 包含年龄、外貌等关键描述
- 简洁、视觉化的描写

---

### 角色名 (Character)

```
SARAH
JOHN (V.O.)
MARY (O.S.)
NARRATOR (CONT'D)
```

**格式规则**：
- 全大写
- 居中或左缩进 3.7 英寸
- 可添加扩展标记：
  - `(V.O.)` - Voice Over 画外音
  - `(O.S.)` - Off Screen 画外
  - `(CONT'D)` - Continued 续说
  - `(PRELAP)` - 声音先于画面

---

### 对白 (Dialogue)

```
SARAH
I've been waiting for two hours.
Where have you been?
```

**格式规则**：
- 紧跟角色名之后
- 左缩进 2.5 英寸，右边距 2.5 英寸
- 不使用引号

---

### 括号动作 (Parenthetical)

```
SARAH
(checking her watch)
I've been waiting for two hours.
(standing up)
Where have you been?
```

**格式规则**：
- 位于角色名和对白之间，或对白中间
- 小写，用括号包围
- 简短的动作或情绪提示

---

### 转场 (Transition)

```
CUT TO:
FADE OUT.
DISSOLVE TO:
SMASH CUT TO:
MATCH CUT TO:
```

**格式规则**：
- 全大写
- 右对齐
- 以冒号或句号结尾

---

## 中文剧本格式

### 场景标题

```
场景1：咖啡厅内 - 白天
第一场：办公室 - 夜晚
内景：卧室 - 清晨
外景：街道 - 黄昏
```

**识别模式**：
- `场景X：` 或 `第X场：`
- `内景：` 或 `外景：`
- 时间通常在末尾

### 角色与对白

```
【张伟】
（看着手机，皱眉）
你到底在哪？我等了两个小时了。

李娜：（推门进入）抱歉，路上堵车。
```

**常见格式**：
- 【角色名】+ 对白
- 角色名：+ 对白
- 角色名（动作）对白

### 动作描述

```
张伟坐在角落的位置，桌上放着一杯已经凉了的咖啡。
他不停地看向门口，表情焦虑。
```

---

## Final Draft 兼容格式

### FDX 文件结构

Final Draft 使用 XML 格式的 `.fdx` 文件：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FinalDraft DocumentType="Script" Version="5">
  <Content>
    <Paragraph Type="Scene Heading">
      <Text>INT. COFFEE SHOP - DAY</Text>
    </Paragraph>
    <Paragraph Type="Action">
      <Text>SARAH sits at a corner table.</Text>
    </Paragraph>
    <Paragraph Type="Character">
      <Text>SARAH</Text>
    </Paragraph>
    <Paragraph Type="Dialogue">
      <Text>Where have you been?</Text>
    </Paragraph>
  </Content>
</FinalDraft>
```

### 段落类型 (Paragraph Type)

| Type | 说明 |
|------|------|
| Scene Heading | 场景标题 |
| Action | 动作描述 |
| Character | 角色名 |
| Dialogue | 对白 |
| Parenthetical | 括号动作 |
| Transition | 转场 |
| Shot | 镜头提示 |
| General | 通用文本 |

---

## 元素识别规则

### 正则表达式模式

**场景标题**：
```regex
^(INT\.|EXT\.|INT/EXT\.|I/E\.)\s*(.+?)(?:\s*[-–—]\s*(.+))?$
```

**中文场景标题**：
```regex
^(?:场景|第)\s*(\d+)\s*(?:场|幕)?[：:\s]*(.+)?$
```

**角色名**（英文）：
```regex
^([A-Z][A-Z\s]+)(?:\s*\(.*\))?$
```

**括号动作**：
```regex
^\s*\((.+)\)\s*$
```

**转场**：
```regex
^(FADE IN:|FADE OUT\.|CUT TO:|DISSOLVE TO:|SMASH CUT:|MATCH CUT:)
```

### 识别优先级

1. 检查是否为场景标题
2. 检查是否为转场
3. 检查是否为括号动作
4. 检查是否为角色名
5. 如果上一行是角色名，则为对白
6. 否则为动作描述

---

## 剧本分析输出格式

```json
{
  "title": "剧本标题",
  "metadata": {
    "scene_count": 10,
    "character_count": 5,
    "estimated_duration": 600
  },
  "scenes": [
    {
      "number": 1,
      "heading": "INT. COFFEE SHOP - DAY",
      "location": "COFFEE SHOP",
      "time_of_day": "DAY",
      "int_ext": "INT.",
      "characters": ["SARAH", "JOHN"],
      "estimated_duration": 45
    }
  ],
  "all_characters": ["SARAH", "JOHN", "MARY"],
  "all_locations": ["COFFEE SHOP", "STREET", "APARTMENT"]
}
```
