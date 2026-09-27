"""
测试题：

0. 下边只有一种方式不能打开文件，请问是哪一种，为什么？
>>> f = open('E:/test.txt', 'w')   # A
>>> f = open('E:\test.txt', 'w')   # B
>>> f = open('E://test.txt', 'w')  # C
>>> f = open('E:\\test.txt', 'w')  # D

B,反斜杠('\')与t会被识别成指标符

1. 打开一个文件我们使用open()函数，通过设置文件的打开模式，
决定打开的文件具有那些性质，请问默认的打开模式是什么呢？

r,只读

2. 请问 >>> open('E:\\Test.bin', 'xb') 是以什么样的模式打开文件的？

二进制文本
      
3. 尽管Python有所谓的“垃圾回收机制”，但对于打开了的文件，
在不需要用到的时候我们仍然需要使用f.close()将文件对象“关闭”，
这是为什么呢？

防止写入不能保存

4. 如何将一个文件对象（f）中的数据存放进列表中？

list(f)

5. 如何迭代打印出文件对象（f）中的每一行数据？

for _ in f:
    print(_)

6. 文件对象的内置方法f.read([size=-1])作用是读取文件对象内容，
size参数是可选的，那如果设置了size=10，例如f.read(10)，将返回什么内容呢？

十位字符串

7. 如何获得文件对象（f）当前文件指针的位置？

f.tell()

8. 还是视频中的那个演示文件（record.txt），请问为何f.seek(45, 0)不会出错，
但f.seek(46)就出错了呢？
>>> f.seek(46)
46
>>> f.readline()
Traceback (most recent call last):
  File "<pyshell#18>", line 1, in <module>
    f.readline()
UnicodeDecodeError: 'gbk' codec can't decode byte 0xe3 in position 4:
illegal multibyte sequence



动动手：

0. 尝试将文件（  OpenMe.mp3 (700 Bytes, 下载次数: 20571) ）打印到屏幕上
"""
f = open("Openme.mp3")
for ch in f:
    print(ch,end= '')
f.close()
"""
1. 编写代码，将上一题中的文件（OpenMe.mp3）保存为新文件（OpenMe.txt）
"""
f = open('Openme.mp3')
f1 = open("Openme.txt",'x')
f1.write(f.read())
f1.close()
f.close()
