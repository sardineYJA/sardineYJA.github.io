---
layout: post
title: "Hbase 系列"
date: 2019-09-09
description: "Hbase 系列"
tag: Bigdata

---

# HBase

## 特点

原型是Google的BigTable论文，受到了该论文思想的启发

* 分布式的、基于列式存储的数据库

* 基于hadoop的hdfs存储

* zookeeper进行管理

* 适合结构化数据和非结构化数据

* HBase不支持事务

* 不支持Join（对JOIN以及多表合并数据的查询性能不好）


## 自动故障处理和负载均衡

HBase运行在HDFS上，所以HBase中的数据以多副本形式存放，数据也服从分布式存放，数据的恢复也可以得到保障。HMaster和RegionServer也是多副本的。


## 架构


![png](/images/posts/all/基于Hadoop的HBase架构.png)

HBase由三个部分：HMaster，ZooKeeper，HRegionServer


## HMaster

* 监控RegionServer

* 处理RegionServer故障转移

* 对Region进行负载均衡，分配到合适的HRegionServer


## ZooKeeper

选举HMaster，对HMaster，HRegionServer进行心跳检测。虽然HBase内置有zookeeper，但一般选择外置独立的Zookeeper集群来监管，效果更佳。


## HRegionServer

* 负责存储HBase的实际数据

* 一个RegionServer可以包含多个HRegion，

* 每个RegionServer维护一个HLog和多个HFiles以及其对应的MemStore

* RegionServer运行于DataNode上，数量可以与DatNode数量一致

![png](/images/posts/all/HBase的RegionServer架构图.png)


## 内含组件

* Write-Ahead logs : HBase的修改记录，当对HBase读写数据的时候，先写在logfile的文件中，再写入内存中，最后才是硬盘。防止数据在内存中，机器爆炸，数据丢失。

* HFile : 在磁盘上保存原始数据的实际的物理文件

* Store : HFile存储在Store中，一个Store对应HBase表中的一个列族

* MemStore : 内存存储，保存当前的数据操作，所以当数据保存在WAL中之后，RegsionServer会在内存中存储键值对

* Region : Hbase表的分片，Region是Hbase中分布式存储和负载均衡的最小单元。

![png](/images/posts/all/HBase的Region结构图.png)



```java
HRegionSerer (运作在DataNode上)
 	├ HLog
 	├ HRegin (相当于表的分片)
 	│	 ├ Store (一个Store对应一个列族，表有几个列族，则有几个Store)
 	│	 │	   ├ MemStore
	│	 │	   ├ StoreFile 
	│	 │	   ├ StoreFile
	│	 │	   └ ... (第三层：MemStore,StoreFile)
 	│	 ├ Store
 	│	 ├ Store
 	│	 └ ... (第二层：Store)
 	├ HRegin
 	├ HRegin
 	└ ... (第一层：HLog,HRegin)
```

## Meta Table

HBase中有一个特殊的起目录作用的表格，称为META table。
META table中保存集群region的地址信息。
ZooKeeper中会保存META table的位置。

## 逻辑存储模型

```sh
| RowKey |        ColumnFamily:CF1        |       ColumnFamily:CF2     |   TimeStamp  |
|        |  Column:Name | Column:Address  |  Column:Age | Column:Sex   |              |
| rk001  |     yang     |      CH         |      33     |      M       |      t1      |
| rk002  |    chang     |      US         |      21     |      M       |      t2      |
```

RowKey：Hbase 使用 Rowkey 来唯一的区分某一行的数据

列族：Hbase 通过列族划分数据的存储，列族下面可以包含任意多的列，实现灵活的数据存取。
官方推荐的是列族最好小于或者等于3。

时间戳：TimeStamp 对 Hbase 来说至关重要，因为它是实现 Hbase 多版本的关键。
在 Hbase 中使用不同的 timestame 来标识相同 rowkey 行对应的不通版本的数据。

Cell：HBase 中通过 rowkey 和 columns 确定的为一个存储单元称为 cell。
每个 cell 都保存着同一份 数据的多个版本。版本通过时间戳来索引。


## 高可用

每一个Region server都在ZooKeeper中创建相应的ephemeral node。
HMaster通过监控这些ephemeral node的状态来发现正常工作的或发生故障下线的Region server。
HMaster之间通过互相竞争创建ephemeral node进行Master选举。
ZooKeeper会选出区中第一个创建成功的作为唯一一个活跃的HMaster。
活跃的HMaster向ZooKeeper发送心跳信息来表明自己在线的状态。
不活跃的HMaster则监听活跃HMaster的状态，并在活跃HMaster发生故障下线之后重新选举，从而实现了HBase的高可用性。


## 列簇创建

rowKey 最好要创建有规则的 rowKey，即最好是有序的。

HBase 中一张表最好只创建一到两个列族比较好，因为 HBase 不能很好的处理多个列族。



## 使用场景

* 数据有很多列，且包含很多空字段
* 数据包含了不定数量的列
* 需要维护数据的版本
* 需要很高的横向扩展性
* 需要大量的压缩数据
* 需要大量的I/O
* 几十亿列数据，同时在单位时间内有数以千、万记的读写操作


## 相对于Hadoop，HBase存在的必要

* 可以快速检索数据，单纯的Hadoop文件系统HDFS所做不到的。
* HBase作为列式数据库，有数据库的特性，满足急剧增长的应用负载。
* HBase可以支持对数据的更新操作。
* HBase弥补Hadoop不支持实时数据处理的缺陷。


## HBase 和 Hive

- Hive是一种类SQL的引擎，并且运行MapReduce任务，可以用来进行统计查询
- Hive适用于离线的数据分析和清洗，延迟较高
- Hive本身不存储和计算数据，它完全依赖于HDFS和MapReduce
- Hbase是一种在Hadoop之上的NoSQL 的Key/vale数据库，可以用来进行实时查询
- Hbase与Hive都是架构在hadoop之上的。都是用hadoop作为底层存储
- Hive是建立在Hadoop之上为了减少MapReducejobs编写工作的批处理系统
- HBase是为了支持弥补Hadoop对实时操作的缺陷的项目


## HBase 读数据流程

- Client访问Zookeeper获取meta table，从而得知HRegionServer的信息。

- Client通过HRegionServer查询负责管理自己想访问的row key地址。

- Client访问对应的HRegionServer，然后扫描所在HRegionServer的Memstore和Storefile来查询数据。

- 最后HRegionServer把查询到的数据响应给Client。


## HBase 写数据流程

- Client也是先访问zookeeper，找到Meta表，并获取Meta表元数据。确定当前将要写入的数据所对应的HRegion和HRegionServer服务器。

- Client向该HRegionServer服务器发起写入数据请求，然后HRegionServer收到请求并响应。

- Client先把数据写入到HLog（磁盘上），以防止数据丢失。然后将数据写入到Memstore。如果HLog和Memstore均写入成功，则这条数据写入成功。

- 如果Memstore达到阈值，会把Memstore中的数据flush到Storefile中。当Storefile越来越多，会触发Compact合并操作，把过多的Storefile合并成一个大的Storefile。当Storefile越来越大，Region也会越来越大，达到阈值后，会触发Split操作，将Region一分为二。


## Minor Compaction

HBase会自动选取一些较小的HFile进行合并，并将结果写入几个较大的HFile中。

通过Merge sort的形式将较小的文件合并为较大的文件，从而减少了存储的HFile的数量，提升HBase的性能。


## Major Compaction

HBase将对应于某一个Column family的所有HFile重新整理并合并为一个HFile，并在这一过程中删除已经删除或过期的cell，更新现有cell的值。这一操作大大提升读的效率。但是因为Major compaction需要重新整理所有的HFile并写入一个HFile，这一过程包含大量的硬盘I/O操作以及网络数据通信。这一过程也称为写放大（Write amplification）。在Major compaction进行的过程中，当前Region基本是处于不可访问的状态。

Major compaction可以配置在规定的时间自动运行。为避免影响业务，Major compaction一般安排在夜间或周末进行。

Major compaction会将当前Region所服务的所有远程数据下载到本地Region server上。这些远程数据可能由于服务器故障或者负载均衡等原因而存储在于远端服务器上。


## Region split

随着region中数据量的增加，region会被分割成两个子region。每一个子region中存储原来一半的数据。同时Region server会通知HMaster这一分割。出于负载均衡的原因，HMaster可能会将新产生的region分配给其他的Region server管理（这也就导致了Region server服务远端数据的情况的产生）。



## Data Replication

HDFS会自动备份WAL和HFile。


## Region Server 宕机


当Region server宕机的时候，其所管理的region在这一故障被发现并修复之前是不可访问的。ZooKeeper负责根据服务器的心跳信息来监控服务器的工作状态。当某一服务器下线之后，ZooKeeper会发送该服务器下线的通知。HMaster收到这一通知之后会进行恢复操作。

HMaster会首先将宕机的Region server所管理的region分配给其他仍在工作的活跃的Region server。然后HMaster会将该服务器的WAL分割并分别分配给相应的新分配的Region server进行存储。新的Region server会读取并顺序执行WAL中的数据操作，从而重新创建相应的MemStore。


## Data Recovery

当MemStore中存储的数据因为某种原因丢失之后，HBase以WAL对其进行恢复。

## flush 机制

- 参数：`hbase.hregion.memstore.flush.size：134217728`当MemStore达到阈值，将Memstore中的数据Flush进Storefile，128M就是Memstore的默认阈值。

- 参数：`hbase.regionserver.global.memstore.upperLimit：0.4`当单个HRegion内所有的Memstore大小总和超过指定值时，flush该HRegion的所有memstore。RegionServer的flush是通过将请求添加一个队列，模拟生产消费模式来异步处理的。那这里就有一个问题，当队列来不及消费，产生大量积压请求时，可能会导致内存陡增，最坏的情况是触发OOM。

- 参数：`hbase.regionserver.global.memstore.lowerLimit：0.38`当MemStore使用内存总量达到hbase.regionserver.global.memstore.upperLimit指定值时，将会有多个MemStores flush到文件中，MemStore flush 顺序是按照大小降序执行的，直到刷新到MemStore使用内存略小于lowerLimit。



## 节点服役（commissioning）

当启动regionserver时，regionserver会向Hmaster注册并开始接收本地数据，开始的时候，新加入的节点不会有任何数据，平衡器开启的情况下，将会有新的region移动到开启的RegionServer上。如果启动和停止进程是使用ssh和HBase脚本，那么会将新添加的节点的主机名加入到conf/regionservers文件中。

## 节点退役（decommissioning）

删除某个RegionServer：

1. 停止负载平衡器：`hbase > balance_switch false`
2. 停止RegionServer：`hbase > hbase-daemon.sh stop regionserver`
3. RegionServer一旦停止，会关闭维护的所有region
4. Zookeeper上的该RegionServer节点消失
5. Master节点检测到该RegionServer下线
6. RegionServer的region服务得到重新分配

以上关闭方法比较传统，需要花费一定的时间，而且会造成部分region短暂的不可用。

另一种方法：

1. RegionServer先卸载所管理region：`bin/graceful_stop.sh xxx.xxx.xxx.xxx（IP）`
2. 自动平衡数据
3. 接下来步骤为上个方法2-6


# reference

https://www.jianshu.com/p/479bc6308381