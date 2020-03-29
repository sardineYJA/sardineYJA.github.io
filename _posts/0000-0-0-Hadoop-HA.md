---
layout: post
title: "Hadoop HA高可用"
date: 2020-03-20
description: "Hadoop HA高可用"
tag: Hadoop

---


# HDFS HV

![png](/images/posts/all/HDFS-HA原理图.png)


- Standby NameNode 和 Active NameNode中的元数据是同步的

- active standby保存两份元数据edits操作文件,同时定时同步JournalNode

- ZKFailoverController 及时检测到 NameNode 的健康状况，在主 NameNode 故障时借助 Zookeeper 实现自动的主备选举和切换


![png](/images/posts/all/HDFS-HA原理图2.png)

- ZKFailoverController 在初始化的时候会创建 HealthMonitor 检测 NameNode 的状态

- ActiveStandbyElector 完成 Namenode(包括 YARN ResourceManager) 的主备选举


## zookeeper 节点

- ActiveStandbyElector 就会发起一次主备选举，尝试在 Zookeeper 上创建 ActiveStandbyElectorLock 的临时节点，成功则会成为主 NameNode


## fencing 隔离

- 创建 ActiveBreadCrumb 的持久节点，保存了 Active NameNode 的地址信息

- 当 Active NameNode 正常关闭，ActiveStandbyElectorLock 和 ActiveBreadCrumb 节点正常删除

- 当 Active NameNode 假死（暂时不可用后恢复），ActiveBreadCrumb 会保留，另一个 NameNode 选主成功，会对 ActiveBreadCrumb信息（即上一个Active）进行隔离，当然后续会覆盖新的。



# Yarn HA

![png](/images/posts/all/HDFS-HA原理图2.png)

## ResourceManager(RM):

启动的时候会通过向ZK写Lock文件，写成功则成为Active，否则为Standby。

接收客户端任务请求，接收和监控NodeManager(NM)的资源情况汇报，负责资源的分配与调度，启动和监控ApplicationMaster(AM)。

## NodeManager

节点上的资源管理，启动Container运行task计算，上报资源、container情况汇报给RM和任务处理情况汇报给AM。

## ApplicationMaster

单个Application(Job)的task管理和调度，向RM进行资源的申请，向NM发出launch Container指令，接收NM的task处理状态信息。

## RMStateStore

RM 的作业信息存储在ZK的/rmstore下，Active RM向这个目录写App信息。

当Active RM挂掉，另外一个Standby RM成功转换为Active RM后，会从/rmstore读取相应的作业信息，重新构建作业的内存信息。然后启动内部服务，开始接收NM的心跳，构建集群资源信息，并接收客户端提交作业的请求等。


# reference 

https://blog.csdn.net/qq_33283716/article/details/81097092

https://blog.csdn.net/realoyou/article/details/79464504




