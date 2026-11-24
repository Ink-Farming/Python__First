"""生成 HTML 报告。

只负责模板结构与数据拼装，样式在 styles.py，分类在 categories.py。
"""
import os
import webbrowser
from datetime import datetime
from html import escape

from config import OUTPUT_PATH, REPORT_TITLE, REPORT_FOOTER
from categories import CATEGORIES, classify_task
from styles import CSS_STYLES, JS_SCRIPT


def format_period_short(scope, period):
    if scope == 'daily' and len(period) == 10:
        return period[5:]              # 09-16
    if scope == 'weekly':
        if '_W' in period:
            date_part, w = period.split('_')
            return f"{date_part[5:]} {w}"   # 09 W2
        return period                  # 兼容老数据 'W5'
    if scope == 'monthly' and len(period) >= 7:
        return period[:7]              # 2026-09
    return period


def generate_html(records, stats):
    # 月度趋势数据
    months = list(stats['monthly'].keys())
    month_rates = []
    for m in months:
        t = stats['monthly'][m]['total']
        d = stats['monthly'][m]['done']
        month_rates.append(round(d / t * 100, 1) if t else 0)

    # 各维度总体进度
    cat_html = ''
    for key, info in CATEGORIES.items():
        st = stats['all_cat'].get(key, {'done': 0, 'total': 0, 'tasks': []})
        pct = round(st['done'] / st['total'] * 100, 1) if st['total'] else 0
        tasks = st.get('tasks', [])

        if tasks:
            rows = []
            for t in tasks:
                icon = {'daily': '📅', 'weekly': '📆', 'monthly': '🗓️'}.get(t['scope'], '·')
                label = format_period_short(t['scope'], t['period'])
                check = '✅' if t['done'] else '⬜'
                cls = 'done' if t['done'] else ''
                rows.append(
                    f'<div class="cat-task {cls}">'
                    f'<span class="task-meta">{icon} {label}</span>'
                    f'<span class="task-text">{check} {escape(t["text"])}</span>'
                    f'</div>'
                )
            task_rows = ''.join(rows)
        else:
            task_rows = '<div class="cat-empty">该维度暂无任务</div>'

        cat_html += f'''
        <div class="cat-card" style="border-left:4px solid {info['color']}; background:{info['bg']}">
            <div class="cat-summary" onclick="toggleCat(this)">
                <div class="cat-name">{info['name']}</div>
                <div class="cat-num">{st['done']}/{st['total']}</div>
                <div class="mini-bar"><div class="mini-fill" style="width:{pct}%; background:{info['color']}"></div></div>
                <div class="cat-pct" style="color:{info['color']}">{pct}%</div>
            </div>
            <div class="cat-detail">{task_rows}</div>
        </div>
        '''

    # 月度趋势图（纯 CSS 柱状图）
    bar_html = ''
    max_rate = max(month_rates) if month_rates else 100
    for m, rate in zip(months, month_rates):
        bar_html += f'''
        <div class="trend-col">
            <div class="trend-bar-wrap">
                <div class="trend-bar" style="height:{rate/max_rate*100}%;">{rate}%</div>
            </div>
            <div class="trend-label">{m}</div>
        </div>
        '''

    # 历史明细
    detail_html = ''
    scope_names = {'daily': '📅 每日记录', 'weekly': '📆 每周记录', 'monthly': '🗓️ 每月记录'}
    for scope in ['monthly', 'weekly', 'daily']:
        items = records[scope]
        if not items:
            continue
        detail_html += f'<h3 class="scope-title">{scope_names[scope]}</h3>'
        for item in items:
            pct = round(item['done'] / item['total'] * 100) if item['total'] else 0
            done_class = 'done' if pct == 100 else ''

            tasks_html = ''
            for q in item['quests']:
                cat = classify_task(q.get('text', ''))
                color = CATEGORIES.get(cat, CATEGORIES['other'])['color']
                check = '✅' if q.get('done') else '⬜'
                strike = 'style="text-decoration:line-through; opacity:0.5;"' if q.get('done') else ''
                tasks_html += (
                    f'<div class="task-line" {strike}>'
                    f'<span style="color:{color}">{check}</span> {q.get("text", "")}'
                    f'</div>'
                )

            period_label = item['period']
            if scope == 'weekly' and '_W' in period_label:
                parts = period_label.split('_')
                period_label = f"{parts[0][:4]}年{int(parts[0][5:7])}月 第{parts[1][1:]}周"
            elif scope == 'monthly':
                period_label = f"{period_label[:4]}年{int(period_label[5:7])}月"
            elif scope == 'daily':
                period_label = f"{period_label[:4]}年{int(period_label[5:7])}月{int(period_label[8:10])}日"

            detail_html += f'''
            <div class="history-card">
                <div class="history-header" onclick="toggle(this)">
                    <span class="history-date">{period_label}</span>
                    <span class="history-rate {done_class}">{item['done']}/{item['total']} · {pct}%</span>
                </div>
                <div class="history-body">
                    {tasks_html}
                </div>
            </div>
            '''

    total_pct = round(stats['total_done'] / stats['total_tasks'] * 100, 1) if stats['total_tasks'] else 0

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{REPORT_TITLE}</title>
<style>
{CSS_STYLES}
</style>
</head>
<body>

<h1>{REPORT_TITLE}</h1>
<div class="subtitle">基于任务成就系统历史数据生成 · {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>

<!-- 总览 -->
<div class="card">
    <h2>📊 总体概览</h2>
    <div class="overview-grid">
        <div class="stat-box">
            <div class="stat-num" style="color:#34c759;">{stats['total_done']}</div>
            <div class="stat-label">已完成任务</div>
        </div>
        <div class="stat-box">
            <div class="stat-num" style="color:#ff9500;">{stats['total_tasks']}</div>
            <div class="stat-label">总任务数</div>
        </div>
        <div class="stat-box">
            <div class="stat-num" style="color:#007aff;">{len(months)}</div>
            <div class="stat-label">有记录月份</div>
        </div>
        <div class="stat-box">
            <div class="stat-num" style="color:#af52de;">{total_pct}%</div>
            <div class="stat-label">总完成率</div>
        </div>
    </div>
    <div class="main-progress"><div class="main-fill" style="width:{total_pct}%"></div></div>
</div>

<!-- 各维度 -->
<div class="card">
    <h2>🧭 年度计划各维度进度</h2>
    <div class="cat-grid">
        {cat_html}
    </div>
</div>

<!-- 月度趋势 -->
<div class="card">
    <h2>📈 月度完成率趋势</h2>
    {'<div class="trend-chart">' + bar_html + '</div>' if months else '<div class="empty">暂无月度数据</div>'}
</div>

<!-- 历史明细 -->
<div class="card">
    <h2>📜 历史明细（点击展开）</h2>
    {detail_html if detail_html else '<div class="empty">暂无历史记录</div>'}
</div>

<footer>{REPORT_FOOTER}</footer>

<script>
{JS_SCRIPT}
</script>

</body>
</html>'''

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ 报告已生成: {OUTPUT_PATH}")
    webbrowser.open(f"file:///{OUTPUT_PATH.replace(os.sep, '/')}")