---
layout: post
title: "Hadoop知识点"
date: 2019-06-01
description: "简单介绍一下Hadoop知识点"
tag: Hadoop

---

# Hadoop知识点

## Hadoop发行版本

1. Apache版本最原始（最基础）的版本。
2. Cloudera在大型互联网企业中用的较多。
3. Hortonworks文档较好。


## Hadoop1.x与Hadoop2.x的区别

1.x：MapReduce(计算+资源调度)，HDFS(数据存储)，Common(辅助工具)

2.x：MapReduce(计算)，`Yarn(资源调度)`，HDFS(数据存储)，Common(辅助工具)


## HDFS

1. NameNode：存储文件的元数据
2. DataNode：存储文件块数据
3. Secondary NameNode：获取元数据快照


## Yarn

1. ResourceManager:资源分配调度
2. NodeManager:管理单个节点上的资源
3. ApplicationMaster:数据切片
4. Container:资源抽象


## 启动

1. 第一次启动需要格式化NameNode:`hdfs namenode -format`
2. 启动HDFS:`sbin/start-dfs.sh`
3. 启动Yarn:`sbin/start-yarn.sh`

> NameNode和ResourceManger如果不是同一台机器，不能在NameNode上启动 YARN，应该在ResouceManager所在的机器上启动YARN。

>格式化NameNode，会产生新的集群id,导致NameNode和DataNode的集群id不一致，集群找不到已往数据。所以，格式NameNode时，一定要先删除data数据和log日志，然后再格式化NameNode。


## 各个服务组件逐一启动/停止
1. 分别启动/停止HDFS组件

`hadoop-daemon.sh  start/stop  namenode/datanode/secondarynamenode`

2. 启动/停止YARN

`yarn-daemon.sh  start/stop  resourcemanager/nodemanager`

3. 整体启动/停止HDFS

`start-dfs.sh   /  stop-dfs.sh`

4. 整体启动/停止YARN

`start-yarn.sh  /  stop-yarn.sh`



## hdfs操作
bin/hadoop fs 具体命令 或者 bin/hdfs dfs 具体命令
```
-help
-ls /
-mkdir /test
-put ./1.txt /test/           从本地拷贝到HDFS
-copyFromLocal ./1.txt /test  从本地拷贝到HDFS
-moveFromLocal ./1.txt /test  从本地剪切到HDFS
-copyToLocal /test/2.txt ./   从HDFS拷贝到本地
-get /test/2.txt ./           从HDFS拷贝到本地
-getmerge /test/* ./1/txt     从HDFS合并拷贝到本地
-appendToFile ./1.txt /test/2.txt   
-cat /2.txt
-cp /test/2.txt /app/3.txt    HDFS的复制
-mv /test/2.txt /app/         HDFS的移动
-rm
-rmdir
-du      统计文件夹的大小信息
-setrep  设置HDFS中文件副本数量
```

## HDFS写入数据
1. Client向NameNode请求上传文件
2. NameNode响应可以上传
3. Client请求上传第一个Block，请求返回DateNode
4. NameNode返回dn1, dn2, dn3
5. Client向DateNode请求建立Block传输通道
6. DateNode应答成功
7. Client传输数据packet
8. 从第3步骤开始第二个Block


## HDFS读取数据
1. Client向NameNode请求下载文件
2. NameNode 返回目标文件的元数据
3. Client向DataNode请求读取数据
4. DataNode传输数据


## NameNode和SecondaryNameNode
1. NameNode(元数据)存放在内存
2. 元数据备份文件FsImage存在磁盘
3. 元数据的操作追加到Edits文件
4. SecondaryNameNode定期进行FsImage和Edits的合并


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


## 回收站


## 小文件存档


## 快照管理


## 集群时间同步


## Hadoop源码编译





