---
layout: post
title: "Spark Submit 提交任务"
date: 2019-07-30
description: "Spark Submit 提交任务"
tag: Spark

---


# Spark 提交任务

单机测试：

```sh
bin/spark-submit \
--class test.WeiboFolloerSpark \
--master spark://172.16.7.124:7077 \
--executor-memory 4G \
--total-executor-cores 10 \
--driver-cores 2 \
--driver-memory 1G \
myJar/test.WeiboFolloerSpark-p1000-D.jar \
hdfs://172.16.7.124:9000/weibo/Large.txt \
hdfs://172.16.7.124:9000/weibo/output
```

spark-shell用于调试，spark-submit用于生产

```sh
--master spark://master:7077 --deploy-mode client
--master spark://master:7077 --deploy-mode cluster
```



# Spark-yarn 提交

## yarn-client 提交任务

在client节点配置中spark-env.sh添加Hadoop_HOME的配置目录即可提交yarn任务

`export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop`

注意client只需要有Spark的安装包即可提交任务，不需要其他配置（比如slaves）!!!

提交命令：
```sh
./spark-submit --master yarn ...
./spark-submit --master yarn-client ...
./spark-submit --master yarn --deploy-mode client ...
```

## 原理图

![png](/images/posts/all/Spark-Submit的yarn-client提交模式原理.png)

Yarn-client模式同样是适用于测试，因为Driver运行在本地，Driver会与yarn集群中的Executor进行大量的通信，会造成客户机网卡流量的大量增加。

ApplicationMaster的作用：为当前的Application申请资源，给NodeManager发送消息启动Executor。


## yarn-cluster 提交任务

提交命令：
```sh
./spark-submit --master yarn-cluster ...
./spark-submit --master yarn --deploy-mode cluster ...
```

## 原理图

![png](/images/posts/all/Spark-Submit的yarn-cluster提交模式原理.png)

Yarn-Cluster主要用于生产环境中，因为Driver运行在Yarn集群中某一台nodeManager中，每次提交任务的Driver所在的机器都是随机的，不会产生某一台机器网卡流量激增的现象。
缺点是任务提交后不能看到日志，只能通过yarn查看日志。

ApplicationMaster的作用：为当前的Application申请资源，给nodemanager发送消息 启动Excutor。任务调度(和client模式的区别是AM具有调度能力，因为其就是Driver端，包含Driver进程)

# reference

https://www.cnblogs.com/LHWorldBlog/p/8414342.html



