# 简易文件比较
file_01 = input("请输入第一个文件的名字：")
file_02 = input("请输入第二个文件的名字：")

try:
    with open(file_01, 'r', encoding='utf-8') as f1:
        f1_lines = f1.readlines()

    with open(file_02, 'r', encoding='utf-8') as f2:
        f2_lines = f2.readlines()

except FileNotFoundError as e:
    print(f"文件不存在：{e}")
    raise SystemExit(1)

# 比较共同行
error_line = []
for i in range(min(len(f1_lines), len(f2_lines))):
    if f1_lines[i] != f2_lines[i]:
        error_line.append(i + 1)

if error_line:
    for line_no in error_line:
        print(f"第 {line_no} 行不同")
else:
    print("两个文件在共同行范围内没有差异")

# 比较行数
if len(f1_lines) != len(f2_lines):
    print(f"两个文件行数不同：")
    print(f"  第一个文件：{len(f1_lines)} 行")
    print(f"  第二个文件：{len(f2_lines)} 行")

    if len(f1_lines) > len(f2_lines):
        print(f"  第一个文件多出 {len(f1_lines) - len(f2_lines)} 行")
    else:
        print(f"  第二个文件多出 {len(f2_lines) - len(f1_lines)} 行")
else:
    print("两个文件行数相同")

# 如果完全一样
if f1_lines == f2_lines:
    print("两个文件完全相同。")
