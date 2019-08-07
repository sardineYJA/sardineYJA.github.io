---
layout: post
title: "Spark Core"
date: 2019-06-23
description: "介绍一下Spark Core"
tag: 大数据

---

# Spark:

1. Spark Core       （操作RDD：创建->转换->缓存->行动->输出）
2. Spark SQL         (操作SQL)
3. Spark Streaming   (流式数据处理)
4. Spark MLlib
5. 集群管理器（YARN,Mesos,独立调度器）


## 部署模式
Local 和 Local-Cluster (单机模式)
Standalone    （使用自带的独立调度器）
Yarn          （使用YARN）
Mesos          (使用Mesos)


# RDD

## 简介

弹性分布式数据集 (Resilient Distributed Dataset)，是分布式数据的抽象，为用户屏蔽了底层复杂的计算和映射环境

1. 对数据的所有操作不外乎创建 RDD、转化已有RDD 以及调用 RDD 操作进行求值

2. 每个 RDD（一组分片）都被分为多个分区，这些分区运行在集群中的不同节点上

3. RDD表示只读的分区的数据集

4. RDD 是弹性的

  （1）存储：自动将RDD缓存到内存或磁盘

  （2）容错：可通过血统或检查点机制恢复

  （3）计算：分层计算=应用->job->stage->TaskSet->Task

  （4）分片：RDD以分片分布 


## 算子

1. transformations : 转换构建RDD血缘关系

2. actions：触发RDD的计算

## 依赖

1. 窄依赖：上游RDD与下游RDD一一对应

2. 宽依赖：上游RDD的每个分区与下游RDD的每个分区都有关

3. 宽依赖会引起 shuffle

4. 区别：是否要进行shuffle阶段（合并分区的过程）

5. 应用在执行过程中，是分为多个Stage来进行的，划分Stage的关键就是判断是不是存在宽依赖。从Action往前去推整个Stage的划分。

## 缓存

1. 直接从缓存处取而不用再根据血缘关系计算

2. 加速后期的重用

3. 缓存方法：persist() 和 cache()

4. 调用方法时不会立即缓存，而是触发action

5. cache() 最终也是调用 persist()


## checkpoint

1. 持久化的存储到HDFS

2. 切断之前的血缘关系

3. 适合场景：

  （1）DAG中的Lineage过长，重算开销过大

  （2）在宽依赖上做Checkpoint获得的收益更大

4. checkpoint的使用

  （1）先创建一个RDD

  （2）需要设置目录，sparkContext.setCheckpointDir("....")

  （3）在RDD上调用checkpoint方法
     
  （4）触发RDD的行动操作，让RDD的数据真实写入checkpoint目录




# RDD 编程

## 集群中组件包含关系

1. { Master Node ( Driver < SparkContext > ) }
2. { Worker Node ( Executor < Task Task ... > ) }
3. Cluster Manager : Standalone, yarn, mesos, ...

## 创建 RDD

1. 从集合中创建

```java
sc.parallelize(seq)        // 把seq数据并行划分片到节点
sc.makeRDD(seq)            // 把seq数据并行划分片到节点（实现就是parallelize）
sc.makeRDD(seq[(T, seq)])  // 可以指定RDD的存放位置
```

2. 从外部存储创建 `sc.textFile("path")`

3. 从其他RDD转换过来


## RDD 分区

1. HashPartitioner 分区可能导致每个分区中数量不均

2. RangePartitioner 尽量保证每个分区中的数量的均匀

```java
// 获取分区方式：Option[org.apache.spark.Partitioner] = None
sc.parallelize(List((1,1), (2,2), (3,3))).partitioner

// 修改分区方式：
sc.parallelize(List((1,1), (2,2), (3,3))).partitionBy(new org.apache.spark.HashPartitioner(2))
```

3. 自定义分区

（1）实现numPartitions:Int，返回分区数

（2）实现getPartition(key:Any):Int，返回给定键的分区编号

（3）(不用实现)equals()，检查你的分区器对象是否和其他分区器实例相同

```java
import org.apache.spark.{Partitioner, SparkContext, SparkConf}

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
  def main(args: Array[String]): Unit = {
    val conf = new SparkConf().setAppName("WC").setMaster("local")
    val sc = new SparkContext(conf)

    val data = sc.parallelize(List("aa.2", "bb.2", "cc.3", "dd.5", "ee.5"))
    data.map((_,1))
      .partitionBy(new CustomerPartitioner(5))
      .keys
      .saveAsTextFile("D:\\output")
  }
}
```

## 数据读取与保存

```java

sc.testFile("./1.txt")
  .saveAsTextFile("hdfs://xxx.xxx.xxx.xxx:9000/test")

sc.makeRDD(List((1,1),(2,2)))
  .saveAsSequenceFile("hdfs://xxx.xxx.xxx.xxx:9000/test")

sc.makeRDD(List((1,1),(2,2)))
  .saveAsObjectFile("hdfs://xxx.xxx.xxx.xxx:9000/test")
  .objectFile[(Int, Int)]("hdfs://xxx.xxx.xxx.xxx:9000/p*")


sc.textFiles(path)
// 将path 里的所有文件内容读出，每一行相当于列表的一个元素

sc.wholeTextFiles(path)
// 返回的是[(key, val), (key, val)...]的形式，其中key是文件路径，val是文件内容
// [('.../1.txt', '1context'), ('.../2.txt', '2context')]
```



## 累加器

```java
// 统计文本中空行的数量
notice = sc.textFile("1.txt")
val blanklines = sc.accumulator(0)   // 累加器，初始化0

val tmp = notice.flatMap(line => {
	if (line == "") {
		blanklines += 1
	}
	line.split("")
}) 

tmp.count()
blanklines.values
```

## 自定义累加器

```java
import java.util

import org.apache.spark.util.AccumulatorV2
import org.apache.spark.{SparkConf, SparkContext}

import scala.collection.JavaConversions._

class LogAccumulator extends AccumulatorV2[String,java.util.Set[String]] {

  // 定义一个累加器的内存结构，用于保存带有字母的字符串
  private val _logArray: java.util.Set[String] = new java.util.HashSet[String]()

  // 重写方法检测累加器内部数据结构是否为空
  override def isZero: Boolean = {
    _logArray.isEmpty
  }

  override def copy(): AccumulatorV2[String, util.Set[String]] = {
    val newAcc = new LogAccumulator()
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
      case o: LogAccumulator => _logArray.addAll(o.value)
    }
  }

  // 输出value值
  override def value: util.Set[String] = {
    java.util.Collections.unmodifiableSet(_logArray)
  }
}


// 过滤带字母的
object LogAccumulator {
  def main(args: Array[String]): Unit ={
    val conf = new SparkConf().setAppName("CP").setMaster("local")
    val sc = new SparkContext(conf)

    val accum = new LogAccumulator
    sc.register(accum, "logAccum")
    val sum = sc.parallelize(Array("1", "2a", "3", "4b", "5", "6", "7cd", "8", "9"), 2)
      .filter(line => {
        val pattern = """^-?(\d+)"""
        val flag = line.matches(pattern)
        if (!flag) {
          accum.add(line)
        }
        flag
      }).map(_.toInt).reduce(_+_)

    println("sum : " + sum)                // sum : 32
    for (v <- accum.value) print(v + "")   // 7cd 4b 2a 
    println()
    sc.stop()
  }
}
```


## RDD 广播变量

1. 广播变量的出现时为了解决只读大对象分发的问题。

2. 如果不是广播变量，那么使用的变量会跟分区进行分发，效率比较低。

3. 广播变量的使用：
       
       (1)通过SparkContext.broadcast(对象)  来声明一个广播变量。
       
       (2)通过广播变量的变量名的value方法来获取广播变量的值。

       (3)变量一旦被定义为一个广播变量，那么这个变量只能读，不能修改

```java
// 定义一个广播变量
val a = Array(1,2,3,4,5)
val b = sc.broadcast(a)
// 还原一个广播变量
val c = b.value
```


使用广播变量的注意事项：

1. 能不能将一个 RDD 使用广播变量广播出去？

   不能，因为RDD是不存储数据的。可以将RDD的结果广播出去。

2. 广播变量只能在 Driver 端定义，不能在 Executor 端定义。

3. 在 Driver 端可以修改广播变量的值，在 Executor 端无法修改广播变量的值。

4. 广播变量允许程序员将一个只读的变量缓存在每台机器上，而不用在任务之间传递变量。

5. 广播变量可被用于有效地给每个节点一个大输入数据集的副本

6. Spark还尝试使用高效地广播算法来分发变量，进而减少通信的开销。



