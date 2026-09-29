#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

SRC = Path("app_data.json")              # 原文件
BACKUP = Path("app_data.backup.json")    # 备份文件
OUT = SRC                                # 直接覆盖原文件；想先预览可改成 Path("app_data.sorted.json")


def parse_sort_key(key: str):
    """
    把 key 转成可排序元组。
    支持：
    quest_daily_v4_2026-09-24
    quest_weekly_v4_2026-09_W4
    quest_monthly_v4_2026-09
    """
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
        # 形如 2026-08_W5
        m2 = re.match(r"^(\d{4})-(\d{2})_W(\d+)$", period)
        if m2:
            y, mo, w = map(int, m2.groups())
            # 粗略转成该月第 w 周对应的日期，方便和 daily 混排
            d = date(y, mo, 1) + timedelta(weeks=w - 1)
            return (d.year, d.month, d.day, 1, key)

    elif typ == "monthly":
        # 形如 2026-09
        m2 = re.match(r"^(\d{4})-(\d{2})$", period)
        if m2:
            y, mo = map(int, m2.groups())
            return (y, mo, 1, 2, key)

    return (9999, 12, 31, 9, key)


def main():
    if not SRC.exists():
        print(f"找不到文件：{SRC}")
        return

    # 1. 备份
    shutil.copy2(SRC, BACKUP)
    print(f"已备份到：{BACKUP}")

    # 2. 读取 JSON
    with SRC.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # 3. 顺手检查 key 和 value.period 是否不一致
    for k, v in data.items():
        try:
            inner = json.loads(v)
            p = inner.get("period")
        except Exception:
            continue

        m = re.match(r"^quest_(?:daily|weekly|monthly)_v4_(.+)$", k)
        if m and p and m.group(1) != p:
            print(f"警告：key={k} 与 value.period={p} 不一致")

    # 4. 按时间排序
    sorted_items = sorted(data.items(), key=lambda kv: parse_sort_key(kv[0]))
    sorted_data = dict(sorted_items)

    # 5. 写回
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"已按时间顺序写入：{OUT}")


if __name__ == "__main__":
    main()
