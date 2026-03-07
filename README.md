# HSkills

Claude Code 自用 Skills 集合，提供一系列专业技能扩展功能。

## 项目简介

HSkills 是一个 Claude Code Skills 仓库，包含多个自定义技能模块，用于扩展 Claude Code 的能力。每个 Skill 都是独立的功能单元，可通过自然语言触发，帮助用户完成特定领域的复杂任务。

## 包含的 Skills

### 1. script-to-video-prompts (短剧剧本转AI视频提示词生成器)

将短剧剧本文档智能拆解为可直接用于AI视频生成的完整提示词体系。

**触发词：**
- "剧本转视频提示词"
- "拆解剧本生成分镜"
- "短剧转AI视频"
- "批量生成分镜提示词"
- "剧本可视化"

**功能特性：**
- 支持多种剧本格式：Word/PDF/TXT/Markdown/Final Draft (.fdx)
- 智能解析场次、角色、对白、动作
- 自动生成角色设定提示词
- 自动生成场景设定提示词
- 逐镜头分镜提示词生成
- 跨镜头一致性校验
- 多格式导出（JSON/CSV/Markdown/Excel/HTML）

**目录结构：**
```
script-to-video-prompts/
├── SKILL.md                 # Skill 定义文件
├── scripts/                 # Python 自动化脚本
│   ├── parse_script.py      # 剧本解析器
│   ├── character_extractor.py   # 角色信息提取
│   ├── scene_analyzer.py    # 场景分析
│   ├── storyboard_generator.py  # 分镜生成
│   ├── consistency_checker.py   # 一致性校验
│   ├── export_utils.py      # 多格式导出
│   └── prompt_optimizer.py  # 提示词优化
├── references/              # 规范文档
│   ├── screenplay_format_spec.md   # 剧本格式规范
│   ├── character_template.md       # 角色设定模板
│   ├── scene_template.md           # 场景设定模板
│   ├── shot_terminology.md         # 景别/运镜术语
│   ├── mood_keywords_library.md    # 情绪氛围关键词库
│   ├── video_style_guide.md        # AI视频风格指南
│   ├── consistency_control.md      # 一致性控制指南
│   └── prompt_patterns.md          # 高效提示词模式库
└── assets/                  # 模板资源
    ├── storyboard_template.csv     # 分镜脚本模板
    ├── export_template.html        # 可视化导出模板
    ├── character_profile_template.json  # 角色档案模板
    └── prompt_cheatsheet.md        # 提示词速查表
```

**工作流程：**

```
剧本文档 → 剧本解析 → 角色提取 → 场景分析 → 分镜生成 → 一致性校验 → 导出
```

**输出内容：**

1. **项目元数据** - 片名、集数、总时长、场次数
2. **风格总设定** - 画面风格、色彩体系、光影风格
3. **角色设定库** - JSON结构化数据 + 自然语言描述
4. **场景设定库** - JSON结构化数据 + 自然语言描述
5. **完整分镜提示词** - 按场次顺序排列
6. **一致性参考表** - 角色/场景一致性种子词

---

## 使用方法

### 在 Claude Code 中使用

在 Claude Code 对话中直接使用触发词即可激活对应的 Skill：

```
用户: 帮我把这个剧本文档转成视频提示词
Claude: [自动触发 script-to-video-prompts skill]
```

### 脚本独立使用

每个脚本都可以独立运行：

```bash
# 解析剧本
python script-to-video-prompts/scripts/parse_script.py my_script.txt

# 查看导出工具帮助
python script-to-video-prompts/scripts/export_utils.py
```

---

## 技术栈

- **语言**: Python 3
- **依赖**:
  - `python-docx` - Word 文档解析
  - `pdfplumber` - PDF 文档解析
  - `openpyxl` - Excel 导出

---

## 开发计划

- [ ] 添加更多 Skills
- [ ] 支持更多剧本格式
- [ ] 集成主流 AI 视频平台 API
- [ ] 添加多语言支持

---

## 许可证

MIT License

---

## 贡献

欢迎提交 Issue 和 Pull Request。