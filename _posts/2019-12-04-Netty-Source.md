---
layout: post
title: "Netty 源码解析"
date: 2019-12-04
description: "Netty 源码解析"
tag: Other

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
    .channel(NioServerSocketChannel.class)       // A
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

## 服务端Channel

A 标记：.channel()函数传入NioServerSocketChannel类，并反射

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


