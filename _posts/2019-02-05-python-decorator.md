---
layout: post
title: "python装饰器介绍"
date: 2019-02-05
description: "简单介绍一下python装饰器"
tag: python

---

# 简介
python装饰器本质上就是一个函数，它可以让其他函数在不需要做任何代码变动的前提下增加额外的功能，
装饰器的返回值也是一个函数对象（函数的指针）。装饰器函数的外部函数传入我要装饰的函数名字，
返回经过修饰后函数的名字；内层函数（闭包）负责修饰被修饰函数。

# 使用方法
## 函数的函数装饰器
```python
import time
def decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func()
        end_time = time.time()
        print(end_time - start_time)
    return wrapper

@decorator 
def func():
    time.sleep(0.8)

func() # 函数调用
# 输出：0.800644397735595
```
在上面代码中 func是我要装饰器的函数，我想用装饰器显示func函数运行的时间。
@decorator这个语法相当于执行 func = decorator(func)，为func函数装饰并返回。
在来看一下我们的装饰器函数 -decorator，该函数的传入参数是func（被装饰函数），返回参数是内层函数

## 类方法的函数装饰器
```python
import time
def decorator(func):
    def wrapper(me_instance):
        start_time = time.time()
        func(me_instance)
        end_time = time.time()
        print(end_time - start_time)
    return wrapper

class Method(object):
    @decorator 
    def func(self):
        time.sleep(0.8)
p1 = Method()
p1.func() # 函数调用
```
对于类方法来说，都会有一个默认的参数self，它实际表示的是类的一个实例，
所以在装饰器的内部函数wrapper也要传入一个参数 -me_instance就表示将类的实例p1传给wrapper，
其他的用法都和函数装饰器相同。

## 类装饰器
```python
class Decorator(object):
    def __init__(self, f):
        self.f = f
    def __call__(self):  # __call__()是特殊方法，将一个类实例变成一个可调用对象
        print("decorator start")
        self.f()
        print("decorator end")
@Decorator
def func():
    print("func")
func()

p = Decorator(func) # p是类Decorator的一个实例
p()                 # 实现了__call__()方法后，p可以被调用
```

# 装饰器链
```python
def makebold(f):
	return lambda:"<b>"+f()+"</b>"
def makeitalic(f):
	return lambda:"<i>"+f()+"</i>"

@makebold
@makeitalic
def say():
	return "Hello"
print(say())

# 输出 <b><i>Hello</i></b>
```

# 装饰器库functools
```python
def decorator(func):
    def inner_function():
        pass
    return inner_function

@decorator
def func():
    pass

print(func.__name__)
# 输出： inner_function
```
上述代码最后执行的结果不是 func，而是 inner_function！这表示被装饰函数自身的信息丢失了！
怎么才能避免这种问题的发生呢？可以借助functools.wraps()函数：

```python
from functools import wraps
def decorator(func):
    @wraps(func) 
    def inner_function():
        pass
    return inner_function

@decorator
def func():
    pass

print(func.__name__)
#输出： func
```


# 参考
1. https://www.cnblogs.com/lianyingteng/p/7743876.html