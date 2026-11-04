"""数据读取与解析。"""
import json
import os
import sys
from collections import defaultdict

from config import DATA_PATH
from categories import classify_task


def load_data():
    if not os.path.exists(DATA_PATH):
        print(f"未找到数据文件: {DATA_PATH}")
        input("按回车退出...")
        sys.exit(1)
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_records(raw_data):
    records = {'daily': [], 'weekly': [], 'monthly': []}
    for key, val in raw_data.items():
        if not key.startswith('quest_'):
            continue
        parts = key.split('_')
        if len(parts) < 4:
            continue
        scope = parts[1]  # daily/weekly/monthly
        if scope == 'weekly':
            period = parts[-2] + '_' + parts[-1]
        else:
            period = parts[-1]

        try:
            data = json.loads(val) if isinstance(val, str) else val
        except Exception:
            continue

        quests = data.get('quests', [])
        done = sum(1 for q in quests if q.get('done'))
        total = len(quests)

        # 分类统计
        cat_stats = defaultdict(lambda: {'done': 0, 'total': 0})
        for q in quests:
            cat = classify_task(q.get('text', ''))
            cat_stats[cat]['total'] += 1
            if q.get('done'):
                cat_stats[cat]['done'] += 1

        records[scope].append({
            'period': period,
            'done': done,
            'total': total,
            'quests': quests,
            'cat_stats': dict(cat_stats),
            'date_sort': period
        })

    for scope in records:
        records[scope].sort(key=lambda x: x['date_sort'], reverse=True)
    return records