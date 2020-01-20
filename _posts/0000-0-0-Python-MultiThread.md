---
layout: post
title: "Python 并发并行"
date: 2018-05-01
description: "介绍python读并发并行"
tag: Python

---

# 简介

## GIL
python中由于全局解释锁（Global Interpreter Lock）的存在，每次只能执行一个线程。每个线程在执行的过程都需要先获取GIL，保证同一时刻只有一个线程可以执行代码。仅仅是因为在CPython解释器，难以移除GIL。

## 计算密集型任务(CPU-bound) 
特点是要进行大量的计算，占据着主要的任务，消耗CPU资源，一直处于满负荷状态。比如复杂的加减乘除、计算圆周率、对视频进行高清解码等等，全靠CPU的运算能力。这种计算密集型任务虽然也可以用多任务完成，但是任务越多，花在任务切换的时间就越多，CPU执行任务的效率就越低，所以，要最高效地利用CPU，计算密集型任务同时进行的数量应当等于CPU的核心数。计算密集型任务由于主要消耗CPU资源，因此，代码运行效率至关重要。Python这样的脚本语言运行效率很低，完全不适合计算密集型任务。对于计算密集型任务，最好用C语言编写。

## IO密集型任务(I/O bound)
特点是指磁盘IO、网络IO占主要的任务，CPU消耗很少，任务的大部分时间都在等待IO操作完成（因为IO的速度远远低于CPU和内存的速度）。IO密集型任务执行期间，99%的时间都花在IO上，花在CPU上的时间很少，因此，用运行速度极快的C语言替换用Python这样运行速度极低的脚本语言，完全无法提升运行效率。对于IO密集型任务，任务越多，CPU效率越高，但也有一个限度。常见的大部分任务都是IO密集型任务，比如请求网页、读写文件等。当然我们在Python中可以利用sleep达到IO密集型任务的目的。对于IO密集型任务，最合适的语言就是开发效率最高（代码量最少）的语言，脚本语言是首选，C语言最差。

## 解决GIL
1. 用多进程代替多线程。每一个Python进程都有自己的Python解释器和内存空间，因此GIL不会成为问题。 
2. 替换Python解释器，用C,Java,C#和Python编写的CPython，JPython，IronPython和PyPy是最受欢迎的，GIL只存在CPython中

执行I/O密集型操作，多线程是有用的，一个线程在等待网络响应时，执行I/O操作的函数会释放GIL，然后再运行一个线程。

执行CPU密集型操作，使用多进程，使用concurrent.futures包中的ProcessPoolExecutor并行计算，因为它使用ProcessPoolExecutor 类把工作分配给多个 Python 进程处理CPU密集型处理，使用这个模块能绕开 GIL，利用所有可用的 CPU 核心。

系统开进程的个数是有限的，线程的出现就是为了解决这个问题，于是在进程之下又分出多个线程。能不能用同一线程来同时处理若干连接，于是协程就出现了。协程在实现上试图用一组少量的线程来实现多个任务，一旦某个任务阻塞，则可能用同一线程继续运行其他任务，避免大量上下文的切换，而且，各个协程之间的切换，往往是用户通过代码来显式指定的，不需要系统参与，可以很方便的实现异步。协程本质上是异步非阻塞技术。


# 进程，线程，协程

## 进程
进程是程序运行资源分配（CPU，内存，磁盘）的最小单位。

多进程的优势：一个子进程崩溃并不会影响其他子进程和主进程的运行；
多进程的缺点：不能一次性启动太多进程，会严重影响系统的资源调度；

## 线程
线程是CPU调度的最小单位，必须依赖于进程。同一进程中的多条线程共享全部系统资源。
线程自己基本上不拥有系统资源,只拥有一点在运行中必不可少的资源(如程序计数器,一组寄存器和栈)。
线程间通信主要通过共享内存，上下文切换很快，资源开销较少，但相比进程不够稳定容易丢失数据。

多线程的优势：线程间切换快，资源消耗低；
多线程的缺点：一个线程挂掉会影响到所有线程；

## 协程
协程是一种用户态的轻量级线程，协程的调度`完全由用户控制`。协程拥有自己的寄存器上下文和栈。
与线程相比协程的优点：一是可控的切换时机，二是很小的切换代价。
线程进程都是同步机制，而协程则是异步。

协程：asyncio模块、async/await关键字、yield关键字

# 测试代码

```python
import time
import requests

# 开发中网络请求测试服务
NUMBERS = range(13)
URL = 'http://httpbin.org/get?a={}'
def fetch(a):
    r = requests.get(URL.format(a))
    print(r.json()['args']['a'])   # 乱序即多线程
    return r.json()['args']['a']


# 测试单线程
def test1():
    start = time.time()
    for num in NUMBERS:
        result = fetch(num)
        print('fetch({}) = {}'.format(num, result))
    end = time.time()
    print('单线程 cost time: {}'.format(end-start))


# 测试 threading
def test2():
    import threading
    class MyThread(threading.Thread):
        def __init__(self, func, args):
            threading.Thread.__init__(self)
            self.func = func
            self.args = args
        def run(self):
            self.result = self.func(self.args)
        def get_result(self):
            return self.result
    t = {}
    start = time.time()
    for num in NUMBERS:
        t[num] = MyThread(fetch, num)
        t[num].start()
    for num in NUMBERS:
        t[num].join()    # 等待所有线程结束
        result = t[num].get_result()
        print('fetch({}) = {}'.format(num, result))
    end = time.time()
    print('threading cost time: {}'.format(end-start))


# 测试 multiprocessing
def test3():
    from multiprocessing import Process
    p = {}
    if __name__ == '__main__':
        start = time.time()
        for num in NUMBERS:
            p[num] = Process(target=fetch, args=(num,))
            p[num].start()
        for num in NUMBERS:
            p[num].join()
        end = time.time()
        print('multiprocessing cost time: {}'.format(end - start))


# 测试 concurrent
# 多线程ThreadPoolExecutor
# 多进程ProcessPoolExecutor
def test4():
    from concurrent.futures import ThreadPoolExecutor
    start = time.time()
    with ThreadPoolExecutor(max_workers=5) as executor:
        for num, result in zip(NUMBERS, executor.map(fetch, NUMBERS)):
            print('fetch({}) = {}'.format(num, result))
    end = time.time()
    print('concurrent cost time: {}'.format(end-start))


# 测试 asyncio 协程
def test5():
    import asyncio
    import aiohttp
    async def fetch_async(a):
        async with aiohttp.request('GET', URL.format(a)) as r:
            data = await r.json()
            print(data['args']['a'])     # 乱序即多线程
        return data['args']['a']
    start = time.time()
    loop = asyncio.get_event_loop()
    tasks = [fetch_async(num) for num in NUMBERS]
    results = loop.run_until_complete(asyncio.gather(*tasks))
    for num, results in zip(NUMBERS, results):
        print('fetch({}) = {}'.format(num, results))
    end = time.time()
    print('asyncio cost time: {}'.format(end-start))


# test1()
# test2()
# test3()
# test4()
# test5()
```


# concurrent的多进程、多线程

## concurrent.futures 模块详解

将常用的 multiprocessing 和 threding 模块进行进一步封装 concurrent.futures，达成较好的支持异步操作，最终在 Python 3.2 中被引入 。该做法会以子程序的形式，平行地运行多个解释器，从而令python程序能够利用多核心CPU来提升执行速度。由于子进程与主解释器相分离，所以，他们的全局解释器锁也是相互独立的。每个子进程都可以完整的利用一个CPU内核，而且这些子进程都与主进程之间有着联系，通过这条联系渠道，子进程可以接收主进程发过来的指令，并把计算结果返回给主进程。



## Executor对象

### class concurrent.futures.Executor

Executor是一个抽象类，它提供了异步执行调用的方法。它不能直接使用，但可以通过它的两个子类ThreadPoolExecutor或者ProcessPoolExecutor进行调用。可以将相应的tasks直接放入线程池/进程池，不需要维护Queue来操心死锁的问题，线程池/进程池会自动帮我们调度。Future可以把它理解为一个在未来完成的操作，这是异步编程的基础，传统编程模式下比如我们操作queue.get的时候，在等待返回结果之前会产生阻塞，cpu不能让出来做其他事情，而Future的引入帮助我们在等待的这段时间可以完成其他的操作。

### 2.1.1 Executor.submit(fn, \*args, \*\*kwargs)

submit(fn,\*args,\*\*kwargs) 异步提交任务
fn：需要异步执行的函数
\*args, \*\*kwargs：fn参数
使用submit函数来提交线程需要执行的任务（函数名和参数）到线程池中，并`返回该任务的句柄`（类似于文件、画图），注意submit()不是阻塞的，而是立即返回。
通过submit函数返回的任务句柄，能够使用`done()`方法判断该任务是否结束。
使用`cancel()`方法可以取消提交的任务，如果任务已经在线程池中运行了，就取消不了。

### 2.1.2 Executor.map(func, \*iterables, timeout=None)

相当于map(func, \*iterables)，但是func是异步执行。timeout的值可以是int或float，如果操作超时，会返回raisesTimeoutError；如果不指定timeout参数，则不设置超时间。
func：需要异步执行的函数
\*iterables：可迭代对象，如列表等。每一次func执行，都会从iterables中取参数。
timeout：设置每次异步操作的超时时间

### 2.1.3 Executor.shutdown(wait=True)

释放系统资源,在`Executor.submit()`或 `Executor.map()`等异步操作后调用。使用`with语句`可以避免显式调用此方法。
shutdown(wait=True) 相当于进程池的pool.close()+pool.join()操作
wait=True，等待池内所有任务执行完毕回收完资源后才继续，-------->默认
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
# ProcessPoolExecutor,ThreadPoolExecutor 用法相似
# 进程池 需要 __main__

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

进程池中的回调函数是父进程调用的，和子进程没有关系

线程池中的回调函数是子线程调用的，和父线程没有关系 (current thread())

```python
from concurrent.futures import ThreadPoolExecutor
import time
def func(num):
    info = '这是我的第%s' % num
    time.sleep(3)
    return info
def call_back_func(res):
    print(res.result())

if __name__ == '__main__':
    p = ThreadPoolExecutor(20)
    for i in range(1000):
        p.submit(func, i).add_done_callback(call_back_func)
    p.shutdown()
```


# reference

https://blog.csdn.net/weixin_33763244/article/details/87994789

https://www.cnblogs.com/DSKer/p/10603441.html