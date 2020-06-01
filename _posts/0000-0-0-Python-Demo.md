---
layout: post
title: "Python Demo"
date: 2020-06-01
description: "python"
tag: Python

---




## global 全局变量

global 全局变量，但仅限于在一个模块（py文件）中调用，通过定义全局变量模块，实现跨文件全局。
（main函数中声明的变量默认为global）

```python
# 定义全局模块，gol.py

def _init():#初始化
    global _global_dict
    _global_dict = {}
 
def set_value(key, value):
    _global_dict[key] = value
 
def get_value(key, defValue=None):
    try:
        return _global_dict[key]
    except KeyError:

```

```python
import gol
gol._init() # 先必须在Main主模块初始化
# 定义跨模块全局变量
gol.set_value('id',uuid)
```

```python
import gol
# 不需要再初始化了
id = gol.get_value('id')
```


## threading.Timer 定时任务

```python
import threading
import time

def sayHello(name):
    print ("hello %s\n", name) 
    global timer                                      # 定义全局，timer.cancel才能作用到此处
    timer = threading.Timer(2.0, sayHello, ["Meki"])  # 2秒
    timer.start()                                     # 非阻塞

if __name__ == "__main__":
    timer = threading.Timer(2.0, sayHello, ["Meki"])
    timer.start()                                     # 开启新线程

    time.sleep(10)
    timer.cancel()   # 取消
```

> start() 运行的就是 thread 的 run() 即开启新线程，而且都会 join (即main线程会等待所有线程结束才会结束)。cancel取消不会立刻中断定时任务，会等待此定时任务完成（但不会产生新Timer）。



## join 阻塞主线程

```python
# join之后,主线程被线程1阻塞,在线程1返回结果之前,主线程无法执行下一轮循环
threads = [Thread() for i in range(5)]
for thread in threads:
    thread.start()
    thread.join()

# 正确做法
threads = [Thread() for i in range(5)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
```


