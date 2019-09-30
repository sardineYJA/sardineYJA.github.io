---
layout: post
title: "Spark Streaming Java编程"
date: 2019-07-29
description: "介绍一下Spark java编程"
tag: Spark

---


# Spark Streaming

## JavaStreamingContext 和 SparkConf


```java
SparkConf conf = new SparkConf().setMaster("local[*]").setAppName("Streaming");
JavaStreamingContext jssc = new JavaStreamingContext(conf, Durations.seconds(1));
```

```java
// 从服务器获取数据， JavaDStream 和 JavaReceiverInputDStream
// JavaDStream<String> dStream = jssc.socketTextStream("172.16.7.124", 9999);
JavaReceiverInputDStream<String> dStream = jssc.socketTextStream("172.16.7.124", 9999);
dStream.print();
// 过滤
JavaDStream<String> errorLine = dStream.filter(new Function<String, Boolean>() {
    @Override
    public Boolean call(String v) throws Exception {
        return v.contains("error");
    }
});
errorLine.print();
jssc.start();
jssc.awaitTermination();
```

统计每一次输入的单词数

```java
JavaReceiverInputDStream<String> inputDStream = jssc.socketTextStream("172.16.7.124", 9999);
JavaDStream<String> dStream = inputDStream.flatMap(
        (FlatMapFunction<String, String>) s -> Arrays.asList(s.split(" ")).iterator());
JavaPairDStream<String, Integer> pairDStream = dStream.mapToPair(new PairFunction<String, String, Integer>() {
    @Override
    public Tuple2<String, Integer> call(String s) throws Exception {
        return new Tuple2<>(s, 1);
    }
});
JavaPairDStream<String, Integer> wordCount = pairDStream.reduceByKey((v1, v2) -> v1 + v2);
wordCount.print();
jssc.start();
jssc.awaitTermination();
```

## 有状态转换操作(stateful)

reduceByKeyAndWindow 用于计算IP地址单位时间的访问量

```java
SparkConf conf = new SparkConf().setMaster("local[*]").setAppName("Streaming");
JavaStreamingContext jssc = new JavaStreamingContext(conf, Durations.seconds(3));
jssc.checkpoint("D:/checpoint");        // 检查点设置
JavaDStream<String> dStream = jssc.socketTextStream("172.16.7.124", 9999);
JavaPairDStream<String, Long> pairDStream = dStream.mapToPair(new PairFunction<String, String, Long>() {
    @Override
    public Tuple2<String, Long> call(String s) throws Exception {
        return new Tuple2<>(s, 1L);
    }
});

JavaPairDStream<String, Long> windowWordCount = pairDStream.reduceByKeyAndWindow(
        new Function2<Long, Long, Long>() { // 新进入窗口元素
            @Override
            public Long call(Long v1, Long v2) throws Exception {
                return v1 + v2;
            }
        },
        new Function2<Long, Long, Long>() { // 离开窗口元素，减为0后不再减少
            @Override
            public Long call(Long v1, Long v2) throws Exception {
                return v1 - v2;
            }
        },
        Durations.seconds(9), Durations.seconds(3)); // 窗口大小9s，滑动步长3s

windowWordCount.print();
jssc.start();
jssc.awaitTermination();
```

## foreachRDD 写数据到 MySQL

```java
public class ConnectionPool {
    private static LinkedList<Connection> connectionQueue;

    static {
        try {
            Class.forName("com.mysql.jdbc.Driver");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public synchronized static Connection getConnection() {
        try {
            if (connectionQueue == null) {
                connectionQueue = new LinkedList<>();
            }
            for (int i = 0; i < 10; i++) {
                Connection conn = DriverManager.getConnection("jdbc:mysql://spark1:3307/test", "root", "root");
                connectionQueue.push(conn);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return connectionQueue.poll();
    }

    public static void returnConnection(Connection conn) {
        connectionQueue.push(conn);
    }
}
```

```java
result.foreachRDD(rdd -> {
    rdd.foreachPartition(partitionOfRecords -> {
        Connection connection = ConnectionPool.getConnection();
        Tuple2<String, Integer> wordCount;

        while (partitionOfRecords.hasNext()) {
            wordCount = partitionOfRecords.next();
            String sql = "insert into wordcount(word,count) " + "values('" + wordCount._1 + "',"
                    + wordCount._2 + ")";
            Statement stmt = connection.createStatement();
            stmt.executeUpdate(sql);
        }
        ConnectionPool.returnConnection(connection);
    });
});
```

# Spark Streaming 读取 Kafka 两种方式

## Receiver-base

对于所有的接收器，从kafka接收来的数据会存储在spark的executor中，之后spark streaming提交的job会处理这些数据。

Receiver-based的Kafka读取方式是基于Kafka高阶(high-level) api来实现对Kafka数据的消费。

## Direct

这种方式是延迟的，当action真正触发时才会去kafka里面接收数据

无需经由ZooKeeper，driver来决定读取多少offsets，并将offsets交由checkpoints来维护。

## 比较


1. 提高成本：Direct需要用户采用checkpoint或者第三方存储来维护offsets，而不像Receiver-based 那样，通过ZooKeeper来维护Offsets，此提高了用户的开发成本。

2. 监控可视化：Receiver-based方式指定topic指定consumer的消费情况均能通过ZooKeeper来监控，而Direct则没有这种便利，如果做到监控并可视化，则需要投入人力开发。

3. 基于receiver的方式，是使用Kafka的高阶API来在ZooKeeper中保存消费过的offset的。这是消费Kafka数据的传统方式。这种方式配合着WAL机制可以保证数据零丢失的高可靠性，但是却无法保证数据被处理一次且仅一次，可能会处理两次。因为Spark和ZooKeeper之间可能是不同步的。官方现在也已经不推荐这种整合方式，官网`推荐`的第二种方式kafkaUtils的`createDirectStream()`方式。



## Streaming 基于 Receiver 读 Kafka


```xml
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-streaming-kafka_2.11</artifactId>
    <version>1.6.2</version>
</dependency>
```

需先启动Zookeeper

启动Kafka：`bin/kafka-server-start.sh config/server.properties &`

启动生产者：`bin/kafka-console-producer.sh --broker-list xxx.xxx.xxx.xxx:9092 --topic MyTopic` (ip注意换)

group id 查看：config/consumer.properties

缺少 spark-core_2.11-1.5.2.logging.jar 包，下载：https://github.com/sardineYJA/MySource

```java
SparkConf conf = new SparkConf().setAppName("KafkaWordCount").setMaster("local[*]");
JavaStreamingContext jssc = new JavaStreamingContext(conf, Durations.seconds(3));
jssc.checkpoint("D:/checkpoint");

// 每个partition对应一个单独线程从kafka取数据到Spark Streaming
Map<String, Integer> topicThread = new HashMap<>(1);
topicThread.put("MyTopic", 1);  // topic中每一个分区被1个线程消费
JavaPairInputDStream<String, String> dStream = KafkaUtils.createStream(
        jssc,
        "172.16.7.124:2181",
        "test-consumer-group",
        topicThread);

dStream.print();

JavaDStream<String> words = dStream
        .flatMap((FlatMapFunction<Tuple2<String, String>, String>) t -> Arrays.asList(SPACE.split(t._2)).iterator());

JavaPairDStream<String, Integer> result = words
        .mapToPair((PairFunction<String, String, Integer>) s -> new Tuple2<>(s, 1))
        .reduceByKey((Function2<Integer, Integer, Integer>) (v1, v2) -> v1+v2);
result.print();

jssc.start();
jssc.awaitTermination();
```

> ERROR ReceiverTracker: Deregistered receiver for stream 0: Error starting receiver 0 - org.I0Itec.zkclient.exception.ZkTimeoutException: Unable to connect to zookeeper server within timeout: 10000

端口写成9092，写2181即可



```java
SparkConf conf = new SparkConf().setAppName("Direct").setMaster("local[*]");
JavaStreamingContext jssc = new JavaStreamingContext(conf, Durations.seconds(3));

Map<String, String> kafkaParams = new HashMap<String, String>();
kafkaParams.put("metadata.broker.list", "172.16.7.124:9092");
kafkaParams.put("group.id", "test-consumer-group");

HashSet<String> topics = new HashSet<>();
topics.add("MyTopic");

JavaPairInputDStream<String, String> directStream = KafkaUtils.createDirectStream(
        jssc,
        String.class,        // key 类型
        String.class,        // value 类型
        StringDecoder.class, // 解码器
        StringDecoder.class,
        kafkaParams,
        topics
);
directStream.print();
jssc.start();
jssc.awaitTermination();
```


Scala版本

```java
object ReceiverKafkaScala {
  def main(args: Array[String]): Unit = {
    val sparkConf: SparkConf = new SparkConf()
      .setAppName("Receiver")
      .setMaster("local[2]")
      .set("spark.streaming.receiver.writeAheadLog.enable","true")// 开启wal预写日志，保存数据源的可靠性

    val sc = new SparkContext(sparkConf)
    sc.setLogLevel("WARN")
    val ssc = new StreamingContext(sc, Seconds(5))
    ssc.checkpoint("D:/checkpoint")

    val topics=Map("MyTopic"->1)
    val stream: ReceiverInputDStream[(String, String)]=KafkaUtils.createStream(
      ssc, "172.16.7.124:2181", "test-consumer-group", topics)

    stream.print()
    ssc.start()
    ssc.awaitTermination()
  }
}
```


```java
import org.apache.spark.streaming.kafka.KafkaUtils

object DirectKafkaScala {
  def main(args: Array[String]): Unit = {
    val sparkConf: SparkConf = new SparkConf().setAppName("Direct").setMaster("local[2]")
    val sc = new SparkContext(sparkConf)
    sc.setLogLevel("WARN")
    val ssc = new StreamingContext(sc,Seconds(5))


    // 配置kafka相关参数
    val kafkaParams=Map("metadata.broker.list"->"172.16.7.124:9092","group.id"->"test-consumer-group")

    // 定义topic
    val topics=Set("MyTopic")

    // 通过 KafkaUtils.createDirectStream接受kafka数据，采用是kafka低级api偏移量不受zk管理
    val dstream: InputDStream[(String, String)] = KafkaUtils.createDirectStream[String,String,StringDecoder,StringDecoder](ssc,kafkaParams,topics)

    // 获取kafka中topic中的数据
    val topicData: DStream[String] = dstream.map(_._2)

    // 切分每一行,每个单词计为1
    val wordAndOne: DStream[(String, Int)] = topicData.flatMap(_.split(" ")).map((_,1))

    // 相同单词出现的次数累加
    val result: DStream[(String, Int)] = wordAndOne.reduceByKey(_+_)

    result.print()
    ssc.start()
    ssc.awaitTermination()
  }
}
```

问题：

> Exception in thread "main" org.apache.spark.SparkException: java.io.EOFException

> java.io.EOFException: Received -1 when reading from channel, socket has likely been closed.

端口写成2181，写9092即可


问题：

>  kafka.cluster.BrokerEndPoint cannot be cast to kafka.cluster.Broker

原来写了两个依赖，去掉上面那个即可

```xml
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-streaming-kafka-0-10_2.11</artifactId>
    <version>${spark.version}</version>
</dependency>

<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-streaming-kafka_2.11</artifactId>
    <version>1.6.2</version>
</dependency>
```


