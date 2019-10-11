---
layout: post
title: "Spark 优化3"
date: 2019-09-23
description: "Spark 优化"
tag: Spark

---

# shuffle 调优

(待补充)

# 算子调优

## mapPartitions 替换 map 提高性能

- 区别：
map 算子的操作，在一个分区中，数据会一条一条进入函数内部；
mapPartitions 则会把分区中所有数据都导入到函数执行。

- mapPartitions 操作的优点：
如果是 map，比如一个partition中有1万条数据，那么function要执行和计算1万次。但是，使用MapPartitions操作之后，一个task仅仅会执行一次function，function一次接收所有的partition数据。只要执行一次就可以了，性能比较高。
在 map 过程中需要频繁创建额外的对象(例如将rdd中的数据通过jdbc写入数据库，map需要为每个元素创建一个链接，而mapPartition为每个partition创建一个链接)，则mapPartitions效率比map高的多。

- mapPartitions 的缺点：
如果是map操作，一次function的执行就处理一条数据；如果内存不够用的情况下，比如处理了1千条数据了，那么这个时候内存不够了，那么就可以将已经处理完的1千条数据从内存里面垃圾回收掉，或者用其他方法，腾出空间来吧。
所以说普通的map操作通常不会导致内存的OOM异常。
但是MapPartitions操作，对于大量数据来说，比如甚至一个partition，100万数据，一次传入一个function以后，那么可能一下子内存不够，但是又没有办法去腾出内存空间来，可能就OOM，内存溢出。

- 适合用 mapPartitions 系列操作的场景：
就是说，数据量不是特别大的时候，都可以用这种MapPartitions系列操作，性能还是非常不错的，是有提升的。
但是也有过出问题的经验，MapPartitions只要一用，直接OOM，内存溢出，崩溃。
在项目中，先去估算一下RDD的数据量，以及每个partition的量，还有分配给每个executor的内存资源。
看看一下子内存容纳所有的partition数据，行不行。如果行，可以试一下，能跑通就好。性能肯定是有提升的。
但是试了以后，发现OOM了，那就放弃吧。

- mapPartitions 出现 OOM 的解决方法：
将数据切成较多的partition : `repartition(100).mapPartitions(xx)`；
设置较大的处理器内存 : `--executor-memory 8g`



## foreachPartition 代替 foreach 写入外部存储系统

- foreach：
task 为每个数据，都要去执行一次function函数。
每个数据都要去创建一个数据库连接。
每个数据发送一次 SQL 语句。
数据库连接的创建和销毁，多次发送SQL语句，都是非常非常消耗性能的。

- foreachPartition：
一次传入一个partition所有的数据。
创建或者获取一个数据库连接就可以。
只要向数据库发送一次SQL语句和多组参数即可。



## reduceByKey 进行本地聚合操作

reduceByKey，相较于普通的shuffle操作（比如groupByKey），它的一个特点，就是说，会进行map端的本地聚合。

举个例子：`rdd.groupByKey().mapValue(_.sum)`比`rdd.reduceByKey`的效率低，
原因如下，区别就是 reduceByKey 减少了shuffle的数据量。

![png](/images/posts/all/ReduceByKey.png)
![png](/images/posts/all/GroupByKey.png)

reduceByKey 优势：
- 在map端的数据量就变少了，减少磁盘IO，减少磁盘空间的占用
- 下一个stage，拉取数据的量变少了，减少网络的数据传输的性能消耗
- 在reduce端进行数据缓存的内存占用变少了
- reduce端，要进行聚合的数据量也变少了



## repartition 解决 spark sql 无法改变并行度问题

手动设置spark.default.parallelism参数，指定为cpu core总数的2-3倍。
```java
SparkConf conf = new SparkConf().set("spark.default.parallelism", "500") 
```

自己指定的并行度，只会在没有Spark SQL的stage中生效。在用Spark SQL的那个 stage 的并行度无法自己指定。
例如第一个stage，用了Spark SQL从 hive 表中查询数据，然后做transformation操作，接着做shuffle操作(groupByKey)；
下一个stage，在shuffle操作之后，做了一些transformation操作。
hive表，对应了一个hdfs文件，有20个block；
你自己设置了spark.default.parallelism参数为100。
第一个stage的并行度，是不受控制的，就只有20个task；第二个stage，才会变成自己设置的那个并行度，100。
导致第一个stage的速度特别慢，第二个stage非常快。


解决：
可以将你用Spark SQL查询出来的RDD，使用repartition算子，去重新进行分区，从repartition以后的RDD，再往后，并行度和task数量，就会按照设置的来了。

```java
DataFrame.javardd.repartition(partitionNum)
```


## filter 过后使用 coalesce

filter 过后 RDD 中的每个 partition 的数据量，可能都不太一样了。（原本每个partition的数据量可能是差不多的）
每个partition数据量变少，数据量不一样，会导致后面的每个task处理每个partition的时候，每个task要处理的数据量就不同。
就会导致有些task运行的速度很快，有些task运行的速度很慢（数据倾斜）。

减少分区
```java
rdd1.coalesce(10,true)
```




# 参考

https://blog.csdn.net/m0_37139189/article/details/100672783




