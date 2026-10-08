#计算大小
from pathlib import Path

def format_size(size):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    for unit in units:
        if size < 1024:
            return f"{size:>8.2f} {unit:<2}"
        size /= 1024
    return f"{size:>8.2f} PB"

root = Path(".")
total = 0
files = []

for p in root.rglob("*"):
    if p.is_file():
        size = p.stat().st_size
        total += size
        files.append((size, p))

if not files:
    print("没有文件")
else:
    max_name_len = max(len(str(p)) for _, p in files)
    print("-" * (max_name_len + 40))
    for size, p in files:
        name = str(p)
        print(f"| 文件大小: [{format_size(size)}] | 文件名: 【{name:<{max_name_len}}】")
    print("-" * (max_name_len + 40))
    print(f"总的大小为：【{format_size(total)}】")
