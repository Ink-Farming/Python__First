# 🎯 年度计划执行报告生成器（report_viewer）

从任务成就系统的历史数据（`app_data.json`）中读取每日 / 每周 / 每月任务，
按「年度计划维度」自动分类统计，生成一份可交互的本地 HTML 报告并自动在浏览器打开。

---

## 📁 项目结构

```
项目目录/
├── report_viewer.py     # 主入口：串联 读取 → 统计 → 生成 流程
├── config.py            # 全局配置：文件名、路径、报告标题
├── categories.py        # 计划维度分类：关键词、颜色、图标
├── data_loader.py       # 数据读取与记录解析
├── stats.py             # 统计计算（月度聚合、维度聚合）
├── styles.py            # 报告前端资源：CSS 样式 + JS 脚本
├── html_generator.py    # HTML 模板结构与拼装逻辑
├── app_data.json        # 输入数据（任务成就系统导出）
└── report.html          # 输出报告（运行后自动生成）
```

> 拆分的核心目的：**改什么只动一个文件**，不必在几百行的单文件里大海捞针。

---

## 🚀 快速开始

### 1. 准备数据

把任务成就系统导出的 `app_data.json` 放到与脚本相同目录。

数据结构要求（关键字段）：

```json
{
  "quest_daily_2025-09-16": "{\"quests\":[{\"text\":\"Python 练习题\",\"done\":true}]}",
  "quest_weekly_2025-09_2025-W2": "{\"quests\":[...]}",
  "quest_monthly_2025-09": "{\"quests\":[...]}"
}
```

- Key 格式：`quest_{scope}_{period}`
  - `scope` 取值：`daily` / `weekly` / `monthly`
  - `weekly` 的 period 形如 `2025-09_2025-W2`（倒数两段拼接）
  - `daily` 形如 `2025-09-16`
  - `monthly` 形如 `2025-09`
- Value：JSON 字符串或对象，内含 `quests` 数组，每项有 `text` 和 `done`

### 2. 运行

```bash
python report_viewer.py
```

控制台会依次输出「读取 → 分析 → 生成 → 完成」，报告生成后自动用默认浏览器打开 `report.html`。

### 3. 打包为 exe（可选）

```bash
pyinstaller -F -w report_viewer.py
```

把所有 `.py` 一起打包即可。`config.py` 中的 `frozen` 判断会保证 exe 运行时数据文件路径正确（读的是 exe 同目录下的 `app_data.json`）。

---

## 🧩 各文件职责与常见修改场景

### `config.py` — 全局配置

| 变量 | 说明 |
| --- | --- |
| `DATA_FILENAME` | 输入数据文件名，默认 `app_data.json` |
| `REPORT_FILENAME` | 输出报告文件名，默认 `report.html` |
| `REPORT_TITLE` | 报告大标题（浏览器标签页 + 页面 h1） |
| `REPORT_FOOTER` | 页脚文案 |
| `DATA_PATH` / `OUTPUT_PATH` | 由 `BASE_DIR` 自动推导，一般不用改 |
| `get_base_dir()` | 兼容 PyInstaller 打包的路径解析 |

**修改场景**
- 想换数据文件名 → 改 `DATA_FILENAME`
- 想换生成的报告名 → 改 `REPORT_FILENAME`
- 想换页面标题 / 页脚 → 改 `REPORT_TITLE` / `REPORT_FOOTER`

---

### `categories.py` — 计划维度分类

`CATEGORIES` 字典定义了 8 个维度（python / career / english / exercise / music / exam / reading / coding）+ 兜底的 `other`。

每个维度包含：

```python
'python': {
    'name': '🔥 Python 学习',          # 报告中显示的名称（含 emoji）
    'color': '#ff9500',                # 主色（进度条 / 文字）
    'bg': 'rgba(255,149,0,0.15)',      # 卡片背景色
    'keywords': ['python', '语法', ...] # 命中任一关键词即归入此维度（不区分大小写）
}
```

`classify_task(text)` 按 `CATEGORIES` 声明顺序遍历，第一个命中的关键词决定分类；都不命中则归入 `other`。

**修改场景**
- 新增一个维度 → 在 `CATEGORIES` 里加一项（放在 `other` 之前）
- 调整关键词 → 直接改对应维度的 `keywords` 列表
- 换颜色 / 图标 → 改 `color` / `bg` / `name`

> ⚠️ 注意：`other` 必须保留在字典里（用于兜底），且 `classify_task` 会跳过它。

---

### `data_loader.py` — 数据读取与解析

| 函数 | 作用 |
| --- | --- |
| `load_data()` | 读 `DATA_PATH`；文件不存在则提示并退出 |
| `parse_records(raw)` | 解析所有 `quest_*` key，按 `daily/weekly/monthly` 归组，逐条统计完成数、维度分布，并按周期倒序排序 |

解析后每条记录的字段：

```python
{
    'period': '2025-09-16',      # 周期标识
    'done': 3,                   # 完成数
    'total': 5,                  # 总数
    'quests': [...],             # 原始任务列表
    'cat_stats': {               # 按维度统计
        'python': {'done': 2, 'total': 3},
        ...
    },
    'date_sort': '2025-09-16'    # 排序键
}
```

**修改场景**
- 数据源 key 格式变了 → 改 `parts` 解析逻辑（如 `scope = parts[1]` 的分段方式）
- 想加过滤条件（例如只统计近一年）→ 在 append 前判断

---

### `stats.py` — 统计计算

`compute_stats(records)` 返回：

```python
{
    'monthly': {
        '2025-09': {
            'done': 12, 'total': 20,
            'cat': {'python': {'done': 6, 'total': 8}, ...}
        },
        ...
    },
    'all_cat': {
        'python': {
            'done': 20, 'total': 30,
            'tasks': [{'text':..., 'done':..., 'scope':..., 'period':...}, ...]
        },
        ...
    },
    'total_done': 120,
    'total_tasks': 200
}
```

**月份归属规则**（`monthly` 聚合时）：

| 周期格式 | 归属月份 |
| --- | --- |
| `2025-09_2025-W2`（weekly） | `2025-09` |
| `2025-09`（monthly） | `2025-09` |
| `2025-09-16`（daily） | `2025-09` |

**修改场景**
- 想换聚合粒度（如按季度）→ 在月份提取处改成季度 key
- 想加新的整体指标（如连续打卡天数）→ 在此函数里追加字段，然后在 `html_generator.py` 中渲染

---

### `styles.py` — 前端资源

包含两个字符串常量：

- `CSS_STYLES`：全部样式（暗色主题、卡片、进度条、趋势柱状图、手风琴展开等）
- `JS_SCRIPT`：两个交互函数
  - `toggle(header)`：历史明细卡片展开/收起；页面加载时自动展开第一个
  - `toggleCat(summary)`：维度卡片展开/收起

**修改场景**
- 换主题色 → 改 `body` / `.card` / 渐变里的颜色
- 调整布局宽度 → 改 `body { max-width }`
- 调整趋势图高度 → 改 `.trend-chart { height }` 和 `.trend-bar-wrap { height }`
- 加动画 / 改过渡 → 改 `transition` 属性
- 改默认展开行为 → 改 `JS_SCRIPT` 里 `if (i === 0) h.click();`

> 由于 `html_generator.py` 直接内嵌 `{CSS_STYLES}` 和 `{JS_SCRIPT}`，改完样式无需动其他文件。

---

### `html_generator.py` — HTML 生成

| 函数 | 作用 |
| --- | --- |
| `format_period_short(scope, period)` | 维度卡片里用的短周期标签（`09-16` / `09 W2` / `2026-09`） |
| `generate_html(records, stats)` | 拼装四大板块 + 写文件 + 打开浏览器 |

报告四大板块：

1. **📊 总体概览**：完成数、总数、有记录月份数、总完成率 + 主进度条
2. **🧭 各维度进度**：8+1 个维度卡片，点击展开任务明细
3. **📈 月度完成率趋势**：纯 CSS 柱状图（无外部依赖）
4. **📜 历史明细**：按「月 / 周 / 日」分组的手风琴列表

**修改场景**
- 增删板块 → 直接改 `html` f-string 结构
- 改维度卡片里的任务行样式 → 改 `cat_html` 里的 `rows` 拼接（同时配套改 `styles.py` 的 `.cat-task`）
- 改历史卡片周期标签格式 → 改 `period_label` 的格式化分支
- 不想自动打开浏览器 → 注释掉 `webbrowser.open(...)`

---

### `report_viewer.py` — 主入口

只有 20 行左右，负责：

```python
load_data()        → 读原始 JSON
parse_records()    → 解析成结构化 records
compute_stats()    → 算出统计
generate_html()    → 生成并打开报告
```

**修改场景**
- 想加日志 / 计时 → 在这几个调用之间插入
- 想拆成 CLI 参数（如 `--no-open`）→ 用 `argparse` 在 `main()` 里处理

---

## 🔄 常见修改速查表

| 我想… | 改哪个文件 |
| --- | --- |
| 换数据文件名 / 报告文件名 | `config.py` |
| 换报告标题 / 页脚 | `config.py` |
| 新增 / 删除计划维度 | `categories.py` |
| 调整关键词、颜色、图标 | `categories.py` |
| 改整体配色、布局、动画 | `styles.py` |
| 改交互逻辑（展开、默认状态） | `styles.py` 的 `JS_SCRIPT` |
| 增删报告板块、改文案 | `html_generator.py` |
| 改统计口径（如按季度） | `stats.py` |
| 改数据解析规则 | `data_loader.py` |
| 加 CLI 参数 / 日志 | `report_viewer.py` |

---

## 🐛 已知注意事项

1. **维度统计去重**：早期版本在 `compute_stats` 里对 `all_cat` 的 `done/total` 累加过两次（`cat_stats` 一次 + `quests` 一次），导致维度总数翻倍。现版本只在遍历 `quests` 时累加一次，`monthly` 仍走 `cat_stats`。
2. **`other` 维度必须存在**：`classify_task` 兜底返回 `'other'`，若删除会 KeyError。
3. **`weekly` 的 period 解析**：依赖 key 分段，`quest_weekly_YYYY-MM_YYYY-Wn` 共 4 段，取 `parts[-2] + '_' + parts[-1]`。若历史数据格式不同需在 `data_loader.py` 兼容。
4. **PyInstaller 打包**：`config.get_base_dir()` 已处理 `sys.frozen` 情况，exe 同目录放 `app_data.json` 即可。

---

## 📦 依赖

仅使用 Python 标准库，无需 `pip install` 任何第三方包：

- `json` / `os` / `sys` / `webbrowser`
- `datetime` / `collections.defaultdict` / `html.escape`

Python 3.7+ 均可运行。

---

## 📄 License

个人使用项目，无特殊授权要求。