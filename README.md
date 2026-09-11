# NovelCraft

> 把一个虚拟作家人格放进一个具体故事，用最少的文件把它写下去。

`novel-writer` 是一个面向中文长篇小说的 AI 写作 Skill。它不做流程管理，也不做质量评分——它只回答一个具体问题：**写这一章时该怎么决定。**

- **做什么**：把虚拟作家人格、故事承诺与主题命题、卷 / 幕 / 章三级纲要、一份状态快照放进一个项目，让长篇能连续地写下去。
- **指导什么**：这一场谁要什么、什么挡着、演到哪停；这一章必须发生什么变化；下一章动笔前要记得什么；哪些写法是这本书的敌人。
- **核心在哪**：正文。`章纲 → 草稿 → 定稿` 是唯一产出；人格、设定、纲要、状态都只为让下一章写得更好而存在。
- **不做什么**：不生成风格报告（属 [author-persona-skill](#与-author-persona-skill-协作)），不裁决文学好坏，不替用户定稿，不做检查与评分。

## 设计取向

这个 Skill 的核心假设是：**规则越密，越容易被跳过或走形式。**

它的前身曾经是一套完整的流程系统——7 个脚本、10 类一致性检查、机械 AI 味体检、幕末归档快照。结果是写 3000 字正文的流程成本接近甚至超过正文本身，规则密度过高反而降低了规则的实际约束力。0.7.0 起主动砍回最小形态：删掉全部检查与门禁，只留一个"把目录和模板摆成约定形状"的脚本。

所以这里没有必须通过的关卡，没有评分。**文学判断由虚拟作家（模型）完成，正文定稿由用户确认。**

## 工作流

```text
人格与故事承诺 → 卷定方向 → 幕定因果 → 章前规划
→ 章纲 → 草稿 → 用户确认定稿 → 更新状态
→ 从真实结果规划下一幕
```

### 新项目

1. **读人格来源**：有外部风格能力报告就完整读一遍，按 `references/style_report_mapping.md` 转译；没有就按用户描述提炼。
2. **写人格**：填 `state/author_persona.md`，不变量层写决策句，姿态层填场景表。
3. **写设定**：填 `state/story_bible.md`，故事承诺六件事、主题命题、Canon、主要人物引擎。
4. **写纲要**：第一卷纲、第一幕纲。
5. **试写验收**：写 2–3 个短场景给用户看；用户认可后把 `memory.md` 项目状态改为 `ready`，开始写第一章。

### 每章

1. 读 `author_persona.md`、`current_state.md`、当前幕纲和上一章正文。
2. 写章纲到 `workspace/outlines/`。
3. 写草稿到 `workspace/drafts/`。
4. 提交用户确认；定稿后复制进 `workspace/chapters/`，更新 `current_state.md`。

四步之外没有别的动作。

## 项目骨架

```text
state/
  author_persona.md    人格：每章开写前完整读一遍
  story_bible.md       故事承诺、主题命题、Canon、人物引擎
  current_state.md     此刻接着写需要记得什么
  memory.md            项目状态、坐标、下一步、用户偏好
workspace/
  volumes/   acts/   outlines/   drafts/   chapters/   summaries/
```

卷、幕编号两位，章三位；章号全书递增，已定稿章号不回改。

```bash
python scripts/init_project.py <项目根>
```

脚本只建目录、复制四份状态模板，已存在文件不覆盖。卷纲 / 幕纲 / 章纲 / 摘要模板在 `assets/templates/`，按需取用——字段随书自由增删，模板是起点，不是表格。

## 作家人格

`author_persona.md` 是日常写作的唯一人格输入，分两轨：

- **不变量层**（每章必读，3–6 条）：写决策句——"面对什么材料，做什么决定"。它保证跨场景仍是同一个人在决定。
- **姿态层**（按场景类型查表）：战斗 / 日常 / 仪式 / 独白 / 转场 → 句长、段落、对白占比、描写配比、禁用项。它决定"这一类场景怎么写"。

冲突时的优先级：

```text
不变量层 > 红线 > 风格基调 > 姿态层与技法卡
```

故事承诺高于人格。这套设计的意图是**稳定内核，不冻结姿态**——同一位作者写战斗和葬礼会换语域，不变的是做决定的方式。

## 与 author-persona-skill 协作

两个技能构成一套创作系统的先后两环：

```text
author-persona-skill（能力理解）：语料 → 四层风格能力报告（观察与证据，留在项目外）
        ↓  按 references/style_report_mapping.md 一次落位
novel-writer（故事创作）：报告能力 → state/author_persona.md 项目专属作家人格
        + state/story_bible.md 设定
        → 故事纲要、正文与连续性维护
```

前者交付**观察与证据**，后者依据本书故事承诺裁决采用、改写、舍弃哪些能力。转译一次完成，不维护独立转接文件；报告的证据引文不进人格，人格只留行文机制。

上游仓库：[author-persona-skill](https://github.com/ouzx6696-cmyk/author_persona_skill)

## 目录导览

| 路径 | 内容 |
|---|---|
| `SKILL.md` | 技能主文档：工作流、人格架构、规划与状态规范 |
| `manifest.yaml` | 平台清单：权限与函数声明 |
| `scripts/init_project.py` | 唯一的可执行代码：建骨架、复制模板 |
| `references/anti_ai.md` | 去 AI 味的 10 条写前场景纪律 + 写后回看清单 |
| `references/style_report_mapping.md` | 外部风格报告四层 → 人格与设定的落位表 |
| `assets/templates/` | 9 份模板：4 份状态文件 + 卷 / 幕 / 章纲要与摘要 |
| `assets/examples/persona_translation_example.md` | 一次完整转译的示范与取舍记录 |
| `CHANGELOG.md` | 版本变更记录 |

## 测试

```bash
python -m pytest tests/ -q
```

5 项用例，只覆盖建骨架脚本与文档自洽（技能描述与 manifest 逐字一致、引用的文件都存在）。刻意不覆盖"写作质量"——那不归工具裁决。

## 安装

作为 Skill 使用时，把整个目录放进你的 Agent 平台的 skills 目录即可。目录名需为 `novel-writer`。

- 只需 `python`（3.9+，用到 `list[str]` 泛型标注；实际测试于 3.12）。
- 无第三方依赖。

## 版本

当前 `0.7.1`。变更历史见 [CHANGELOG.md](CHANGELOG.md)。

## 授权

[MIT](LICENSE)
