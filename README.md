# 🐍 Python__First

> 从零开始学 Python 的练习归档 —— 课后作业、算法题、小工具，以及几个真正在用的程序。

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white">
  <img alt="最后更新" src="https://img.shields.io/badge/%E6%9C%80%E5%90%8E%E6%9B%B4%E6%96%B0-2026--11-2F81F7">
  <img alt="用途" src="https://img.shields.io/badge/%E7%94%A8%E9%80%94-%E5%AD%A6%E4%B9%A0%E4%B8%8E%E8%87%AA%E7%94%A8-22C55E">
</p>

## 这是什么

2025 年 9 月起步的自学仓库。它不是教程，也不是框架，而是一段学习过程的可运行快照：
按主题分成 `basics` / `data_structure` / `algorithm` / `projects` 四个区，绝大多数脚本可以单独
`python 文件名.py` 直接跑，用来回头看「当时是怎么把这道题啃下来的」。

`projects/` 里则慢慢长出了几个不再是练习、而是真的每天在用的东西：一个周期任务管理程序、
一个读写 Minecraft 存档的工具，外加几个实验数据和小文件处理脚本。

## 目录结构

```text
Python__First/
├── algorithm/                     # 算法与递归练习（S1E5 – S1E25）
│   ├── S1E5.py  S1E6.py
│   ├── S1E14.py S1E15.py
│   ├── S1E22.py S1E23_24.py       # 递归：十进制 → 二进制
│   └── S1E25.py                   # 字典 / 映射 / 散列
├── basics/                        # 语法与控制流练习
│   ├── FishC_Test/                # S1E17 – S1E30 课后作业 + 配套文本、音频
│   ├── Test/                      # 期中测试题 S1midterm.txt
│   ├── BaiduStar_01_Discount.py   # 百度之星练习题：套餐折扣最优解
│   ├── address_book.py            # JSON 持久化通讯录（函数 + 文件读写）
│   ├── control_flow_exercises.py  # if / while / for 综合练习
│   ├── guess_number.py            # 猜数字
│   └── password_strength_checker.py  # 密码强度分级
├── data_structure/                # 列表 / 元组 / 字典 / 集合（S1E12 – S2E10）
├── projects/                      # 小项目
│   ├── CycleQuest/                # 周期任务成就系统（源码版）
│   ├── CycleQuest_1.0.0/          # 发布快照：exe + 安卓 APK + 源码 + 维护日志
│   ├── 我的世界基岩版玩家数据移动工具/  # 直接读写存档 db 的玩家数据搬运工具
│   ├── Physics_Experiment_Calculator.py
│   ├── Physics_Experiment_Calculator_1.py
│   ├── Word_Count.py              # 字符统计
│   ├── list_drive.py              # 递归列出磁盘目录
│   └── rename_demo.py             # 批量重命名
└── README.md
```

## 分区说明

| 目录 | 内容 | 来源 |
| --- | --- | --- |
| `basics/` | 变量、分支、循环、函数、文件读写 | 《零基础入门学习 Python》课后作业 + 自出题 |
| `data_structure/` | 列表、元组、字典、集合的增删改查与嵌套 | 同上，第一季到第二季 |
| `algorithm/` | 递归、进制转换、字典映射等解法整理 | 课后题与练习 |
| `projects/` | 完整小项目，含打包好的程序 | 自定需求 |

`FishC_Test/` 里的编号就是课程集数，答案和推导都写在文件顶部的三引号注释里，代码在下面。

## 重点项目

### 1. CycleQuest · 周期任务成就系统

每日 / 每周 / 每月三档任务追踪，带成就提示、历史回顾和可视化报告。

- 1.x：`pywebview` + `app.html`，数据存 `app_data.json`
- 2.x：合并成一个单文件 `CycleQuest.exe` —— 本地只监听 `127.0.0.1` 的 HTTP 服务 + Edge 应用窗口，
  包含总览 / 任务 / 数据 / 工具 / 报告五个分区，新增「补卡」规则（工作日 2 个、周末 3 个，不累积、不可撤销）
- 2.0.1 起附带安卓离线 App（只读历史、只勾今天，靠 JSON 文件手动与电脑交换）

详细说明见 [`projects/CycleQuest/README.md`](projects/CycleQuest/README.md)；
设计细节、接口清单和打包方式见 [`projects/CycleQuest_1.0.0/维护日志.md`](projects/CycleQuest_1.0.0/维护日志.md)。

> `CycleQuest_1.0.0/` 是阶段性发布快照，文件夹名沿用最初的版本号；里面实际是最新的 2.0.1 整合版。

### 2. 我的世界基岩版玩家数据移动工具

直接读写存档里的 `db`（LevelDB），搬运玩家数据：服务器换周目时把 `player_server_<uuid>` 带过去，
或单机存档之间转移 `~local_player`。只 `get` + `put` 指定键，写入前备份旧值、写完逐字节回读校验。

依赖很挑版本：**Python 3.12** + `amulet-leveldb`（3.13 / 3.14 没有预编译轮子，会现场编译 C++ 而失败）。
用法和常见坑见 [`projects/我的世界基岩版玩家数据移动工具/README.md`](projects/我的世界基岩版玩家数据移动工具/README.md)。

### 3. 物理实验数据处理

`Physics_Experiment_Calculator*.py`：斜面实验的原始计时（挡光片遮光时间，单位 ms）批量处理，
按 `v = d/t` 求瞬时速度、`a = (v₂² − v₁²) / 2s` 求加速度，再按「垫几个垫块」分组求平均。
两个版本的区别只是数据组织方式：前者把原始数据直接写在脚本里，后者抽出 `calc_a()` 函数并输出中间量。

### 4. 顺手写的小工具

| 文件 | 作用 |
| --- | --- |
| `list_drive.py` | 递归列出指定磁盘 / 目录下的全部文件，支持进度显示与输出到文件 |
| `rename_demo.py` | 批量重命名演示（自动生成测试文件，可安全反复跑） |
| `Word_Count.py` | 统计输入字符串里每个字符出现的次数 |
| `BaiduStar_01_Discount.py` | 百度之星练习题：枚举套餐，求优惠比例最大的选择 |

## 环境与运行

大多数练习只需要标准库：

```bash
git clone https://github.com/Ink-Farming/Python__First.git
cd Python__First
python basics/guess_number.py
```

需要额外环境的部分：

| 项目 | 要求 |
| --- | --- |
| 通用练习 | Python 3.8+，无第三方依赖 |
| `我的世界基岩版玩家数据移动工具` | Python **3.12**、`pip install -r requirements.txt`（`amulet-leveldb`） |
| `CycleQuest/`（1.x 源码） | `pip install pywebview` |
| `CycleQuest_1.0.0/` | 免环境，双击 `CycleQuest.exe`；重新打包需要 PyInstaller |
| 安卓 App | Android 7.0+，debug 签名，可侧载安装 |

## 命名约定

| 前缀 | 含义 |
| --- | --- |
| `S1Exx` | 《零基础入门学习 Python》第一季 第 xx 集 |
| `S2Exx` | 第二季 第 xx 集 |
| `S1Exx_y` | 同一集的第 y 份作业 / 延伸写法 |
| `_1`、`_2` 后缀 | 同一题的不同版本，保留对比用 |

## 学习进度

| 主题 | 状态 | 代表代码 |
| --- | --- | --- |
| 变量、分支、循环 | ✅ | `control_flow_exercises.py`、`guess_number.py` |
| 函数、递归、参数 | ✅ | `algorithm/S1E23_24.py`、`basics/address_book.py` |
| 列表 / 元组 / 字典 / 集合 | ✅ | `data_structure/`、`algorithm/S1E25.py` |
| 字符串与文件读写 | ✅ | `Word_Count.py`、`address_book.py`、`list_drive.py` |
| 异常处理 | 🟡 | 零散使用（`control_flow_exercises.py` 的输入校验） |
| 面向对象 | 🟡 | 主要在 `CycleQuest` 的服务端与报告模块中用到，系统性练习还少 |
| 第三方库 / 打包 | ✅ | `amulet-leveldb`、`pywebview`、`PyInstaller` |
| 完整项目落地 | ✅ | `CycleQuest`、`我的世界基岩版玩家数据移动工具` |

## 关于仓库体积

`projects/` 里提交了打包好的 `CycleQuest.exe`、`main.exe` 和安卓 APK，仓库约 37 MB。
只想看代码的话：

```bash
git clone --depth 1 https://github.com/Ink-Farming/Python__First.git
```

或者直接在网页上打开对应目录，只下载 `.py` 文件。

## 交流与许可

- 个人学习仓库，代码比较随意，不保证工程规范；
- 有问题、有更好的写法，欢迎提 Issue 交流；
- 未附带开源许可证，默认保留所有权利；仓库内的练习代码可自行取用参考。

## 致谢

- [小甲鱼《零基础入门学习 Python》](https://fishc.com.cn/forum-243-1.html) —— `S1Exx` / `S2Exx` 系列题目来源；
- [amulet-leveldb](https://github.com/Amulet-Team/Amulet-LevelDB) —— 让基岩版存档可以被正常读写；
- [pywebview](https://pywebview.flowrl.com/) —— `CycleQuest` 1.x 的窗口方案。

---

<p align="center"><sub>持续更新中 · 写于 2026-11</sub></p>
