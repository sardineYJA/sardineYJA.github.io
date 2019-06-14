---
layout: post
title: "concurrent的多进程、多线程"
date: 2019-04-02
description: "介绍concurrent的多进程、多线程"
tag: python

---

# 简介

常用的 multiprocessing 和 threding 模块进行进一步封装 concurrent.future，达成较好的支持异步操作，最终这个提案在 Python 3.2 中被引入 。

# concurrent.futures 模块详解

## Executor对象

### class concurrent.futures.Executor
Executor是一个抽象类，它提供了异步执行调用的方法。它不能直接使用，但可以通过它的两个子类ThreadPoolExecutor或者ProcessPoolExecutor进行调用。可以将相应的tasks直接放入线程池/进程池，不需要维护Queue来操心死锁的问题，线程池/进程池会自动帮我们调度。Future可以把它理解为一个在未来完成的操作，这是异步编程的基础，传统编程模式下比如我们操作queue.get的时候，在等待返回结果之前会产生阻塞，cpu不能让出来做其他事情，而Future的引入帮助我们在等待的这段时间可以完成其他的操作。

### 2.1.1 Executor.submit(fn, \*args, \*\*kwargs)
submit(fn,\*args,\*\*kwargs) 异步提交任务
fn：需要异步执行的函数
\*args, \*\*kwargs：fn参数
使用submit函数来提交线程需要执行的任务（函数名和参数）到线程池中，并返回该任务的句柄（类似于文件、画图），注意submit()不是阻塞的，而是立即返回。
通过submit函数返回的任务句柄，能够使用done()方法判断该任务是否结束。
使用cancel()方法可以取消提交的任务，如果任务已经在线程池中运行了，就取消不了。

### 2.1.2 Executor.map(func, \*iterables, timeout=None)
相当于map(func, \*iterables)，但是func是异步执行。timeout的值可以是int或float，如果操作超时，会返回raisesTimeoutError；如果不指定timeout参数，则不设置超时间。
func：需要异步执行的函数
\*iterables：可迭代对象，如列表等。每一次func执行，都会从iterables中取参数。
timeout：设置每次异步操作的超时时间

### 2.1.3 Executor.shutdown(wait=True)
释放系统资源,在Executor.submit()或 Executor.map()等异步操作后调用。使用with语句可以避免显式调用此方法。
shutdown(wait=True) 相当于进程池的pool.close()+pool.join()操作
wait=True，等待池内所有任务执行完毕回收完资源后才继续，--------》默认
wait=False，立即返回，并不会等待池内的任务执行完毕
但不管wait参数为何值，整个程序都会等到所有任务执行完毕
submit和map必须在shutdown之前

## 2.3 ThreadPoolExecutor对象
ThreadPoolExecutor类是Executor子类，使用线程池执行异步调用.
class concurrent.futures.ThreadPoolExecutor(max_workers)
使用max_workers数目的线程池执行异步调用
executor = ThreadPoolExecutor(concurrent_size)
 
## 2.4 ProcessPoolExecutor对象
ThreadPoolExecutor类是Executor子类，使用进程池执行异步调用.
class concurrent.futures.ProcessPoolExecutor(max_workers=None)
使用max_workers数目的进程池执行异步调用，如果max_workers为None则使用机器的处理器数目（如4核机器max_worker配置为None时，则使用4个进程进行异步并发）。
executor = ProcessPoolExecutor(concurrent_size)
ProcessPoolExecutor(n):n表示池里面存放多少个进程，之后的连接最大就是n的值


# 样例

```python
from concurrent.futures import ProcessPoolExecutor
import time
def my_task(message):
    time.sleep(2)   # 逻辑耗时
    for i in range(10):
        print(message+'__'+str(i))
    return message + ' -- OK'

if __name__ == '__main__':

    # submit 和 shutdown 函数使用
    pool = ProcessPoolExecutor(max_workers=2)  # 进程池，容量2
    f1 = pool.submit(my_task, ('task1'))       # 任务1,2先进行，3后来进行
    f2 = pool.submit(my_task, ('task2'))
    f3 = pool.submit(my_task, ('task3'))
    print(f1.done())
    time.sleep(3)
    print(f2.done())     # 判断task是否结束True/False
    print(f1.result())   # 得到task返回结果
    print(f3.result())
    pool.shutdown()      # 释放系统资源，使用with语句可以避免显式调用此方法

    # 提交多任务，使用 map 函数
    with ProcessPoolExecutor(max_workers=3) as executor:
        for num, data in zip(range(16), executor.map(my_task, ['A','B','C','D','E'])):
            print(num, '---', data)            # map(function, args)  # 提交五个任务
```

# 参考
1. https://blog.csdn.net/weixin_33763244/article/details/87994789
2. https://www.cnblogs.com/DSKer/p/10603441.html
