---
layout: post
title: "Kafka 知识点"
date: 2019-07-14
description: "Kafka"
tag: Bigdata

---

## 简介

一般用来缓存数据，是一个分布式消息队列，高吞吐量、低延迟

kafka集群依赖于zookeeper集群保存meta信息

kafka的内存是不经过JVM的，是基于Linux内核的Page

## 成员

- Broker 一台Kafka节点就是一个Broker，多个Broker组成Kafka集群

- Topic 可理解为一个队列，Kafka根据Topic对消息进行归类

- Producer 消息生产者，向kafka broker发送消息的客户端

- Consumer 消息消费者，向kafka broker取消息的客户端

- Consumer Group (CG) 实现topic消息的广播和单播，即分组发送消息。每个Consumer属于一个特定的CG，一条消息可以发送到多个不同的CG，但是一个CG中只能有一个Consumer能够消费该消息

- Partition 一个Topic可分为多个Partition，每个Partition内部是有序的。，同一个partition可能有多个replication（副本），副本间选择一个Leader，producer和consumer只与Leader交互，其他replication作为follower从Leader中复制数据


- replica partition的副本，保障partition的高可用

- leader replica中的角色，producer和consumer只跟leader交互

- follower replica中的角色，从leader中复制数据

- controller 集群中一个服务器，用于leader选举和故障转移

![png](/images/posts/all/Kafka的拓扑结构.png)


## 发布消息

Kafka 采取拉取模型(Poll)，由自己控制消费速度，以及消费的进度，消费者可以按照任意的偏移量进行消费。


![png](/images/posts/all/Kafka的Topic结构图.png)

producer 采用 push 模式将消息发布到 broker，每条消息都被 append 到 partition 中，属于顺序写磁盘。

选择分区算法：

1. 指定了 partition，则直接使用

2. 未指定 partition 但指定 key，通过对 key 的 value 进行hash 选出一个 partition

3. partition 和 key 都未指定，使用轮询选出一个 partition 


每个分区都是一个顺序的、不可变的消息队列，并且可以持续添加。
分区中的消息都被分配了一个序列号，称之为偏移量（offset），在每个分区中此偏移量都是唯一的。

分区是由多个Segment组成的，是为了方便进行日志清理、恢复等工作。每个Segment以该Segment第一条消息的offset命名并以“.log”作为后缀。另外还有一个索引文件，他标明了每个Segment下包含的Log Entry的offset范围，文件命名方式也是如此，以“.index”作为后缀。

![png](/images/posts/all/Kafka索引与日志文件内部关系图.png)


## 写入流程

1. producer先从zookeeper的 "/brokers/.../state"节点找到该partition的leader

2. producer将消息发送给该leader

3. leader将消息写入本地log

4. followers从leader pull消息，写入本地log后向leader发送ACK

5. leader收到所有ISR中的replication的ACK后，增加HW（high watermark，最后commit 的offset）并向producer发送ACK


## 消息存储策略

- 无论消息是否被消费，kafka都会保留所有消息

- 删除旧数据方式（1）基于时间：log.retention.hours=168

- 删除旧数据方式（2）基于大小：log.retention.bytes=1073741824

- producer不在zk中注册，consumer在zk中注册

## 消费

1. consumer采用pull（拉）模式从broker中读取数据

2. pull模式可根据consumer的消费能力以适当的速率消费消息

3. 每个partition，同一个消费组中的消费者，同一时刻只能有一个消费者消费


## API

- 高级API：简单，无需自行去管理offset，系统通过zookeeper自行管理，无需管理分区、副本等情况，系统自动管理

低级API：能够控制offset，想从哪里读取就从哪里读取，自行控制连接分区，对分区自定义进行负载均衡，对zookeeper的依赖性降低





# reference

https://www.cnblogs.com/jixp/p/9778937.html

https://blog.csdn.net/weixin_35353187/article/details/82999041

