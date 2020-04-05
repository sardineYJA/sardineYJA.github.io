---
layout: post
title: "Spark Submit 提交任务"
date: 2019-07-30
description: "Spark Submit 提交任务"
tag: Spark

---


# Spark 提交任务

## 总结

- standlone 模式 driver一定在master之上, Executor在worker之上。

- yarn-client 模式 Driver(初始SparkContext程序) 运行在 Client(提交jar包的节点,与resourcemanager无关)上，应用程序运行结果会在客户端显示。

- yarn-cluster 模式 Driver程序在 YARN 中运行，应用的运行结果不能在客户端显示。


## Spark 应用程序执行过程

1. 用户Client端Submit作业，Driver运行创建SparkContext

2. SparkContext向资源管理器（Standalone, yarn, Mesos）注册申请资源

3. 资源分配给Executor

4. SparkContext构建DAG图，并分解成Stage，将Taskset发送给Task Scheduler

5. Executor向SparkContext申请Task，Task Scheduler将Task发送给Executor，SparkContext将程序代码发送给Executor

6. Task在Executor上运行，运行完毕后释放资源



## 单机测试

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



