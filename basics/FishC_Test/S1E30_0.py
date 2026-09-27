#0. 编写一个程序，统计当前目录下每个文件类型的文件数
from pathlib import Path

# 获取当前脚本所在目录，或者你可以用 Path(".")
base_dir = Path(".")

# 创建一个字典用来保存统计结果
# 格式预计为：{'.txt': 1, '.png': 2, '文件夹': 2}
counts = {}

# 遍历当前目录下所有内容
for p in base_dir.iterdir():
    
    # 【关键点】判断是否是文件夹
    if p.is_dir():
        category = "文件夹"
    # 如果是文件
    elif p.is_file():
        # 获取后缀名（例如 .txt），并转为小写
        ext = p.suffix.lower()
        # 如果没有后缀名（比如 README），单独归类
        if not ext:
            category = "无后缀文件"
        else:
            category = ext
    else:
        # 忽略无法识别的特殊文件（如快捷方式、设备文件等）
        continue
        
    # 字典计数的经典套路：get(键, 默认值0) + 1
    counts[category] = counts.get(category, 0) + 1

# 遍历字典，格式化输出结果
for category, count in counts.items():
    print(f"该文件夹下共有类型为【{category}】的文件 {count} 个")
