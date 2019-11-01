---
layout: post
title: "Hadoop 知识点"
date: 2019-06-01
description: "简单介绍一下Hadoop知识点"
tag: Hadoop

---

# 知识点

## Hadoop1.x与Hadoop2.x的区别

1.x：MapReduce(计算+资源调度)，HDFS(数据存储)，Common(辅助工具)

2.x：MapReduce(计算)，`Yarn(资源调度)`，HDFS(数据存储)，Common(辅助工具)


## HDFS

- NameNode：存储文件的元数据
- DataNode：存储文件块数据
- Secondary NameNode：获取元数据快照

HDFS块的大小设置主要取决于磁盘传输速率。

## Yarn

- ResourceManager:资源分配调度
- NodeManager:管理单个节点上的资源
- ApplicationMaster:数据切片
- Container:资源抽象

![png](/images/posts/all/yarn架构图.PNG)


## 资源调度器

yarn-default.xml文件
```xml
<property>
    <description>The class to use as the resource scheduler.</description>
    <name>yarn.resourcemanager.scheduler.class</name>
	<value>org.apache.hadoop.yarn.server.resourcemanager.scheduler.capacity.CapacityScheduler</value>
</property>
```

Hadoop作业调度器主要有三种

- FIFO（先进先出）：job按到达时间排序，有新的服务器节点资源，再分配

- Capacity Scheduler（容量调度）：job按到达时间排序，分多队列并行计算，每个队列采用FIFO

- Fair Scheduler（公平调度）：job按缺额排序，分多队列并行计算，缺额越大越优先



## 工作机制

shuffle机制
![png](/images/posts/all/hadoop的shuffle机制图.PNG)

MapTask工作机制
![png](/images/posts/all/hadoop的MapTask工作机制.PNG)

ReduceTask工作机制
![png](/images/posts/all/hadoop的ReduceTask工作机制.PNG)


总结：

- Read --> Map --> Collect --> Spill(快速排序) --> Combine --> Copy --> Merge(归并排序) --> Reduce

- 从Map端拷贝到Reduce端的数据都是局部排序的，所以很适合归并排序


## 启动

1. 第一次启动需要格式化NameNode:`hdfs namenode -format`
2. 启动HDFS:`sbin/start-dfs.sh`
3. 启动Yarn:`sbin/start-yarn.sh`

> NameNode和ResourceManger如果不是同一台机器，不能在NameNode上启动 YARN，应该在ResouceManager所在的机器上启动YARN。

> 格式化NameNode，会产生新的集群id,导致NameNode和DataNode的集群id不一致，集群找不到已往数据。所以，格式NameNode时，一定要先删除data数据和log日志，然后再格式化NameNode。



## hdfs 操作

bin/hadoop fs 具体命令 或者 bin/hdfs dfs 具体命令
```
-help
-ls /
-mkdir /test
-put ./1.txt /test/           从本地拷贝到HDFS
-copyFromLocal ./1.txt /test  从本地拷贝到HDFS
-moveFromLocal ./1.txt /test  从本地剪切到HDFS
-copyToLocal /test/2.txt ./   从HDFS拷贝到本地
-get /test/2.txt ./           从HDFS拷贝到本地
-getmerge /test/* ./1/txt     从HDFS合并拷贝到本地
-appendToFile ./1.txt /test/2.txt   
-cat /2.txt
-cp /test/2.txt /app/3.txt    HDFS的复制
-mv /test/2.txt /app/         HDFS的移动
-rm
-rmdir
-du      统计文件夹的大小信息
-setrep  设置HDFS中文件副本数量
```

## HDFS写入数据

![png](/images/posts/all/hdfs写入数据流程图.PNG)

1. Client向NameNode请求上传文件
2. NameNode响应可以上传
3. Client请求上传第一个Block，请求返回DateNode
4. NameNode返回dn1, dn2, dn3
5. Client向DateNode请求建立Block传输通道
6. DateNode应答成功
7. Client传输数据packet
8. 从第3步骤开始第二个Block


## HDFS读取数据

![png](/images/posts/all/hdfs读取数据流程图.PNG)

1. Client向NameNode请求下载文件
2. NameNode 返回目标文件的元数据
3. Client向DataNode请求读取数据
4. DataNode传输数据


## NameNode和SecondaryNameNode 的 Checkpoint 机制

第一阶段：NameNode启动

1. 第一次启动NameNode格式化后，创建Fsimage和Edits文件。如果不是第一次启动，直接加载编辑日志和镜像文件到内存。

2. 客户端对元数据进行增删改的请求。

3. NameNode记录操作日志，更新滚动日志。

4. NameNode在内存中对数据进行增删改。

第二阶段：Secondary NameNode工作

1. Secondary NameNode询问NameNode是否需要CheckPoint。直接带回NameNode是否检查结果。

2. Secondary NameNode请求执行CheckPoint。

3. NameNode滚动正在写的Edits日志。

4. 将滚动前的编辑日志和镜像文件拷贝到Secondary NameNode。

5. Secondary NameNode加载编辑日志和镜像文件到内存，并合并。

6. 生成新的镜像文件fsimage.chkpoint。

7. 拷贝fsimage.chkpoint到NameNode。

8. NameNode将fsimage.chkpoint重新命名成fsimage。


