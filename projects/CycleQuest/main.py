import webview
import os
import sys
import json
from datetime import datetime, timedelta

# ==================== 路径处理 ====================
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def get_data_path(filename='app_data.json'):
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)

DATA_PATH = get_data_path()

# ==================== 暴露给 JS 的 API ====================
class Api:
    def save_all_data(self, payload):
        try:
            with open(DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            print(f"[保存成功] {DATA_PATH}")
            return True
        except Exception as e:
            print(f"[保存失败] {e}")
            return False
    
    def load_all_data(self):
        try:
            if os.path.exists(DATA_PATH):
                with open(DATA_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[加载失败] {e}")
        return {}
    
    def enable_debug_skip(self):
        try:
            debug_file = os.path.join(os.path.dirname(DATA_PATH), '.debug_skip')
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            d = datetime.now()
            
            # 计算本周一
            day = d.weekday()  # Monday=0, Sunday=6
            monday = d - timedelta(days=day)
            
            # 计算本月第几周（按周一所在周计算）
            first_day = monday.replace(day=1)
            first_weekday = first_day.weekday() + 1  # 转为 1-7（周一=1，周日=7）
            days_in_first_week = 8 - first_weekday
            monday_date = monday.day
            
            if monday_date <= days_in_first_week:
                week_num = 1
            else:
                week_num = ((monday_date - days_in_first_week - 1) // 7) + 2
            
            frozen_weekly = monday.strftime('%Y-%m') + f'_W{week_num}'
            
            info = {
                "activated": today,
                "frozen_daily": yesterday,
                "frozen_weekly": frozen_weekly,
                "frozen_monthly": d.strftime('%Y-%m')
            }
            with open(debug_file, 'w', encoding='utf-8') as f:
                json.dump(info, f)
            print(f"[调试模式启用] {info}")
            return True
        except Exception as e:
            print(f"[调试模式失败] {e}")
            return False
    
    def get_debug_info(self):
        debug_file = os.path.join(os.path.dirname(DATA_PATH), '.debug_skip')
        if not os.path.exists(debug_file):
            return None
        try:
            with open(debug_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
            today = datetime.now().strftime('%Y-%m-%d')
            if info.get('activated') != today:
                os.remove(debug_file)
                print("[调试模式] 已过期，自动清除并回归正常日期")
                return None
            return info
        except Exception as e:
            return None
    
    def disable_debug_skip(self):
        debug_file = os.path.join(os.path.dirname(DATA_PATH), '.debug_skip')
        if os.path.exists(debug_file):
            os.remove(debug_file)
        return True

api = Api()

# ==================== 主程序 ====================
def main():
    window = webview.create_window(
        '每日任务成就系统',
        resource_path("app.html"),
        width=520,
        height=780,
        resizable=False,
        text_select=False,
        js_api=api
    )
    
    def on_closing():
        print("窗口关闭")
    
    window.events.closing += on_closing
    webview.start(debug=False)

if __name__ == '__main__':
    main()
