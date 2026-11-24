"""年度计划维度分类配置。

以后要调整分类（关键词、颜色、名称、图标），只改这里。
"""

CATEGORIES = {
    'skip': {
        'name': '空集',
        'color': '#BDBDBD',            # 浅灰（弱化）
        'bg': 'rgba(189,189,189,0.15)',
        'keywords': ['不']
    },
    'python': {
        'name': '🔥 Python 学习',
        'color': '#FF7A00',            # 橙
        'bg': 'rgba(255,122,0,0.15)',
        'keywords': ['python', '语法', '变量', '数据类型', '运算符', 'hello world',
                     '练习题', '筑基', '项目', '数据结构']
    },
    'career': {
        'name': '🔍 职业方向探索',
        'color': '#7B61FF',            # 靛紫
        'bg': 'rgba(123,97,255,0.15)',
        'keywords': ['职业', '方向', '路线图', '调研', '对比表', '后端', '数据分析', '自动化', '工作']
    },
    'english': {
        'name': '⭐ 英语积累',
        'color': '#0A84FF',            # 蓝
        'bg': 'rgba(10,132,255,0.15)',
        'keywords': ['英语', '单词', '听力', '阅读', 'list', '语感']
    },
    'exercise': {
        'name': '💤 身体锻炼',
        'color': '#1FBF75',            # 绿
        'bg': 'rgba(31,191,117,0.15)',
        'keywords': ['锻炼']
    },
    'music': {
        'name': '🎵 音乐兴趣',
        'color': '#FF3B6B',            # 玫红
        'bg': 'rgba(255,59,107,0.15)',
        'keywords': ['音乐', '钢琴', '竖笛', '唱歌']
    },
    'reading': {
        'name': '📖 阅读',
        'color': '#FFC300',            # 金黄
        'bg': 'rgba(255,195,0,0.15)',
        'keywords': ['阅读', '读书', '书', '文章']
    },
    'coding': {
        'name': '💻 编程练习',
        'color': '#00BCD4',            # 青
        'bg': 'rgba(0,188,212,0.15)',
        'keywords': ['leetcode', '刷题', '算法题', '编程题']
    },
    'learning': {
        'name': '📖 自主练习',
        'color': '#8BC34A',            # 黄绿
        'bg': 'rgba(139,195,74,0.15)',
        'keywords': ['学习', '整理']
    },
    'other': {
        'name': '🌸 其他兴趣',
        'color': '#8E8E93',            # 中性灰
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
