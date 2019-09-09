---
layout: post
title: "Spark Streaming Java编程"
date: 2019-07-29
description: "介绍一下Spark java编程"
tag: 大数据

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

## Streaming 基于 Receiver 读 Kafka


```xml
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-streaming-kafka_2.11</artifactId>
    <version>1.6.2</version>
</dependency>
```

启动Kafka：`bin/kafka-server-start.sh config/server.properties &`

启动生产者：`bin/kafka-console-producer.sh --broker-list xxx.xxx.xxx.xxx:9092 --topic MyTopic`

group id 查看：config/consumer.properties

缺少 spark-core_2.11-1.5.2.logging.jar 包，下载：https://github.com/sardineYJA/MySource

```java
SparkConf conf = new SparkConf().setAppName("KafkaWordCount").setMaster("local[*]");
JavaStreamingContext jssc = new JavaStreamingContext(conf, Durations.seconds(3));
jssc.checkpoint("D:/checkpoint");

// 每个partition对应一个单独线程从kafka取数据到Spark Streaming
Map<String, Integer> topicThread = new HashMap<>(1);
topicThread.put("MyTopic", 1);
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

发现端口2181写成9092




