---
layout: post
title: "Python 语法复习"
date: 2018-03-16
description: "简单复习python语法"
tag: Python

---

# 赋值

```python
import copy
a = ['a', [1,2,3,4,5], 100]
b = copy.copy(a)
b[0] = 'b'
b[1].append(6)
b[2] = 10
b.append(111)
print(a)   # ['a', [1, 2, 3, 4, 5, 6], 100]
print(b)   # ['b', [1, 2, 3, 4, 5, 6], 10, 111]
```

`浅拷贝：不可变类型相互不影响，可变类型共同引用`

```python
a = ['a', [1,2,3,4,5], 100]
c = copy.deepcopy(a)
c[0] = 'c'
c[1].append(6)
c[2] = 10
c.append(111)
print(a)    # ['a', [1, 2, 3, 4, 5], 100]
print(c)    # ['c', [1, 2, 3, 4, 5, 6], 10, 111]
```

`深拷贝：全部互相不影响`

```python
a = ['a', [1,2,3,4,5], 100]
d = a
d[0] = 'd'
d[1].append(6)
d[2] = 10
d.append(111)
print(a)    # ['d', [1, 2, 3, 4, 5, 6], 10, 111]
print(d)    # ['d', [1, 2, 3, 4, 5, 6], 10, 111]
```

`直接复制：全部影响（注意a是列表）`

```python
a = ['a', [1,2,3,4,5], 100]
e = a[:]
e[0] = 'e'
e[1].append(6)
e[2] = 10
e.append(111)
print(a)   # ['a', [1, 2, 3, 4, 5, 6], 100]
print(e)   # ['e', [1, 2, 3, 4, 5, 6], 10, 111]
``` 

`a[:]赋值相当于浅拷贝`


# 方法

## map(function, iterable)
第一个参数 function 以参数序列中的每一个元素调用 function 函数，返回迭代器
```python
def square(x):
    return x ** 2
list(map(square, [1,2,3,4,5]))                # [1, 4, 9, 16, 25]
list(map(lambda x: x ** 2, [1, 2, 3, 4, 5]))  # 使用 lambda 匿名函数 [1, 4, 9, 16, 25]
```

## filter(function, iterable)
用于过滤序列，过滤掉不符合条件的元素，返回迭代器，要转换为列表使用 list() 
```python 
def is_odd(n):
    return n % 2 == 1   # 当语句为true返回元素
print(list(filter(is_odd, [1, 2, 3, 4, 5, 6])))
print(list(filter(lambda x:x%2==1, [1, 2, 3, 4, 5, 6])))
```

## reduce(function, iterable)
函数会对参数序列中元素进行累运算，第1、2个元素进行操作，得到的结果再与第3个运算
Python3 中，reduce() 已被全局名字空间里移除，被放置在 functools 模块里
```python
from functools import reduce
print(reduce(lambda x,y:x*y, [1,2,3,4,5]))  # 120
```

# 单例模式

## 1、使用__new__实现

```python
class Singleton:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance
s0 = Singleton()
s1 = Singleton()
print(id(s0))
print(id(s1))
```

## 2、使用装饰器实现

```python
from functools import wraps
def singleton(cls):
    instances = {}
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances
    return get_instance

@singleton
class Bar:
    pass

b0 = Bar()
b1 = Bar()
print(id(b0))
print(id(b1))
```

# @property介绍
可以使实例方法用起来像实例属性一样，使代码更加简明

```python
class Goods:
    def __init__(self):
        self.age = 24

    @property
    def price(self):
        return self.age

    @price.setter  # 设置,仅可接收除self外的一个参数
    def price(self, value):
        self.age = value

    @price.deleter  # 删除
    def price(self):
        del self.age

obj = Goods()   # 实例化对象
print(obj.age)  # 直接获取 age属性值
obj.age = 35    # 修改age的值
print(obj.age)
del obj.age     # 删除age属性的值
```

# 类

一般来说，要使用某个类的方法，需要先实例化一个对象再调用方法。
而使用@staticmethod或@classmethod，就可以不需要实例化，直接类名.方法名()来调用。

1. self表示一个具体的实例本身。用了staticmethod就可以无视self。
2. cls表示这个类本身。

```python
class A(object):
    a = 'a'

    @staticmethod
    def foo1(name):
        print('hello', name)
        print(A.a)
        # print(A.foo2('A.f1.f2'))

    def foo2(self, name):
        print('hello', name)

    @classmethod
    def foo3(cls, name):
        print('hello', name)
        print(A.a)
        print(cls().foo2('A.f3.f2'))

a = A()
a.foo1('a1')
a.foo2('a2')
a.foo3('a3')

A.foo1('A1')
# A.foo2('A2')  # 报错
A.foo3('A3')
```

## 区别
1. @staticmethod不需要表示自身对象的self和自身类的cls参数，就跟使用函数一样。
2. @classmethod也不需要self参数，但第一个参数需要是表示自身类的cls参数。
3. @staticmethod中要调用到这个类的一些属性方法，只能直接类名.属性名或类名.方法名。
4. @classmethod因为持有cls参数，可以来调用类的属性，类的方法，实例化对象等，避免硬编码。
5. 在classmethod中可以调用类中定义的其他方法、类的属性
6. 但staticmethod只能通过A.a调用类的属性，但无法通过在该函数内部调用A.foo2()

# 参考

1. https://blog.csdn.net/qq_33733970/article/details/78792656
2. https://www.cnblogs.com/happyyangyanghappy/p/10917139.html
3. https://blog.csdn.net/sinat_33718563/article/details/81298785