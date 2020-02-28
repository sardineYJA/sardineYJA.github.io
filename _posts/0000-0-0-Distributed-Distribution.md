---
layout: post
title: "分布式理论知识点"
date: 2019-07-08
description: "分布式理论知识点"
tag: Distributed Service

---


# 分布式理论

## CAP 定理

- Consistency (一致性)：数据在多个副本之间能够保持一致的特性。

- Availability (可用性)：系统提供的服务必须一直处于可用的状态。

- Partition tolerance (分区容错性)：分布式系统在遇到任何网络分区故障的时候，仍然能够对外提供满足一致性和可用性的服务。


集群间网络延迟/断开问题：

- 牺牲数据一致性，保证可用性。响应旧的数据给用户。 
- 牺牲可用性，保证数据一致性。阻塞等待，直到网络连接恢复，数据更新操作完成之后，再给用户响应最新的数据。 


## BASE 理论

- Basically Available (基本可用)：相比较正常的系统而言：响应时间、功能的损失。

- Soft State (软状态)：允许系统在多个不同节点的数据副本存在数据延时（允许系统中的数据存在中间状态）。

- Eventually Consistent (最终一致性)：软状态必须有个时间期限，最终数据一致。


## 分布式锁

- 数据库的唯一索引：（锁没有失效时间，解锁失败会导致死锁）

- Redis 的 SETNX 指令：（键值对设置一个过期时间，从而避免了死锁的发生）

- Zookeeper 的有序节点：羊群效应（所有子节点会收到通知，可只希望它的后一个子节点收到通知）


## 分布式 Session

在分布式场景下，一个用户的 Session 如果只存储在一个服务器上，那么当负载均衡器把用户的下一个请求转发到另一个服务器上，该服务器没有用户的 Session，就可能导致用户需要重新进行登录等操作。

可以使用 Redis 和 Memcached 这种内存型数据库对 Session 进行存储，可以大大提高 Session 的读写效率。


## 负载均衡

- 轮询：适合每个服务器的性能差不多。

- 加权轮询：根据服务器的性能差异，为服务器赋予一定的权值。

- 最少连接：将请求发送给当前最少请求连接数的服务器上。

- 源地址哈希法 (IP Hash)：保证同一 IP 的客户端都会被 hash 到同一台服务器上。


## 高可用之“脑裂”

当两（多）个节点同时认为自已是唯一处于活动状态的服务器从而出现争用资源的情况，这种争用资源的场景即是所谓的“脑裂”（split-brain）或“区间集群”（partitioned cluster）。


## 一致性问题

FLP定理告诉我们，一致性算法的可靠性是无法保证的，同时满足 safety和 liveness 的一致性协议是不存在的，即不存在一个能在异步网络上能够容忍各种故障并保持一致的分布式系统。


## 解决一致性问题的协议

- 2PC (tow phase commit)两阶段提交：分成两个阶段，先由协调者(coordinator)进行提议(propose)并收集其他参与者(participants)的反馈(vote)，再根据反馈决定提交(commit)或中止(abort)事务。

- 3PC (three phase commit)三阶段提交：增加了准备提交(prepare to commit)阶段，防止participant宕机后整个系统进入阻塞态。

- Paxos 协议

- Raft 协议

- Zab 协议



# reference

https://github.com/wangzhiwubigdata/God-Of-BigData

