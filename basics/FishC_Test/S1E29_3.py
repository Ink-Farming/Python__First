file_name = input("请输入要打开的文件（C:\\test.txt）：")

f = open(file_name, 'r')
lines = list(f)

n = input("请输入需要显示的行数【格式如 13:21 或 :21 或 21: 】：").split(':')

if n[0].strip() == '':
    a = 0
    start_line = 1
else:
    a = int(n[0]) - 1
    start_line = int(n[0])

if len(n) < 2 or n[1].strip() == '':
    b = len(lines)
    end_line = len(lines)
else:
    b = int(n[1])
    end_line = int(n[1])

if a == 0 and b == len(lines):
    print(f"文件{file_name}全部内容如下：")
elif a == 0:
    print(f"文件{file_name}从开始到第{end_line}行的内容如下：")
elif b == len(lines):
    print(f"文件{file_name}第{start_line}行到末尾的内容如下：")
else:
    print(f"文件{file_name}第{start_line}行到第{end_line}行的内容如下：")

for line in lines[a:b]:
    print(line)
