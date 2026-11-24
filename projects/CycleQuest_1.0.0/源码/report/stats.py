"""统计计算。"""
from collections import defaultdict

from categories import classify_task


def compute_stats(records):
    # 按月份聚合 (YYYY-MM)
    monthly = defaultdict(lambda: {
        'done': 0, 'total': 0,
        'cat': defaultdict(lambda: {'done': 0, 'total': 0})
    })

    # 所有记录汇总（按维度）
    all_cat = defaultdict(lambda: {'done': 0, 'total': 0, 'tasks': []})
    total_done = 0
    total_tasks = 0

    for scope, items in records.items():
        for item in items:
            # 提取月份
            p = item['period']
            if '_W' in p:
                month_key = p.split('_')[0]
            elif len(p) == 7 and '-' in p:   # YYYY-MM
                month_key = p
            elif len(p) == 10:               # YYYY-MM-DD
                month_key = p[:7]
            else:
                month_key = p[:7] if len(p) >= 7 else p

            monthly[month_key]['done'] += item['done']
            monthly[month_key]['total'] += item['total']

            # 月度按维度聚合（用 cat_stats，避免重复）
            for cat, st in item['cat_stats'].items():
                monthly[month_key]['cat'][cat]['done'] += st['done']
                monthly[month_key]['cat'][cat]['total'] += st['total']

            # 全局按维度聚合 + 保留明细（只从 quests 统计一次，避免重复计数）
            for q in item['quests']:
                text = q.get('text', '')
                done = bool(q.get('done'))
                cat = classify_task(text)
                all_cat[cat]['total'] += 1
                if done:
                    all_cat[cat]['done'] += 1
                all_cat[cat]['tasks'].append({
                    'text': text,
                    'done': done,
                    'scope': scope,
                    'period': item['period'],
                })

            total_done += item['done']
            total_tasks += item['total']

    for cat in all_cat:
        all_cat[cat]['tasks'].sort(key=lambda t: t['period'], reverse=True)

    sorted_months = sorted(monthly.keys())
    return {
        'monthly': {k: monthly[k] for k in sorted_months},
        'all_cat': dict(all_cat),
        'total_done': total_done,
        'total_tasks': total_tasks
    }