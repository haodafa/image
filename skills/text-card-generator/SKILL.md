---
model: sonnet
description: "为文本内容生成公众号风格的卡片配图（PNG）。输入 Markdown 文件或纯文本，自动识别适合做成卡片的段落，生成对应图片。当用户需要为文章生成配图、将文字转为卡片图时使用。"
argument-hint: "<markdown-file|text> [--output-dir <dir>] [--card-type <type>]"
---

## 前置环境

执行前先跑 `bash <skill-dir>/scripts/check_env.sh`；若有 `[MISSING]` 项，跑 `bash <skill-dir>/scripts/setup_env.sh` 自动安装。

## 第一步：输入解析

从 `$ARGUMENTS` 解析出：

- **输入源**：Markdown 文件路径 / 纯文本 / 结构化数据（JSON）
- **输出目录**：`--output-dir` 指定，或文件同级 `images/` 目录。无法推断时通过 AskUserQuestion 确认
- **处理模式**：
  - **自动模式**（默认）：扫描全文，识别适合做卡片的段落，自动匹配类型
  - **指定类型模式**：`--card-type` 指定，只按该类型生成
  - **纯数据模式**：直接传 JSON + card_type，跳到第四步

## 第二步：内容扫描与卡片匹配

按 `references/card-matching-rules.md` 逐段扫描输入内容，判断哪些段落适合做卡片、用哪种类型。

**卡片类型速查**（完整定义见 `references/card-types.md`）：

| 类型 | 适用场景 | 典型识别信号 |
|------|---------|------------|
| `list` | 并列的要点/特性/能力 | 3+ 条带标题+描述的条目 |
| `comparison` | 前后对比/优劣/AB 选择 | 两组对立条目、"vs"、"之前/之后" |
| `flow` | 流程/步骤/循环 | 有序步骤、箭头、判断分支 |
| `terminal` | 命令行/代码演示 | 代码块、shell 命令序列 |
| `fit` | 适合/不适合、是/否 | 正反两组条件 |
| `quote` | 金句/核心结论 | 单条重要结论、slogan |
| `stats` | 数据/指标 | 数字+标签的组合 |
| `architecture` | 系统架构/层级关系 | 组件+连线+分层 |

向用户展示匹配结果（段落摘要 → 卡片类型），确认后继续。

## 第三步：构造卡片数据

为每张卡片构造 JSON。每种类型的完整字段定义见 `references/card-types.md`。

**配色规则**：
- 强调色板（按序取用）：`#FF6B6B` `#4ECDC4` `#45B7D1` `#96CEB4` `#FFB347` `#DDA0DD`
- 背景 `#FAFAFA`，卡片底色 `#FFFFFF`，标题 `#1A1A1A`，描述 `#888888`，分割线 `#F0F0F0`
- `comparison` 类型：左侧用红系（`#FF6B6B` 底 + `#884444` 文字），右侧用绿系（`#4ECDC4` 底 + `#2E6B3E` 文字）
- `terminal` 类型：底色 `#1E1E2E`，窗口按钮 `#F38BA8` `#FAB387` `#A6E3A1`

**中文字体**：脚本内置下载逻辑，使用 Noto Sans CJK SC（Regular + Bold）。

## 第四步：生成 PNG

将 JSON 写入临时文件，调用渲染脚本：

```bash
<skill-dir>/scripts/render_card.py \
  --data-file <data.json> \
  --output <output.png> \
  [--font-dir <font-cache-dir>]
```

脚本自动处理字体下载缓存、画布尺寸计算、文本换行。

生成后用 Read 工具查看 PNG 验收。若文字溢出或布局异常，调整 JSON 数据（缩短文本、增减条目）后重新生成。

## 第五步：交付

展示生成的图片清单（文件名 + 内容摘要 + 输出路径）。

如果输入是 Markdown 文件，询问用户是否将图片引用插入原文对应位置。
