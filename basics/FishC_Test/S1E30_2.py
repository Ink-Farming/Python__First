#2. 编写一个程序，用户输入文件名以及开始搜索的路径，搜索该文件是否存在。
#如遇到文件夹，则进入文件夹继续搜索
from pathlib import Path
def search_file(file_name,path_name):
    start = Path(path_name)
    if not start.exists():
        print(f"路径不存在:{path_name}")
        return []
    if not start.is_dir():
        print(f"不是文件夹:{path_name}")
        return []

    results = [p for p in start.rglob(file_name) if p.is_file()]
    return results

def main():
    path_name = input("输入搜索的路径")
    file_name = input("输入要搜索的文件名字")

    result = search_file(file_name,path_name)

    if results:
        print(f"\n找到 {len(results)} 个匹配文件：")
        for p in results:
            print("  ", p)
    else:
        print("\n未找到该文件。")


if __name__ == "__main__":
    main()
