---
layout: post
title: "快速搭建4 —— Kafka和Flume数据流"
date: 2020-03-29
description: "Bigdata"
tag: Bigdata

---


# Kafka

## 配置

解压kafka_2.11-0.11.0.0.tgz

修改config/server.properties
```sh
# 节点唯一标识
broker.id=1
# 删除topic功能
delete.topic.enable=true
# Kafka数据目录
log.dirs=/home/yang/module/kafka_2.11-0.11.0.0/logs
# 配置Zookeeper
zookeeper.connect=VM124:2181,VM125:2181,VM126:2181
```

修改config/zookeeper.properties
```sh
# Zookeeper的数据存储路径与Zookeeper集群配置保持一致
dataDir=/home/yang/module/zookeeper-3.4.14/zkData
```

修改config/consumer.properties
```sh
# 配置Zookeeper地址
zookeeper.connect=VM124:2181,VM125:2181,VM126:2181
```

修改config/producer.properties
```sh
# 配置Kafka集群地址，分布在三台机器上，旧版metadata.broker.list 
bootstrap.servers=VM124:9092,VM125:9092,VM126:9092
```

同步VM125，VM126亦然
```sh
broker.id=2
```

bin/kafka-run-class.sh 增加，
```sh
export JAVA_HOME=/home/yang/module/jdk1.8.0_241
```

## 启动

首先启动Zookeeper

```sh
# 各个节点启动
bin/kafka-server-start.sh config/server.properties &   # & 后台启动

# 创建topic
bin/kafka-topics.sh --zookeeper localhost:2181 --create --topic test --replication-factor 1 --partitions 1
# 查看topic
bin/kafka-topics.sh --zookeeper localhost:2181 --list
bin/kafka-topics.sh --describe --zookeeper localhost:2181 --topic test

# 生产者生产数据（节点1）
bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test
# 消费者消费数据（节点2），新版将 --zookeeper改成--bootstrap-server localhost:9092
bin/kafka-console-consumer.sh --zookeeper localhost:2181 --topic test --from-beginning
```



## 脚本

```sh
#!/bin/bash

################## 设置相关信息 ###################
root_dir=/home/yang/module/
kafka_dir=${root_dir}kafka_2.11-0.11.0.0/
user_name=yang
kafka_VM=(VM124 VM125 VM126)   # 启动所有kafka VM

################## 下面尽量不要修改 ####################
# 启动
start_kafka(){
	echo -e "\n++++++++++++++++++++ Kafka集群启动 +++++++++++++++++++++"
	for i in ${kafka_VM[*]}
	do
		echo -e "\n=========> 启动 ${i} kafka...."
		ssh ${user_name}@$i ${kafka_dir}bin/kafka-server-start.sh  ${kafka_dir}config/server.properties &
	done
}

# 关闭
stop_kafka(){
	echo -e "\n++++++++++++++++++++ Kafka集群关闭 +++++++++++++++++++++"
	for i in ${kafka_VM[*]}
	do
		echo -e "\n=========> 关闭 ${i} kafka...."
		ssh ${user_name}@$i ${kafka_dir}bin/kafka-server-stop.sh
	done
}


# 获取输入参数个数，如果没有参数，直接退出
pcount=$#
if((pcount==0)); then
	echo no args, example : $0 start/stop;
	exit;

elif [[ "$1" == "start" ]]; then
	echo start;
	start_kafka


elif [[ "$1" == "stop" ]]; then
	echo stop;
	stop_kafka

else
	echo example : $0 start/stop;
	exit;
fi
```



# Flume

## 配置

环境变量
```sh
cp flume-conf.properties.template flume-conf.properties
cp flume-env.sh.template flume-env.sh
vi flume-env.sh
export JAVA_HOME=/home/yang/module/jdk1.8.0_241
export HADOOP_HOME=/home/yang/module/hadoop-2.7.2
export HBASE_HOME=/home/yang/module/hbase-1.3.2
```

同步到其他机器，数据则是VM125 和 VM126 机器汇总到 VM124

VM125 修改 flume-conf.properties
```sh
agent2.sources = r1
agent2.channels = c1
agent2.sinks = k1

agent2.sources.r1.type = exec
agent2.sources.r1.command = tail -F /home/yang/datas/weblog-flume.log
agent2.sources.r1.channels = c1

agent2.channels.c1.type = memory
agent2.channels.c1.capacity = 10000
agent2.channels.c1.transactionCapacity = 10000
agent2.channels.c1.keep-alive = 5

agent2.sinks.k1.type = avro
agent2.sinks.k1.channel = c1
agent2.sinks.k1.hostname = VM124
agent2.sinks.k1.port = 5555
```


VM126 修改 flume-conf.properties
```sh
agent3.sources = r1
agent3.channels = c1
agent3.sinks = k1

agent3.sources.r1.type = exec
agent3.sources.r1.command = tail -F /home/yang/datas/weblog-flume.log
agent3.sources.r1.channels = c1

agent3.channels.c1.type = memory
agent3.channels.c1.capacity = 10000
agent3.channels.c1.transactionCapacity = 10000
agent3.channels.c1.keep-alive = 5

agent3.sinks.k1.type = avro
agent3.sinks.k1.channel = c1
agent3.sinks.k1.hostname = VM124
agent3.sinks.k1.port = 5555
```

待补充...

