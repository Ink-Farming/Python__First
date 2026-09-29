#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CycleQuest 数据编辑器
可视化查看 / 编辑 app_data.json 中的历史任务数据

功能：
- 浏览所有 daily / weekly / monthly 周期的任务
- 勾选完成状态、修改文本、删除任务、添加任务、删除周期
- 保存时自动备份 + 按时间排序 key
"""

import webview
import os
import sys
import json
import shutil
import re
from datetime import datetime, timedelta


# ==================== 路径处理 ====================
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def get_data_path(filename='app_data.json'):
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)


DATA_PATH = get_data_path()


# ==================== 排序辅助 ====================
def parse_sort_key(key: str):
    """把 key 转成可排序元组，和 sort_app_data.py 保持一致"""
    m = re.match(r"^quest_(daily|weekly|monthly)_v4_(.+)$", key)
    if not m:
        return (9999, 12, 31, 9, key)

    typ, period = m.groups()

    if typ == "daily":
        try:
            d = datetime.strptime(period, "%Y-%m-%d").date()
            return (d.year, d.month, d.day, 0, key)
        except ValueError:
            pass

    elif typ == "weekly":
        m2 = re.match(r"^(\d{4})-(\d{2})_W(\d+)$", period)
        if m2:
            y, mo, w = map(int, m2.groups())
            d = datetime(y, mo, 1) + timedelta(weeks=w - 1)
            return (d.year, d.month, d.day, 1, key)

    elif typ == "monthly":
        m2 = re.match(r"^(\d{4})-(\d{2})$", period)
        if m2:
            y, mo = map(int, m2.groups())
            return (y, mo, 1, 2, key)

    return (9999, 12, 31, 9, key)


# ==================== 暴露给 JS 的 API ====================
class Api:
    def load_all(self):
        """读取 app_data.json，返回 { data, path } 或 { error }"""
        try:
            if not os.path.exists(DATA_PATH):
                return {"error": f"未找到数据文件：{DATA_PATH}"}
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return {"error": "数据文件格式不是 JSON 对象"}
            return {"data": data, "path": DATA_PATH}
        except json.JSONDecodeError as e:
            return {"error": f"JSON 解析失败：{e}"}
        except Exception as e:
            return {"error": str(e)}

    def save_all(self, payload):
        """保存数据。会先自动备份，再按时间排序后写入"""
        try:
            if not isinstance(payload, dict):
                return {"error": "保存内容格式错误"}

            # 1. 备份
            backup_path = None
            if os.path.exists(DATA_PATH):
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = os.path.join(
                    os.path.dirname(DATA_PATH),
                    f"app_data.auto_backup_{ts}.json"
                )
                shutil.copy2(DATA_PATH, backup_path)

            # 2. 按时间排序
            sorted_items = sorted(payload.items(), key=lambda kv: parse_sort_key(kv[0]))
            sorted_data = dict(sorted_items)

            # 3. 写入
            with open(DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(sorted_data, f, ensure_ascii=False, indent=2)
                f.write("\n")

            return {
                "ok": True,
                "path": DATA_PATH,
                "backup": backup_path,
                "count": len(sorted_data),
            }
        except Exception as e:
            return {"error": str(e)}

    def backup_now(self):
        """手动备份"""
        try:
            if not os.path.exists(DATA_PATH):
                return {"error": "数据文件不存在"}
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(
                os.path.dirname(DATA_PATH),
                f"app_data.manual_backup_{ts}.json"
            )
            shutil.copy2(DATA_PATH, backup_path)
            return {"ok": True, "path": backup_path}
        except Exception as e:
            return {"error": str(e)}


api = Api()


# ==================== 主程序 ====================
def main():
    window = webview.create_window(
        'CycleQuest 数据编辑器',
        resource_path("editor.html"),
        width=1080,
        height=740,
        min_size=(820, 560),
        text_select=True,
        js_api=api,
    )
    webview.start(debug=False)


if __name__ == '__main__':
    main()
