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
SparkConf sparkConf = new SparkConf().setAppName("SparkApplication").setMaster("local");
JavaStreamingContext jssc = new JavaStreamingContext(sparkConf, new Duration(2000));
JavaDStream lines = jssc.socketTextStream("172.16.7.124", 9999);
lines.print();
jssc.start();
jssc.awaitTermination();
// jssc.stop();
```

