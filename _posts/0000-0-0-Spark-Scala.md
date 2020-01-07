---
layout: post
title: "Spark Scala 编程"
date: 2019-09-23
description: "Spark Scala 编程"
tag: Spark

---

# Spark Core Scala 编程

## WordCount

```java
object WordCountScala {
  def main(args: Array[String]): Unit = {
    val conf = new SparkConf().setAppName("WordCountScala").setMaster("local")
    val sc = new SparkContext(conf)
    val args = Array("D:/test/1.txt", "D:/out")

    val rdd = sc.textFile(args(0))
      .flatMap(_.split(" "))
      .filter(!_.isEmpty)
      .map((_, 1))
      .reduceByKey(_ + _, 1)
      .sortBy(_._2, false)
      // .saveAsTextFile(args(1))
    rdd.foreach(println(_))
    sc.stop()
    println("OK!")
  }
}
```

## 自定义分区

```java
class CustomerPartitioner(numParts:Int) extends Partitioner {
  // 覆盖分区数
  override def numPartitions: Int = numParts
  // 覆盖分区号获取函数
  override def getPartition(key: Any): Int = {
    val ckey: String = key.toString
    // 返回字符串最后一位 % 分区数
    ckey.substring(ckey.length-1).toInt % numParts
  }
}

object CustomerPartitioner {
  def main(args:Array[String]): Unit = {
    val conf = new SparkConf().setAppName("WC").setMaster("local")
    val sc = new SparkContext(conf)
    val data = sc.parallelize(List("aa.2", "bb.2", "cc.3", "dd.5", "ee.5"))
    data.map((_, 1))
      .partitionBy(new CustomerPartitioner(5))
      .keys
      .saveAsTextFile("D:/out")
  }
}
```

## 自定义累加器

```java
class CustomerAccumulator extends AccumulatorV2[String,java.util.Set[String]] {
  // 定义一个累加器的内存结构，用于保存带有字母的字符串
  private val _logArray: java.util.Set[String] = new java.util.HashSet[String]()

  // 重写方法检测累加器内部数据结构是否为空
  override def isZero: Boolean = {
    _logArray.isEmpty
  }
  override def copy(): AccumulatorV2[String, util.Set[String]] = {
    val newAcc = new CustomerAccumulator()
    _logArray.synchronized{
      newAcc._logArray.addAll(_logArray)
    }
    newAcc
  }
  // 重置
  override def reset(): Unit = {
    _logArray.clear()
  }
  // 提供转换或行动操作中添加累加器值的方法
  override def add(v: String): Unit = {
    _logArray.add(v)
  }
  // 提供将多个分区的累加器的值进行合并的操作函数
  override def merge(other: AccumulatorV2[String, util.Set[String]]): Unit = {
    // 通过检测将o这个累加器的值加入都当前_logArray结构中
    other match {
      case o: CustomerAccumulator => _logArray.addAll(o.value)
    }
  }
  // 输出value值
  override def value: util.Set[String] = {
    java.util.Collections.unmodifiableSet(_logArray)
  }
}

object CustomerAccumulator {
  def main(args:Array[String]): Unit = {
    val conf = new SparkConf().setAppName("Accumulator").setMaster("local")
    val sc = new SparkContext(conf)

    val accum = new CustomerAccumulator
    sc.register(accum, "CA")    // 自定义累加器
    val sum = sc.parallelize(Array("1", "2a", "3", "4b", "5", "6", "7cd", "8", "9"), 2)
      .filter(x => {      // 过滤含字母
        val pattern = """^-?(\d+)"""
        val flag = x.matches(pattern)
        if (!flag) {
          accum.add(x)
        }
        flag
      })
      .map(_.toInt)
      .reduce(_+_)

    println("sum : " + sum)
    println(accum.value)
    sc.stop()
  }
}
```

# Spark SQL Scala 编程

## DataFrame 基础

```java
object DataFrameScala {
  def main(args:Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("SparkSQL")
      .master("local")
      .getOrCreate()

    val df = spark.read.json("D:/test/person.json")
    df.show()
    df.groupBy("age").count().show()  // 统计每个年龄的个数
    df.printSchema()                         // 打印表结构

    // 用于将DataFrame隐式转换成RDD, 使df能够使用RDD中的方法
    import spark.implicits._
    df.filter($"age" > 21).show()

    df.createOrReplaceTempView("persons") // 创建临时表
    spark.sql("select * from persons").show()
    // Session退出临时表失效，可使用全局表
    df.createGlobalTempView("people")
    spark.sql("select * from global_temp.people").show()
  }
}
```

# Spark Streaming Scala 编程

## Streaming 处理流

```java
object WordCountStreamingScala {
  def main(args:Array[String]): Unit = {
    val conf = new SparkConf().setAppName("WC").setMaster("local")
    val ssc = new StreamingContext(conf, Seconds(1))
    val dStream = ssc.socketTextStream("172.16.7.124", 9999)
    dStream.print()
    ssc.start()              // 启动消息采集
    ssc.awaitTermination()   // 等待程序终止
    // ssc.stop()            // 手动终止
  }
}
```

## Direct 方式接收 Kafka 

```java
object DirectKafkaScala {
  def main(args: Array[String]): Unit = {
    val sparkConf: SparkConf = new SparkConf().setAppName("Direct").setMaster("local[2]")
    val sc = new SparkContext(sparkConf)
    sc.setLogLevel("WARN")
    val ssc = new StreamingContext(sc,Seconds(5))

    val kafkaParams=Map("metadata.broker.list"->"172.16.7.124:9092",
      "group.id"->"test-consumer-group")
    val topics=Set("MyTopic")

    // 通过 KafkaUtils.createDirectStream接受kafka数据，采用是kafka低级api偏移量不受zk管理
    val dstream: InputDStream[(String, String)] = KafkaUtils.createDirectStream[String,String,StringDecoder,StringDecoder](ssc,kafkaParams,topics)


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

## Receiver 方式接收 Kafka 

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



