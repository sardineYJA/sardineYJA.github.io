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



# 配置

## 单机模式

解压：tar -zxvf XX.tar.gz -C /../module

查看版本：`/bin/hbase version`

编辑 conf/hbase-env.sh
```sh
export JAVA_HOME=/..
export HBASE_MANAGES_ZK=true    # 使用自带Zookeeper
```

编辑 hbase-site.xml，指定HBase数据的存储位置
```xml
<configuration>
    <property>
        <name>hbase.rootdir</name>
        <value>file:///.../hbase/hbase-tmp</value>
    </property>
</configuration>
```

启动：`bin/start-hbase.sh`

操作HBase数据库：`bin/hbase shell` ，状态`status`


## 伪分布式

编辑 conf/hbase-env.sh
```sh
export JAVA_HOME=/...
export HBASE_CLASSPATH=/.../hadoop/conf  # hadoop安装目录conf
export HBASE_MANAGES_ZK=true
```

编辑 conf/hbase-site.xml
```xml
<configuration>
    <property>
        <name>hbase.rootdir</name>   <!-- 存储目录 -->
        <value>hdfs://XXX.XXX.XXX.XXX:9000/hbase</value>
    </property>
    <property>
        <name>hbase.cluster.distributed</name>
        <value>true</value>          <!-- 分布式模式 -->
    </property>
</configuration>
```

## 分布式

```xml
<!-- 设置hbase的根目录，为NameNode所在位置 -->
<property>
	<name>hbase.rootdir</name>
	<value>hdfs://172.16.7.124:9000/hbase</value>
</property>

<!-- 使hbase运行于完全分布式 -->
<property>
	<name>hbase.cluster.distributed</name>
	<value>true</value>
</property>

<!-- Zookeeper集群的地址列表，用逗号分隔 -->
<property>
	<name>hbase.zookeeper.quorum</name>
	<value>172.16.7.124</value>
</property>

<!-- zookeeper保存属性信息的文件，默认为/tmp 重启会丢失 -->
<property>
	<name>hbase.zookeeper.property.dataDir</name>
	<value>../zkData</value>
</property>
```


# 问题

## 多个日志jar

开启`bin/hbase shell`提示：

>SLF4J: Class path contains multiple SLF4J bindings.
SLF4J: Found binding in [jar:file:/home/yangja/module/hbase-2.0.1/lib/slf4j-log4j12-1.7.25.jar!/org/slf4j/impl/StaticLoggerBinder.class]
SLF4J: Found binding in [jar:file:/home/yangja/module/hadoop-2.7.2/share/hadoop/common/lib/slf4j-log4j12-1.7.10.jar!/org/slf4j/impl/StaticLoggerBinder.class]

原因分析：jar包冲突，删除目录下slf4j-log4j12-1.6.4.jar即可


## HBase 启动后 HMaster 进程自动消失

查看日志

> ERROR [main] master.HMasterCommandLine: Master exiting
java.io.IOException: Could not start ZK at requested port of 2181.  ZK was started at port: 2182.  Aborting as clients (e.g. shell) will not be able to find this ZK quorum.

原因分析：当时测试的是单机模式，可是jps发现外置独立的Zookeeper开启了，导致HBase内置的zookeeper无法正确开启。关掉Zookeeper，重启HBase即可。


## HBase 启动后 HMaster 进程自动消失

查看日志

> java.lang.RuntimeException: HMaster Aborted
	at org.apache.hadoop.hbase.master.HMasterCommandLine.startMaster(HMasterCommandLine.java:194)
	at org.apache.hadoop.hbase.master.HMasterCommandLine.run(HMasterCommandLine.java:135)
	at org.apache.hadoop.util.ToolRunner.run(ToolRunner.java:70)
	at org.apache.hadoop.hbase.util.ServerCommandLine.doMain(ServerCommandLine.java:126)
	at org.apache.hadoop.hbase.master.HMaster.main(HMaster.java:2785)
> 2019-08-27 11:07:49,415 INFO  [main-EventThread] zookeeper.ClientCnxn: EventThread shut down

> 172.16.7.124 to 124-centos7-ismg04:8020 failed on connection exception: java.net.ConnectException: 拒绝连接; For more details see:  http://wiki.apache.org/hadoop/ConnectionRefused

原因一：版本问题

原因二：Zookeeper

1. 停止hbase
2. 运行如下代码 ./hbase org.apache.hadoop.hbase.util.hbck.OfflineMetaRepair
3. 运行如下代码 ./zkCli.sh
4. 使用 ls / 
5. 使用 rmr /hbase 
6. 重新启动 hbase




# HBase 数据库操作

HBase是由row key，column family，column和cell组成。
row key确定唯一的一行，column family由若干column组成，column是表的字段，cell存储了实际的值或数据。

开启：`bin/start-hbase.sh`

进入：`bin/hbase shell`

```sh
status  # 数据库状态
help    # 查看帮助
list    # 数据库有哪些表
```

```sh
create 'student','info' 
put 'student','1001','info:name', 'yang'
put 'student','1001','info:sex','male'
put 'student','1001','info:age','28'

get 'student','1001'
get 'student','1001','info:name'
```

```sh
scan 'student'        # 扫描数据
scan 'student',{STARTROW=>'1001',STOPROW=>'1007'}  # 设置范围
describe 'student'   # 表结构
count 'student'      # 统计行数
```

```sh
deleteall 'student','1001'           # 删除某一个rowKey全部的数据
delete 'student','1001','info:sex'   # 删除掉某个rowKey中某一列的数据

truncate 'student'     # 清空表数据

disable 'student'  # 删除前需设置不可用
drop 'student'     # 删除表
```

