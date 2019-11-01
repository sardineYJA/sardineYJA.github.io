---
layout: post
title: "Netty 网络通信"
date: 2019-10-23
description: "Netty 网络通信"
tag: Other

---


## Netty 特点

一个高性能、异步事件驱动的NIO框架，它提供了对TCP、UDP和文件传输的支持，
使用更高效的socket底层，对epoll空轮询引起的cpu占用飙升在内部进行了处理，
避免了直接使用NIO的陷阱，简化了NIO的处理方式。
采用多种decoder/encoder支持，对TCP粘包/分包进行自动化处理，
可使用接受/处理线程池，提高连接效率，对重连、心跳检测的简单支持，
可配置IO线程数、TCP参数， TCP接收和发送缓冲区使用直接内存代替堆内存，
通过内存池的方式循环利用ByteBuf，
通过引用计数器及时申请释放不再引用的对象，降低了GC频率，
使用单线程串行化的方式，高效的Reactor线程模型，
大量使用了volitale、使用了CAS和原子类、线程安全类的使用、读写锁的使用


## 线程模型








(待补充...)

# reference

https://github.com/wangzhiwubigdata/God-Of-BigData





