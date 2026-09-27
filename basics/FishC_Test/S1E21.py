"""
0. 请使用lambda表达式将下边函数转变为匿名函数？
def fun_A(x, y=3):
        return x * y

d = lambda x,y=3 : x*y
d(3)

"""
"""
1. 请将下边的匿名函数转变为普通的屌丝函数？
lambda x : x if x % 2 else None

def fun_B(x):
    if x % 2 == 1:
        return x
    else:
        return None
"""
"""
2. 感受一下使用匿名函数后给你的编程生活带来的变化？

一些暂时的不会长期反复使用的但会在短时间内用多次的函数可以快速写出，
方便读取与修改，不需要写太多函数名，方便维护
"""
"""
3. 你可以利用 filter() 和 lambda 表达式快速求出 100 以内所有 3 的倍数吗？

list(filter(lambda x : x % 3 == 0 ,range(101)))
"""
"""
4. 还记得列表推导式吗？完全可以使用列表推导式代替 filter() 和 lambda 组合，
你可以做到吗？

[x for x in range(1,101) if x % 3 == 0]
"""
"""
5. 还记得 zip 吗？使用 zip 会将两数以元组的形式绑定在一块，例如：
>>> list(zip([1, 3, 5, 7, 9], [2, 4, 6, 8, 10]))
[(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
但如果我希望打包的形式是灵活多变的列表而不是元组
（希望是 [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]] 这种形式），
你能做到吗？（采用 map 和 lambda 表达式）

list(map(list,zip([1, 3, 5, 7, 9], [2, 4, 6, 8, 10])))
"""
"""
6. 请目测以下表达式会打印什么？
def make_repeat(n):
        return lambda s : s * n

double = make_repeat(2)
print(double(8))
print(double('FishC'))

16
FishCFishC
"""
