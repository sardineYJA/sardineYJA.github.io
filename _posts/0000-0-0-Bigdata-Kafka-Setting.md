---
layout: post
title: "Kafka 实践操作"
date: 2019-07-15
description: "Kafka"
tag: Bigdata

---


## 部署Zookeeper

1. 解压：tar -zxvf zookeeper-3.4.10.tar.gz -C ../module/

2. 创建../zookeeper-3.4.10/zkData 目录

3. 配置文件conf目录：cp zoo_sample.cfg zoo.cfg

4. 修改zoo.cfg文件

```
dataDir=/.../zookeeper-3.4.10/zkData
#######################cluster##########################
server.1=hadoop101:2888:3888
server.2=hadoop102:2888:3888
server.3=hadoop103:2888:3888
```

5. 创建 .../zkData/myid文件

6. myid中写上对应编号

```
1
```

7. 配置同步其他节点，除了myid文件

8. 各节点分别启动：`bin/zkServer.sh start`

9. 查看状态：`bin/zkServer.sh status`


## 部署Kafka

0. 下载：http://kafka.apache.org/downloads.html

1. 解压：tar -zxvf kafka_2.11-0.11.0.0.tgz -C /.../module/

2. 创建目录 ../kafka_2.11-0.11.0.0/logs

3. 修改配置文件 config/server.properties

```
#broker的全局唯一编号，不能重复
broker.id=0
#删除topic功能使能
delete.topic.enable=true
#kafka运行日志存放的路径
log.dirs=/.../kafka/logs
#配置连接Zookeeper集群地址
zookeeper.connect=hadoop101:2181,hadoop102:2181,hadoop103:2181
```

4. 配置环境变量：`vi /etc/profile`

```
#KAFKA_HOME
export KAFKA_HOME=/.../kafka_2.11-0.11.0.0
export PATH=$PATH:$KAFKA_HOME/bin
```

5. 配置同步其他节点，除了server.properties中的broker.id

6. 依次启动节点：`bin/kafka-server-start.sh config/server.properties &`


## kafka命令

1. 查看所有topic：`bin/kafka-topics.sh --list --zookeeper hadoop101:2181`

2. 创建topic：`bin/kafka-topics.sh --create --zookeeper hadoop101：2181 --replication-factor 3 --partitions 1 --topic topicName`

3. 删除topic：`bin/kafka-topics.sh --delete --zookeeper hadoop101:2181 -topic topicName`

4. 发送消息：`bin/kafka-console-producer.sh --broker-list hadoop101:9092 --topic topicName`

5. 消费消息：`bin/kafka-console-consumer.sh --zookeeper hadoop101:2181 --from-beginning --topic topicName`

6. 查看某个topic：`bin/kafka-topics.sh --topic topicName --describe --zookeeper hadoop101:2181`

7. 启动一个消费者：bin/kafka-console-consumer.sh --zookeeper xxx.xxx.xxx.xxx:2181 --topic MyTopic

8. 启动一个生产者：bin/kafka-console-producer.sh --broker-list xxx.xxx.xxx.xxx:9092 --topic MyTopic



## 查看offset消费情况

使用kafka的bin目录下面的kafka-consumer-groups.sh命令可以查看offset消费情况。

注意，如果你的offset是存在kafka集群上的，就指定kafka服务器的地址bootstrap-server：

```sh
./kafka-consumer-groups.sh --bootstrap-server 172.17.6.10:9092 --describe dylog --group dylog
```
```
Note: This will only show information about consumers that use the Java consumer API (non-ZooKeeper-based consumers).
TOPIC     PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG   CONSUMER-ID                                       HOST            CLIENT-ID
friend    0          13949           13949           0     consumer-1-25efc288-c534-4b1b-a57b-4cfdce853439   /172.17.6.181   consumer-1
```



# 测试

## 消费组

需求：测试同一个消费者组中的消费者，同一时刻只能有一个消费者消费

是同组所有消费者都可以接受，还是一个而已，只是时间不同，又哪怎么判断哪个先接受？

1. 三台kafka，修改consumer.properties的group.id=testsxdt

2. 两台启动consumer：bin/kafka-console-consumer.sh --zookeeper hadoop101:2181 --topic topicName --consumer.config config/consumer.properties

3. 一台启动producer：bin/kafka-console-producer.sh --broker-list hadoop101:9092 --topic first

4. 测试接收


# 编程

> WARN NetworkClient: [Consumer clientId=consumer-1, groupId=test] Connection to node -1 (/172.16.7.124:9092) could not be established. Broker may not be available.

1. 配置server.properties

```
broker.id=0
listeners=PLAINTEXT://172.16.7.124:9092
```

2. 启动可以看到kafka在Zookeeper注册

```
bin/zkCli.sh
get /brokers/ids/0
```

依赖

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>2.1.1</version>
</dependency>

<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-streams</artifactId>
    <version>1.0.1</version>
</dependency>
```

## Producer

1. 先启动一个消费者

```
bin/kafka-console-consumer.sh --zookeeper xxx.xxx.xxx.xxx:2181 --topic MyTopic
```

2. 生产者

```java
public class MyKafkaProducer {

    public static void main(String[] args) {
        Properties props = new Properties();
        // kafka服务端的主机
        props.put("bootstrap.servers", "172.16.7.124:9092");
        props.put("acks", "all");       // 等待所有副本节点的应答
        props.put("retries", 0);        // 消息发送最大尝试次数
        props.put("batch.size", 16384); // 一批消息处理大小
        props.put("linger.ms", 1);      // 请求延时
        props.put("buffer.memory", 33554432); // 发送缓存区内存大小

        // key 序列化
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        // value 序列化
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

        Producer<String, String> producer = new KafkaProducer<String, String>(props);
        for (int i=0; i<50; i++) {
            producer.send(new ProducerRecord<String, String>("MyTopic",
                    Integer.toString(i), "Hello "+i));
        }
        producer.close();
    }

}
```

修改，增加回调函数

```java
producer.send(new ProducerRecord<String, String>("MyTopic",
                    Integer.toString(i), "Hello " + i), new Callback() {
                @Override
                public void onCompletion(RecordMetadata recordMetadata, Exception e) {
                    if (recordMetadata != null) {
                        System.err.println(recordMetadata.partition() + "---" +recordMetadata.offset());
                    }
                }
            });
```

## 自定义分区生产者

```java
public class CustomPartitioner implements Partitioner {

	@Override
	public void configure(Map<String, ?> configs) {}

	@Override
	public int partition(String topic, Object key, byte[] keyBytes, Object value, byte[] valueBytes, Cluster cluster) {
        // 控制分区
		return 0;
	}

	@Override
	public void close() {}
}
```

```java
// 自定义分区
props.put("partitioner.class", "com.xxx.xxx.CustomPartitioner");
```



## Consumer

1. 先启动一个生产者

```
bin/kafka-console-producer.sh --broker-list xxx.xxx.xxx.xxx:9092 --topic MyTopic
```

2. 消费者

```java
public class MyKafkaConsumer {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put("bootstrap.servers", "172.16.7.124:9092");
        props.put("group.id", "test");                 // 制定consumer group
        props.put("enable.auto.commit", "true");       // 是否自动确认offset
        props.put("auto.commit.interval.ms", "1000");  // 自动确认offset的时间间隔

        // key的反序列化类
        props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        // value的反序列化类
        props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");

        KafkaConsumer<String, String> consumer = new KafkaConsumer<String, String>(props);
        // 消费者订阅的topic，可同时订阅多个
        consumer.subscribe(Arrays.asList("MyTopic"));
        while (true) {
            // 读取数据，读取超时时间为100ms
            ConsumerRecords<String, String>records = consumer.poll(100);

            for (ConsumerRecord<String, String> record : records) {
                System.out.printf("offset=%d, key=%s, value=%s%n",
                        record.offset(), record.key(), record.value());
            }

        }
    }
}
```


# 拦截器

多个interceptor按序作用于一条消息从而形成拦截链interceptor chain

实现接口org.apache.kafka.clients.producer.ProducerInterceptor

1. configure(conf) 获取配置信息和初始化数据时调用

2. onSend(ProducerRecord) 对消息进行操作

3. onAcknowledgement(RecordMetadata, Exception) 在消息被应答之前或消息发送失败时调用

4. close 资源清理工作

```java
import java.util.Map;
public class TimeInterceptor implements ProducerInterceptor<String, String> {
    @Override
    public ProducerRecord<String, String> onSend(ProducerRecord<String, String> record) {
        // 创建一个新的record，把时间戳写进消息体的最前面
        return new ProducerRecord(record.topic(), record.partition(),
                record.timestamp(), record.key(),
                System.currentTimeMillis() + "," + record.value().toString());
    }

    @Override
    public void onAcknowledgement(RecordMetadata recordMetadata, Exception e) {}
    @Override
    public void close() {}
    @Override
    public void configure(Map<String, ?> map) {}
}
```

```java
public class CounterInterceptor implements ProducerInterceptor<String, String> {
    private int errorCounter = 0;    // 发送失败消息数
    private int successCounter = 0;  // 发送成功消息数

    @Override
    public ProducerRecord<String, String> onSend(ProducerRecord<String, String> producerRecord) {
        return producerRecord;
    }

    @Override
    public void onAcknowledgement(RecordMetadata recordMetadata, Exception e) {
        // 统计次数
        if (e == null) {
            successCounter++;
        } else {
            errorCounter++;
        }
    }

    @Override
    public void close() {
        // 保存结果
        System.out.println("Successful sent : " + successCounter);
        System.out.println("Faild sent : " + errorCounter);
    }

    @Override
    public void configure(Map<String, ?> map) {}
}
```

```java
public class MyInterceptorProducer {
    public static void main(String[] args) {
        // 1 设置配置信息
        Properties props = new Properties();
        // kafka服务端的主机
        props.put("bootstrap.servers", "172.16.7.124:9092");
        props.put("acks", "all");       // 等待所有副本节点的应答
        props.put("retries", 0);        // 消息发送最大尝试次数
        props.put("batch.size", 16384); // 一批消息处理大小
        props.put("linger.ms", 1);      // 请求延时
        props.put("buffer.memory", 33554432); // 发送缓存区内存大小
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

        // 构建拦截链
        List<String> interceptors = new ArrayList<>();
        interceptors.add("testjava.TimeInterceptor");
        interceptors.add("testjava.CounterInterceptor");
        props.put(ProducerConfig.INTERCEPTOR_CLASSES_CONFIG, interceptors);

        String topic = "MyTopic";
        Producer<String, String> producer = new KafkaProducer<String, String>(props);
        for (int i=0; i<30; i++) {
            ProducerRecord<String, String> record = new ProducerRecord<>(topic, "message-" + i);
            producer.send(record);
        }
        producer.close();  // 此时才会调用interceptor的close
    }
}
```
