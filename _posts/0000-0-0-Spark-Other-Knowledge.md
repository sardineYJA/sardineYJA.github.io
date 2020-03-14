---
layout: post
title: "Spark 补充知识点"
date: 2019-09-18
description: "Spark 知识点"
tag: Spark

---

## Spark 集群角色

![png](/images/posts/all/spark集群角色.png)


从物理部署层面上来看，Spark主要分为两种类型的节点，Master节点和Worker节点

- Master节点主要运行集群管理器的中心化部分，所承载的作用是分配Application到Worker节点，维护Worker节点，Driver，Application的状态

- Worker节点负责具体的业务运行

从Spark程序运行的层面来看，Spark主要分为驱动器节点和执行器节点



## RDD与DataFrame区别 

左侧的RDD[Person]虽然以Person为类型参数，但Spark框架本身不了解Person类的内部结构。

右侧的DataFrame却提供了详细的结构信息，使得Spark SQL可以清楚地知道该数据集中包含哪些列，每列的名称和类型各是什么。

DataFrame多了数据的结构信息，即schema。RDD是分布式的Java对象的集合。
DataFrame是分布式的Row对象的集合。

DataFrame除了提供了比RDD更丰富的算子以外，更重要的特点是提升执行效率、减少数据读取以及执行计划的优化，比如filter下推、裁剪等。

DD强调的是不可变对象，每个RDD都是不可变的。DataFrame由于有类型信息所以是可变的

![png](/images/posts/all/RDD&DataFrame.png)


## DataFrame、DataSet

DataFrame只知道字段，但不知字段类型，所以在执行这些操作的时候是没办法在编译的时候检查是否类型失败的，比如你可以对一个String进行减法操作，在执行的时候才报错，而DataSet不仅仅知道字段，而且知道字段类型。


## RDD、DataFrame、DataSet

- RDD (Spark1.0) —> Dataframe(Spark1.3) —> Dataset(Spark1.6)

- RDD、DataFrame、Dataset全都是spark平台下的分布式弹性数据集，都有惰性机制

- 在对DataFrame和Dataset进行操作许多操作需要`import spark.implicits._`




## 计算抽象

- Application
用户编写的Spark程序，完成一个计算任务的处理。它是由一个Driver程序和一组运行于Spark集群上的Executor组成。

- Job
用户程序中，每次调用Action时，逻辑上会生成一个Job，一个Job包含了多个Stage。

- Stage
包括两类：ShuffleMapStage和ResultStage，如果用户程序中调用了需要进行Shuffle计算的Operator，如groupByKey等，就会以Shuffle为边界分成ShuffleMapStage和ResultStage。

- TaskSet
基于Stage可以直接映射为TaskSet，一个TaskSet封装了一次需要运算的、具有相同处理逻辑的Task，这些Task可以并行计算，粗粒度的调度是以TaskSet为单位的。

- Task
是在物理节点上运行的基本单位，Task包含两类：ShuffleMapTask和ResultTask，分别对应于Stage中ShuffleMapStage和ResultStage中的一个执行基本单元。




## Spark与Hadoop的shuffle的异同

- 一个落盘，一个不落盘，spark就是为了解决mr落盘导致效率低下的问题而产生的
- MapReduce 只能从一个 Map Stage shuffle 数据，Spark 可以从多个 Map Stages shuffle 数据

Hadoop Shuffle过程总共会发生3次排序行为：
- map阶段，由环形缓冲区溢出到磁盘上时，落地磁盘的文件会按照key进行分区和排序(快速排序)
- 在map阶段，对溢出的文件进行combiner合并过程中，需要对溢出的小文件进行排序、合并(归并排序)
- 在reduce阶段，reducetask将不同maptask端文件拉去到同一个reduce分区后，对文件进行合并(归并排序)

Spark中Sorted-Based Shuffle：
- 在Mapper端是进行排序的(partition的排序和每个partition内部元素进行排序)
- 在Reducer端没有进行排序


Shuffle Copy的方式：
- Hadoop MapReduce采用框架jetty的方式
- Spark HashShuffle采用netty或者是socket流


## Spark 内存架构


![png](/images/posts/all/Spark内存架构1.6之前.png)

1.6版本之前：

- Spark 应用中代码使用内存：编写的程序中使用到的内存 => 20%
- Spark 数据缓存的时候用到的内存：60% => spark.storage.memoryFraction
- Spark shuffle 过程中使用到的内存：20% => spark.shuffle.memoryFraction


![png](/images/posts/all/Spark内存架构1.6之后.png)

1.6版本之后：

- Storage Memory：主要用于存储 spark 的 cache 数据
- Executor Memory：主要用于存放 Shuffle、Join、Sort、Aggregation 等计算过程中的临时数据
- User Memory：主要用于存储 RDD 转换操作所需要的数据
- Reserved Memory：系统预留内存，会用来存储Spark内部对象

总结：
- Reserved Memory: 固定300M，不能进行修改
- User Memory: 用户代码中使用到的内存, 默认占比：1 - spark.memory.fraction
- spark.memory.fraction:0.75 包括：缓存(Storage Memory)和shuffle(Execution Memory)


优化建议：
如果spark应用缓存比较多，shuffle比较少，调高缓存的内存占比；反之亦然


## Spark 应用程序执行过程

1. 用户Client端Submit作业，Driver运行创建SparkContext

2. SparkContext向资源管理器（Standalone, yarn, Mesos）注册申请资源

3. 资源分配给Executor

4. SparkContext构建DAG图，并分解成Stage，将Taskset发送给Task Scheduler

5. Executor向SparkContext申请Task，Task Scheduler将Task发送给Executor，SparkContext将程序代码发送给Executor

6. Task在Executor上运行，运行完毕后释放资源


## Driver 作用

- 一个Spark作业运行时包含一个Driver进程
- 程序入口点
- 创建SparkContext
- 向集群申请资源
- 解析和调度作业



## hadoop和spark的shuffle过程

hadoop：map端保存分片数据，通过网络收集到reduce端。
spark：spark的shuffle是在DAGSchedular划分Stage的时候产生的，TaskSchedule要分发Stage到各个worker的executor，减少shuffle可以提高性能。


## HashParitioner

分区原理：对于给定的key，计算其hashCode。
弊端是数据不均匀，容易导致数据倾斜。

## RangePartitioner

尽量保证每个分区中数据量的均匀，而且分区与分区之间是有序的，即一个分区中的元素肯定都是比另一个分区内的元素小或者大。
分区内的元素是不能保证顺序的。
简单的说就是将一定范围内的数映射到某一个分区内。


# 案例

## WordCount:
```java
sc.textFile("/1.txt").flatMap(_.split(" ")).filter(!_.isEmpty).map((_,1)).reduceByKey(_+_).sortBy(_._2, false).saveAsTextFile("/2.txt")
```

## 数量：
```java
sc.textFile("/1.txt").count
// 或者
hdfs dfs -cat /1.txt | wc -l
```


给定a、b两个文件，各存放50亿个url，每个url各占64字节，内存限制是4G，让你找出a、b文件共同的url：

1. 大小约为5G×64=320G
2. 对每个url求取hash(url)%1000，每个小文件的大约为300M
3. 将小文件的url存储到hash_set中
4. 再次遍历小文件的每个url，如在刚才构建的hash_set中就是共同的url



1G大小文件，里面每一行是一个词，词的大小不超过16字节，内存限制大小是1M，返回频数最高的100个词：

1. 顺序读文件中，对于每个词x，取hash(x)%5000
2. 对每个小文件，统计词频，并取频率最大的100个词，存入文件得到了5000个文件
3. 5000个文件进行归并排序，取出前100


# reference

https://www.jianshu.com/p/7a8fca3838a4

