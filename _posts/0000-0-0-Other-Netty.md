---
layout: post
title: "Netty 网络通信"
date: 2019-10-23
description: "Netty 网络通信"
tag: Other

---

# Netty

Netty 是一个异步事件驱动的网络应用框架，用于快速开发可维护的高性能服务器和客户端。

## Netty 特点

- 高性能、异步事件驱动的NIO框架
- 提供了对TCP、UDP和文件传输的支持
- 使用更高效的socket底层，对epoll空轮询引起的cpu占用飙升在内部进行了处理
- 避免了直接使用NIO的陷阱，简化了NIO的处理方式
- 采用多种decoder/encoder支持，对TCP粘包/分包进行自动化处理
- 可使用接受/处理线程池，提高连接效率，对重连、心跳检测的简单支持
- 通过内存池的方式循环利用ByteBuf
- 通过引用计数器及时申请释放不再引用的对象，降低了GC频率


## ByteBuf

Netty 里面数据读写是以 ByteBuf 为单位进行交互的

![png](/images/posts/all/Netty的ByteBuf结构图.png)

ByteBuf 是一个字节容器，分为三个部分：

1. 第一部分是已经丢弃的字节，这部分数据是无效的
2. 第二部分是可读字节，这部分数据是 ByteBuf 的主体数据， 从 ByteBuf 里面读取的数据都来自这一部分
3. 第三部分的数据是可写字节，所有写到 ByteBuf 的数据都会写到这一段。最后一部分虚线表示的是该 ByteBuf 最多还能扩容多少容量


## pipeline 与 channelHandler

![png](/images/posts/all/Netty的pipeline与channelHandler.png)

一条连接对应着一个 Channel，这条 Channel 所有的处理逻辑都在一个叫做 ChannelPipeline 的对象里面，ChannelPipeline 是一个双向链表结构，他和 Channel 之间是一对一的关系。

默认情况下会把读写事件传播到下一个 handler。

## channelHandler

接口ChannelHandler两个子接口：
- ChannelInboundHandler (处理读数据的逻辑)
- ChannelOutBoundHandler (处理写数据的逻辑)

## 实现类

- ChannelInboundHandlerAdapter : inBoundHandler 的执行顺序与通过 addLast() 添加的顺序保持一致
- `super.channelRead(ctx, msg);`传递到下一个handler
- adapter 可以通过 ctx.fireChannelRead(msg) 直接把上一个 handler 的输出结果传递到下一个 handler

- ChanneloutBoundHandlerAdapter: outBoundHandler 的执行顺序与通过 addLast() 添加的顺序相反
- `super.write(ctx, msg, promise);`传递到下一个handler
- adapter 也会把对象传递到下一个 outBound 节点，它的传播顺序与 inboundHandler 相反

- inBoundHandler 的事件通常只会传播到下一个 inBoundHandler
- outBoundHandler 的事件通常只会传播到下一个 outBoundHandler，两者相互不受干扰。

# 特殊的handler

## ByteToMessageDecoder 与 MessageToByteEncoder

- ByteToMessageDecoder：收到数据反序列成对象
- MessageToByteEncoder：发送前对象序列化（即`ctx.channel().writeAndFlush(ByteBuf);`前会将Object序列成ByteBuf，此时就可`writeAndFlush(Object)`）

## MessageToMessageCodec

以上两个可合并成一个 MessageToMessageCodec

## SimpleChannelInboundHandler

- SimpleChannelInboundHandler：`类型判断`和`对象传递`都自动帮实现，不再需要强转，不再有冗长乏味的 if else 对象判断，不需要手动传递对象。


## 拆包粘包

拆包，基本原理就是不断从 TCP 缓冲区中读取数据，每次读取完都需要判断是否是一个完整的数据包

- 固定长度的拆包器 FixedLengthFrameDecoder
- 行拆包器 LineBasedFrameDecoder
- 分隔符拆包器 DelimiterBasedFrameDecoder
- 基于长度域拆包器 LengthFieldBasedFrameDecoder

## channelHandler的生命周期

ChannelInboundHandlerAdapter 为例 :
- 开启：handlerAdded() -> channelRegistered() -> channelActive() -> channelRead() -> channelReadComplete()
- 关闭：channelInactive() -> channelUnregistered() -> handlerRemoved()

# reference

https://github.com/wangzhiwubigdata/God-Of-BigData

https://www.jianshu.com/p/a4e03835921a



