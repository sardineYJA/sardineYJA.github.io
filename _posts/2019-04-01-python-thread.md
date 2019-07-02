---
layout: post
title: "python并发并行"
date: 2019-04-01
description: "介绍python读并发并行"
tag: python

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

