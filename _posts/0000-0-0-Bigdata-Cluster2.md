---
layout: post
title: "快速搭建2 —— Hadoop HA高可用"
date: 2020-03-20
description: "Bigdata"
tag: Bigdata

---

# zookeeper 

## 配置

zookeeper-3.4.14.tar.gz解压，并创建目录zkData和文件zkData/myid，写进1

修改配置文件conf/
```sh
cp zoo_sample.cfg zoo.cfg
# Zookeeper服务器之间或客户端与服务器之间维持心跳的时间间隔
tickTime=2000
# 配置 Zookeeper 接受客户端初始化连接时最长能忍受多少个心跳时间间隔数。
initLimit=10
# Leader 与 Follower 之间发送消息，请求和应答时间长度
syncLimit=5
# 数据目录需要提前创建
dataDir=/home/yang/module/zookeeper-3.4.14/zkData
# 访问端口号
clientPort=2181
# server.每个节点服务编号=服务器ip地址：集群通信端口：选举端口
server.1=VM124:2888:3888
server.2=VM125:2888:3888
server.3=VM126:2888:3888
```

修改bin/zkEnv.sh，写进JAVA_HOME="/home/yang/module/jdk1.8.0_241"

> zookeeper.out nohup: 无法运行命令'java': 没有那个文件或目录

```sh
if [ "x${ZOO_LOG_DIR}" = "x" ]
then    # 修改日志zookeeper.out目录
    ZOO_LOG_DIR="/home/yang/module/zookeeper-3.4.14/LogDir"
fi
```

同步到其他节点，并修改myid，分别写进2,3

启动/查看状态：bin/zkServer.sh start/status（jps进程QuorumPeerMain）


## 脚本

```sh
#!/bin/bash
################## 设置相关信息 ###################
root_dir=/home/yang/module/
zookeeper_dir=${root_dir}zookeeper-3.4.14/
user_name=yang
all_VM=(VM124 VM125 VM126) 

################## 下面尽量不要修改 ####################

# 启动
start_zookeeper(){
	echo -e "\n++++++++++++++++++++ Zookeeper集群启动 +++++++++++++++++++++"
	for i in ${all_VM[*]}
	do
		echo -e "\n=========> 启动 ${i} ...."
		ssh ${user_name}@$i ${zookeeper_dir}bin/zkServer.sh start
	done
}


# 关闭
stop_zookeeper(){
	echo -e "\n++++++++++++++++++++ Zookeeper集群关闭 +++++++++++++++++++++"
	for i in ${all_VM[*]}
	do
		echo -e "\n=========> 关闭 ${i} ...."
		ssh ${user_name}@$i ${zookeeper_dir}bin/zkServer.sh stop
	done
}


# 获取输入参数个数，如果没有参数，直接退出
pcount=$#
if((pcount==0)); then
	echo no args, example : $0 start/stop;
	exit;

elif [[ "$1" == "start" ]]; then
	echo start;
	start_zookeeper


elif [[ "$1" == "stop" ]]; then
	echo stop;
	stop_zookeeper

else
	echo example : $0 start/stop;
	exit;
fi
```



# hadoop HA

## 环境变量

解压hadoop-2.7.2.tar.gz

```sh
vi /etc/profile   # root 操作，同步
## HADOOP_HOME
export HADOOP_HOME=/home/yang/module/hadoop-2.7.2
export PATH=$PATH:$HADOOP_HOME/bin
export PATH=$PATH:$HADOOP_HOME/sbin
source /etc/profile
```

hadoop-env.sh
```sh
export HADOOP_PID_DIR=/home/yang/module/hadoop-2.7.2/pids
export JAVA_HOME=/home/yang/module/jdk1.8.0_241
```
yarn-env.sh
```sh
export YARN_PID_DIR=/home/yang/module/hadoop-2.7.2/pids
export JAVA_HOME=/home/yang/module/jdk1.8.0_241
```
mapred-env.sh
```sh
export HADOOP_MAPRED_PID_DIR=/home/yang/module/hadoop-2.7.2/pids
export JAVA_HOME=/home/yang/module/jdk1.8.0_241
```


## hdfs-site.xml
```xml
<!-- 副本数目-->
<property>
		<name>dfs.replication</name>
		<value>3</value>
</property>

<!-- 完全分布式集群名称 -->
<property>
	<name>dfs.nameservices</name>
	<value>mycluster</value>
</property>

<!-- 集群中NameNode节点都有哪些 -->
<property>
	<name>dfs.ha.namenodes.mycluster</name>
	<value>nn1,nn2</value>
</property>

<!-- nn1的RPC通信地址 -->
<property>
	<name>dfs.namenode.rpc-address.mycluster.nn1</name>
	<value>VM124:8020</value>
</property>

<!-- nn2的RPC通信地址 -->
<property>
	<name>dfs.namenode.rpc-address.mycluster.nn2</name>
	<value>VM125:8020</value>
</property>

<!-- nn1的http通信地址 -->
<property>
	<name>dfs.namenode.http-address.mycluster.nn1</name>
	<value>VM124:50070</value>
</property>

<!-- nn2的http通信地址 -->
<property>
	<name>dfs.namenode.http-address.mycluster.nn2</name>
	<value>VM125:50070</value>
</property>

<!-- 指定NameNode元数据在JournalNode上的存放位置(一般和zookeeper部署在一起) -->
<property>
	<name>dfs.namenode.shared.edits.dir</name>
	<value>qjournal://VM124:8485;VM125:8485;VM126:8485/mycluster</value>
</property>

<!-- 声明journalnode服务器存储目录-->
<property>
	<name>dfs.journalnode.edits.dir</name>
	<value>/home/yang/module/hadoop-2.7.2/data/journalnode</value>
</property>

<!-- 配置隔离机制，即同一时刻只能有一台服务器对外响应 -->
<property>
	<name>dfs.ha.fencing.methods</name>
	<value>sshfence</value>
</property>

<!-- 使用隔离机制时需要ssh无秘钥登录-->
<property>
	<name>dfs.ha.fencing.ssh.private-key-files</name>
	<value>/home/yang/.ssh/id_rsa</value>  <!-- yang用户名 -->
</property>

<!-- 关闭权限检查-->
<property>
	<name>dfs.permissions.enable</name>
	<value>false</value>
</property>

<!-- 访问代理类：client，mycluster，active配置失败自动切换实现方式-->
<property>
	<name>dfs.client.failover.proxy.provider.mycluster</name>
	<value>org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider</value>
</property>

<!-- 自动故障转移 -->
<property>
	<name>dfs.ha.automatic-failover.enabled</name>
	<value>true</value>
</property>
```


## core-site.xml
```xml
<!-- 指定HDFS中NameNode的地址 -->
<property>
	<name>fs.defaultFS</name>
	<value>hdfs://mycluster</value>
</property>

<!-- 用户名 -->
<property>  
    <name>hadoop.http.staticuser.user</name>  
    <value>yang</value>  
</property>

<!-- 指定Hadoop运行时产生文件的存储目录 -->
<property>
	<name>hadoop.tmp.dir</name>
	<value>/home/yang/module/hadoop-2.7.2/data/tmp</value>
</property>

<!-- ZooKeeper service -->
<property>
	<name>ha.zookeeper.quorum</name>
	<value>VM124:2181,VM125:2181,VM126:2181</value>
</property>
```

## DataNode集群启动设置

```sh
vi etc/hadoop/slaves
VM124
VM125
VM126
```


## 测试启动 hdfs

前提先把zookeeper启动起来

```sh
# 所有JournalNode节点输入以下命令启动journalnode服务(用来同步两台namenode的数据)
sbin/hadoop-daemon.sh start journalnode

# [nn1]上，对其进行格式化，并启动
bin/hdfs namenode -format
sbin/hadoop-daemon.sh start namenode

# [nn2]上，同步nn1的元数据信息，并启动（nn2不需要格式化）
bin/hdfs namenode -bootstrapStandby
sbin/hadoop-daemon.sh start namenode

# 查看Web
http://VM124:50070
http://VM125:50070
```

自动故障转移开启后，不可手动
```sh
# 手动把nn1设置为active
bin/hdfs haadmin -transitionToActive nn1  # -transitionToStandby
# 查看服务状态
bin/hdfs haadmin -getServiceState nn1
```

```sh
# 第一次使用zkfc需要格式化（在zookpeer创建相应节点）
bin/hdfs zkfc -formatZK
# namenode节点上启动zkfc线程（两个namenode都要启动） 
sbin/hadoop-daemon.sh start zkfc   #（进程DFSZKFailoverController）
```


## 整体启动脚本

```sh
sbin/stop-dfs.sh
sbin/start-dfs.sh
```



## yarn-site.xml
```xml
<!-- Reducer获取数据的方式 -->
<property>
		<name>yarn.nodemanager.aux-services</name>
		<value>mapreduce_shuffle</value>
</property>

<!-- Yarn JobHistory  -->
<property> 
    <name>yarn.log.server.url</name> 
    <value>http://VM124:19888/jobhistory/logs/</value> 
</property>

<!-- 日志聚集功能使能 -->
<property>
    <name>yarn.log-aggregation-enable</name>
    <value>true</value>
</property>

<!-- 日志保留时间设置7天 单位s -->
<property>
	<name>yarn.log-aggregation.retain-seconds</name>
	<value>604800</value>  
</property>

<!-- 启用resourcemanager ha -->
<property>
    <name>yarn.resourcemanager.ha.enabled</name>
    <value>true</value>
</property>

<!-- 声明两台resourcemanager的地址 -->
<property>
    <name>yarn.resourcemanager.cluster-id</name>
    <value>rs</value>
</property>

<property>
    <name>yarn.resourcemanager.ha.rm-ids</name>
    <value>rm1,rm2</value>
</property>

<property>
    <name>yarn.resourcemanager.hostname.rm1</name>
    <value>VM124</value>
</property>

<property>
    <name>yarn.resourcemanager.hostname.rm2</name>
    <value>VM125</value>
</property>

<!--指定zookeeper集群的地址--> 
<property>
    <name>yarn.resourcemanager.zk-address</name>
    <value>VM124:2181,VM125:2181,VM126:2181</value>
</property>

<!--启用自动恢复--> 
<property>
    <name>yarn.resourcemanager.recovery.enabled</name>
    <value>true</value>
</property>

<!--指定resourcemanager的状态信息存储在zookeeper集群--> 
<property>
    <name>yarn.resourcemanager.store.class</name>
    <value>org.apache.hadoop.yarn.server.resourcemanager.recovery.ZKRMStateStore</value>
</property>
```

## 启动 yarn

```sh
# 在VM124中执行
sbin/start-yarn.sh

# 在VM125中执行
sbin/yarn-daemon.sh start resourcemanager

# 查看服务状态
bin/yarn rmadmin -getServiceState rm1

# 查看Web
http://VM124:8088
http://VM125:8088

# 历史记录
sbin/mr-jobhistory-daemon.sh start historyserver
http://VM124:19888
```

## hadoop hdfs 和 yarn 启动脚本

```sh
#!/bin/bash

################## 设置相关信息 ###################
root_dir=/home/yang/module/
hadoop_dir=${root_dir}hadoop-2.7.2/
user_name=yang
 
dfs_VM=VM124                 # 启动start-dfs.sh的VM
jobhistory_VM=VM124          # 启动jobhistory的VM
rm_VM=(VM124 VM125)          # 启动resourcemanager的VM
all_VM=(VM124 VM125 VM126)   # 启动所有nodemanager的VM

################## 下面尽量不要修改 ####################
# 启动
start_hadoop(){
	echo -e "\n++++++++++++++++++++ Hadoop集群启动 +++++++++++++++++++++"

	echo -e "\n=========> 启动 HDFS ...."
	ssh ${user_name}@$dfs_VM ${hadoop_dir}sbin/start-dfs.sh

	echo -e "\n=========> 启动 Yarn ...."
	for i in ${rm_VM[*]}
	do
		ssh ${user_name}@$i ${hadoop_dir}sbin/yarn-daemon.sh start resourcemanager
	done
	for i in ${all_VM[*]}
	do
	    ssh ${user_name}@$i ${hadoop_dir}sbin/yarn-daemon.sh start nodemanager
	done

	echo -e "\n=========> 启动 JobHistoryServer ============="
	ssh ${user_name}@$jobhistory_VM ${hadoop_dir}sbin/mr-jobhistory-daemon.sh start historyserver

}

# 关闭
stop_hadoop(){
	echo -e "\n++++++++++++++++++++ Hadoop集群关闭 +++++++++++++++++++++"

	echo -e "\n=========> 关闭 HDFS ...."
	ssh ${user_name}@$dfs_VM ${hadoop_dir}sbin/stop-dfs.sh

	echo -e "\n=========> 关闭 Yarn ...."
	for i in ${rm_VM[*]}
	do
		ssh ${user_name}@$i ${hadoop_dir}sbin/yarn-daemon.sh stop resourcemanager
	done
	for i in ${all_VM[*]}
	do
	    ssh ${user_name}@$i ${hadoop_dir}sbin/yarn-daemon.sh stop nodemanager
	done

	echo -e "\n=========> 关闭 JobHistoryServer ============="
	ssh ${user_name}@$jobhistory_VM ${hadoop_dir}sbin/mr-jobhistory-daemon.sh stop historyserver

}

# 获取输入参数个数，如果没有参数，直接退出
pcount=$#
if((pcount==0)); then
	echo no args, example : $0 start/stop;
	exit;

elif [[ "$1" == "start" ]]; then
	echo start;
	start_hadoop


elif [[ "$1" == "stop" ]]; then
	echo stop;
	stop_hadoop

else
	echo example : $0 start/stop;
	exit;
fi
```

