# -*- coding: utf-8 -*-
"""CycleQuest 2.0 本地服务：壳页面 + 任务页 + 补卡 + 工具 + 报告。"""

import glob
import hmac
import html as html_lib
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from collections import OrderedDict, defaultdict
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


# ==================== 路径 ====================
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()
DATA_PATH = os.environ.get('CYCLEQUEST_DATA') or os.path.join(BASE_DIR, 'app_data.json')
BASE_DIR = os.path.dirname(DATA_PATH)
MAKEUP_PATH = os.path.join(BASE_DIR, 'makeup_log.json')
REPORT_PATH = os.path.join(BASE_DIR, 'report.html')
BACKUP_KEEP = 40
REPORT_DIR = resource_path('report')

# 手机只读服务
MOBILE_CODE_PATH = os.path.join(BASE_DIR, 'mobile_code.txt')
MOBILE_PORT = None
MOBILE_HTTPD = None
MOBILE_SESSIONS = {}
MOBILE_FAILS = defaultdict(list)
MOBILE_LOCK = threading.Lock()
MOBILE_SESSION_DAYS = 30
MOBILE_MAX_FAILS = 5
MOBILE_FAIL_WINDOW = 600

LOCK = threading.Lock()
LAST_SEEN = time.time()
QUIT = threading.Event()

if getattr(sys, 'frozen', False) and sys.stdout is None:
    try:
        _log = open(os.path.join(BASE_DIR, 'cyclequest.log'), 'a', encoding='utf-8', buffering=1)
        sys.stdout = _log
        sys.stderr = _log
    except Exception:
        pass

try:
    if sys.stdout is not None:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if sys.stderr is not None:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


# ==================== 数据读写 ====================
class Store:
    def _backup_current(self):
        if not os.path.exists(DATA_PATH):
            return None
        ts = datetime.now().strftime('%Y%m%d-%H%M%S')
        path = os.path.join(BASE_DIR, f'app_data.backup-{ts}.json')
        n = 2
        while os.path.exists(path):
            path = os.path.join(BASE_DIR, f'app_data.backup-{ts}-{n}.json')
            n += 1
        shutil.copy2(DATA_PATH, path)
        return path

    def _rotate(self):
        files = glob.glob(os.path.join(BASE_DIR, 'app_data.backup-*.json'))
        files.sort(key=lambda p: os.path.getmtime(p))
        for old in files[:-BACKUP_KEEP]:
            try:
                os.remove(old)
            except OSError:
                pass

    def save(self, data):
        if not isinstance(data, dict):
            return False
        os.makedirs(BASE_DIR, exist_ok=True)
        self._backup_current()
        self._rotate()
        text = json.dumps(data, ensure_ascii=False, indent=2)
        fd, tmp = tempfile.mkstemp(prefix='.app_data-', suffix='.tmp', dir=BASE_DIR)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(text)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, DATA_PATH)
        except Exception:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise
        return True

    def load(self):
        if not os.path.exists(DATA_PATH):
            return {}
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception as e:
            try:
                ts = datetime.now().strftime('%Y%m%d-%H%M%S')
                shutil.copy2(DATA_PATH, os.path.join(BASE_DIR, f'app_data.corrupt-{ts}.json'))
            except OSError:
                pass
            print(f'[加载失败] {e}')
            return {}

    def backup_now(self):
        return self._backup_current()


store = Store()

KEY_RE = re.compile(r'^quest_(daily|weekly|monthly)_v4_(.+)$')


def parse_value(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return {}
    return value if isinstance(value, dict) else {}


def counts(obj):
    quests = obj.get('quests', []) if isinstance(obj, dict) else []
    done = sum(1 for q in quests if q.get('done'))
    return done, len(quests)


def today_str():
    return date.today().strftime('%Y-%m-%d')


def weekday_limit(day):
    return 3 if day.weekday() >= 5 else 2


# ==================== 补卡 ====================
def read_makeup_log():
    if not os.path.exists(MAKEUP_PATH):
        return {}
    try:
        with open(MAKEUP_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def write_makeup_log(log):
    tmp = MAKEUP_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, MAKEUP_PATH)


def makeup_used(day_str):
    return int(read_makeup_log().get(day_str, 0))


def daily_records(db):
    items = []
    for key, value in db.items():
        m = KEY_RE.match(key)
        if not m or m.group(1) != 'daily':
            continue
        period = m.group(2)
        if len(period) != 10:
            continue
        items.append((period, parse_value(value)))
    items.sort(key=lambda x: x[0])
    return items


def eligible_day(db):
    """最近的一个“还有未完成”的过去日期；必须补完它才能往前。"""
    today = today_str()
    for period, obj in reversed(daily_records(db)):
        if period >= today:
            continue
        done, total = counts(obj)
        if total > 0 and done < total:
            return period, obj
    return None


def undone_quests(obj):
    result = []
    for i, q in enumerate(obj.get('quests', [])):
        if not q.get('done'):
            result.append({
                'id': q.get('id') or f'idx{i}',
                'text': q.get('text', ''),
                'meta': q.get('meta', '')
            })
    return result


DEFAULT_DAILY = [
    {'id': 'd1', 'text': '🔥 四级 25 分钟：听力 1 篇', 'done': False},
    {'id': 'd2', 'text': '🔥 数据结构 20 分钟：补 1 道作业', 'done': False},
    {'id': 'd3', 'text': '💤 动一动 10 分钟', 'done': False},
    {'id': 'd4', 'text': '🌸 音乐 10 分钟', 'done': False},
]


def ensure_today(db):
    """今天还没有记录时，从最近一天的每日任务继承一份（done 全部重置）。"""
    t = today_str()
    key = f'quest_daily_v4_{t}'
    if key in db:
        return False

    source = None
    for period, obj in reversed(daily_records(db)):
        if period < t:
            source = obj
            break

    if source and source.get('quests'):
        quests = []
        for q in source['quests']:
            nq = dict(q)
            nq['done'] = False
            quests.append(nq)
    else:
        quests = [dict(q) for q in DEFAULT_DAILY]

    db[key] = json.dumps({'period': t, 'quests': quests}, ensure_ascii=False)
    store.save(db)
    return True


# ==================== 状态 ====================
def build_state(db):
    today = date.today()
    t_str = today.strftime('%Y-%m-%d')
    limit = weekday_limit(today)
    used = makeup_used(t_str)

    total_done = 0
    total_tasks = 0
    monthly = defaultdict(lambda: {'done': 0, 'total': 0})
    daily_rows = []

    for key, value in db.items():
        m = KEY_RE.match(key)
        if not m:
            continue
        scope, period = m.group(1), m.group(2)
        obj = parse_value(value)
        done, total = counts(obj)
        total_done += done
        total_tasks += total

        if scope == 'daily':
            mk = period[:7]
        elif scope == 'monthly':
            mk = period
        else:
            mk = period.split('_')[0]
        monthly[mk]['done'] += done
        monthly[mk]['total'] += total

        if scope == 'daily' and len(period) == 10 and period <= t_str:
            daily_rows.append({
                'date': period,
                'done': done,
                'total': total,
                'pct': round(done / total * 100) if total else 0
            })

    daily_rows.sort(key=lambda x: x['date'], reverse=True)

    el = eligible_day(db)
    eligible = None
    if el:
        period, obj = el
        eligible = {'date': period, 'quests': undone_quests(obj)}

    backups = glob.glob(os.path.join(BASE_DIR, 'app_data.backup-*.json'))

    return {
        'today': t_str,
        'weekday': today.weekday(),
        'quota': {'limit': limit, 'used': used, 'remaining': max(0, limit - used)},
        'eligible': eligible,
        'totals': {'done': total_done, 'total': total_tasks,
                   'pct': round(total_done / total_tasks * 100, 1) if total_tasks else 0},
        'monthly': {k: monthly[k] for k in sorted(monthly)},
        'daily': daily_rows[:45],
        'records': len([k for k in db if KEY_RE.match(k)]),
        'backups': len(backups),
        'report_time': datetime.fromtimestamp(os.path.getmtime(REPORT_PATH)).strftime('%Y-%m-%d %H:%M')
        if os.path.exists(REPORT_PATH) else None
    }


# ==================== 补全 / 排序 ====================
def monday_of(d):
    return d - timedelta(days=d.weekday())


def weekly_period(d):
    mon = monday_of(d)
    first = mon.replace(day=1)
    first_monday = first + timedelta(days=(7 - first.weekday()) % 7)
    n = (mon - first_monday).days // 7 + 1
    return f'{mon:%Y-%m}_W{n}'


def period_parser(kind):
    if kind == 'daily':
        return lambda p: datetime.strptime(p, '%Y-%m-%d').date()
    if kind == 'monthly':
        return lambda p: datetime.strptime(p + '-01', '%Y-%m-%d').date()
    def weekly(p):
        ym, _, wn = p.partition('_W')
        y, m = map(int, ym.split('-'))
        first = date(y, m, 1)
        first_monday = first + timedelta(days=(7 - first.weekday()) % 7)
        return first_monday + timedelta(weeks=int(wn) - 1)
    return weekly


def period_maker(kind):
    if kind == 'daily':
        return lambda d: d.strftime('%Y-%m-%d')
    if kind == 'monthly':
        return lambda d: d.strftime('%Y-%m')
    return weekly_period


def collect_index(db):
    index = {'daily': {}, 'weekly': {}, 'monthly': {}}
    for key, value in db.items():
        m = KEY_RE.match(key)
        if not m:
            continue
        index[m.group(1)][m.group(2)] = parse_value(value)
    return index


def backfill_preview(db, target=None):
    index = collect_index(db)
    target_date = datetime.strptime(target, '%Y-%m-%d').date() if target else date.today()
    added = {'daily': [], 'weekly': [], 'monthly': []}

    templates = {}
    for kind, periods in index.items():
        if periods:
            newest = max(periods, key=period_parser(kind))
            templates[kind] = periods[newest]

    def missing(kind, period):
        return period not in index[kind]

    if index['daily']:
        cur = min(period_parser('daily')(p) for p in index['daily'])
        while cur <= target_date:
            p = period_maker('daily')(cur)
            if missing('daily', p) and 'daily' in templates:
                added['daily'].append(p)
            cur += timedelta(days=1)

    if index['weekly']:
        cur = monday_of(min(period_parser('weekly')(p) for p in index['weekly']))
        end = monday_of(target_date)
        while cur <= end:
            p = period_maker('weekly')(cur)
            if missing('weekly', p) and 'weekly' in templates:
                added['weekly'].append(p)
            cur += timedelta(weeks=1)

    if index['monthly']:
        cur = min(period_parser('monthly')(p) for p in index['monthly']).replace(day=1)
        end = target_date.replace(day=1)
        while cur <= end:
            p = period_maker('monthly')(cur)
            if missing('monthly', p) and 'monthly' in templates:
                added['monthly'].append(p)
            cur = (cur + timedelta(days=32)).replace(day=1)

    return added, templates, target_date


def backfill_apply(db, target=None):
    added, templates, _ = backfill_preview(db, target)
    for kind in ('daily', 'weekly', 'monthly'):
        tpl = templates.get(kind)
        if not tpl:
            continue
        for period in added[kind]:
            quests = []
            for q in tpl.get('quests', []):
                nq = dict(q)
                nq['done'] = False
                quests.append(nq)
            db[f'quest_{kind}_v4_{period}'] = json.dumps(
                {'period': period, 'quests': quests}, ensure_ascii=False
            )
    return added


def sort_preview(db):
    def sort_key(key):
        m = KEY_RE.match(key)
        if not m:
            return (9999, 12, 31, 9, key)
        kind, period = m.groups()
        try:
            if kind == 'daily':
                d = period_parser('daily')(period)
                return (d.year, d.month, d.day, 0, key)
            if kind == 'weekly':
                d = period_parser('weekly')(period)
                return (d.year, d.month, d.day, 1, key)
            d = period_parser('monthly')(period)
            return (d.year, d.month, 1, 2, key)
        except Exception:
            return (9999, 12, 31, 9, key)

    keys = list(db.keys())
    sorted_keys = sorted(keys, key=sort_key)
    warnings = []
    for key, value in db.items():
        m = KEY_RE.match(key)
        if not m:
            continue
        inner = parse_value(value)
        if inner.get('period') and inner['period'] != m.group(2):
            warnings.append(f'{key} 的 period 是 {inner["period"]}')
    changed = sum(1 for a, b in zip(keys, sorted_keys) if a != b)
    return {'changed': changed, 'warnings': warnings, 'sorted': keys == sorted_keys}


# ==================== 报告 ====================
def generate_report(db):
    if REPORT_DIR not in sys.path:
        sys.path.insert(0, REPORT_DIR)
    import config as report_config
    report_config.OUTPUT_PATH = REPORT_PATH
    import data_loader
    import stats
    import html_generator
    html_generator.webbrowser.open = lambda *a, **k: None

    records = data_loader.parse_records(db)
    result = stats.compute_stats(records)
    html_generator.generate_html(records, result)
    return os.path.exists(REPORT_PATH)


# ==================== 手机只读服务 ====================
def get_mobile_code():
    try:
        if os.path.exists(MOBILE_CODE_PATH):
            with open(MOBILE_CODE_PATH, 'r', encoding='utf-8') as f:
                code = f.read().strip()
            if len(code) >= 6:
                return code
        alphabet = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
        code = ''.join(secrets.choice(alphabet) for _ in range(8))
        with open(MOBILE_CODE_PATH, 'w', encoding='utf-8') as f:
            f.write(code)
        return code
    except Exception as e:
        print(f'[mobile] 访问码生成失败: {e}')
        return 'CYCLEQ'


def lan_ips():
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(('8.8.8.8', 80))
        ips.append(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip not in ips:
                ips.append(ip)
    except Exception:
        pass
    result = []
    for ip in ips:
        if ip.startswith('127.') or ip.startswith('169.254.'):
            continue
        if ip not in result:
            result.append(ip)
    return result


def mobile_payload(db):
    today = date.today()
    t_str = today.strftime('%Y-%m-%d')
    today_obj = parse_value(db.get(f'quest_daily_v4_{t_str}', '{}'))
    t_done, t_total = counts(today_obj)

    week = []
    monday = today - timedelta(days=today.weekday())
    for i in range(7):
        d = monday + timedelta(days=i)
        p = d.strftime('%Y-%m-%d')
        obj = parse_value(db.get(f'quest_daily_v4_{p}', '{}'))
        dn, tt = counts(obj)
        week.append({
            'date': p, 'label': ['一', '二', '三', '四', '五', '六', '日'][i],
            'done': dn, 'total': tt, 'today': p == t_str
        })

    month_key = today.strftime('%Y-%m')
    month_obj = parse_value(db.get(f'quest_monthly_v4_{month_key}', '{}'))
    month_tasks = month_obj.get('quests', [])

    limit = weekday_limit(today)
    used = makeup_used(t_str)
    el = eligible_day(db)

    return {
        'today': t_str,
        'weekday': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][today.weekday()],
        'tasks': today_obj.get('quests', []),
        'done': t_done,
        'total': t_total,
        'pct': round(t_done / t_total * 100) if t_total else 0,
        'quota': {'limit': limit, 'used': used, 'remaining': max(0, limit - used)},
        'eligible': {'date': el[0], 'count': len(undone_quests(el[1]))} if el else None,
        'week': week,
        'month_label': month_key,
        'month_tasks': month_tasks,
        'updated': datetime.now().strftime('%H:%M'),
    }


MOBILE_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
background:#f2f2f7;color:#1d1d1f;line-height:1.55;padding:14px 14px 30px;max-width:560px;margin:0 auto;
width:100%;overflow-x:hidden;padding-bottom:calc(30px + env(safe-area-inset-bottom))}
.head{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px}
.head h1{font-size:20px;letter-spacing:-.02em}
.head .date{font-size:12px;color:#86868b;margin-top:2px}
.ro{font-size:10px;color:#8e8e93;border:1px solid #e5e5ea;background:#fff;border-radius:999px;padding:3px 9px;white-space:nowrap}
.card{background:#fff;border-radius:16px;padding:14px;margin-bottom:11px;box-shadow:0 1px 3px rgba(0,0,0,.05);min-width:0}
.title{font-size:12px;font-weight:700;display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px}
.title small{font-size:10px;font-weight:500;color:#86868b}
.big{font-size:24px;font-weight:800;letter-spacing:-.02em}
.bar{height:7px;background:#ececf1;border-radius:4px;overflow:hidden;margin-top:8px}
.bar i{display:block;height:100%;background:#34c759;border-radius:4px}
.task{display:flex;gap:10px;align-items:flex-start;padding:10px 0;border-bottom:1px solid #f2f2f7}
.task:last-child{border-bottom:0;padding-bottom:0}
.task .ck{flex:0 0 22px;width:22px;height:22px;border-radius:7px;border:1.5px solid #d1d1d6;display:flex;
align-items:center;justify-content:center;font-size:12px;color:transparent;background:#fff;margin-top:1px}
.task.done .ck{background:#34c759;border-color:#34c759;color:#fff}
.task .tx{flex:1;min-width:0;overflow-wrap:anywhere;font-size:13.5px;line-height:1.5}
.task.done .tx{color:#a1a1a6;text-decoration:line-through}
.task .mt{font-size:10.5px;color:#86868b;margin-top:2px}
.mk{display:flex;justify-content:space-between;align-items:center;gap:10px}
.mk b{font-size:20px;flex:0 0 auto}
.week{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:5px;text-align:center;min-width:0}
.day{padding:7px 0;border-radius:9px;background:#fafafa}
.day.today{background:#eef5ff;outline:1.5px solid #007aff}
.day .d{font-size:10px;color:#86868b}
.day .n{font-size:11px;font-weight:700;margin-top:2px}
.note{font-size:10.5px;color:#8e8e93;text-align:center;line-height:1.6;margin-top:6px}
.foot{font-size:9.5px;color:#c7c7cc;text-align:center;margin-top:12px}
.empty{font-size:12px;color:#86868b;padding:6px 0}
form{display:flex;gap:8px;margin-top:10px}
input{flex:1;border:1px solid #d1d1d6;border-radius:10px;padding:11px;font-size:16px;letter-spacing:.18em;
font-family:inherit;text-transform:uppercase;background:#fff;outline:none}
input:focus{border-color:#007aff}
button{border:0;background:#1d1d1f;color:#fff;border-radius:10px;padding:0 16px;font-family:inherit;
font-size:13px;font-weight:600;cursor:pointer}
.err{font-size:12px;color:#ff3b30;margin-top:8px}
"""


def render_mobile_login(error=''):
    err = f'<div class="err">{html_lib.escape(error)}</div>' if error else ''
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>CycleQuest · 手机只读</title><style>{MOBILE_CSS}</style></head><body>
<div class="head"><div><h1>CycleQuest</h1><div class="date">手机只读页</div></div><span class="ro">只读</span></div>
<div class="card"><div class="title">输入访问码</div>
<div class="note" style="text-align:left;margin:0 0 4px">访问码在电脑上：工具 → 手机查看。</div>
<form method="post" action="/m/login"><input name="code" maxlength="12" autocomplete="off" autofocus><button>进入</button></form>
{err}
</div>
<div class="foot">只读页面 · 不能修改数据</div>
</body></html>"""


def render_mobile_page(p):
    tasks = p['tasks']
    if tasks:
        task_html = ''.join(
            f'<div class="task {"done" if q.get("done") else ""}">'
            f'<div class="ck">✓</div><div class="tx">{html_lib.escape(q.get("text", ""))}'
            + (f'<div class="mt">{html_lib.escape(q.get("meta", ""))}</div>' if q.get('meta') else '')
            + '</div></div>'
            for q in tasks
        )
    else:
        task_html = '<div class="empty">今天还没有任务。去电脑上打开一次任务页就会生成。</div>'

    week_html = ''.join(
        f'<div class="day {"today" if d["today"] else ""}"><div class="d">{d["label"]}</div>'
        f'<div class="n">{d["done"]}/{d["total"]}</div></div>'
        for d in p['week']
    )

    if p['month_tasks']:
        month_html = ''.join(
            f'<div class="task {"done" if q.get("done") else ""}"><div class="ck">✓</div>'
            f'<div class="tx">{html_lib.escape(q.get("text", ""))}</div></div>'
            for q in p['month_tasks']
        )
    else:
        month_html = '<div class="empty">本月还没有目标。</div>'

    if p['eligible']:
        el_html = f'最近待补：{p["eligible"]["date"]}，还有 {p["eligible"]["count"]} 项。'
    else:
        el_html = '过去没有待补的任务。'

    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta http-equiv="refresh" content="30">
<title>CycleQuest · 今天</title><style>{MOBILE_CSS}</style></head><body>
<div class="head"><div><h1>今天</h1><div class="date">{p['today']} · {p['weekday']}</div></div><span class="ro">只读</span></div>

<div class="card">
  <div class="title">今日任务 <small>{p['done']}/{p['total']} · {p['pct']}%</small></div>
  <div class="big">{p['done']} / {p['total']}</div>
  <div class="bar"><i style="width:{p['pct']}%"></i></div>
  <div style="margin-top:10px">{task_html}</div>
</div>

<div class="card">
  <div class="title">补卡名额 <small>每天 {p['quota']['limit']} 个</small></div>
  <div class="mk"><span>今天还剩</span><b>{p['quota']['remaining']} 个</b></div>
  <div class="note" style="text-align:left">{el_html} 补卡请在电脑上操作。</div>
</div>

<div class="card">
  <div class="title">本周 <small>一 二 三 四 五 六 日</small></div>
  <div class="week">{week_html}</div>
</div>

<div class="card">
  <div class="title">本月目标 <small>{p['month_label']}</small></div>
  {month_html}
</div>

<div class="foot">只读页面 · 每 30 秒刷新 · 更新于 {p['updated']}<br>完成请在电脑上操作</div>
</body></html>"""


class MobileHandler(BaseHTTPRequestHandler):
    server_version = 'CycleQuestMobile/1.0'

    def log_message(self, fmt, *args):
        pass

    def _send(self, code, body, ctype='text/html; charset=utf-8', extra=None, cookie=None):
        if isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
        self.send_header('Content-Security-Policy',
                         "default-src 'none'; style-src 'unsafe-inline'; img-src data:; form-action 'self'")
        if cookie:
            self.send_header('Set-Cookie', cookie)
        if extra:
            for k, v in extra.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _token(self):
        raw = self.headers.get('Cookie', '') or ''
        for part in raw.split(';'):
            k, _, v = part.strip().partition('=')
            if k == 'cq_m':
                return v
        return None

    def _authed(self):
        token = self._token()
        if not token:
            return False
        with MOBILE_LOCK:
            exp = MOBILE_SESSIONS.get(token)
            if not exp:
                return False
            if exp < time.time():
                MOBILE_SESSIONS.pop(token, None)
                return False
            return True

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/m':
            if not self._authed():
                self._send(401, render_mobile_login())
                return
            db = store.load()
            self._send(200, render_mobile_page(mobile_payload(db)))
            return
        if path == '/m/logout':
            token = self._token()
            if token:
                with MOBILE_LOCK:
                    MOBILE_SESSIONS.pop(token, None)
            self._send(303, '', extra={'Location': '/m'},
                       cookie='cq_m=; Path=/m; HttpOnly; SameSite=Strict; Max-Age=0')
            return
        self._send(404, 'not found', 'text/plain; charset=utf-8')

    def do_POST(self):
        if self.path.split('?', 1)[0] != '/m/login':
            self._send(404, 'not found', 'text/plain; charset=utf-8')
            return

        ip = self.client_address[0]
        now = time.time()
        with MOBILE_LOCK:
            recent = [t for t in MOBILE_FAILS[ip] if now - t < MOBILE_FAIL_WINDOW]
            MOBILE_FAILS[ip] = recent
            if len(recent) >= MOBILE_MAX_FAILS:
                self._send(429, render_mobile_login('尝试次数太多，请 10 分钟后再试。'))
                return

        try:
            n = int(self.headers.get('Content-Length', 0) or 0)
            if n <= 0 or n > 2048:
                raise ValueError('bad length')
            body = self.rfile.read(n).decode('utf-8', 'replace')
            from urllib.parse import parse_qs
            code = (parse_qs(body).get('code', [''])[0] or '').strip().upper()
        except Exception:
            self._send(400, render_mobile_login('请求格式不对。'))
            return

        real = get_mobile_code().upper()
        if not hmac.compare_digest(code, real):
            with MOBILE_LOCK:
                MOBILE_FAILS[ip].append(now)
            self._send(401, render_mobile_login('访问码不对。'))
            return

        token = secrets.token_urlsafe(24)
        with MOBILE_LOCK:
            MOBILE_SESSIONS[token] = now + MOBILE_SESSION_DAYS * 86400
            MOBILE_FAILS[ip] = []
            # 顺手清理过期会话
            for k in [k for k, v in MOBILE_SESSIONS.items() if v < now]:
                MOBILE_SESSIONS.pop(k, None)

        cookie = f'cq_m={token}; Path=/m; HttpOnly; SameSite=Strict; Max-Age={MOBILE_SESSION_DAYS * 86400}'
        self._send(303, '', extra={'Location': '/m'}, cookie=cookie)


def start_mobile_server():
    global MOBILE_PORT, MOBILE_HTTPD
    if MOBILE_HTTPD is not None:
        return MOBILE_PORT
    for port in range(47350, 47361):
        try:
            httpd = ThreadingHTTPServer(('0.0.0.0', port), MobileHandler)
            httpd.daemon_threads = True
            MOBILE_PORT = port
            MOBILE_HTTPD = httpd
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
            print(f'[mobile] 只读服务 0.0.0.0:{port}')
            return port
        except OSError:
            continue
    print('[mobile] 没有可用端口（47350-47360）')
    return None


def stop_mobile_server():
    global MOBILE_PORT, MOBILE_HTTPD
    if MOBILE_HTTPD is not None:
        try:
            MOBILE_HTTPD.shutdown()
            MOBILE_HTTPD.server_close()
        except Exception:
            pass
    MOBILE_HTTPD = None
    MOBILE_PORT = None
    with MOBILE_LOCK:
        MOBILE_SESSIONS.clear()


# ==================== HTTP ====================
class Handler(BaseHTTPRequestHandler):
    server_version = 'CycleQuest/2.0'

    def log_message(self, fmt, *args):
        pass

    def _send(self, code, body, ctype='application/json; charset=utf-8', extra=None):
        if isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        if extra:
            for k, v in extra.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def _body(self):
        n = int(self.headers.get('Content-Length', 0) or 0)
        if n <= 0:
            return {}
        return json.loads(self.rfile.read(n).decode('utf-8'))

    def _file(self, path, ctype):
        try:
            with open(path, 'rb') as f:
                self._send(200, f.read(), ctype)
        except Exception as e:
            self._send(404, f'not found: {e}', 'text/plain; charset=utf-8')

    def do_GET(self):
        global LAST_SEEN
        LAST_SEEN = time.time()
        path = self.path.split('?', 1)[0]

        if path in ('/', '/index.html'):
            self._file(resource_path('shell.html'), 'text/html; charset=utf-8')
        elif path in ('/app', '/app/'):
            self._file(resource_path('app.html'), 'text/html; charset=utf-8')
        elif path == '/api/state':
            with LOCK:
                db = store.load()
                ensure_today(db)
            self._json(200, {'data': db, 'meta': build_state(db)})
        elif path == '/api/quest/load':
            with LOCK:
                db = store.load()
                ensure_today(db)
            self._json(200, db)
        elif path == '/report/view':
            if not os.path.exists(REPORT_PATH):
                self._file(resource_path('shell.html'), 'text/html; charset=utf-8')
            else:
                self._file(REPORT_PATH, 'text/html; charset=utf-8')
        elif path == '/api/ping':
            self._json(200, {'ok': True})
        elif path == '/api/mobile/export-today':
            with LOCK:
                db = store.load()
                ensure_today(db)
            day = today_str()
            obj = parse_value(db.get(f'quest_daily_v4_{day}', '{}'))
            tasks = []
            for i, q in enumerate(obj.get('quests', [])):
                tasks.append({
                    'id': q.get('id') or f'idx{i}',
                    'text': q.get('text', ''),
                    'meta': q.get('meta', ''),
                    'done': bool(q.get('done'))
                })
            payload = {'app': 'CycleQuestPC', 'version': 1, 'date': day,
                       'tasks': tasks, 'void_ids': []}
            text = json.dumps(payload, ensure_ascii=False, indent=2)
            self._send(200, text, 'application/json; charset=utf-8',
                       extra={'Content-Disposition': f'attachment; filename="cyclequest-today-{day}.json"'})
        elif path == '/api/pair-info':
            if self.client_address[0] not in ('127.0.0.1', '::1'):
                self._json(403, {'ok': False, 'error': 'local only'})
                return
            ips = lan_ips()
            code = get_mobile_code()
            self._json(200, {
                'ok': True,
                'running': MOBILE_HTTPD is not None,
                'port': MOBILE_PORT,
                'code': code,
                'urls': [f'http://{ip}:{MOBILE_PORT}/m' for ip in ips] if MOBILE_PORT else []
            })
        else:
            self._json(404, {'error': 'not found'})

    def do_POST(self):
        global LAST_SEEN
        LAST_SEEN = time.time()
        path = self.path.split('?', 1)[0]

        try:
            body = self._body()
        except Exception as e:
            self._json(400, {'ok': False, 'error': str(e)})
            return

        if path == '/api/save':
            data = body.get('data') if isinstance(body.get('data'), dict) else body
            with LOCK:
                ok = store.save(data)
            self._json(200 if ok else 500, {'ok': ok})
            return

        if path == '/api/makeup':
            self._json(200, self._makeup(body))
            return

        if path == '/api/tools/backfill':
            self._json(200, self._backfill(body))
            return

        if path == '/api/tools/sort':
            self._json(200, self._sort(body))
            return

        if path == '/api/backup':
            with LOCK:
                p = store.backup_now()
            self._json(200, {'ok': bool(p), 'path': p, 'backups': len(glob.glob(os.path.join(BASE_DIR, 'app_data.backup-*.json')))})
            return

        if path == '/api/mobile/import-done':
            if self.client_address[0] not in ('127.0.0.1', '::1'):
                self._json(403, {'ok': False, 'error': 'local only'})
                return
            if body.get('app') != 'CycleQuestMobile':
                self._json(400, {'ok': False, 'error': '不是手机导出的 done.json'})
                return
            day = body.get('date')
            ids = body.get('done_ids')
            if day != today_str():
                self._json(400, {'ok': False, 'error': '只接受今天的完成记录'})
                return
            if not isinstance(ids, list) or len(ids) > 200:
                self._json(400, {'ok': False, 'error': 'done_ids 格式不对'})
                return

            with LOCK:
                db = store.load()
                ensure_today(db)
                key = f'quest_daily_v4_{day}'
                obj = parse_value(db.get(key, '{}'))
                quests = obj.get('quests', [])
                by_id = {(q.get('id') or f'idx{i}'): q for i, q in enumerate(quests)}

                applied = already = skipped = 0
                for qid in ids:
                    q = by_id.get(str(qid))
                    if q is None or q.get('void'):
                        skipped += 1
                        continue
                    if q.get('done'):
                        already += 1
                        continue
                    q['done'] = True
                    applied += 1

                db[key] = json.dumps(obj, ensure_ascii=False)
                store.save(db)
                state = build_state(db)

            self._json(200, {'ok': True, 'applied': applied, 'already': already,
                             'skipped': skipped, 'meta': state})
            return

        if path == '/api/mobile/start':
            if self.client_address[0] not in ('127.0.0.1', '::1'):
                self._json(403, {'ok': False, 'error': 'local only'})
                return
            port = start_mobile_server()
            self._json(200, {'ok': bool(port), 'port': port})
            return

        if path == '/api/mobile/stop':
            if self.client_address[0] not in ('127.0.0.1', '::1'):
                self._json(403, {'ok': False, 'error': 'local only'})
                return
            stop_mobile_server()
            self._json(200, {'ok': True})
            return

        if path == '/api/report':
            with LOCK:
                ok = generate_report(store.load())
            self._json(200, {'ok': ok, 'url': '/report/view?t=' + str(int(time.time()))})
            return

        if path == '/api/heartbeat':
            self._json(200, {'ok': True})
            return

        if path == '/api/quit':
            QUIT.set()
            self._json(200, {'ok': True})
            return

        self._json(404, {'error': 'not found'})

    # ---------- 补卡 ----------
    def _makeup(self, body):
        day = body.get('date', '')
        ids = body.get('ids') or []
        with LOCK:
            db = store.load()
            el = eligible_day(db)
            if not el or el[0] != day:
                return {'ok': False, 'error': '只能补最近一个还有未完成的日期'}
            obj = el[1]
            remaining = weekday_limit(date.today()) - makeup_used(today_str())
            if remaining <= 0:
                return {'ok': False, 'error': '今天的补卡名额用完了'}
            if len(ids) > remaining:
                return {'ok': False, 'error': f'今天只剩 {remaining} 个名额'}

            undone = {q.get('id'): q for q in obj.get('quests', []) if not q.get('done')}
            chosen = [undone[i] for i in ids if i in undone]
            if len(chosen) != len(ids) or not chosen:
                return {'ok': False, 'error': '任务已变化，请刷新后重试'}

            for q in chosen:
                q['done'] = True

            for key, value in list(db.items()):
                m = KEY_RE.match(key)
                if m and m.group(1) == 'daily' and m.group(2) == day:
                    db[key] = json.dumps(obj, ensure_ascii=False)
                    break

            store.save(db)
            log = read_makeup_log()
            log[today_str()] = log.get(today_str(), 0) + len(chosen)
            write_makeup_log(log)

            return {'ok': True, 'data': db, 'meta': build_state(db)}

    # ---------- 补全 ----------
    def _backfill(self, body):
        mode = body.get('mode', 'preview')
        target = body.get('target') or None
        with LOCK:
            db = store.load()
            added, templates, target_date = backfill_preview(db, target)
            if mode == 'apply':
                backfill_apply(db, target)
                store.save(db)
                return {'ok': True, 'added': added, 'target': str(target_date),
                        'data': db, 'meta': build_state(db)}
            return {'ok': True, 'added': added, 'target': str(target_date),
                    'total': sum(len(v) for v in added.values())}

    # ---------- 排序 ----------
    def _sort(self, body):
        mode = body.get('mode', 'preview')
        with LOCK:
            db = store.load()
            info = sort_preview(db)
            if mode == 'apply':
                def sort_key(key):
                    m = KEY_RE.match(key)
                    if not m:
                        return (9999, 12, 31, 9, key)
                    kind, period = m.groups()
                    try:
                        if kind == 'daily':
                            d = period_parser('daily')(period)
                            return (d.year, d.month, d.day, 0, key)
                        if kind == 'weekly':
                            d = period_parser('weekly')(period)
                            return (d.year, d.month, d.day, 1, key)
                        d = period_parser('monthly')(period)
                        return (d.year, d.month, 1, 2, key)
                    except Exception:
                        return (9999, 12, 31, 9, key)
                db = dict(sorted(db.items(), key=lambda kv: sort_key(kv[0])))
                store.save(db)
                return {'ok': True, 'data': db, 'meta': build_state(db), **info}
            return {'ok': True, **info}


def start_server():
    for port in range(47321, 47341):
        try:
            httpd = ThreadingHTTPServer(('127.0.0.1', port), Handler)
            httpd.daemon_threads = True
            return httpd, port
        except OSError:
            continue
    raise RuntimeError('没有可用端口')


def find_edge():
    candidates = [
        os.path.expandvars(r'%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe'),
        os.path.expandvars(r'%ProgramFiles%\Microsoft\Edge\Application\msedge.exe'),
        os.path.expandvars(r'%LocalAppData%\Microsoft\Edge\Application\msedge.exe'),
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return None


def open_window(url):
    edge = find_edge()
    if edge:
        profile = os.path.join(tempfile.gettempdir(), 'cyclequest2-edge-profile')
        try:
            subprocess.Popen([
                edge, f'--app={url}', '--window-size=560,860',
                f'--user-data-dir={profile}', '--no-first-run', '--no-default-browser-check'
            ])
            return
        except Exception as e:
            print(f'[edge] {e}')
    webbrowser.open(url)


def main():
    global LAST_SEEN
    httpd, port = start_server()
    url = f'http://127.0.0.1:{port}/'
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    print(f'[服务] {url}')
    if not os.environ.get('CYCLEQUEST_NO_WINDOW'):
        open_window(url)

    LAST_SEEN = time.time()
    while not QUIT.is_set():
        time.sleep(1)
        if time.time() - LAST_SEEN > 300:
            break
    httpd.shutdown()


if __name__ == '__main__':
    main()
