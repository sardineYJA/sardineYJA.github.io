---
layout: post
title: "Kafka 知识点"
date: 2019-07-14
description: "Kafka"
tag: Bigdata

---

## 简介

分布式发布-订阅消息系统，最初是由LinkedIn公司开发的

一般用来缓存数据，是一个分布式消息队列，高吞吐量、低延迟

kafka集群依赖于zookeeper集群保存meta信息

kafka的内存是不经过JVM的，是基于Linux内核的Page


## 作用

- 缓冲：上游数据时有突发流量，下游可能扛不住，或者下游没有足够多的机器来保证冗余，kafka在中间可以起到一个缓冲的作用，把消息暂存在kafka中，下游服务就可以按照自己的节奏进行慢慢处理。

- 健壮性：消息队列可以堆积请求，所以消费端业务即使短时间死掉，也不会影响主要业务的正常进行。

- 异步通信：很多时候，用户不想也不需要立即处理消息。消息队列提供了异步处理机制，允许用户把一个消息放入队列，但并不立即处理它。


## Zookeeper 作用

- 存储meta信息，consumer的消费状态，group的管理以及offset的值

- 选举controller，检测broker是否存活


## producer 向 kafka 输入数据，ack 为 0， 1， -1 

- 1（默认）  数据发送到Kafka后，经过leader成功接收消息的的确认，就算是发送成功了。在这种情况下，如果leader宕机了，则会丢失数据。

- 0 生产者将数据发送出去就不管了，不去等待任何返回。这种情况下数据传输效率最高，但是数据可靠性确是最低的。

- -1 producer需要等待ISR中的所有follower都确认接收到数据后才算一次发送完成，可靠性最高。当ISR中所有Replica都向Leader发送ACK时，leader才commit，这时候producer才能认为一个请求中的消息都commit了。



## 成员

- Broker 一台Kafka节点就是一个Broker，多个Broker组成Kafka集群

- Topic 可理解为一个队列，Kafka根据Topic对消息进行归类

- Producer 消息生产者，向kafka broker发送消息的客户端

- Consumer 消息消费者，向kafka broker取消息的客户端

- Consumer Group (CG) 实现topic消息的广播和单播，即分组发送消息。每个Consumer属于一个特定的CG，一条消息可以发送到多个不同的CG，但是一个CG中只能有一个Consumer能够消费该消息

- Partition 一个Topic可分为多个Partition，每个Partition内部是有序的。同一个partition可能有多个replication（副本），副本间选择一个Leader，producer和consumer只与Leader交互，其他replication作为follower从Leader中复制数据

- replica partition的副本，保障partition的高可用

- leader replica中的角色，producer和consumer只跟leader交互

- follower replica中的角色，从leader中复制数据

- controller 集群中一个服务器，用于leader选举和故障转移

- ISR（In-Sync Replicas）副本同步队列

- AR（Assigned Replicas）所有副本

![png](/images/posts/all/Kafka的拓扑结构.png)


## Controller

kafka在所有broker中选出一个controller，所有Partition的Leader选举都由controller决定。

每个数据有多个备份，与producer、consumer交互的则是leader，其他叫follower。

每台Broker可能有leader，follower（此时follower是另一个leader的备份）。


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

5. leader收到所有ISR（In-Sync Replicas 副本同步队列）中的replication的ACK后，增加HW（high watermark，最后commit 的offset）并向producer发送ACK


## 消息存储策略

- 无论消息是否被消费，kafka都会保留所有消息

- 删除旧数据方式（1）基于时间：log.retention.hours=168

- 删除旧数据方式（2）基于大小：log.retention.bytes=1073741824

- producer不在zk中注册，consumer在zk中注册

## 消费

1. consumer采用pull（拉）模式从broker中读取数据

2. pull模式可根据consumer的消费能力以适当的速率消费消息

3. 每个partition，同一个消费组中的消费者，同一时刻只能有一个消费者消费


# 消息丢失和重复消费

## 消息发送

方式：同步（sync）和异步（async），默认同步，可通过producer.type属性进行配置。

配置request.required.acks属性来确认消息的生产：

- 0---表示不进行消息接收是否成功的确认
- 1---表示当Leader接收成功时确认
- -1---表示Leader和Follower都接收成功时确认


## 消息消费

- 高级API：简单，无需自行去管理offset，系统通过zookeeper自行管理，无需管理分区、副本等情况，系统自动管理

- 低级API：能够控制offset，想从哪里读取就从哪里读取，自行控制连接分区，对分区自定义进行负载均衡，对zookeeper的依赖性降低

## 消息丢失

情景1：使用High-level API，可能存在一个问题，当消息消费者从集群中把消息取出来、并提交了新的消息offset值后，还没来得及消费就挂掉了，那么下次再消费时之前没消费成功的消息就丢失了。

解决：同步模式下，确认机制设置为-1，即让消息写入Leader和Follower之后再确认消息发送成功。

情景2：使用异步模式的时候，当缓冲区满了，如果配置为0（还没有收到确认的情况下，缓冲池一满，就清空缓冲池里的消息），数据就会被立即丢弃掉。

解决：在配置文件中设置成不限制阻塞超时的时间，也就说让生产端一直阻塞，这样也能保证数据不会丢失。


## 重复消费

consumer有些消息处理了，但是没来得及提交commit offset。

解决：将消息的唯一标识保存到外部介质中，每次消费处理时判断是否处理过（如将处理过的id保存到Redis）。



# reference

https://www.cnblogs.com/jixp/p/9778937.html

https://blog.csdn.net/weixin_35353187/article/details/82999041

https://blog.csdn.net/qq_28900249/article/details/90346599
