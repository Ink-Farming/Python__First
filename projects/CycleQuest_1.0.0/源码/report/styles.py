"""报告前端资源：CSS 样式与 JS 脚本。

以后要调整生成的 HTML 的样式（颜色、布局、动画等），只改这个文件。
"""

CSS_STYLES = """
* { margin:0; padding:0; box-sizing:border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #0f0f1a; color: #e0e0e0;
    padding: 24px; max-width: 900px; margin: 0 auto;
    line-height: 1.6;
}
h1 { font-size: 28px; margin-bottom: 8px; background: linear-gradient(90deg, #ff9500, #af52de); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.subtitle { color: #8e8e93; font-size: 14px; margin-bottom: 24px; }

.card {
    background: #1a1a2e;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    border: 1px solid #2a2a3e;
}
.card h2 { font-size: 18px; margin-bottom: 16px; color: #fff; display: flex; align-items: center; gap: 8px; }

/* 总览 */
.overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 16px;
    margin-bottom: 20px;
}
.stat-box {
    text-align: center;
    padding: 16px;
    background: #0f0f1a;
    border-radius: 12px;
}
.stat-num { font-size: 32px; font-weight: 700; color: #fff; }
.stat-label { font-size: 12px; color: #8e8e93; margin-top: 4px; }
.main-progress {
    width: 100%; height: 10px;
    background: #2a2a3e;
    border-radius: 5px;
    overflow: hidden;
    margin-top: 8px;
}
.main-fill {
    height: 100%;
    background: linear-gradient(90deg, #ff9500, #af52de);
    border-radius: 5px;
    transition: width 1s ease;
}

/* 维度卡片 */
.cat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    align-items: start;
}
.cat-card {
    padding: 16px;
    border-radius: 12px;
    position: relative;
}
.cat-name { font-size: 14px; font-weight: 600; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
.cat-name::after {
    content: '▾';
    font-size: 10px;
    color: #8e8e93;
    transition: transform 0.2s;
}
.cat-card.open .cat-name::after { transform: rotate(180deg); }
.cat-num { font-size: 12px; color: #8e8e93; margin-bottom: 8px; }
.mini-bar {
    width: 100%; height: 6px;
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
    overflow: hidden;
}
.mini-fill { height: 100%; border-radius: 3px; transition: width 1s ease; }
.cat-pct { font-size: 20px; font-weight: 700; margin-top: 8px; text-align: right; }

/* 维度卡片展开 */
.cat-summary { cursor: pointer; user-select: none; }
.cat-summary:hover { filter: brightness(1.15); }
.cat-detail {
    display: none;
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px dashed rgba(255,255,255,0.12);
    max-height: 260px;
    overflow-y: auto;
}
.cat-card.open .cat-detail { display: block; }
.cat-task {
    display: flex;
    gap: 8px;
    padding: 6px 0;
    font-size: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.cat-task:last-child { border-bottom: none; }
.cat-task.done .task-text { text-decoration: line-through; opacity: 0.5; }
.task-meta { flex-shrink: 0; min-width: 76px; color: #8e8e93; font-size: 11px; }
.task-text { flex: 1; color: #c7c7cc; word-break: break-word; }
.cat-empty { font-size: 12px; color: #555; text-align: center; padding: 8px; }

/* 趋势图 */
.trend-chart {
    display: flex;
    align-items: flex-end;
    gap: 12px;
    height: 160px;
    padding: 20px 0 30px;
    border-bottom: 1px solid #2a2a3e;
    position: relative;
}
.trend-col {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
}
.trend-bar-wrap {
    width: 100%;
    height: 120px;
    display: flex;
    align-items: flex-end;
    justify-content: center;
}
.trend-bar {
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
}
.trend-label {
    font-size: 11px;
    color: #8e8e93;
    white-space: nowrap;
}

/* 历史明细 */
.scope-title {
    font-size: 16px;
    color: #fff;
    margin: 24px 0 12px;
    padding-left: 12px;
    border-left: 3px solid #af52de;
}
.history-card {
    background: #0f0f1a;
    border-radius: 12px;
    margin-bottom: 10px;
    overflow: hidden;
    border: 1px solid #2a2a3e;
}
.history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 18px;
    cursor: pointer;
    transition: background 0.2s;
    user-select: none;
}
.history-header:hover { background: #1a1a2e; }
.history-date { font-weight: 600; font-size: 14px; }
.history-rate {
    font-size: 13px;
    padding: 4px 10px;
    border-radius: 10px;
    background: #2a2a3e;
    color: #8e8e93;
}
.history-rate.done { background: #1a3a1a; color: #34c759; }
.history-body {
    padding: 0 18px 14px;
    display: none;
    border-top: 1px dashed #2a2a3e;
    margin-top: 0;
    padding-top: 12px;
}
.history-body.open { display: block; }
.task-line {
    font-size: 13px;
    padding: 4px 0;
    color: #c7c7cc;
}

/* 空状态 */
.empty { text-align: center; color: #555; padding: 40px; font-size: 14px; }

footer {
    text-align: center;
    color: #555;
    font-size: 12px;
    margin-top: 40px;
    padding-bottom: 20px;
}
"""

JS_SCRIPT = """
function toggle(header) {
    const body = header.nextElementSibling;
    body.classList.toggle('open');
}
// 默认展开第一个
document.querySelectorAll('.history-header').forEach((h, i) => {
    if (i === 0) h.click();
});

function toggleCat(summary) {
    summary.parentElement.classList.toggle('open');
}
"""