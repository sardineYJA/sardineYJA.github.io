---
layout: post
title: "集群常用脚本"
date: 2019-08-23
description: "简单介绍集群常用脚本"
tag: 工具

---

# 端口




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

# 脚本

## 集群启动脚本

```sh
echo "+++++++++++++++++ 集群启动 ++++++++++++++++++"

echo "============== 启动 NameNode ============="
ssh yangja@hadoop101 '.../sbin/hadoop-daemon.sh start namenode'

echo "============== 启动 SecondaryNameNode ============="
ssh yangja@hadoop102 '.../sbin/hadoop-daemon.sh start secondarynamenode'

echo "============== 启动 DataNode ============="
for i in yangja@hadoop101 yangja@hadoop102 yangja@hadoop103
do
	ssh $i '.../sbin/hadoop-daemon.sh start datanode'
done


echo "============== 启动 ResourceManager ============="
ssh yangja@hadoop103 '.../sbin/yarn-daemon.sh start resourcemanager'

echo "============== 启动 NodeManager ============="
for i in yangja@hadoop101 yangja@hadoop102 yangja@hadoop103
do
	ssh $i '.../sbin/yarn-daemon.sh start nodemanager'
done


echo "============== 启动 JobHistoryServer ============="
ssh yangja@hadoop101 '.../sbin/mr-jobhistory-daemon.sh start historyserver'
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