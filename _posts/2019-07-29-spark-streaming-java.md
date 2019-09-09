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

