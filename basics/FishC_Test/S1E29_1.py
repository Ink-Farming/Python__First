#简易文件比较
file_name01 = input('请输入第一个文件名：')
file_name02 = input('请输入第二个文件名：')

f_01 = open(file_name01,'r')
f_02 = open(file_name02,'r')

lines01 = list(f_01)
lines02 = list(f_02)
f_01.close()
f_02.close()

error_line = []
for i in range(min(len(lines01),len(lines02))):
    if lines01[i] != lines02[i]:
        error_line.append(i+1)
print(f"共有{len(error_line)}处不一样")
for _ in error_line:
    print(f"第{_}行不一样")
