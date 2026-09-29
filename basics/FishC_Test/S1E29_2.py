file_name = input("输入要打开的文件：")
n = int(input("请输入显示前几行："))

with open(file_name, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for line in lines[:n]:
    print(line, end='')
