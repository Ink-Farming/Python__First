# CycleQuest · 周期任务成就系统

一个基于 **pywebview + HTML** 的本地任务管理工具，支持 **每日 / 每周 / 每月** 三种周期的任务追踪、成就反馈与历史回顾，并可生成执行报告。

> 项目名：**CycleQuest**  
> 中文名：**周期任务成就系统**  
> 副标题：日 / 周 / 月计划与成就追踪

---

## ✨ 功能特性

- **三种周期视图**：今日任务、本周计划、本月目标，标签页一键切换
- **任务勾选与进度**：实时显示完成率、进度条，完成时播放音效并弹出 Toast 成就提示
- **历史回顾面板**：查看每日 / 每周 / 每月的历史记录，点击展开任务明细
- **本地数据持久化**：通过 `pywebview` 将数据保存到 `app_data.json`，无需联网
- **调试跳过功能**：可临时冻结日期，方便测试历史数据与成就逻辑
- **额外工具**：
  - `sort_app_data.py`：按时间顺序整理 `app_data.json` 中的任务键
  - `report_viewer.py`：读取数据并生成可视化 HTML 报告（`report.html`）

---

## 📁 文件说明

| 文件 | 说明 |
|---|---|
| `main.py` | 主程序，创建 pywebview 窗口，加载 `app.html`，提供保存/加载数据的 API |
| `app.html` | 前端界面，包含全部交互逻辑与样式 |
| `app_data.json` | 数据存储文件，运行后自动生成（与程序同目录） |
| `sort_app_data.py` | 数据排序脚本，按时间顺序整理 `app_data.json` 中的 key |
| `report_viewer.py` | 报告生成脚本，读取 `app_data.json` 并生成 `report.html` |
| `main.exe` | 已打包的 Windows 可执行文件（仅包含 `main.py` + `app.html`） |

---

## 🚀 快速开始

### 方式一：直接使用 `main.exe`（Windows）

1. 下载 `main.exe`，放到任意文件夹。
2. 双击运行，即可打开任务管理窗口。
3. 数据会自动保存在同目录下的 `app_data.json` 中。

> ⚠️ `main.exe` **只包含任务管理界面**，不包含数据排序与报告生成功能。  
> 如需排序或生成报告，请参考下方“额外工具使用”。

### 方式二：从源码运行

1. 安装 Python 3.8+。
2. 安装依赖：
   ```bash
   pip install pywebview
   ```
3. 运行主程序：
   ```bash
   python main.py
   ```

---

## 🧰 额外工具使用

### 1. 数据排序：`sort_app_data.py`

按时间顺序重新整理 `app_data.json` 中的任务键（如 `quest_daily_v4_2026-09-24`、`quest_weekly_v4_2026-09_W4` 等），并自动备份原文件为 `app_data.backup.json`。

```bash
python sort_app_data.py
```

- 默认直接覆盖 `app_data.json`
- 备份文件：`app_data.backup.json`
- 如需预览结果，可修改脚本中的 `OUT = Path("app_data.sorted.json")`

### 2. 生成报告：`report_viewer.py`

读取 `app_data.json`，分析任务完成情况，生成带图表的 HTML 报告 `report.html`，并自动在浏览器中打开。

```bash
python report_viewer.py
```

报告内容包括：
- 总体概览（已完成、总任务数、有记录月份、总完成率）
- 年度计划各维度进度（Python、职业探索、英语、锻炼、音乐等）
- 月度完成率趋势图
- 历史明细（点击展开每日 / 每周 / 每月任务）

> 运行 `report_viewer.py` 需要 Python 环境，并确保 `app_data.json` 与脚本在同一目录。

---

### 3. 可视化编辑数据：`data_editor.py`

提供一个可视化界面，用于查看和修改 `app_data.json` 中的历史任务数据。

```bash
python data_editor.py

## 💾 数据存储

- 数据文件：`app_data.json`
- 位置：
  - 使用 `main.exe` 时：与 `exe` 同目录
  - 从源码运行 `main.py` 时：与 `main.py` 同目录
- 格式：JSON，键为 `quest_{scope}_v4_{period}`，值为 JSON 字符串（包含 `period` 和 `quests` 数组）
- 建议定期备份 `app_data.json`

---

## 📦 打包说明（可选）

若需自行打包 `main.exe`，可使用 PyInstaller：

```bash
pyinstaller --onefile --windowed --add-data "app.html;." main.py
```

- `--add-data "app.html;."` 将 `app.html` 一并打包
- 生成的 `main.exe` 位于 `dist/` 目录
- 注意：打包后的 exe **不包含** `sort_app_data.py` 和 `report_viewer.py`

---

## 📋 依赖

- Python 3.8+
- [pywebview](https://pywebview.flowrl.com/)
- 可选：`pyinstaller`（仅打包时需要）

---

## ❓ 常见问题

**Q：`main.exe` 运行时提示缺少 WebView2？**  
A：Windows 10/11 通常已内置 Edge WebView2。若缺失，请安装 [Microsoft Edge WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/)。

**Q：为什么 `main.exe` 没有生成报告的功能？**  
A：`main.exe` 仅打包了 `main.py` 和 `app.html`。报告生成与数据排序是独立的 Python 脚本，需要单独运行。

**Q：数据会丢失吗？**  
A：数据保存在本地 `app_data.json`，建议定期备份。`sort_app_data.py` 会自动生成 `.backup.json` 备份。

**Q：如何修改任务默认模板？**  
A：编辑 `app.html` 中的 `DEFAULTS` 对象，修改 `daily`、`weekly`、`monthly` 的初始任务列表。

---

## 📄 许可证

本项目仅供个人学习与使用，可自由修改和分发。

---

**CycleQuest** — 让每一天、每一周、每一个月都成为可追踪的成就。
