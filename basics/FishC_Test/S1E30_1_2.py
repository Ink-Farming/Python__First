import os

base_dir = "."
counts = {}

for name in os.listdir(base_dir):
    full_path = os.path.join(base_dir, name)
    
    if os.path.isdir(full_path):
        category = "文件夹"
    elif os.path.isfile(full_path):
        ext = os.path.splitext(name)[1].lower()  # os模块切割后缀的方法
        if not ext:
            category = "无后缀文件"
        else:
            category = ext
    else:
        continue
        
    counts[category] = counts.get(category, 0) + 1

for category, count in counts.items():
    print(f"该文件夹下共有类型为【{category}】的文件 {count} 个")
