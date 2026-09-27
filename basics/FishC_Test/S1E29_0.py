#简单的文件创建
file_name = input("请输入文件名：")
print("输入内容，以:w结束:")
lines = []
while True:
    line = input()
    if line == ':w':
        break
    lines.append(line)
f = open(file_name,'w')
temp = '\n'.join(lines)
f.write(temp)
f.close()

