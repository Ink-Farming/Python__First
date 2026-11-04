"""年度计划维度分类配置。

以后要调整分类（关键词、颜色、名称、图标），只改这里。
"""

CATEGORIES = {
    'python': {
        'name': '🔥 Python 学习',
        'color': '#ff9500',
        'bg': 'rgba(255,149,0,0.15)',
        'keywords': ['python', '语法', '变量', '数据类型', '运算符', 'hello world',
                     '练习题', '筑基', '项目', '数据结构']
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
    """根据关键词把任务归入某个维度。"""
    t = text.lower()
    for key, info in CATEGORIES.items():
        if key == 'other':
            continue
        for kw in info['keywords']:
            if kw in t:
                return key
    return 'other'