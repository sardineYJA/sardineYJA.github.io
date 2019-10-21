---
layout: post
title: "Flink"
date: 2019-10-06
description: "Flink"
tag: Bigdata

---


# 简介

Apache Flink是一个面向分布式数据流处理和批量数据处理的开源计算平台，提供支持流处理和批处理两种类型应用的功能。

## 优势

* 支持高吞吐、低延迟、高性能的流处理

* 支持高度灵活的窗口（Window）操作

* 支持有状态计算的Exactly-once语义

* 提供DataStream API和DataSet API



# 组件

![png](/images/posts/all/Flink组件栈.png)

## Deployment 层

主要涉及了Flink的部署模式，Flink支持多种部署模式：本地、集群（Standalone/YARN）、云（GCE/EC2）。

![png](/images/posts/all/Flink的Deployment层.png)

## Runtime 层

Runtime层提供了支持Flink计算的全部核心实现，比如：支持分布式Stream处理、JobGraph到ExecutionGraph的映射、调度等等，为上层API层提供基础服务。

## API 层

API层主要实现了面向无界Stream的流处理和面向Batch的批处理API，其中面向流处理对应DataStream API，面向批处理对应DataSet API。

## Libaries 层

* 在API层之上构建的满足特定应用的实现计算框架，也分别对应于面向流处理和面向批处理两类

* 面向流处理支持：CEP(复杂事件处理)、基于SQL-like的操作(基于Table的关系操作)

* 面向批处理支持：FlinkML(机器学习库)、GElly(图处理)


# 架构

Flink是基于Master-Slave风格的架构，集群启动时，会启动一个JobManager进程、至少一个TaskManager进程

![png](/images/posts/all/Flink基本架构.png)

## JobManager

* Flink系统的协调者，它负责接收Flink Job，调度组成Job的多个Task的执行

* 收集Job的状态信息，并管理Flink集群中从节点TaskManager

## TaskManager 

* 实际负责执行计算的Worker，在其上执行Flink Job的一组Task

* TaskManager负责管理其所在节点上的资源信息，如内存、磁盘、网络，在启动的时候将资源的状态向JobManager汇报

## Client

* 用户提交一个Flink程序时，会首先创建一个Client，该Client首先会对用户提交的Flink程序进行预处理，并提交到Flink集群

* Client会将用户提交的Flink程序组装一个JobGraph， 并且是以JobGraph的形式提交的


# 安装

## 安装 maven 配置环境变量

地址：https://maven.apache.org/download.cgi

```sh
vi /etc/profile
export MAVEN_HOME=/opt/maven/apache-maven-3.6.2
export PATH=$PATH:$MAVEN_HOME/bin
source /etc/profile
```

## 单机版

下载：https://flink.apache.org/downloads.html

tar -zxvf flink-1.7.2-bin-scala_2.11.tgz -C ../module/

bin/start-cluster.sh
(StandaloneSessionClusterEntrypoint、TaskManagerRunner)

进入 web 页面：http://172.16.7.124:8081


## 测试



# reference

https://github.com/wangzhiwubigdata/God-Of-BigData


