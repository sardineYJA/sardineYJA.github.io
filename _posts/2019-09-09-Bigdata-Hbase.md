---
layout: post
title: "Hbase 系列"
date: 2019-09-09
description: "Hbase 系列"
tag: Bigdata

---

# HBase

## 简介

原型是Google的BigTable论文，受到了该论文思想的启发

* 提供表状的面向列的数据存储

* 针对表状数据的随机读写进行优化

* 优化了多次读，以及多次写

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


## HBase 读数据流程

- Client访问Zookeeper，获取meta表在哪个HRegionServer。

- Client通过刚才HRegionServer读取meta元数据。

- Client通过元数据中存储的信息，访问对应的HRegionServer，然后扫描所在HRegionServer的Memstore和Storefile来查询数据。

- 最后HRegionServer把查询到的数据响应给Client。


## HBase 写数据流程

- Client也是先访问zookeeper，找到Meta表，并获取Meta表元数据。确定当前将要写入的数据所对应的HRegion和HRegionServer服务器。

- Client向该HRegionServer服务器发起写入数据请求，然后HRegionServer收到请求并响应。

- Client先把数据写入到HLog，以防止数据丢失。然后将数据写入到Memstore。如果HLog和Memstore均写入成功，则这条数据写入成功

- 如果Memstore达到阈值，会把Memstore中的数据flush到Storefile中。当Storefile越来越多，会触发Compact合并操作，把过多的Storefile合并成一个大的Storefile。当Storefile越来越大，Region也会越来越大，达到阈值后，会触发Split操作，将Region一分为二。


## flush 机制

- 参数：`hbase.hregion.memstore.flush.size：134217728`当MemStore达到阈值，将Memstore中的数据Flush进Storefile，128M就是Memstore的默认阈值。

- 参数：`hbase.regionserver.global.memstore.upperLimit：0.4`当单个HRegion内所有的Memstore大小总和超过指定值时，flush该HRegion的所有memstore。RegionServer的flush是通过将请求添加一个队列，模拟生产消费模式来异步处理的。那这里就有一个问题，当队列来不及消费，产生大量积压请求时，可能会导致内存陡增，最坏的情况是触发OOM。

- 参数：`hbase.regionserver.global.memstore.lowerLimit：0.38`当MemStore使用内存总量达到hbase.regionserver.global.memstore.upperLimit指定值时，将会有多个MemStores flush到文件中，MemStore flush 顺序是按照大小降序执行的，直到刷新到MemStore使用内存略小于lowerLimit。

## compact 机制

把小的Memstore文件合并成大的Storefile文件。

## split 机制

当Region达到阈值，会把过大的Region一分为二。




