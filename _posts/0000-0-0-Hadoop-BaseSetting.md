---
layout: post
title: "Hadoop 功能配置"
date: 2019-06-07
description: "简单介绍一下搭建Hadoop功能配置"
tag: Hadoop

---

# 功能配置

## NameNode故障处理

恢复数据方法：将SecondaryNameNode中数据拷贝到NameNode存储数据的目录
1. kill -9 NameNode
2. 删除NameNode数据：`rm -rf hadoop-2.7.2/data/tmp/dfs/name/*`
3. 拷贝数据：`scp -r root@hadoop103:/.../dfs/namesecondary/* ./name/ `
4. 注意NameNode在hadoop101，SecondaryNameNode在hadoop103
5. 重启：`sbin/hadoop-daemon.sh start namenode`


## 增加新节点

1. ip和hostname的修改
2. /etc/hosts文件的修改
3. Java和hadoop安装
4. hadoop配置文件的同步
5. 直接启动DataNode
```
[hadoop105]$ sbin/hadoop-daemon.sh start datanode
[hadoop105]$ sbin/yarn-daemon.sh start nodemanager
```


## distcp 分布式拷贝

用于大规模集群内部和集群之间拷贝的工具。它使用Map/Reduce实现文件分发，错误处理和恢复，以及报告生成。
hadoop distcp dir1 dir2 可用来代替scp，但又有所不同，分为如下两种情况：
1. dir2 不存在，则新建dir2，dir1下文件全部复制到dir2
2. dir2 存在，则目录dir1被复制到dir2下，形成dir2/dir1结构，这样的差异原因是为了避免直接覆盖原有目录文件。可以使用-overwrite，保持同样的目录结构同时覆盖原有文件。

[hadoop101]$ `bin/hadoop distcp hdfs://haoop101:9000/test hdfs://hadoop102:9000/`




## 配置历史服务器

1. mapred-site.xml

```xml
<!-- 历史服务器端地址 -->
<property>
	<name>mapreduce.jobhistory.address</name>
	<value>hadoop101:10020</value>
</property>
<!-- 历史服务器web端地址 -->
<property>
    <name>mapreduce.jobhistory.webapp.address</name>
    <value>hadoop101:19888</value>
</property>
```

2. 启动历史服务器

`sbin/mr-jobhistory-daemon.sh start historyserver`

3. 查看JobHistory

`http://hadoop101:19888`



## 配置日志聚集

日志聚集概念：应用运行完成以后，将程序运行日志信息上传到HDFS系统上。
开启日志聚集功能，需要重新启动NodeManager 、ResourceManager和HistoryManager。

1. yarn-site.xml

```xml
<!-- 日志聚集功能使能 -->
<property>
	<name>yarn.log-aggregation-enable</name>
	<value>true</value>
</property>
<!-- 日志保留时间设置7天 -->
<property>
	<name>yarn.log-aggregation.retain-seconds</name>
	<value>604800</value>
</property>
```

2. 关闭NodeManager 、ResourceManager和HistoryManager
```
sbin/yarn-daemon.sh stop resourcemanager
sbin/yarn-daemon.sh stop nodemanager
sbin/mr-jobhistory-daemon.sh stop historyserver
```

3. 启动NodeManager 、ResourceManager和HistoryManager
```
// 在yarn配置的节点关闭
sbin/yarn-daemon.sh start resourcemanager
sbin/yarn-daemon.sh start nodemanager
sbin/mr-jobhistory-daemon.sh start historyserver
```

4. 删除HDFS上已经存在的输出文件

`bin/hdfs dfs -rm -R /user/atguigu/output`

5. 执行WordCount程序

`hadoop jar
 share/hadoop/mapreduce/hadoop-mapreduce-examples-2.7.2.jar wordcount /user/atguigu/input /user/atguigu/output`

6. 查看日志：http://hadoop101:19888




## SecondaryNameNode 的 CheckPoint 时间设置

```xml
<!-- SecondaryNameNode 默认一小时执行一次 -->
<property>
	<name>dfs.namenode.checkpoint.period</name>
	<value>3600</value>
</property>
```

设置成一分钟检查一次操作次数，当操作次数达到1百万时，SecondaryNameNode执行一次。

```xml
<property>
  <name>dfs.namenode.checkpoint.txns</name>
  <value>1000000</value>
<description> 操作动作次数 </description>
</property>

<property>
  <name>dfs.namenode.checkpoint.check.period</name>
  <value>60</value>
<description> 1分钟检查一次操作次数 </description>
</property>
```



## NameNode 本地多目录配置

1. 可将NameNode的本地目录配置成多个，且每个目录存放内容相同
2. 修改hdfs-site.xml

```xml
<property>
	<name>dfs.namenode.name.dir</name>
	<value>file:///${hadoop.tmp.dir}/dfs/name1,file:///${hadoop.tmp.dir}/dfs/name2</value>
</property>
```

3. 删除每个节点的data和logs:`rm -rf data/ logs/`
4. 格式化集群：`bin/hdfs namenode -format`
5. 启动：`sbin/start-dfs.sh`




## DataNode掉线时限设置

超时公式：TimeOut = dfs.namenode.heartbeat.recheck-interval + 10\*dfs.heartbeat.interval
其中recheck-interval单位ms，默认5分钟；interval单位s，默认3秒

```xml
<property>
    <name>dfs.namenode.heartbeat.recheck-interval</name>
    <value>300000</value>
</property>
<property>
    <name>dfs.heartbeat.interval</name>
    <value>3</value>
</property>
```



## 退役旧数据节点

### 添加白名单：

1. 创建hadoop-2.7.2/etc/hadoop/dfs.hosts文件

2. 增加白名单的主机名：
```
hadoop101
hadoop102
hadoop103
```
3. hdfs-site.xml增加dfs.hosts属性

```xml
<property>
	<name>dfs.hosts</name>
	<value>/.../hadoop-2.7.2/etc/hadoop/dfs.hosts</value>
</property>
```

4. 所有节点同步配置文件

5. 刷新NameNode:`hdfs dfsadmin -refreshNodes`

6. 刷新ResourceManager:`yarn rmadmin -refreshNodes`

7. 实现数据均衡：`./start-balancer.sh`

### 添加黑名单：

1. 创建hadoop-2.7.2/etc/hadoop/dfs.hosts.exclude文件

2. 增加黑名单的主机名：

```
hadoop104
```

3. hdfs-site.xml增加dfs.hosts.exclude属性

```xml
<property>
	<name>dfs.hosts.exclude</name>
	<value>/.../hadoop-2.7.2/etc/hadoop/dfs.hosts.exclude</value>
</property>
```

4. 同步配置文件，刷新

5. 注意服役节点小于副本数是不能退役成功的

6. 数据均衡



## DataNode多目录配置

1. DataNode也可以配置多个目录，但每个目录存储的数据不一样。
2. 修改hdfs-site.xml

```xml
<property>
	<name>dfs.datanode.data.dir</name>
	<value>file:///${hadoop.tmp.dir}/dfs/data1,file:///${hadoop.tmp.dir}/dfs/data2</value>
</property>
```

3. 所有节点同步配置文件
4. 删除日志文件：`rm -rf data/ logs/`
5. 格式化：`bin/hdfs namenode -format`
6. 启动：`sbin/start-dfs.sh`


