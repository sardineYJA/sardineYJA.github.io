---
layout: post
title: "Zookeeper 分布式管理"
date: 2019-07-09
description: "Zookeeper"
tag: Bigdata

---

# Zookeeper

为分布式应用提供协调服务：统一命名服务、统一配置管理、统一集群管理、服务器节点动态上下线、软负载均衡等。

是一个基于观察者模式设计的分布式服务管理框架，负责存储和管理的数据，然后接受观察者的注册，一旦这些数据的状态发生变化，Zookeeper负责通知已经注册的观察者做出相应的反应。

Zookeeper = 文件系统 + 通知机制。


## 集群架构

![png](/images/posts/all/Zookeeper集群架构.png)


## 角色

- Leader 负责进行投票的发起和决议，更新系统状态

- Follower 接收客户请求并向客户端返回结果，参与选举

- ObServer 接收客户端连接，将请求转发给Leader，不参与投票选举，只同步 leader 状态。 ObServer 的目的是扩展系统，提高速度。



## 特点

1. 一个Leader，多个Follower

2. 集群中只要半数以上节点存活就能正常服务

3. 全局数据一致：每个Server保存一份相同的数据副本，Client无论连接到哪个Server，数据都是一致的

4. 数据更新原子性


## 选举机制

1. 半数机制：集群中半数以上机器存活，集群可用，适合安装奇数台服务器

2. 选举机制：Leader是通过内部的选举机制临时产生


## 节点类型

1. 持久（persistent）：客户端与服务器端断开连接后，创建的节点不删除

2. 短暂（ephemeral）：客户端与服务器端断开连接后，创建的节点自己删除


## 监听器原理

1. main()线程中创建zkClient客户端

2. zkClient创建俩个线程：connect负责网络连接通信，listener负责监听

3. 通过connect线程将注册的监听事件发送给Zookeeper

4. 在Zookeeper的注册监听器列表中将注册的监听事件添加到列表中

5. Zookeeper监听到有数据或路径变化，就会将消息发送给listener线程

6. listener线程内部调用process()方法


## 写数据流程

1. Client向Zookeeper的Server发送写请求

2. Server不是Learder，则Server将请求发送给Leader。Leader将写请求广播给各个Server

3. 各个Server完成写请求，通知Leader

4. Leader收到半数以上的通知，则说明数据写成功

5. Leader会通知先前的Server，由先前的Server通知Client完成写操作


## Split-Brain (脑裂)问题

脑裂：由于假死会发起新的master选举，选举出一个新的master，但旧的master网络又通了，导致出现了两个master ，有的客户端连接到老的master 有的客户端链接到新的master。

解决：半数以上选举。


## ZAB 协议

ZAB 协议是为分布式协调服务ZooKeeper专门设计的一种支持崩溃恢复的一致性协议，这个机制保证了各个server之间的同步。全称 Zookeeper Atomic Broadcast Protocol - Zookeeper 原子广播协议。

两种模式：恢复模式和广播模式。



# 安装部署

## 本地模式

1. 下载：https://zookeeper.apache.org

2. 解压：tar -zxvf zookeeper-3.4.10.tar.gz -C /../module/

3. 创建../zookeeper-3.4.10/zkData 目录

4. 配置文件conf目录：cp zoo_sample.cfg zoo.cfg

5. 修改zoo.cfg文件

```
dataDir=/.../zookeeper-3.4.10/zkData
```

6. 启动：bin/zkServer.sh start

7. 查看进程jps：QuorumPeerMain

8. 查看状态：bin/zkServer.sh status

9. 启动客户端：bin/zkCli.sh

10. 退出客户端：quit

11. 停止Zookeeper：bin/zkServer.sh stop


## 分布式安装

1. 创建zkData/myid文件，并写入

```
1
```

2. 编辑zoo.cfg，dataDir要绝对路径

```
dataDir=/.../zookeeper-3.4.10/zkData
#######################cluster##########################
server.1=hadoop101:2888:3888
server.2=hadoop102:2888:3888
server.3=hadoop103:2888:3888
```

3. 同步各个节点的配置文件，除了myid文件

4. 各个节点分别启动


# 客户端操作

启动客户端：bin/zkCli.sh

命令
```
help               显示所有操作
ls /               显示当前znode中包含的内容
ls /jiedian watch  监听路径变化
ls2 /              当前znode详细数据
create /jiedian "context"   创建节点（-s含序列，-e临时）
get /jiedian       获取节点的值
get /jiedian watch 监听值的变化
set /jiedian       修改节点的值
stat /jiedian      节点状态
delete /jiedian    删除节点
rmr    /jiedian    递归删除节点
```

# reference

https://blog.csdn.net/lingbo229/article/details/81052078

https://segmentfault.com/a/1190000019153800?utm_source=tag-newest

