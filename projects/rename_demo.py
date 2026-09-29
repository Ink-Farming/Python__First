from pathlib import Path

work = Path("rename_demo")
work.mkdir(exist_ok=True)

#测试用例，创建五个测试文件
if not any(work.iterdir()):
    for i in range(1,6):
        (work / f"新建 文档 {i}.txt").write_text(f"第{i}个文件", encoding="UTF-8")
# 找出要重命名的 txt 文件
#按照前缀查找
#files = sorted(work.glob("note_.txt"))
#按照后缀查找
#files = sorted(work.glob("_2026.txt"))
#关键词查找
files = sorted(work.glob("*新建 文档*.txt"))
prefix = "note"        #这是更改后的名字

plan = []
for i, p in enumerate(files, 1):
    new = p.with_name(f"{prefix}_{i:03d}{p.suffix.lower()}")
    plan.append((p, new))
    print(f"{p.name}  ->  {new.name}")

# 确认预览没问题后，取消下面注释，真正执行
for old, new in plan:
    if new.exists():
        print(f"跳过：{new.name} 已存在")
    else:
        old.rename(new)
print("重命名完成")
