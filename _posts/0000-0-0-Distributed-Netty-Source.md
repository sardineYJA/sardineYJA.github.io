---
layout: post
title: "Netty 源码解析"
date: 2019-12-04
description: "Netty 源码解析"
tag: Distributed Service

---

## Netty 组件

![png](/images/posts/all/Netty对socket抽象.png)

- NioEventLoop -> Thread
- Channel -> Socket
- Pipeline 
- ChannelHandler -> Logic 逻辑事务处理
- ByteBuf


## Server 案例

```java
NioEventLoopGroup boosGroup = new NioEventLoopGroup();
NioEventLoopGroup workerGroup = new NioEventLoopGroup(); 
final ServerBootstrap serverBootstrap = new ServerBootstrap();

serverBootstrap
    .group(boosGroup, workerGroup)
    .channel(NioServerSocketChannel.class)       // 反射
    .option(ChannelOption.SO_BACKLOG, 1024)
    .childOption(ChannelOption.TCP_NODELAY, true)
    .childAttr(AttributeKey.newInstance("childAttr"), yourValue)
    .handler(new YourHandler())
    .childHandler(new ChannelInitializer<NioSocketChannel>() {
        protected void initChannel(NioSocketChannel ch) {
            ch.pipeline().addLast(new YourHandler());
        }
    });
```

# Channel

.channel()函数传入NioServerSocketChannel类，并反射

```java
bind()  // 用户代码入口
  └initAndRegister()  // 初始化并注册
    ├newChannel()     // 创建服务端channel
    └init()           // 初始化服务端channel
```

NioServerSocketChannel 类构造函数：

```java
newSocket()                     // 通过Jdk来创建底层jdk channel
NioServerSocketChannelConfig()  // tcp参数配置类
AbstractNioChannel()
  ├configureBlocking(false)  // 阻塞模式
  └AbstractChannel()         // 创建id, unsafe, pipline
```

初始化 channel：

```java
init()   // 初始化入口
  ├set ChannelOptions, ChannelAttrs
  ├set ChildOptions, ChildAttrs
  ├config Handler               // 配置服务端pipeline
  └add ServerBootstrapAcceptor  // 添加连接器
```

注册 selector（事件轮询器）：

```java
AbstractChannel.register(channel)   // 入口
  ├this.eventLoop = eventLoop   // 绑定线程
  └register0()    // 实际注册
    ├doRegister()              // 调用jdk底层注册selector
    ├invokeHandlerAddedIfNeeded()
    └fireChannelRegistered()   // 传播事件
```

端口绑定：

```java
AbstractUnsafe.bind()     // 入口
  ├doBind()
  │ └javaChannel().bind()  // jdk底层绑定
  └pipline.fireChannelActive()   // 传播事件
    └HeadContext.readIfIsAutoRead()  
```


# NioEventLoop


- 默认情况下，Netty服务端起多少线程？何时启动？

- Netty是如何解决jdk空轮询bug？

- Netty如何保证异步串行无锁化？


## NioEventLoop 创建

```java
new NioEventLoopGroup()     // 线程组，默认2*cpu
  ├new ThreadPerTaskExecutor()    // 线程创建器
  ├for(){newChild()}              // 构造NioEventLoop
  └chooserFactory.newChooser()    // 线程选择器，给连接绑定NioEventLoop
```

## ThreadPerTaskExecutor

- 每次执行任务都会创建一个线程实体

- NioEventLoop线程命名规则：nioEventLoop-1-xx

## newchild()

- 保存线程执行器 ThreadPerTaskExecutor

- 创建一个 MpscQueue：保存任务队列

- 创建一个 selector：轮询连接

## chooserFactory.newChooser()

```java
isPowerOfTwo()  // 判断是否是2的幂，如2,4,8
  ├PowerOfTwoEventExecutorChooser    // 优化
  │ └index++ & (length-1)
  └GenericEventExecutorChooser       // 普通 
    └abs(index++ % length)
```


## NioEventLoop 启动

```java
bind() -> execute(task)      // 入口
  └startThread() -> doStartThread()    // 创建线程
     └ThreadPerTaskExecutor.execute()
        ├thread=Thread.currentThread()
        └NioEventLoop.run()            // 启动
```


## NioEventLoop.run()

```java
run()->for(;;)
  ├select()                // 轮询检查是否有io事件
  ├processSelectedKeys()   // 处理io事件
  └runAllTasks()           // 处理异步任务队列
```

## select() 执行逻辑

- deadline 以及任务穿插逻辑处理

- 阻塞式select

- 避免jdk空轮询的bug，设定512阀值

