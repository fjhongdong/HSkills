# 角色/场景一致性控制指南

## 目录

1. [一致性挑战与原理](#一致性挑战与原理)
2. [角色一致性控制](#角色一致性控制)
3. [场景一致性控制](#场景一致性控制)
4. [光线一致性控制](#光线一致性控制)
5. [实操工作流程](#实操工作流程)
6. [质量检查清单](#质量检查清单)

---

## 一致性挑战与原理

### 为什么一致性困难

AI视频生成每一帧都是独立生成的，没有"记忆"：
- 角色外貌可能逐帧变化
- 场景元素位置可能漂移
- 光线方向可能不统一
- 服装细节可能改变

### 一致性控制原理

通过以下方式引导AI保持一致：
1. **种子词锁定**：使用固定的角色/场景描述作为锚点
2. **参考图控制**：提供参考图像
3. **特征强调**：重复强调关键特征
4. **排除变化**：明确排除不希望的变化

---

## 角色一致性控制

### 角色种子词模板

```
[CHARACTER:角色标识符] [年龄性别], [体型], [发型发色],
[标志性特征], [服装风格],
consistent appearance, same person, maintaining identity
```

### 示例

```
[CHARACTER:SARAH] 28 year old Asian female, slim build,
long black wavy hair with side part, large almond eyes,
beauty mark near left eye, dimples when smiling,
wearing white blazer and black trousers,
consistent appearance, same person, maintaining identity
```

### 关键特征优先级

按重要性排序，确保核心特征始终出现：

1. **最高优先级**（必须每帧出现）
   - 性别、年龄范围
   - 发型发色
   - 最明显的面部特征

2. **高优先级**（应该一致）
   - 体型
   - 肤色
   - 服装主体

3. **中优先级**（尽量一致）
   - 配饰
   - 细节特征
   - 表情基调

### 多镜头角色控制策略

**策略1：种子词前缀**
```
每个包含该角色的镜头提示词开头都加上：
[CHARACTER:SARAH] consistent with previous shots,
```

**策略2：参考图锚定**
```
如果平台支持参考图：
1. 先生成一张高质量的角色定妆照
2. 所有后续镜头都引用这张参考图
```

**策略3：特征重复强调**
```
在每个镜头中重复3-5个核心特征词：
long black wavy hair, almond eyes, beauty mark left eye
```

### 服装变化处理

当剧情需要换装时：

```
场景1-5的种子词：
[CHARACTER:SARAH] ... wearing white blazer outfit (COSTUME A)

场景6-10的种子词：
[CHARACTER:SARAH] ... wearing burgundy dress (COSTUME B),
same person as previous scenes, only outfit changed
```

---

## 场景一致性控制

### 场景种子词模板

```
[SCENE:场景标识符] [室内/室外] [地点类型],
[空间特征], [关键道具],
[光线条件], [色彩氛围],
consistent environment, maintaining location
```

### 示例

```
[SCENE:COFFEE_SHOP] interior modern coffee shop,
exposed brick wall on left, large windows on right,
wooden tables, hanging pendant lights, green plants,
warm morning light from windows, cozy earth tones,
consistent environment, maintaining location
```

### 空间元素锁定

确保以下元素保持一致：

| 元素 | 控制方法 |
|------|----------|
| 墙壁/背景 | 明确指定方位（左墙、右墙） |
| 窗户/门 | 固定位置描述 |
| 主要家具 | 列出并固定相对位置 |
| 装饰元素 | 选择2-3个标志性装饰 |

### 摄影角度与场景一致性

```
同一场景内的镜头，标注相对位置关系：

镜头1-1：[SCENE:COFFEE_SHOP] wide shot from entrance...
镜头1-2：[SCENE:COFFEE_SHOP] same location, now shooting from counter...
镜头1-3：[SCENE:COFFEE_SHOP] same location, reverse angle...
```

---

## 光线一致性控制

### 光线种子词模板

```
[LIGHTING:场景光线ID] [光源类型] lighting,
[光线方向] from [方位],
[色温] tones, [强度] intensity,
consistent lighting throughout scene
```

### 示例

```
[LIGHTING:COFFEE_MORNING] mixed natural and artificial lighting,
soft daylight from large windows on right side,
warm pendant lights overhead,
warm golden tones, medium soft intensity,
consistent lighting throughout scene
```

### 光线方向锁定

关键是保持光源方向一致：

```
错误示例（光线跳变）：
镜头1: light from left
镜头2: light from right  ❌

正确示例：
镜头1: key light from left window, 45 degrees
镜头2: same lighting setup, key light from left  ✓
```

### 时间段光线参考

| 时间段 | 光线描述 |
|--------|----------|
| 早晨 | morning soft light, warm, low angle sun from east |
| 正午 | midday bright light, neutral, overhead sun |
| 下午 | afternoon warm light, golden, sun from west |
| 黄昏 | golden hour, orange warm glow, long shadows |
| 夜晚 | artificial lighting, [specify sources], cool or warm |

---

## 实操工作流程

### 第一步：建立一致性档案

在开始生成前，为每个角色和场景创建档案：

```yaml
# 角色档案
character_profiles:
  - id: SARAH
    seed_prompt: "28yo Asian female, slim, long black wavy hair..."
    key_features: ["black wavy hair", "almond eyes", "beauty mark"]
    costumes:
      - scenes: 1-5
        description: "white blazer, black trousers"
      - scenes: 6-10
        description: "burgundy wrap dress"

# 场景档案
scene_profiles:
  - id: COFFEE_SHOP
    seed_prompt: "modern coffee shop, brick wall, large windows..."
    key_elements: ["exposed brick", "pendant lights", "wooden tables"]
    lighting: "warm morning light from windows"

  - id: STREET_NIGHT
    seed_prompt: "city street at night, wet pavement..."
    key_elements: ["neon signs", "street lights", "reflections"]
    lighting: "neon and street lamp mix, cold with warm accents"
```

### 第二步：生成关键帧

1. 先为每个角色生成"定妆照"作为参考
2. 为每个场景生成"空镜头"作为场景参考
3. 确认满意后再批量生成

### 第三步：镜头生成顺序

推荐按角色分组生成，而非按场景顺序：

```
先生成所有 SARAH 单独出镜的镜头
→ 检查一致性
→ 再生成 SARAH + JOHN 的镜头
→ 检查一致性
→ 最后生成群戏镜头
```

### 第四步：质量检查与修正

生成后检查：
- 角色是否可识别为同一人
- 场景元素位置是否一致
- 光线方向是否统一
- 服装是否正确

如有问题，调整种子词后重新生成该镜头。

---

## 质量检查清单

### 角色一致性检查

- [ ] 发型发色是否一致
- [ ] 面部特征是否可识别
- [ ] 体型比例是否一致
- [ ] 服装是否符合当前场景设定
- [ ] 标志性特征是否保留（痣、疤痕等）

### 场景一致性检查

- [ ] 背景元素位置是否一致
- [ ] 关键道具是否存在
- [ ] 空间比例是否合理
- [ ] 窗户/门的位置是否一致
- [ ] 装饰元素是否一致

### 光线一致性检查

- [ ] 光源方向是否一致
- [ ] 阴影方向是否匹配光源
- [ ] 色温是否统一
- [ ] 亮度是否符合时间设定
- [ ] 人物与环境光线是否匹配

### 整体连贯性检查

- [ ] 前后镜头是否可以流畅衔接
- [ ] 动作是否连续（如有）
- [ ] 情绪氛围是否一致
- [ ] 是否有明显的跳变或错误

---

## 一致性问题排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 角色脸部变化 | 特征描述不够具体 | 增加更多面部细节词 |
| 发型改变 | 发型描述权重不够 | 将发型描述放在前面，加强调 |
| 服装颜色变化 | 颜色描述不精确 | 使用具体颜色词而非模糊描述 |
| 场景元素消失 | 关键元素未强调 | 在种子词中明确列出必须出现的元素 |
| 光线方向不一致 | 未指定光源方向 | 明确标注光源位置和方向 |
| 整体风格跳变 | 风格词不一致 | 统一使用相同的风格关键词组 |
