#简易打印前n行内容
file_name = input("输入要打开的文件：")
f = open(file_name,'r')
n = int(input("请输入显示前几行："))
lines = list(f)
f.close()
for _ in lines[:n]:
    print(_)
