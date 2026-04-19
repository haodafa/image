---
description: "每种卡片类型的 JSON 数据结构定义、渲染规格和示例。"
---

# 卡片类型数据结构

所有卡片统一宽度 1080px，高度自适应内容。

## list — 要点列表卡片

带彩色圆形图标的条目列表，每条含标题和描述。

```json
{
  "card_type": "list",
  "title": "卡片总标题",
  "items": [
    {
      "icon_text": "单字图标",
      "icon_color": "#FF6B6B",
      "title": "条目标题",
      "desc": "条目描述，支持较长文本自动换行"
    }
  ]
}
```

**约束**：
- `icon_text`：1-3 个字符，显示在彩色圆形中
- `items` 数量：3-8 条
- `title` 长度：建议 15 字以内
- `desc` 长度：建议单行，不超过 40 字

---

## comparison — 对比卡片

左右两栏对比，左侧负面/旧方案（红系），右侧正面/新方案（绿系）。

```json
{
  "card_type": "comparison",
  "left_title": "左侧标题",
  "right_title": "右侧标题",
  "left_items": ["条目1", "条目2"],
  "right_items": ["条目1", "条目2"]
}
```

**约束**：
- 左右条目数量尽量对等（3-6 条）
- 每条不超过 20 字
- 左侧条目前显示红色 × 图标，右侧显示绿色 ✓ 图标

---

## flow — 流程卡片

带箭头连接的步骤方框，支持判断菱形和循环回路。

```json
{
  "card_type": "flow",
  "title": "流程标题",
  "steps": [
    {"label": "步骤名称\n副标题", "color": "#45B7D1", "shape": "box"},
    {"label": "判断条件", "color": "#96CEB4", "shape": "diamond"}
  ],
  "connections": [
    {"from": 0, "to": 1, "label": ""},
    {"from": 1, "to": 0, "label": "未通过", "color": "#FF6B6B", "style": "loop_top"}
  ],
  "done": {"label": "完成", "after_step": 1, "label_on_arrow": "通过"},
  "bottom_note": "底部备注文字（可选）"
}
```

**约束**：
- `steps` 数量：2-5 个
- `shape`：`box`（矩形）或 `diamond`（菱形，用于判断）
- `connections.style`：空为直线箭头，`loop_top` 为从右侧绕到顶部的回路
- `label` 中 `\n` 表示换行
- `done` 可选，表示成功出口

---

## terminal — 终端演示卡片

模拟终端窗口的深色代码展示。

```json
{
  "card_type": "terminal",
  "title": "终端窗口标题",
  "lines": [
    {"color": "#6C7086", "text": "# 注释行"},
    {"color": "#89B4FA", "text": "$ 命令行"},
    {"color": "#A6E3A1", "text": "输出（表头/成功）"},
    {"color": "#CDD6F4", "text": "输出（普通数据）"},
    {"color": "", "text": ""}
  ]
}
```

**约束**：
- 空 `text` + 空 `color` 表示空行
- 建议不超过 18 行
- 深色背景 `#1E1E2E`，窗口 chrome `#11111B`

**常用颜色**：
- `#6C7086`：注释
- `#89B4FA`：命令（$ 开头）
- `#A6E3A1`：成功输出、表头
- `#CDD6F4`：普通输出
- `#F38BA8`：错误输出

---

## fit — 适合/不适合卡片

分为"适合"（绿色 ✓）和"不适合"（灰色 —）两组。

```json
{
  "card_type": "fit",
  "title": "标题（如：适合你吗？）",
  "fit_title": "适合使用",
  "fit_items": ["条件1", "条件2"],
  "nofit_title": "可以不用",
  "nofit_items": ["条件1", "条件2"]
}
```

**约束**：
- `fit_items`：2-6 条
- `nofit_items`：1-4 条
- 每条不超过 30 字

---

## quote — 金句卡片

突出展示单条核心观点或结论。

```json
{
  "card_type": "quote",
  "text": "核心观点文字",
  "source": "来源（可选）",
  "accent_color": "#45B7D1"
}
```

**约束**：
- `text` 不超过 60 字
- 左侧有粗色条装饰

---

## stats — 数据指标卡片

横排展示数字指标。

```json
{
  "card_type": "stats",
  "title": "标题",
  "metrics": [
    {"value": "21.8 万", "label": "代码行数", "color": "#FF6B6B"},
    {"value": "368", "label": "测试文件", "color": "#4ECDC4"},
    {"value": "1020", "label": "源文件", "color": "#45B7D1"}
  ]
}
```

**约束**：
- `metrics` 数量：2-5 个
- `value`：简短数字文本
- 横排等分排列

---

## architecture — 架构图卡片

分层的方框 + 箭头架构图。

```json
{
  "card_type": "architecture",
  "title": "架构标题",
  "layers": [
    {
      "label": "层标题（可选）",
      "boxes": [
        {"label": "组件名", "color": "#4ECDC4"}
      ]
    }
  ],
  "arrows": [
    {"from_layer": 0, "to_layer": 1, "label": "连接标签"}
  ],
  "center_box": {
    "label": "中心大框标题",
    "color": "#FFB347",
    "sub_modules": ["模块1", "模块2"],
    "note": "底部备注"
  },
  "bottom_note": "全局底部备注"
}
```

**约束**：
- `layers` 数量：2-4 层
- 每层 `boxes`：1-5 个
- `center_box` 可选，用于突出中间的核心组件
