---
layout: post
title: "Spark 通信框架"
date: 2019-10-17
description: "Spark 通信框架"
tag: Spark

---


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


## Submit 提交任务交互流程

![png](/images/posts/all/Spark的Submit提交任务交互流程.png)

1. 应用提交(橙色) 
2. --> 启动Driver进程(紫色) 
3. --> 注册Application(红色) 
4. --> 启动Executor进程(蓝色) 
5. --> 启动Task执行(粉色) 
6. --> Task运行完成(绿色)

## 橙色：提交用户Spark程序

1. 用户spark-submit脚本提交一个Spark程序，会创建一个ClientEndpoint对象，该对象负责与Master通信交互

2. ClientEndpoint向Master发送一个RequestSubmitDriver消息，表示提交用户程序

3. Master收到RequestSubmitDriver消息，向ClientEndpoint回复SubmitDriverResponse，表示用户程序已经完成注册

4. ClientEndpoint向Master发送RequestDriverStatus消息，请求Driver状态

5. 如果当前用户程序对应的Driver已经启动，则ClientEndpoint直接退出，完成提交用户程序

## 紫色：启动Driver进程

1. Maser内存中维护着用户提交计算的任务Application，每次内存结构变更都会触发调度，向Worker发送LaunchDriver请求

2. Worker收到LaunchDriver消息，会启动一个DriverRunner线程去执行LaunchDriver的任务

3. DriverRunner线程在Worker上启动一个新的JVM实例，该JVM实例内运行一个Driver进程，该Driver会创建SparkContext对象

## 红色：注册Application

1. 创建SparkEnv对象，创建并管理一些数基本组件

2. 创建TaskScheduler，负责Task调度

3. 创建StandaloneSchedulerBackend，负责与ClusterManager进行资源协商

4. 创建DriverEndpoint，其它组件可以与Driver进行通信

5. 在StandaloneSchedulerBackend内部创建一个StandaloneAppClient，负责处理与Master的通信交互

6. StandaloneAppClient创建一个ClientEndpoint，实际负责与Master通信

7. ClientEndpoint向Master发送RegisterApplication消息，注册Application

8. Master收到RegisterApplication请求后，回复ClientEndpoint一个RegisteredApplication消息，表示已经注册成功

## 蓝色：启动Executor进程

1. Master向Worker发送LaunchExecutor消息，请求启动Executor；同时Master会向Driver发送ExecutorAdded消息，表示Master已经新增了一个Executor（此时还未启动）

2. Worker收到LaunchExecutor消息，会启动一个ExecutorRunner线程去执行LaunchExecutor的任务

3. Worker向Master发送ExecutorStageChanged消息，通知Executor状态已发生变化

4. Master向Driver发送ExecutorUpdated消息，此时Executor已经启动

## 粉色：启动Task执行

1. StandaloneSchedulerBackend启动一个DriverEndpoint

2. DriverEndpoint启动后，会周期性地检查Driver维护的Executor的状态，如果有空闲的Executor便会调度任务执行

3. DriverEndpoint向TaskScheduler发送Resource Offer请求

4. 如果有可用资源启动Task，则DriverEndpoint向Executor发送LaunchTask请求

5. Executor进程内部的CoarseGrainedExecutorBackend调用内部的Executor线程的launchTask方法启动Task

6. Executor线程内部维护一个线程池，创建一个TaskRunner线程并提交到线程池执行

## 绿色：Task运行完成

1. Executor进程内部的Executor线程通知CoarseGrainedExecutorBackend，Task运行完成

2. CoarseGrainedExecutorBackend向DriverEndpoint发送StatusUpdated消息，通知Driver运行的Task状态发生变更

3. StandaloneSchedulerBackend调用TaskScheduler的updateStatus方法更新Task状态

4. StandaloneSchedulerBackend继续调用TaskScheduler的resourceOffers方法，调度其他任务运行

