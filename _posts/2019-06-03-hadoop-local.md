---
layout: post
title: "搭建Hadoop单机模式"
date: 2019-06-03
description: "简单介绍一下如何搭建Hadoop单机模式"
tag: 大数据

---

# 本地模式

安装hadoop成功后即可测试：
## 统计个数
其中input文件夹中包括需统计的文件,output输出目录（自动创建）
`hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-2.7.2.jar grep input output 'he[a-z.]+'`
`hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-2.7.2.jar wordcount input output`


# 伪分布运行模式

将MapReduce指定在HDFS上运行

## hadoop-env.sh（省略此步骤）
export JAVA_HOME=/opt/module/jdk1.8.0_144

## core-site.xml
```xml
<!-- 指定HDFS中NameNode的地址 -->
<property>
	<name>fs.defaultFS</name>
    <value>hdfs://hadoop101:9000</value>
</property>

<!-- 指定Hadoop运行时产生文件的存储目录 -->
<property>
	<name>hadoop.tmp.dir</name>
	<value>/opt/tmp</value>
</property>
```

## hdfs-site.xml
```xml
<!-- 指定HDFS副本的数量 -->
<property>
	<name>dfs.replication</name>
	<value>1</value>
</property>
```

## 第一次必须格式化
`bin/hdfs namenode -format`

## 启动
`sbin/hadoop-daemon.sh start namenode`
`sbin/hadoop-daemon.sh start datanode`

## 关闭防火墙
`firewall-cmd --state`
`systemctl stop firewalld.service`
`systemctl disable firewalld.service`
访问：http://xxx.xxx.xxx.xxx:50070

## 问题
### hadoop.tmp.dir值必须绝对目录
> ERROR namenode.NameNode: Failed to start namenode.
> java.lang.IllegalArgumentException: URI has an authority component

### hadoop.tmp.dir目录必须未创建
> java.io.IOException: Cannot create directory /home/yangja/tmp/dfs/name/current

### jps未找到命令
java版本过低或者jps未安装：
1. 卸载安装java1.8及以上即可
2. 或者安装openjdk-devel
(之前测试系统的jdk是1.7，安装相应的openjdk-devel即可)
```
rpm -qa |grep -i jdk
java-1.7.0-openjdk-headless-1.7.0.65-3.b17.el7.x86_64
查看版本后，安装相应版本
yum install java-1.7.0-openjdk-devel.x86_64
```

# 伪分布运行模式

将MapReduce指定在Yarn上运行，需先完成上面Namenode和Datanode并启动

## yarn-env.sh 和 mapred-env.sh（省略此步骤）
`export JAVA_HOME=/opt/module/jdk1.8.0_144`

## yarn-site.xml 
```xml
<!-- Reducer获取数据的方式 -->
<property>
 	<name>yarn.nodemanager.aux-services</name>
 	<value>mapreduce_shuffle</value>
</property>

<!-- 指定YARN的ResourceManager的地址 -->
<property>
	<name>yarn.resourcemanager.hostname</name>
	<value>hadoop101</value>
</property>

```

## mapred-site.xml
`cp mapred-site.xml.template mapred-site.xml`
```xml
<!-- 指定MR运行在YARN上 -->
<property>
	<name>mapreduce.framework.name</name>
	<value>yarn</value>
</property>
```

## 启动
`sbin/yarn-daemon.sh start resourcemanager`
`sbin/yarn-daemon.sh start nodemanager`
访问：http://xxx.xxx.xxx.xxx:8088