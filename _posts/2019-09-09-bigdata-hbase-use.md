---
layout: post
title: "Hbase"
date: 2019-09-09
description: "Hbase"
tag: 大数据

---


## HBase 启动后 HMaster 进程自动消失

查看日志out

> SLF4J: Class path contains multiple SLF4J bindings.
> SLF4J: Found binding in [jar:file:/home/yangja/module/hbase-0.98.6-hadoop2/lib/slf4j-log4j12-1.6.4.jar!/org/slf4j/impl/StaticLoggerBinder.class]

jar包冲突，删除目录下slf4j-log4j12-1.6.4.jar即可

查看日志log

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


```xml
<!-- 设置hbase的根目录，为NameNode所在位置 -->
<property>
	<name>hbase.rootdir</name>
	<value>hdfs://172.16.7.124:8020/hbase</value>
</property>

<!-- 使hbase运行于完全分布式 -->
<property>
	<name>hbase.cluster.distributed</name>
	<value>true</value>
</property>

<!-- HMaster的端口号 -->
<property>
	<name>hbase.master.port</name>
	<value>60000</value>
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






