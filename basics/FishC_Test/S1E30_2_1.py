import os

def find_first(filename, start_path):
    for dirpath, dirnames, filenames in os.walk(start_path):
        if filename in filenames:
            return os.path.join(dirpath, filename)   # 直接返回文件地址
    return None   # 没找到

path = find_first("test.txt", "D:/data")
if path:
    print("文件地址：", path)
else:
    print("未找到")
