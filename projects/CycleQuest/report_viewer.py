import json
import os
import sys
import webbrowser
from datetime import datetime
from collections import defaultdict
from html import escape

# ==================== 路径 ====================
def get_data_path(filename='app_data.json'):
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)

DATA_PATH = get_data_path()
OUTPUT_PATH = os.path.join(os.path.dirname(DATA_PATH), 'report.html')

# ==================== 年度计划维度分类 ====================
CATEGORIES = {
    'python': {
        'name': '🔥 Python 学习',
        'color': '#ff9500',
        'bg': 'rgba(255,149,0,0.15)',
        'keywords': ['python', '语法', '变量', '数据类型', '运算符', 'hello world', '练习题', '筑基', '项目', '数据结构']
    },
    'career': {
        'name': '🔍 职业方向探索',
        'color': '#af52de',
        'bg': 'rgba(175,82,222,0.15)',
        'keywords': ['职业', '方向', '路线图', '调研', '对比表', '后端', '数据分析', '自动化', '工作']
    },
    'english': {
        'name': '⭐ 英语积累',
        'color': '#007aff',
        'bg': 'rgba(0,122,255,0.15)',
        'keywords': ['英语', '单词', '听力', '阅读', 'list', '语感']
    },
    'exercise': {
        'name': '💤 身体锻炼',
        'color': '#34c759',
        'bg': 'rgba(52,199,89,0.15)',
        'keywords': ['锻炼']
    },
    'music': {
        'name': '🎵 音乐兴趣',
        'color': '#ff2d55',
        'bg': 'rgba(255,45,85,0.15)',
        'keywords': ['音乐', '钢琴', '竖笛', '唱歌']
    },
    'exam': {
        'name': '📚 软考准备',
        'color': '#5ac8fa',
        'bg': 'rgba(90,200,250,0.15)',
        'keywords': ['软考', '软工']
    },
    'reading': {
        'name': '📖 阅读',
        'color': '#ffcc00',
        'bg': 'rgba(255,204,0,0.15)',
        'keywords': ['阅读', '读书', '书', '文章']
    },
    'coding': {
        'name': '💻 编程练习',
        'color': '#00c7be',
        'bg': 'rgba(0,199,190,0.15)',
        'keywords': ['leetcode', '刷题', '算法题', '编程题']
    },
    'other': {
        'name': '🌸 其他兴趣',
        'color': '#8e8e93',
        'bg': 'rgba(142,142,147,0.15)',
        'keywords': []
    }
}

def classify_task(text):
    t = text.lower()
    for key, info in CATEGORIES.items():
        if key == 'other':
            continue
        for kw in info['keywords']:
            if kw in t:
                return key
    return 'other'

# ==================== 数据读取 ====================
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
        except:
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
    
    # 排序
    for scope in records:
        records[scope].sort(key=lambda x: x['date_sort'], reverse=True)
    return records

# ==================== 统计计算 ====================
def compute_stats(records):
    # 按月份聚合 (YYYY-MM)
    monthly = defaultdict(lambda: {'done': 0, 'total': 0, 'cat': defaultdict(lambda: {'done': 0, 'total': 0})})
    
    # 所有记录汇总
    all_cat = defaultdict(lambda: {'done': 0, 'total': 0, 'tasks':[]})#新增tasks保留详细任务/计划
    total_done = 0
    total_tasks = 0
    
    for scope, items in records.items():
        for item in items:
            # 提取月份
            p = item['period']
            if '_W' in p:
                month_key = p.split('_')[0]
            elif len(p) == 7 and '-' in p:  # YYYY-MM
                month_key = p
            elif len(p) == 10:  # YYYY-MM-DD
                month_key = p[:7]
            else:
                month_key = p[:7] if len(p) >= 7 else p
            
            monthly[month_key]['done'] += item['done']
            monthly[month_key]['total'] += item['total']
            
            for cat, st in item['cat_stats'].items():
                monthly[month_key]['cat'][cat]['done'] += st['done']
                monthly[month_key]['cat'][cat]['total'] += st['total']
                all_cat[cat]['done'] += st['done']
                all_cat[cat]['total'] += st['total']

            for q in item['quests']:
                text = q.get('text','')
                done = bool(q.get('done'))
                cat = classify_task(text)
                all_cat[cat]['total'] += 1
                if done:
                    all_cat[cat]['done'] += 1
                all_cat[cat]['tasks'].append({
                    'text':text,
                    'done':done,
                    'scope':scope,
                    'period':item['period'],
                })
                
            total_done += item['done']
            total_tasks += item['total']

    for cat in all_cat:
        all_cat[cat]['tasks'].sort(key=lambda t: t['period'],reverse = True)
        
    # 排序月份
    sorted_months = sorted(monthly.keys())
    
    return {
        'monthly': {k: monthly[k] for k in sorted_months},
        'all_cat': dict(all_cat),
        'total_done': total_done,
        'total_tasks': total_tasks
    }

# ==================== HTML 生成 ====================
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
        month_rates.append(round(d/t*100, 1) if t else 0)
    
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
    for i, (m, rate) in enumerate(zip(months, month_rates)):
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
    # 按 scope 分组展示
    scope_names = {'daily': '📅 每日记录', 'weekly': '📆 每周记录', 'monthly': '🗓️ 每月记录'}
    for scope in ['monthly', 'weekly', 'daily']:
        items = records[scope]
        if not items:
            continue
        detail_html += f'<h3 class="scope-title">{scope_names[scope]}</h3>'
        for item in items:
            pct = round(item['done']/item['total']*100) if item['total'] else 0
            done_class = 'done' if pct == 100 else ''
            
            # 任务列表
            tasks_html = ''
            for q in item['quests']:
                cat = classify_task(q.get('text', ''))
                color = CATEGORIES.get(cat, CATEGORIES['other'])['color']
                check = '✅' if q.get('done') else '⬜'
                strike = 'style="text-decoration:line-through; opacity:0.5;"' if q.get('done') else ''
                tasks_html += f'<div class="task-line" {strike}><span style="color:{color}">{check}</span> {q.get("text", "")}</div>'
            
            # 周期标签美化
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

    total_pct = round(stats['total_done']/stats['total_tasks']*100, 1) if stats['total_tasks'] else 0
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>🎯 年度计划执行报告</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #0f0f1a; color: #e0e0e0;
    padding: 24px; max-width: 900px; margin: 0 auto;
    line-height: 1.6;
}}
h1 {{ font-size: 28px; margin-bottom: 8px; background: linear-gradient(90deg, #ff9500, #af52de); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.subtitle {{ color: #8e8e93; font-size: 14px; margin-bottom: 24px; }}

.card {{
    background: #1a1a2e;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    border: 1px solid #2a2a3e;
}}
.card h2 {{ font-size: 18px; margin-bottom: 16px; color: #fff; display: flex; align-items: center; gap: 8px; }}

/* 总览 */
.overview-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 16px;
    margin-bottom: 20px;
}}
.stat-box {{
    text-align: center;
    padding: 16px;
    background: #0f0f1a;
    border-radius: 12px;
}}
.stat-num {{ font-size: 32px; font-weight: 700; color: #fff; }}
.stat-label {{ font-size: 12px; color: #8e8e93; margin-top: 4px; }}
.main-progress {{
    width: 100%; height: 10px;
    background: #2a2a3e;
    border-radius: 5px;
    overflow: hidden;
    margin-top: 8px;
}}
.main-fill {{
    height: 100%;
    background: linear-gradient(90deg, #ff9500, #af52de);
    border-radius: 5px;
    transition: width 1s ease;
}}

/* 维度卡片 */
.cat-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
}}
.cat-card {{
    padding: 16px;
    border-radius: 12px;
    position: relative;
}}
.cat-name {{ font-size: 14px; font-weight: 600; margin-bottom: 8px; }}
.cat-num {{ font-size: 12px; color: #8e8e93; margin-bottom: 8px; }}
.mini-bar {{
    width: 100%; height: 6px;
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
    overflow: hidden;
}}
.mini-fill {{ height: 100%; border-radius: 3px; transition: width 1s ease; }}
.cat-pct {{ font-size: 20px; font-weight: 700; margin-top: 8px; text-align: right; }}

/* 趋势图 */
.trend-chart {{
    display: flex;
    align-items: flex-end;
    gap: 12px;
    height: 160px;
    padding: 20px 0 30px;
    border-bottom: 1px solid #2a2a3e;
    position: relative;
}}
.trend-col {{
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
}}
.trend-bar-wrap {{
    width: 100%;
    height: 120px;
    display: flex;
    align-items: flex-end;
    justify-content: center;
}}
.trend-bar {{
    width: 100%;
    max-width: 40px;
    background: linear-gradient(180deg, #007aff, #5ac8fa);
    border-radius: 6px 6px 0 0;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 4px;
    font-size: 11px;
    font-weight: 600;
    color: #fff;
    transition: height 1s ease;
}}
.trend-label {{
    font-size: 11px;
    color: #8e8e93;
    white-space: nowrap;
}}

/* 历史明细 */
.scope-title {{
    font-size: 16px;
    color: #fff;
    margin: 24px 0 12px;
    padding-left: 12px;
    border-left: 3px solid #af52de;
}}
.history-card {{
    background: #0f0f1a;
    border-radius: 12px;
    margin-bottom: 10px;
    overflow: hidden;
    border: 1px solid #2a2a3e;
}}
.history-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 18px;
    cursor: pointer;
    transition: background 0.2s;
    user-select: none;
}}
.history-header:hover {{ background: #1a1a2e; }}
.history-date {{ font-weight: 600; font-size: 14px; }}
.history-rate {{
    font-size: 13px;
    padding: 4px 10px;
    border-radius: 10px;
    background: #2a2a3e;
    color: #8e8e93;
}}
.history-rate.done {{ background: #1a3a1a; color: #34c759; }}
.history-body {{
    padding: 0 18px 14px;
    display: none;
    border-top: 1px dashed #2a2a3e;
    margin-top: 0;
    padding-top: 12px;
}}
.history-body.open {{ display: block; }}
.task-line {{
    font-size: 13px;
    padding: 4px 0;
    color: #c7c7cc;
}}

/* 空状态 */
.empty {{ text-align: center; color: #555; padding: 40px; font-size: 14px; }}

footer {{
    text-align: center;
    color: #555;
    font-size: 12px;
    margin-top: 40px;
    padding-bottom: 20px;
}}
/* 维度卡片展开 */
.cat-grid {{ align-items: start; }}
.cat-summary {{ cursor: pointer; user-select: none; }}
.cat-summary:hover {{ filter: brightness(1.15); }}
.cat-name {{ display: flex; justify-content: space-between; align-items: center; }}
.cat-name::after {{
    content: '▾';
    font-size: 10px;
    color: #8e8e93;
    transition: transform 0.2s;
}}
.cat-card.open .cat-name::after {{ transform: rotate(180deg); }}
.cat-detail {{
    display: none;
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px dashed rgba(255,255,255,0.12);
    max-height: 260px;
    overflow-y: auto;
}}
.cat-card.open .cat-detail {{ display: block; }}
.cat-task {{
    display: flex;
    gap: 8px;
    padding: 6px 0;
    font-size: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}}
.cat-task:last-child {{ border-bottom: none; }}
.cat-task.done .task-text {{ text-decoration: line-through; opacity: 0.5; }}
.task-meta {{ flex-shrink: 0; min-width: 76px; color: #8e8e93; font-size: 11px; }}
.task-text {{ flex: 1; color: #c7c7cc; word-break: break-word; }}
.cat-empty {{ font-size: 12px; color: #555; text-align: center; padding: 8px; }}</style>
</head>
<body>

<h1>🎯 年度计划执行报告</h1>
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

<footer>由 年度计划历史查看器 自动生成</footer>

<script>
function toggle(header) {{
    const body = header.nextElementSibling;
    body.classList.toggle('open');
}}
// 默认展开第一个
document.querySelectorAll('.history-header').forEach((h, i) => {{
    if (i === 0) h.click();
}});

function toggleCat(summary) {{
    summary.parentElement.classList.toggle('open');
}}
</script>

</body>
</html>'''
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 报告已生成: {OUTPUT_PATH}")
    webbrowser.open(f"file:///{OUTPUT_PATH.replace(os.sep, '/')}")

# ==================== 主程序 ====================
def main():
    print("📂 正在读取历史数据...")
    raw = load_data()
    print("📊 正在分析数据...")
    records = parse_records(raw)
    stats = compute_stats(records)
    print("🎨 正在生成报告...")
    generate_html(records, stats)
    print("✨ 完成！")
    input("按回车退出...")

if __name__ == '__main__':
    main()
