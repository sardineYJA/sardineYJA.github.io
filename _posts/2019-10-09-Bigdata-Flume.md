---
layout: post
title: "Flume"
date: 2019-10-09
description: "Flume"
tag: Bigdata

---

# Flume框架
	
## Flume框架简介

Flume(日志采集系统) 和 Kafka(消息中间件) 用来实时进行数据收集，Spark、Storm用来实时处理数据，impala用来实时查询。

Flume提供一个分布式的，可靠的，对大数据量的日志进行高效收集、聚集、移动的服务，Flume只能在Unix环境下运行。

Flume基于流式架构，容错性强，也很灵活简单，主要用于在线实时分析。

## 场景使用

Flume和Kafka应该结合来使用，Flume作为日志收集端，Kafka作为日志消费端

线上数据 -> flume -> kafka -> hdfs -> MR离线计算

线上数据 -> flume -> kafka -> storm

## 角色

- Source
用于采集数据，Source是产生数据流的地方，同时Source会将产生的数据流传输到Channel，这个有点类似于Java IO部分的Channel。

- Channel
用于桥接Sources和Sinks，类似于一个队列。

- Sink
从Channel收集数据，将数据写到目标源（可以是下一个Source，也可以是HDFS或者HBase）。

![png](/images/posts/all/flume角色图.png)

- Event
数据传输的基本单元，以事件的形式将数据从源头送至目的地

![png](/images/posts/all/flume传输单元.png)


source监控某个文件，文件产生新的数据，拿到该数据后，
将数据封装在一个Event中，并put到channel后commit提交，
channel队列先进先出，sink去channel队列中拉取数据，然后写入到hdfs或者HBase中。


## 安装配置FLume

解压：`tar -zxvf apache-flume-1.9.0-bin.tar.gz -C ../module/`

cp模板，flume-env.sh配置Java的环境变量：`export JAVA_HOME=...`

Flume帮助命令：`$ bin/flume-ng`



# 案例：Flume监听端口，输出端口数据

cp模板：`cp flume-conf.properties.template flume-telnet.conf`

文件中配置行后面`不可有中文注释`

```sh
# Name the components on this agent
a1.sources = r1    
a1.sinks = k1
a1.channels = c1

# Describe/configure the source
a1.sources.r1.type = netcat   
a1.sources.r1.bind = localhost
a1.sources.r1.port = 44444 

# Describe the sink
a1.sinks.k1.type = logger

# Use a channel which buffers events in memory
a1.channels.c1.type = memory   
a1.channels.c1.capacity = 1000 
a1.channels.c1.transactionCapacity = 100

# Bind the source and sink to the channel
a1.sources.r1.channels = c1  
a1.sinks.k1.channel = c1
```

sources 可以发送到多个 channel 如：c1 c2 c3

chnnel 只能发送到一个 sinks


## 开启

```sh
bin/flume-ng agent --conf conf/      \
--name a1                            \
--conf-file conf/flume-telnet.conf   \
-Dflume.root.logger==INFO,console
```


## 安装telnet工具

> telnet: connect to address 127.0.0.1: Connection refused

需要安装telnet-server

```sh 
$ sudo rpm -ivh telnet-server-0.17-59.el7.x86_64.rpm 
$ sudo rpm -ivh telnet-0.17-59.el7.x86_64.rpm
# 首先判断44444端口是否被占用
$ netstat -an | grep 44444
# 使用telnet工具向本机的44444端口发送内容
$ telnet localhost 44444
# flume 可以立刻获取数据
```


# 案例：Flume监听整个目录

配置文件flume-dir.conf

```sh
a3.sources = r3
a3.sinks = k3
a3.channels = c3

# Describe/configure the source
a3.sources.r3.type = spooldir
a3.sources.r3.spoolDir = /home/yangja/data
a3.sources.r3.fileHeader = true
#忽略所有以.tmp结尾的文件，不上传
a3.sources.r3.ignorePattern = ([^ ]*\.tmp)

# Describe the sink
a3.sinks.k3.type = hdfs
a3.sinks.k3.hdfs.path = hdfs://172.16.7.124:9000/flume/%Y%m%d/%H
#上传文件的前缀
a3.sinks.k3.hdfs.filePrefix = upload-
#是否按照时间滚动文件夹
a3.sinks.k3.hdfs.round = true
#多少时间单位创建一个新的文件夹
a3.sinks.k3.hdfs.roundValue = 1
#重新定义时间单位
a3.sinks.k3.hdfs.roundUnit = hour
#是否使用本地时间戳
a3.sinks.k3.hdfs.useLocalTimeStamp = true
#积攒多少个Event才flush到HDFS一次
a3.sinks.k3.hdfs.batchSize = 100
#设置文件类型，可支持压缩
a3.sinks.k3.hdfs.fileType = DataStream
#多久生成一个新的文件
a3.sinks.k3.hdfs.rollInterval = 600
#设置每个文件的滚动大小
a3.sinks.k3.hdfs.rollSize = 134217700
#文件的滚动与Event数量无关
a3.sinks.k3.hdfs.rollCount = 0
#最小冗余数
a3.sinks.k3.hdfs.minBlockReplicas = 1

# Use a channel which buffers events in memory
a3.channels.c3.type = memory
a3.channels.c3.capacity = 1000
a3.channels.c3.transactionCapacity = 100

# Bind the source and sink to the channel
a3.sources.r3.channels = c3
a3.sinks.k3.channel = c3
```

执行测试
```sh
bin/flume-ng agent --conf conf/    \
--name a3                          \
--conf-file conf/flume-dir.conf    \
-Dflume.root.logger==INFO,console
```

注意事项：
1. 不要在监控目录中创建并持续修改文件
2. 上传完成的文件会以.COMPLETED结尾
3. 被监控文件夹每600毫秒扫描一次变动



# 案例：Kafka消费Flume

创建 flume-kafka.conf

```sh
agent.sources = s1  
agent.channels = c1
agent.sinks = k1

agent.sources.s1.type = exec
agent.sources.s1.command = tail -F /home/yangja/data/flume-kafka.txt
agent.sources.s1.channels = c1

agent.channels.c1.type = memory
agent.channels.c1.capacity = 10000
agent.channels.c1.transactionCapacity = 100

#设置Kafka接收器
agent.sinks.k1.type = org.apache.flume.sink.kafka.KafkaSink
#设置Kafka的broker地址和端口号
agent.sinks.k1.brokerList = 172.16.7.124:9092
#设置Kafka的Topic 
agent.sinks.k1.topic = MyTopic

#设置序列化方式
agent.sinks.k1.serializer.class = kafka.serializer.StringEncoder
agent.sinks.k1.channel = c1
```

```sh
bin/flume-ng agent --conf conf/    \
--name agent                       \
--conf-file conf/flume-kafka.conf  \
-Dflume.root.logger==INFO,console
```

启动消费者，需要先开启Zookeeper和Kafka：

`bin/zkServer.sh start`

`bin/kafka-server-start.sh config/server.properties &`

`kafka-console-consumer.sh --zookeeper 172.16.7.124:2181 --topic MyTopic --from-beginning`


测试：echo helloWorld > flume-kafka.txt



# 案例：监听上传Hive日志文件到HDFS

创建flume-hdfs.conf文件

```sh
# Name the components on this agent
a2.sources = r2
a2.sinks = k2
a2.channels = c2

# Describe/configure the source
a2.sources.r2.type = exec
a2.sources.r2.command = tail -f /opt/modules/cdh/hive-0.13.1-cdh5.3.6/logs/hive.log
a2.sources.r2.shell = /bin/bash -c

# Describe the sink
a2.sinks.k2.type = hdfs
a2.sinks.k2.hdfs.path = hdfs://172.16.7.124:9000/flume/%Y%m%d/%H
#上传文件的前缀
a2.sinks.k2.hdfs.filePrefix = events-hive-
#是否按照时间滚动文件夹
a2.sinks.k2.hdfs.round = true
#多少时间单位创建一个新的文件夹
a2.sinks.k2.hdfs.roundValue = 1
#重新定义时间单位
a2.sinks.k2.hdfs.roundUnit = hour
#是否使用本地时间戳
a2.sinks.k2.hdfs.useLocalTimeStamp = true
#积攒多少个Event才flush到HDFS一次
a2.sinks.k2.hdfs.batchSize = 100
#设置文件类型，可支持压缩
a2.sinks.k2.hdfs.fileType = DataStream
#多久生成一个新的文件
a2.sinks.k2.hdfs.rollInterval = 600
#设置每个文件的滚动大小
a2.sinks.k2.hdfs.rollSize = 134217700
#文件的滚动与Event数量无关
a2.sinks.k2.hdfs.rollCount = 0
#最小冗余数
a2.sinks.k2.hdfs.minBlockReplicas = 1


# Use a channel which buffers events in memory
a2.channels.c2.type = memory
a2.channels.c2.capacity = 1000
a2.channels.c2.transactionCapacity = 100

# Bind the source and sink to the channel
a2.sources.r2.channels = c2
a2.sinks.k2.channel = c2
```

执行监控配置

```sh
bin/flume-ng agent --conf conf/   \
--name a2                         \
--conf-file conf/flume-hdfs.conf  \
-Dflume.root.logger==INFO,console
```


# reference

http://flume.apache.org/releases/content/1.9.0/FlumeUserGuide.html

