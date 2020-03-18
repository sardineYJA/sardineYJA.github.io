---
layout: post
title: "Hbase 环境配置"
date: 2019-09-09
description: "Hbase 系列"
tag: Bigdata

---

# 搭建

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
    <property>
        <name>hbase.master.info.port</name>
        <value>60010</value>          <!-- Web打开http://172.16.7.124:60010 -->
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


## 高可用

- 在conf下创建backup-masters文件，写入高可用节点`echo hadoop101.com > backup-masters`

- 将conf目录同步到其他节点

- Web打开查看是否配置成功：http://172.16.7.124:60010



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

