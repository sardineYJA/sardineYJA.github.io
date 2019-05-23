---
layout: post
title: "虚拟机搭建Hadoop集群"
date: 2019-02-04
description: "简单介绍一下如何用虚拟机搭建Hadoop集群"
tag: 大数据

---

# 安装准备
## 安装JDK
卸载现有JDK
1. 查询是否安装Java软件：`[hadoop101 opt]$ rpm -qa | grep java`
2. 如果安装的版本低于1.7，卸载该JDK：`[hadoop101 opt]$ sudo rpm -e 软件包`
3. 查看JDK安装路径：`[hadoop101 ~]$ which java`
4. 解压JDK：`[hadoop101 software]$ tar -zxvf jdk-8u144-linux-x64.tar.gz -C /opt/module/`
5. 配置JDK环境变量：`[hadoop101 software]$ sudo vi /etc/profile`
```
#JAVA_HOME
export JAVA_HOME=/opt/module/jdk1.8.0_144
export PATH=$PATH:$JAVA_HOME/bin
```
6. 让修改后的文件生效：`[hadoop101 jdk1.8.0_144]$ source /etc/profile`
7. 测试JDK是否安装成功：`[@hadoop101 jdk1.8.0_144]# java -version`

## 安装hadoop
1. [Hadoop下载](https://archive.apache.org/dist/hadoop/common/hadoop-2.7.2/)
2. 解压安装文件：`[hadoop101 software]$ tar -zxvf hadoop-2.7.2.tar.gz -C /opt/module/`
3. 将Hadoop添加到环境变量：`[hadoop101 hadoop-2.7.2]$ sudo vi /etc/profile`
```
##HADOOP_HOME
export HADOOP_HOME=/opt/module/hadoop-2.7.2
export PATH=$PATH:$HADOOP_HOME/bin
export PATH=$PATH:$HADOOP_HOME/sbin
```
4. 让修改后的文件生效：`[hadoop101 jdk1.8.0_144]$ source /etc/profile`
5. 测试JDK是否安装成功：`[@hadoop101 jdk1.8.0_144]# hadoop -version`

# 修改配置文件
## 集群部署规划
||hadoop101|hadooop102|hadoop103|
|:-:|:-:|:-:|:-:|
|HDFS|NameNode&DataNode|DataNode|SecondaryNameNode&DataNode|
|YARN|NodeManager|ResourceManager&NodeManager|NodeManager|

## core-site.xml
```
<!-- 指定HDFS中NameNode的地址 -->
<property>
		<name>fs.defaultFS</name>
      <value>hdfs://hadoop101:9000</value>
</property>

<!-- 指定Hadoop运行时产生文件的存储目录 -->
<property>
		<name>hadoop.tmp.dir</name>
		<value>/opt/module/hadoop-2.7.2/data/tmp</value>
</property>
```

## hadoop-env.sh yarn-env.sh mapred-env.sh
增加`export JAVA_HOME=/opt/module/jdk1.8.0_144`

## hdfs-site.xml
```
<property>
		<name>dfs.replication</name>
		<value>3</value>
</property>

<!-- 指定Hadoop辅助名称节点主机配置 -->
<property>
      <name>dfs.namenode.secondary.http-address</name>
      <value>hadoop103:50090</value>
</property>
```

## yarn-site.xml
```
<!-- Reducer获取数据的方式 -->
<property>
		<name>yarn.nodemanager.aux-services</name>
		<value>mapreduce_shuffle</value>
</property>

<!-- 指定YARN的ResourceManager的地址 -->
<property>
		<name>yarn.resourcemanager.hostname</name>
		<value>hadoop102</value>
</property>
```

## mapred-site.xml
```
<!-- 指定MR运行在Yarn上 -->
<property>
		<name>mapreduce.framework.name</name>
		<value>yarn</value>
</property>
```

## 最后同步三台虚拟机

# 启动
1. 配置slaves：
```
cd /opt/module/hadoop-2.7.2/etc/hadoop/slaves
vi slaves
hadoop101
hadoop102
hadoop103
```
2. 第一次启动，需要格式化NameNode：`[hadoop101]$ hadoop namenode -format`
3. 启动、停止
```
[hadoop101]$ sbin/start-dfs.sh
[hadoop102]$ sbin/start-yarn.sh
```

# 参考
1. 尚硅谷大数据教程