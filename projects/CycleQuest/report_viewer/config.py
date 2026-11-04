"""全局配置：文件路径、文件名、报告标题等。

以后要改数据文件名、报告输出文件名、报告标题，只改这里。
"""
import os
import sys

# ==================== 文件名配置 ====================
DATA_FILENAME = 'app_data.json'      # 输入的数据文件
REPORT_FILENAME = 'report.html'      # 生成的报告文件

# ==================== 报告文案 ====================
REPORT_TITLE = '🎯 年度计划执行报告'
REPORT_FOOTER = '由 年度计划历史查看器 自动生成'

# ==================== 路径计算（支持 PyInstaller 打包）====================
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()
DATA_PATH = os.path.join(BASE_DIR, DATA_FILENAME)
OUTPUT_PATH = os.path.join(BASE_DIR, REPORT_FILENAME)