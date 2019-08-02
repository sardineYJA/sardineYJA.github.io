---
layout: post
title: "Spark Streaming"
date: 2019-07-05
description: "介绍一下Spark Streaming"
tag: 大数据

---

# Spark Streaming

SPark Streaming是Spark中一个组件，基于Spark Core进行构建，用于对流式进行处理，类似于Storm。

## StreamingContext和SparkContext的关系

可以通过已经创建好的SparkContext来创建SparkStreaming


# 编程

增加依赖

```xml
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-streaming_2.11</artifactId>
    <version>${spark.version}</version>
    <scope>provided</scope>
</dependency>
```

程序打包上传

```java
import org.apache.spark.SparkConf
import org.apache.spark.streaming.{Seconds, StreamingContext}

object WordStreaming {
  def main(args:Array[String]): Unit = {
    val conf = new SparkConf().setAppName("WS")
    val ssc = new StreamingContext(conf, Seconds(1))

    // 创建 DStream 连接 hostname:port
    val lines = ssc.socketTextStream("172.16.7.124", 9999)

    val wordCounts = lines.flatMap(_.split(" "))
                          .map(w => (w, 1))
                          .reduceByKey(_+_)
    wordCounts.print()

    ssc.start()              // 启动消息采集
    ssc.awaitTermination()   // 等待程序终止
    // ssc.stop()            // 手动终止
  }
}
```

开启发送数据

```
// 通过Netcat发送数据
yum -y install nmap-ncat
nc -lk 9999
```

运行：`bin/spark-submit --class test.WordStreaming myJar/ws.jar`

log日志太多，可以将spark conf目录下的log4j文件里面的日志级别改成WARN



# 数据源

streamingContext.fileStream[KeyClass, ValueClass, InputFormatClass](dataDirectory)

1. Spark Streaming 将会监控dataDirectory目录并不断处理移动进来的文件

2. 目前不支持嵌套目录

3. 文件需要有相同的数据格式

4. 文件进入dataDirectory的方式需要通过移动或者重命名来实现

5. 一旦文件移动进入目录，则不能再修改，即使修改了也不会读取新数据

streamingContext.textFileStream(dataDirectory)

1. 可用于文件比较简单的时候

2. 文件流不需要接收器，不需要单独分配CPU核数



提前建好目录，测试上传文件

```java
import org.apache.spark.streaming._
val ssc = new StreamingContext(sc, Seconds(1))
val lines = ssc.textFileStream(".../data/")
val words = lines.flatMap(_.split(" "))
val wordCounts = words.map(x => (x, 1)).reduceByKey(_ + _)
wordCounts.print()
ssc.start()
```

## 自定义数据源


继承Receiver，实现onStart，onStop方法

```java
import java.io.{BufferedReader, InputStreamReader}
import java.net.Socket
import java.nio.charset.StandardCharsets

import org.apache.spark.SparkConf
import org.apache.spark.storage.StorageLevel
import org.apache.spark.streaming.{Seconds, StreamingContext}
import org.apache.spark.streaming.receiver.Receiver

class CustomReceiver (host:String, port:Int)
  extends Receiver[String](StorageLevel.MEMORY_AND_DISK_2) {

  // Receiver 启动时需调用的方法
  override def onStart(): Unit = {
    new Thread("Socket Receiver") {
      override def run() {receive()}  // 新线程运行receive
    }.start()
  }
  // Receiver 停止需调用的方法
  override def onStop(): Unit = {

  }

  private def receive(): Unit = {
    var socket: Socket = null
    var userInput: String = null
    try {
      // Socket 连接
      socket = new Socket(host, port)
      // 获取输入
      val reader = new BufferedReader(
        new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8))

      userInput = reader.readLine()  // 获取第一条输入
      while(!isStopped() && userInput != null) {
        store(userInput)    // 将数据提交到Spark框架
        userInput = reader.readLine()
      }
      reader.close()
      socket.close()

      // connect again when server is active again
      restart("Trying to connect again")
    } catch {
      case e: java.net.ConnectException => restart("Error connecting to " + host + ":" + port, e)
      case t: Throwable => restart("Error receiving data", t)
    }
  }
}

object CustomReceiver {
  def main(args: Array[String]): Unit = {
    val conf = new SparkConf().setAppName("NetworkWordCount")
    val ssc = new StreamingContext(conf, Seconds(2))
    val lines = ssc.receiverStream(new CustomReceiver("172.16.7.124", 9999))
    val words = lines.flatMap(_.split(" "))
    val pairs = words.map(word => (word, 1))
    val wordCount = pairs.reduceByKey(_+_)
    wordCount.print()
    ssc.start()
    ssc.awaitTermination()
  }
}
```

发送数据：`nc -lk 9999`

打包上传：`bin/spark-submit --class te.CustomReceiver myJar/cr.jar`

## RDD队列数据源

通过使用streamingContext.queueStream(queueOfRDDs)来创建DStream，每一个推送到这个队列中的RDD，都会作为一个DStream处理

```java
import org.apache.spark.SparkConf
import org.apache.spark.rdd.RDD
import org.apache.spark.streaming.{Seconds, StreamingContext}
import scala.collection.mutable

object QueueRdd {
  def main(args: Array[String]) {
    val conf = new SparkConf().setAppName("QueueRdd")
    val ssc = new StreamingContext(conf, Seconds(1))

    // 创建RDD队列
    val rddQueue = new mutable.synchronizedQueue[RDD[Int]]()
    val inputStream = ssc.queueStream(rddQueue)

    // 处理加入队列中的RDD数据
    val reduceStream = inputStream.map(x = > (x % 10, 1)).reduceByKey(_+_)
    // 打印结果
    reduceStream.print()

    ssc.start()

    // 创建RDD并放入队列中
    for (i <- 1 to 30) {
      rddQueue += ssc.sparkContext.makeRDD(1 to 300, 10)
      Thread.sleep(2000)
    }

    ssc.awaitTerminationOrTimeout()
  }
}
```


## 高级数据源

Kaffa之类，后期补充


# DStreams

DStream是类似于RDD和DataFrame的针对流式计算的抽象类。
在源码中DStream是通过HashMap来保存他所管理的数据流的。
K是RDD中数据流的时间，V是包含数据流的RDD。

DStream 分 ： Transformations(转化) 和 Output Operations(输出)

Transformations(转化) 分： 无状态（stateless） 和 有状态（stateful）

无状态的转换（前面处理的数据和后面处理的数据没啥关系）

有转换转换（前面处理的数据和后面处理的数据是有关系的，比如叠加关系）

有状态（stateful）转化操作：基于滑动窗口的转化操作 和 追踪状态变化的转化操作

## UpdateStateByKey 追踪状态变化

实现统计每次输入的词数的总和，而不是统计每次输入的

```java
import org.apache.spark.SparkConf
import org.apache.spark.streaming.{Seconds, StreamingContext}

object StateWordCount {
  def main(args: Array[String]) {

    // 定义更新状态方法，参数values:Array(1,1)为当前批次单词频率，state为以往批次单词频率，是框架提供
    val updateFunc = (values:Seq[Int], state:Option[Int]) => {
      // 计算当前批次相同key的单词总数
      val currentCount = values.foldLeft(0)(_+_)
      // 获取上一次保存的单词总数
      val previousCount = state.getOrElse(0)
      // 返回新的单词总数
      Some(currentCount + previousCount)
    }

    val conf = new SparkConf().setAppName("StateWordCount")
    val ssc = new StreamingContext(conf, Seconds(3))
    ssc.checkpoint("/home/yangja/tmp/")   // 会使用检查点来保存状态

    val lines = ssc.socketTextStream("172.16.7.124",9999)
    val stateDstream = lines.flatMap(_.split(" "))
                            .map(word => (word,1))
                            .updateStateByKey[Int](updateFunc)
    stateDstream.print()

    ssc.start()
    ssc.awaitTermination()
  }
}
```

发送数据：`nc -lk 9999`

打包上传测试：`bin/spark-submit --class test.StateWordCount myJar/statewc.jar`


## Window Operations 基于滑动窗口

实现统计每个窗口输入的词数的总和，而不是统计每次输入的

```java
import org.apache.spark.SparkConf
import org.apache.spark.streaming.{Seconds, StreamingContext}

object WindowWordCount {

  def main(args:Array[String]) {
    val conf = new SparkConf().setAppName("WindowWordCount")
    val ssc = new StreamingContext(conf, Seconds(3))
    ssc.checkpoint("/home/yangja/tmp/")

    val lines = ssc.socketTextStream("172.16.7.124", 9999)
    val wordCounts = lines.flatMap(_.split(" "))
      .map(word => (word, 1))
      .reduceByKeyAndWindow((a:Int, b:Int) => (a+b), Seconds(12), Seconds(6))
      // 其中3s一个批次（RDD）,12表示窗口大小4个，6表示滑动大小2个

    wordCounts.print()
    ssc.start()
    ssc.awaitTermination()
  }
}
```




















