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

同步到其他机器


## 数据流向

VM125 和 VM126 机器汇总到 VM124

VM124 再发送到 kafka 和 hbase


## VM125 修改 flume-conf.properties

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


## VM126 修改 flume-conf.properties

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


## VM124 修改 flume-conf.properties

```sh
agent1.sources = r1
agent1.channels = kafkaC hbaseC 
agent1.sinks =  kafkaSink hbaseSink

agent1.sources.r1.type = avro
agent1.sources.r1.channels = hbaseC kafkaC
agent1.sources.r1.bind = VM124
agent1.sources.r1.port = 5555
agent1.sources.r1.threads = 5

# flume --> hbase
agent1.channels.hbaseC.type = memory
agent1.channels.hbaseC.capacity = 100000
agent1.channels.hbaseC.transactionCapacity = 100000
agent1.channels.hbaseC.keep-alive = 20

agent1.sinks.hbaseSink.type = asynchbase
agent1.sinks.hbaseSink.table = weblogs
agent1.sinks.hbaseSink.columnFamily = info
agent1.sinks.hbaseSink.channel = hbaseC
agent1.sinks.hbaseSink.serializer = org.apache.flume.sink.hbase.SimpleAsyncHbaseEventSerializer
agent1.sinks.hbaseSink.serializer.payloadColumn = datatime,userid,searchname,retorder,cliorder,cliurl


#flume  --> kafka
agent1.channels.kafkaC.type = memory
agent1.channels.kafkaC.capacity = 100000
agent1.channels.kafkaC.transactionCapacity = 100000
agent1.channels.kafkaC.keep-alive = 20

agent1.sinks.kafkaSink.channel = kafkaC
agent1.sinks.kafkaSink.type = org.apache.flume.sink.kafka.KafkaSink
agent1.sinks.kafkaSink.brokerList = VM124:9092,VM125:9092,VM126:9092
agent1.sinks.kafkaSink.topic = weblogs
agent1.sinks.kafkaSink.zookeeperConnect = VM124:2181,VM124:2181,VM124:2181
agent1.sinks.kafkaSink.requiredAcks = 1
agent1.sinks.kafkaSink.batchSize = 1
agent1.sinks.kafkaSink.serializer.class = kafka.serializer.StringEncoder
```


## 源码修改


路径：`apache-flume-1.9.0-src\flume-ng-sinks\flume-ng-hbase-sink\src\main\java\org\apache\flume\sink\hbase`

对 SimpleAsyncHbaseEventSerializer.java 修改 getActions()：

```java
public List<PutRequest> getActions() {
        List<PutRequest> actions = new ArrayList<>();
        if (payloadColumn != null) {
            byte[] rowKey;
            try {
                /*---------------------------代码修改开始---------------------------------*/
                //解析列字段
                String[] columns = new String(this.payloadColumn).split(",");
                //解析flume采集过来的每行的值
                String[] values = new String(this.payload).split(",");
                for(int i=0;i < columns.length;i++) {
                    byte[] colColumn = columns[i].getBytes();
                    byte[] colValue = values[i].getBytes(Charsets.UTF_8);

                    //数据校验：字段和值是否对应
                    if (colColumn.length != colValue.length) break;
                    //时间
                    String datetime = values[0].toString();
                    //用户id
                    String userid = values[1].toString();
                    //根据业务自定义Rowkey
                    rowKey = SimpleRowKeyGenerator.getKfkRowKey(userid, datetime);
                    //插入数据
                    PutRequest putRequest = new PutRequest(table, rowKey, cf,
                            colColumn, colValue);
                    actions.add(putRequest);
                    /*---------------------------代码修改结束---------------------------------*/
                }
            } catch (Exception e) {
                throw new FlumeException("Could not get row key!", e);
            }
        }
        return actions;
    }
```


对 SimpleRowKeyGenerator.java 增加：

```java
public class SimpleRowKeyGenerator {
  public static byte[] getKfkRowKey(String userid,String datetime)throws UnsupportedEncodingException {
    return (userid + datetime + String.valueOf(System.currentTimeMillis())).getBytes("UTF8");
  }
}
```

对 flume-ng-hbase-sink 打包成：lume-ng-hbase-sink-1.9.0.jar，放到flume/lib目录下


待补充...



# reference

https://yq.aliyun.com/articles/557454

https://github.com/TALKDATA/JavaBigData/blob/master/news-project.md
