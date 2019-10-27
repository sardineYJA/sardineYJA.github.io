---
layout: post
title: "Spark 通信框架"
date: 2019-10-17
description: "Spark 通信框架"
tag: Spark

---


# Spark 框架

## 通信架构

Spark 2, Spark 已经完全抛弃 Akka，全部使用Netty

![png](/images/posts/all/Spark通信架构-高层视图.png)

![png](/images/posts/all/Spark通信架构-端点概览.png)

- RpcEndpoint：RPC端点 ，Spark针对于每个节点（Client/Master/Worker）都称之一个Rpc端点

- RpcEnv：RPC上下文环境，每个Rpc端点运行时依赖的上下文环境称之为RpcEnv

- Dispatcher：消息分发器，针对于RPC端点需要发送消息或者从远程RPC接收到的消息，分发至对应的指令收件箱/发件箱

- Inbox：指令消息收件箱，一个本地端点对应一个收件箱

- OutBox：指令消息发件箱，一个远程端点对应一个发件箱

- TransportClient：Netty通信客户端，根据OutBox消息的receiver信息，请求对应远程TransportServer

- TransportServer：Netty通信服务端，一个RPC端点一个TransportServer,接受远程消息后调用Dispatcher分发消息至对应收发件箱



## Master-Worker节点启动交互流程

![png](/images/posts/all/Spark的Master-Worker节点启动交互流程.png)

1. Master启动时首先创一个RpcEnv对象，负责管理所有通信逻辑

2. Master通过RpcEnv对象创建一个Endpoint，Master就是一个Endpoint，Worker可以与其进行通信

3. Worker启动时也是创一个RpcEnv对象

4. Worker通过RpcEnv对象创建一个Endpoint

5. Worker通过RpcEnv对，建立到Master的连接，获取到一个RpcEndpointRef对象，通过该对象可以与Master通信

6. Worker向Master注册，注册内容包括主机名、端口、CPU Core数量、内存数量

7. Master接收到Worker的注册，将注册信息维护在内存中的Table中，其中还包含了一个到Worker的RpcEndpointRef对象引用

8. Master回复Worker已经接收到注册，告知Worker已经注册成功

9. 此时如果有用户提交Spark程序，Master需要协调启动Driver；而Worker端收到成功注册响应后，开始周期性向Master发送心跳


