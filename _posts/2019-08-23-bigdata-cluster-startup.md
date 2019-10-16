---
layout: post
title: "集群常用脚本"
date: 2019-08-23
description: "简单介绍集群常用脚本"
tag: Bigdata

---


# 启动命令

## Hadoop

```
sbin/hadoop-daemon.sh start namenode          (NameNode)(注意在配置节点启动)
sbin/hadoop-daemon.sh start datanode          (DataNode)
sbin/hadoop-daemon.sh start secondarynamenode (SecondaryNameNode)(注意在配置节点启动)
或
sbin/start-dfs.sh

sbin/yarn-daemon.sh start resourcemanager  (ResourceManager)(注意在配置节点启动)
sbin/yarn-daemon.sh start nodemanager      (NodeManager)
或
sbin/start-yarn.sh

sbin/mr-jobhistory-daemon.sh start historyserver （JobHistoryServer）
```
## Spark

```
sbin/start-all.sh             (Master, Worker)
sbin/start-history-server.sh  (HistoryServer)
```

## Zookeeper

```
bin/zkServer.sh start  (QuorumPeerMain)
```

## HBase

```
bin/hbase-daemon.sh start master         (HMaster)(内置ZooKeeperMain)
bin/hbase-daemon.sh start regionserver   (HRegionServer)
或者
bin/start-hbase.sh
```

## Kafka

```
bin/kafka-server-start.sh config/server.properties &     (Kafka)
```


# Linux 命令

```sh
free -h                    # 内存

systemctl status 程序名    # 状态

netstat -an | grep 端口号  # 端口 

```


# 脚本

## 集群启动脚本

```sh
#!/bin/bash

################## 设置相关信息 ###################
root_dir=/home/yangja/module/
hadoop_dir=${root_dir}hadoop-2.7.2/
spark_dir=${root_dir}spark-2.1.1-bin-hadoop2.7/

user_name=yangja
namenode_ip=172.16.7.124
secondarynamenode_ip=172.16.7.124
resourcemanager_ip=172.16.7.124
historyserve_ip=172.16.7.124
datanode_ip=(172.16.7.124)


################## 下面尽量不要修改 ####################

# 启动集群 hadoop 函数
start_hadoop(){
	echo -e "\n++++++++++++++++++++ 集群启动 +++++++++++++++++++++"

	echo -e "\n============== 启动 NameNode ============="
	# echo ssh ${user_name}@$namenode_ip ${hadoop_dir}sbin/hadoop-daemon.sh start namenode
	ssh ${user_name}@$namenode_ip ${hadoop_dir}sbin/hadoop-daemon.sh start namenode

	echo -e "\n============== 启动 SecondaryNameNode ============="
	# echo ssh ${user_name}@$secondarynamenode_ip ${hadoop_dir}sbin/hadoop-daemon.sh start secondarynamenode
	ssh ${user_name}@$secondarynamenode_ip ${hadoop_dir}sbin/hadoop-daemon.sh start secondarynamenode

	echo -e "\n============== 启动所有 DataNode ============="
	for i in ${datanode_ip[*]}
	do
		# echo ssh ${user_name}@$i ${hadoop_dir}sbin/hadoop-daemon.sh start datanode
		ssh ${user_name}@$i ${hadoop_dir}sbin/hadoop-daemon.sh start datanode
	done


	echo -e "\n============== 启动 ResourceManager ============="
	# echo ssh ${user_name}@$resourcemanager_ip ${hadoop_dir}sbin/yarn-daemon.sh start resourcemanager
	ssh ${user_name}@$resourcemanager_ip ${hadoop_dir}sbin/yarn-daemon.sh start resourcemanager

	echo -e "\n============== 启动所有 NodeManager ============="
	for i in ${datanode_ip[*]}
	do
		# echo ssh ${user_name}@$i ${hadoop_dir}sbin/yarn-daemon.sh start nodemanager
	    ssh ${user_name}@$i  ${hadoop_dir}sbin/yarn-daemon.sh start nodemanager
	done

	echo -e "\n============== 启动 JobHistoryServer ============="
	# echo ssh ${user_name}@$historyserve_ip ${hadoop_dir}sbin/mr-jobhistory-daemon.sh start historyserver
	ssh ${user_name}@$historyserve_ip ${hadoop_dir}sbin/mr-jobhistory-daemon.sh start historyserver
}


# 关闭集群 hadoop 函数
stop_hadoop(){
	echo -e "\n++++++++++++++++++++ 集群关闭 +++++++++++++++++++++"

	echo -e "\n============== 关闭 NameNode ============="
	# echo ssh ${user_name}@$namenode_ip ${hadoop_dir}sbin/hadoop-daemon.sh stop namenode
	ssh ${user_name}@$namenode_ip ${hadoop_dir}sbin/hadoop-daemon.sh stop namenode

	echo -e "\n============== 关闭 SecondaryNameNode ============="
	# echo ssh ${user_name}@$secondarynamenode_ip ${hadoop_dir}sbin/hadoop-daemon.sh stop secondarynamenode
	ssh ${user_name}@$secondarynamenode_ip ${hadoop_dir}sbin/hadoop-daemon.sh stop secondarynamenode

	echo -e "\n============== 关闭所有 DataNode ============="
	for i in ${datanode_ip[*]}
	do
		# echo ssh ${user_name}@$i ${hadoop_dir}sbin/hadoop-daemon.sh stop datanode
		ssh ${user_name}@$i ${hadoop_dir}sbin/hadoop-daemon.sh stop datanode
	done


	echo -e "\n============== 关闭 ResourceManager ============="
	# echo ssh ${user_name}@$resourcemanager_ip ${hadoop_dir}sbin/yarn-daemon.sh stop resourcemanager
	ssh ${user_name}@$resourcemanager_ip ${hadoop_dir}sbin/yarn-daemon.sh stop resourcemanager

	echo -e "\n============== 关闭所有 NodeManager ============="
	for i in ${datanode_ip[*]}
	do
		# echo ssh ${user_name}@$i ${hadoop_dir}sbin/yarn-daemon.sh stop nodemanager
	    ssh ${user_name}@$i  ${hadoop_dir}sbin/yarn-daemon.sh stop nodemanager
	done

	echo -e "\n============== 关闭 JobHistoryServer ============="
	# echo ssh ${user_name}@$historyserve_ip ${hadoop_dir}sbin/mr-jobhistory-daemon.sh stop historyserver
	ssh ${user_name}@$historyserve_ip ${hadoop_dir}sbin/mr-jobhistory-daemon.sh stop historyserver
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


## 同步文件脚本

```sh
#!/bin/bash
#1 获取输入参数个数，如果没有参数，直接退出
pcount=$#
if((pcount==0)); then
echo no args;
exit;
fi

#2 获取文件名称
p1=$1
fname=`basename $p1`
echo fname=$fname

#3 获取上级目录到绝对路径
pdir=`cd -P $(dirname $p1); pwd`
echo pdir=$pdir

#4 获取当前用户名称
user=`whoami`

#5 循环
for((host=101; host<105; host++)); do
        echo ------------------- hadoop$host --------------
        rsync -rvl $pdir/$fname $user@hadoop$host:$pdir
done
```


## sh脚本问题

> $'\r': 未找到命令

因为在dos/window下按一次回车键实际上输入的是“回车（CR)”和“换行（LF）”，而Linux/unix下按一次回车键只输入“换行（LF）”，所以文件在每行都会多了一个CR，所以Linux下运行时就会报错找不到命令，所以，解决问题之道，就是把dos文件格式转换为unix格式。

使用notepad++在windows系统下使用notepad++编辑该sh文件，双击文件右下角编码区域选择"转换为UNIX格式"。
