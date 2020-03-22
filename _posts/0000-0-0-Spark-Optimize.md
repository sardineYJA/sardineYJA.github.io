---
layout: post
title: "Spark 优化"
date: 2019-09-23
description: "Spark 优化"
tag: Spark

---


# 调优顺序

1. 分配资源、并行度、RDD架构与缓存

2. shuffle 调优

3. spark 算子调优

4. JVM 调优、 广播大变量、 Kryo 序列化、 fastutil 工具类



# 资源分配优化

## spark-submit

```sh
--driver-memory 100m \     配置driver的内存
--driver-cores 2 \         配置driver的cpu core数量

--num-executors 3 \        配置executor的数量
--executor-memory 2g \     配置每个executor的内存大小
--executor-cores 2 \       配置每个executor的cpu core数量
--total-executor-cores 6 \ 配置所有executor的cpu core总数量
```

## Standalone 集群和 Yarn 集群

在Standalone模式下:
- 每个节点使用的最大内存数：`SPARK_WORKER_INSTANCES * SPARK_WORKER_MEMORY`
- 每个节点的最大并发task数：`SPARK_WORKER_INSTANCES * SPARK_WORKER_CORES`

在YARN模式下：
- 集群task并行度：`SPARK_EXECUTOR_INSTANCES * SPARK_EXECUTOR_CORES`
- 集群内存总量：`(executor个数) * (SPARK_EXECUTOR_MEMORY + spark.yarn.executor.memoryOverhead) + (SPARK_DRIVER_MEMORY + spark.yarn.driver.memoryOverhead)`

重点强调：Spark对 Executor 和 Driver 额外添加堆内存大小
- Executor端：由spark.yarn.executor.memoryOverhead设置，默认值executorMemory * 0.07与384的最大值。
- Driver端：由spark.yarn.driver.memoryOverhead设置，默认值driverMemory * 0.07与384的最大值。



## Slave, Worker, executor

调整并行的executor的数量两种方式：

1. 每个worker内始终跑一个executor，但是调整单台slave上并行的worker的数量。
比如，`SPARK_WORKER_INSTANCES`可以设置每个slave的worker的数量，但是在改变这个参数的时候，比如改成2，
一定要相应设置`SPARK_WORKER_CORES`的值，让每个worker使用原有一半的core，这样才能让两个worker一同工作。

2. 每台slave内始终只部署一个worker，但是worker内部署多个executor。
我们是在YARN框架下采用这个调整来实现executor数量改变的，
一种典型办法是，一个host只跑一个worker，然后配置`spark.executor.cores`为host上CPU core的N分之一，
同时也设置`spark.executor.memory`为host上分配给Spark计算内存的N分之一，这样这个host上就能够启动N个executor。


## job 对CPU利用率很低

可以尝试减少每个executor占用CPU core的数量，增加并行的executor数量，同时配合增加分片，整体上增加了CPU的利用率，加快数据处理速度。


## executor的数量增加

分配到每个executor的内存数量减小，在内存里直接操作的越来越少，spill over到磁盘上的数据越来越多，自然性能就变差了。


## job 容易内存溢出

增大分片数量，从而减少了每片数据的规模，同时还减少并行的executor数量，这样相同的内存资源分配给数量更少的executor，相当于增加了每个task的内存分配。


## 数据量特别少，有大量的小文件生成

减少文件分片，没必要创建那么多task。这种情况，如果只是最原始的input比较小，一般都能被注意到；
但是，如果是在运算过程中，比如应用某个reduceBy或者某个filter以后，数据大量减少，这种低效情况就很少被留意到。


## 设置Spark Application的并行度

合理的并行度的设置，应该是要设置的足够大，大到可以完全合理的利用你的集群资源
```java
SparkConf conf = new SparkConf().set("spark.default.parallelism", "500") 
```

task数量，`至少`设置成与Spark application的总cpu core数量相同；官方是推荐，设置成spark application总cpu core数量的2-3倍，这样某些cpu的task先完成后可以继续进行其他task，就尽量让cpu core不要空闲。





# 内存优化

## Executor内存

executor的内存大小通过`spark.executor.memory`参数配置，默认是512M。
'spark.storage.memoryFraction'参数配置，默认是0.6。
即默认每个executor的内存是512M，其中512M*0.6=307.2M用于RDD缓存，
其余 512M*0.4=204.8用来给spark算子函数的运行使用的，存放函数中自己创建的对象。

```java
SparkConf conf = new SparkConf().set("spark.storage.memoryFraction", "0.3")
```


优化：

- 如果executor报OOM内存不足，需要考虑增大spark.executor.memory。

- 如果频繁Full GC，可能是executor中用于Task任务计算的内存不足:
需要考虑降低spark.storage.memoryFraction的比例，即减小用于缓存的内存大小，增大用于Task任务计算的内存大小。需要考虑优化RDD中的数据结构，减小数据占用的内存大小。

- 如果频繁Minor GC, 需要考虑增大年轻代内存的大小。



## executor堆外内存

如果spark作业处理的数据量特别特别大，几亿数据量；然后spark作业一运行，时不时的报错，shuffle file cannot find，executor、task lost，out of memory（内存溢出）；

可能是说executor的堆外内存不太够用，导致executor在运行的过程中，可能会内存溢出；然后可能导致后续的stage的task在运行的时候，可能要从一些executor中去拉取shuffle map output文件，但是executor可能已经挂掉了，关联的block manager也没有了；所以可能会报shuffle output file not found；resubmitting task；executor lost；spark作业彻底崩溃。


spark-submit脚本里面，去用--conf的方式，去添加配置；一定要注意！！！切记，不是在你的spark作业代码中，用new SparkConf().set()这种方式去设置，不要这样去设置，是没有用的！

```sh
--conf spark.yarn.executor.memoryOverhead=2048
```

默认情况下，这个堆外内存上限大概是300多M；通常项目中，真正处理大数据的时候，这里都会出现问题，导致spark作业反复崩溃，无法运行；此时就会去调节这个参数，到至少1G（1024M），甚至说2G、4G。通常这个参数调节上去以后，就会避免掉某些JVM OOM的异常问题，同时呢，会让整体spark作业的性能，得到较大的提升。


## 内存回收信息打印

spark-env.sh中设置，来获取每一次内存回收的信息。
```sh
SPARK_JAVA_OPTS="-verbose:gc -XX:+PrintGCDetails -XX:+PrintGCTimeStamps $ SPARK_JAVA_OPTS"
```

## 连接等待时长

处于 GC 过程中，所有的工作线程全部停止；相当于只要一旦进行 GC，executor停止工作，

executor优先从本地关联的BlockManager中获取某份数据，
如果本地block manager没有的话，那么会通过TransferService，去远程连接其他节点上executor的block manager去获取，
正好碰到那个exeuctor的JVM在垃圾回收。

此时就会没有响应，无法建立网络连接；会卡住；ok，spark默认的网络连接的超时时长，是60s；如果卡住60s都无法建立连接的话，那么就宣告失败了。碰到一种情况，偶尔，偶尔，偶尔！！！没有规律！！！某某file。一串file id。uuid（dsfsfd-2342vs--sdf--sdfsd）。not found。file lost。

这种情况下，很有可能是有那份数据的executor在jvm gc。所以拉取数据的时候，建立不了连接。然后超过默认60s以后，直接宣告失败。

报错几次，几次都拉取不到数据的话，可能会导致spark作业的崩溃。
也可能会导致DAGScheduler，反复提交几次stage。TaskScheduler，反复提交几次task。
大大延长spark作业的运行时间。


设置连接的超时时长：

spark-submit：`--conf spark.core.connection.ack.wait.timeout=300`

切记，不是在new SparkConf().set()这种方式来设置的。


## GC 时间限制

GC默认情况下有一个限制，默认是GC时间不能超过2%的CPU时间。
但是如果大量对象创建，就会导致大量的GC时间，从而出现`OutOfMemoryError: GC overhead limit exceeded`
可以通过设置`-XX:-UseGCOverheadLimit`关闭。



# 内存溢出优化

OOM 问题可能性：
1. map(flatMap, filter, mapPatitions等)执行内存溢出
2. shuffle(join, reduceByKey, repartirion等)后内存溢出


## map过程产生大量对象导致内存溢出：
    
这种溢出的原因是在单个map中产生了大量的对象导致的，例如：`rdd.map(x=>for(i <- 1 to 10000) yield i.toString)`，这个操作在rdd中，每个对象都产生了10000个对象，这肯定很容易产生内存溢出的问题。针对这种问题，在不增加内存的情况下，可以通过减少每个Task的大小，以便达到每个Task即使产生大量的对象Executor的内存也能够装得下。具体做法可以在会产生大量对象的map操作之前调用repartition方法，分区成更小的块传入map。例如：`rdd.repartition(10000).map(x=>for(i <- 1 to 10000) yield i.toString)`。

面对这种问题注意，不能使用rdd.coalesce方法，这个方法只能减少分区，不能增加分区，不会有shuffle的过程。


## 数据不平衡导致内存溢出：

数据不平衡除了有可能导致内存溢出外，也有可能导致性能的问题，解决方法和上面说的类似，就是调用repartition重新分区。


## coalesce调用导致内存溢出：

因为hdfs中不适合存小文件，所以Spark计算后如果产生的文件太小，我们会调用coalesce合并文件再存入hdfs中。但是这会导致一个问题，例如在coalesce之前有100个文件，这也意味着能够有100个Task，现在调用coalesce(10)，最后只产生10个文件，因为coalesce并不是shuffle操作，这意味着coalesce并不是按照我原本想的那样先执行100个Task，再将Task的执行结果合并成10个，而是从头到位只有10个Task在执行，原本100个文件是分开执行的，现在每个Task同时一次读取10个文件，使用的内存是原来的10倍，这导致了OOM。解决这个问题的方法是令程序按照我们想的先执行100个Task再将结果合并成10个文件，这个问题同样可以通过repartition解决，调用repartition(10)，因为这就有一个shuffle的过程，shuffle前后是两个Stage，一个100个分区，一个是10个分区，就能按照我们的想法执行。


## shuffle后内存溢出：

shuffle内存溢出的情况可以说都是shuffle后，单个文件过大导致的。在Spark中，join，reduceByKey这一类型的过程，都会有shuffle的过程，在shuffle的使用，需要传入一个partitioner，大部分Spark中的shuffle操作，默认的partitioner都是HashPatitioner，默认值是父RDD中最大的分区数,这个参数通过spark.default.parallelism控制(在spark-sql中用spark.sql.shuffle.partitions) ， spark.default.parallelism参数只对HashPartitioner有效，所以如果是别的Partitioner或者自己实现的Partitioner就不能使用spark.default.parallelism这个参数来控制shuffle的并发量了。如果是别的partitioner导致的shuffle内存溢出，就需要从partitioner的代码增加partitions的数量。


## standalone模式下资源分配不均匀导致内存溢出：

在standalone的模式下如果配置了--total-executor-cores 和 --executor-memory 这两个参数，但是没有配置--executor-cores这个参数的话，就有可能导致，每个Executor的memory是一样的，但是cores的数量不同，那么在cores数量多的Executor中，由于能够同时执行多个Task，就容易导致内存溢出的情况。这种情况的解决方法就是同时配置--executor-cores或者spark.executor.cores参数，确保Executor资源分配均匀。


## 在RDD中，共用对象能够减少OOM的情况：

这个比较特殊，这里说记录一下，遇到过一种情况，类似这样rdd.flatMap(x=>for(i <- 1 to 1000) yield ("key","value"))导致OOM，但是在同样的情况下，使用rdd.flatMap(x=>for(i <- 1 to 1000) yield "key"+"value")就不会有OOM的问题，这是因为每次("key","value")都产生一个Tuple对象，而"key"+"value"，不管多少个，都只有一个对象，指向常量池。具体测试如下：这个例子说明("key","value")和("key","value")在内存中是存在不同位置的,也就是存了两份,但是"key"+"value"虽然出现了两次,但是只存了一份,在同一个地址,这用到了JVM常量池的知识。于是乎,如果RDD中有大量的重复数据,或者Array中需要存大量重复数据的时候我们都可以将重复数据转化为String,能够有效的减少内存使用。

```java
scala > ("key", "value") eq ("key", "value")
res0: Boolean = false

scala > "key"+"value" eq "key"+"value"
res1: Boolean =  true
```




# RDD架构与缓存优化

## 缓存等级

默认存储在内存中。

persist方法或cache方法，在后面触发action时，RDD将会把数据以序列化的形式缓存在 JVM 的堆空间（默认），并供后面重用。
cache最终也是调用了persist方法，默认的存储级别都是仅在内存存储一份。

```java
def persist(): this.type = persist(StorageLevel.MEMORY_ONLY)
def cache(): this.type = persist()
```

![png](/images/posts/all/Spark持久化等级.png)

在存储级别的末尾加上`_2`来把持久化数据存为两份。


## RDD重复计算问题

HDFS -> RDD1 -> RDD2 -> RDD3
                     └> RDD4

获取 RDD3 : HDFS -> RDD1 -> RDD2 -> RDD3

获取 RDD4 : HDFS -> RDD1 -> RDD2 -> RDD4

默认情况下，多次对一个RDD执行算子，去获取不同的RDD；都会对这个RDD以及之前的父RDD，全部重新计算一次。
如上：HDFS -> RDD1 -> RDD2 就会多执行一次，时间翻倍。


## 优化：

1. 对于要多次计算和使用的公共RDD，一定要进行持久化

2. 持久化，是可以进行序列化的，减少内存空间，但是在获取数据的时候，需要反序列化，增大CUP处理时间

3. 如果序列化纯内存方式，还是导致OOM，只能考虑磁盘的方式，内存+磁盘

4. 为了数据的高可靠性，而且内存充足，可以使用双副本机制(存储级别末尾加上`_2`)


## 总结 persist 使用场景

* 某个步骤计算非常耗时，需要进行 persist 持久化

* 计算链条非常长，重新恢复要算很多步骤

* checkpoint所在的rdd要持久化persist，框架发现有checnkpoint，checkpoint时单独触发一个job，需要重算一遍，checkpoint前要持久化，写个rdd.cache或者rdd.persist，将结果保存起来，再写checkpoint操作，这样执行起来会非常快，不需要重新计算rdd链条了。checkpoint之前一定会进行persist

* shuffle之后需要persist，shuffle要进性网络传输，风险很大，数据丢失重来，恢复代价很大

* shuffle之前进行persist，框架默认将数据持久化到磁盘，这个是框架自动做的



## 为什么要 checkpoint

为了保证数据安全性，需要对运行出的中间结果进行 checkpoint，最好将结果 checkpoint 到 hdfs，便于集群所有节点进行访问；checkpoint 之前先进行 cache（persist），将数据放在缓存中。

## 什么时候 checkpoint

在发生 shuffle 之后做 checkpoint
```java
sc.setCheckpointDir("hdfs://XXX/ck")
rdd1.cache()
rdd1.checkpoint()
```





# 广播变量优化

task执行的算子中，使用了外部的变量，每个task都会获取一份变量的副本。
广播变量，变成每个节点的executor才一份副本。

广播变量，初始的时候，就在Drvier上有一份副本。
task在运行的时候，想要使用广播变量中的数据，此时首先会在自己本地的Executor对应的BlockManager中，尝试获取变量副本。
如果本地没有，那么就从Driver远程拉取变量副本，并保存在本地的BlockManager中。
也可能从其他节点的BlockManager上拉取变量副本，越近越好，网络传输速度大大增加。
此后这个executor上的task，都会直接使用本地的BlockManager中的副本。

![png](/images/posts/all/Spark广播变量.jpg)

如果task数量多，并且未使用广播变量，每个task都会获取一份变量的副本，增大网络传输的开销。
并且增加不必要的内存的消耗和占用，就导致了在进行RDD持久化到内存，也许就没法完全在内存中放下；
就只能写入磁盘，最后导致后续的操作在磁盘IO上消耗性能；
task在创建对象的时候，也许会发现堆内存放不下所有对象，也许就会导致频繁的GC。
GC的时候，一定是会导致工作线程停止，也就是导致Spark暂停工作那么一点时间。
频繁GC的话，对Spark作业的运行的速度会有相当可观的影响。




# 本地化时间优化

Spark在Driver上，对Application的每一个stage的task，进行分配之前，都会计算出每个task要计算的是哪个分片数据，RDD的某个partition；Spark的task分配算法，优先，会希望每个task正好分配到它要计算的数据所在的节点，这样的话，就不用在网络间传输数据；

但是可能task没有机会分配到它的数据所在的节点，可能那个节点的计算资源和计算能力都满了；所以这种时候，通常来说，Spark会等待一段时间，默认情况下是3s钟（不是绝对的，还有很多种情况，对不同的本地化级别，都会去等待），到最后，实在是等待不了了，就会选择一个比较差的本地化级别，比如说，将task分配到靠它要计算的数据所在节点，比较近的一个节点，然后进行计算。

但是对于第二种情况，通常来说，肯定是要发生数据传输，task会通过其所在节点的BlockManager来获取数据，BlockManager发现自己本地没有数据，会通过一个getRemote()方法，通过TransferService（网络数据传输组件）从数据所在节点的BlockManager中，获取数据，通过网络传输回task所在节点。

最好的，当然是task和数据在一个节点上，直接从本地executor的BlockManager中获取数据，纯内存，或者带一点磁盘IO；如果要通过网络传输数据的话，那么实在是，性能肯定会下降的，大量网络传输，以及磁盘IO，都是性能的杀手。


## 本地化级别

- PROCESS_LOCAL：进程本地化，代码和数据在`同一个进程中`(同一个executor中)；计算数据的task由executor执行，数据在executor的BlockManager中；性能最好

- NODE_LOCAL：节点本地化，代码和数据在`同一个节点中`；比如说，数据作为一个HDFS block块，就在节点上，而task在节点上某个executor中运行；或者是，数据和task在一个节点上的不同executor中；数据需要在进程间进行传输

- NO_PREF：对于task来说，数据从哪里获取都一样，没有好坏之分

- RACK_LOCAL：机架本地化，数据和task在一个机架的两个节点上；数据需要通过网络在节点之间进行传输

- ANY：数据和task可能在集群中的任何地方，而且不在一个机架中，性能最差



## 如何调优

观察日志，spark作业的运行日志，推荐大家在测试的时候，先用client模式，在本地就直接可以看到比较全的日志。

日志里面会显示，starting task...，PROCESS LOCAL、NODE LOCAL

观察大部分task的数据本地化级别

如果大多都是PROCESS_LOCAL，那就不用调节了

如果是发现，好多的级别都是NODE_LOCAL、ANY，那么最好就去调节一下数据本地化的等待时长

调节完，应该是要反复调节，每次调节完以后，再来运行，观察日志

看看大部分的task的本地化级别有没有提升；看看，整个spark作业的运行时间有没有缩短

但是因为大量的等待时长，spark作业的运行时间反而增加了，那就还是不要调节了

## 项目实践

一次电信数据项目中，LOCAL级别，花费大量时间。
直接在spark-submit参数中修改成0s。

```sh
bin/spark-submit \
--conf "spark.locality.wait=0s" \
```
spark.locality.wait=0。此时，排队的task会去其他excutor上去执行，不会排队。local级别，变成了跨网络去数据。如果是默认值3s，task会等3s，超时后再分配到其他的excutor上执行。


## 修改参数

默认情况下，下面3个的等待时长，都是跟上面那个是一样的，都是3s
```java
spark.locality.wait.process
spark.locality.wait.node
spark.locality.wait.rack
new SparkConf().set("spark.locality.wait", "10")
```





# 数据结构优化

## 检测对象内存消耗方法

Spark 默认使用Java序列化对象，虽然Java对象的访问速度更快，但其占用的空间通常比其内部的属性数据大2-5倍。
最好的检测对象内存消耗的办法就是创建RDD，然后放到cache里面去，然后在UI上面看storage的变化。



## 对象所占内存，优化数据结构

1. 使用对象数组以及原始类型（primitive type）数组以替代Java或者Scala集合类（collection class)。
fastutil 库为原始数据类型提供了非常方便的集合类，且兼容Java标准类库。

2. 尽可能地避免采用含有指针的嵌套数据结构来保存小对象。

3. 考虑采用数字ID或者枚举类型以便替代String类型的主键。

4. 如果内存少于32GB，设置JVM参数-XX:+UseCompressedOops以便将8字节指针修改成4字节。
与此同时，在Java7或者更高版本，设置JVM参数-XX:+UseCompressedStrings以便采用8比特来编码每一个ASCII字符。



## Kryo序列化

Spark内部是使用Java的序列化机制，ObjectOutputStream / ObjectInputStream，对象输入输出流机制，来进行序列化
好处在于处理起来比较方便；只需实现Serializable接口的，可序列化即可。
缺点在于效率不高，序列化的速度比较慢；序列化以后的数据，占用的内存空间相对还是比较大。

Kryo序列化机制，比默认的Java序列化机制，速度要快，序列化后的数据要更小，大概是Java序列化机制的1/10。
可以让网络传输的数据变少；在集群中耗费的内存资源大大减少。


Kryo序列化生效地方:

1. 算子函数中使用到的外部变量：使用Kryo以后，优化网络传输的性能，可以优化集群中内存的占用和消耗。

2. 持久化RDD（StorageLevel.MEMORY_ONLY_SER）：优化内存的占用和消耗，持久化RDD占用的内存越少，task执行的时候，创建的对象，就不至于频繁的占满内存，频繁发生GC。

3. shuffle：可以优化网络传输的性能。


Kryo序列化使用方法：一、设置属性；二、注册自定义类

```java
SparkConf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
SparkConf.registerKryoClasses(new Class[]{CustomClass.class})
```


## fastutil 集合类

fastutil是扩展了Java标准集合框架（Map、List、Set；HashMap、ArrayList、HashSet）的类库，提供了特殊类型的map、set、list和queue。

替代平时使用的JDK的原生的Map、List、Set，好处在于，fastutil集合类，可以减小内存的占用，并且在进行集合的遍历、根据索引（或者key）获取元素的值和设置元素的值的时候，提供更快的存取速度。


fastutil 使用场景：

1. 如果算子函数使用了外部变量；第一、可以使用Broadcast广播变量优化；第二、可以使用Kryo序列化类库，提升序列化性能和效率；第三、如果外部变量是某种比较大的集合，那么可以考虑使用fastutil改写外部变量，首先从源头上就减少内存的占用，通过广播变量进一步减少内存占用，再通过Kryo序列化类库进一步减少内存占用。

2. 在算子函数里，即task要执行的计算逻辑里面，如果有逻辑中，出现要创建比较大的Map、List等集合，可能会占用较大的内存空间，而且可能涉及到消耗性能的遍历、存取等集合操作；那么此时，可以考虑将这些集合类型使用fastutil类库重写，使用了fastutil集合类以后，就可以在一定程度上，减少task创建出来的集合类型的内存占用。避免executor内存频繁占满，频繁唤起GC，导致性能下降。


fastutil 的使用：

```xml
<dependency>
    <groupId>fastutil</groupId>
    <artifactId>fastutil</artifactId>
    <version>5.0.9</version>
</dependency>
```

例如：IntList 代替 List<Integer>；Int2IntMap 代替 Map 表示 key-value 映射 等等。





# 配置优化


## 开启推测机制

推测机制，如果集群中，某一台机器的几个task特别慢，推测机制会将任务分配到其他机器执行，最后Spark会选取最快的作为最终结果。

在spark-default.conf 中添加：`spark.speculation true`

推测机制与以下几个参数有关：
1. spark.speculation.interval 100：检测周期，单位毫秒；
2. spark.speculation.quantile 0.75：完成task的百分比时启动推测；
3. spark.speculation.multiplier 1.5：比其他的慢多少倍时启动推测。


## 在内存不足的使用，使用`rdd.persist(StorageLevel.MEMORY_AND_DISK_SER)`代替`rdd.cache()`

`rdd.cache()`和`rdd.persist(Storage.MEMORY_ONLY)`是等价的，在内存不足的时候rdd.cache()的数据会丢失，再次使用的时候会重算，而`rdd.persist(StorageLevel.MEMORY_AND_DISK_SER)`在内存不足的时候会存储在磁盘，避免重算，只是消耗点IO时间。


## 在spark使用hbase的时候，spark和hbase搭建在同一个集群：

在spark结合hbase的使用中，spark和hbase最好搭建在同一个集群上上，或者spark的集群节点能够覆盖hbase的所有节点。hbase中的数据存储在HFile中，通常单个HFile都会比较大，另外Spark在读取Hbase的数据的时候，不是按照一个HFile对应一个RDD的分区，而是一个region对应一个RDD分区。所以在Spark读取Hbase的数据时，通常单个RDD都会比较大，如果不是搭建在同一个集群，数据移动会耗费很多的时间。



# 算子优化

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

- RDD强调的是不可变对象，每个RDD都是不可变的，当调用RDD的map类型操作的时候，都是产生一个新的对象，这就导致了一个问题，如果对一个RDD调用大量的map类型操作的话，每个map操作会产生一个到多个RDD对象，这虽然不一定会导致内存溢出，但是会产生大量的中间数据，增加了gc操作。mapPartitons中将RDD大量的操作写在一起，避免产生大量的中间rdd对象。



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



# 参数优化

## spark.driver.memory (default 1g)
    
设置Driver的内存。在Spark程序中，SparkContext，DAGScheduler都是运行在Driver端的。对应rdd的Stage切分也是在Driver端运行，如果用户自己写的程序有过多的步骤，切分出过多的Stage，这部分信息消耗的是Driver的内存，这个时候就需要调大Driver的内存。

## spark.rdd.compress (default false)

这个参数在内存吃紧的时候，又需要persist数据有良好的性能，就可以设置这个参数为true，在使用`persist(StorageLevel.MEMORY_ONLY_SER)`的时候，就能够压缩内存中的rdd数据。减少内存消耗，就是在使用的时候会占用CPU的解压时间。

## spark.serializer (default org.apache.spark.serializer.JavaSerializer)

建议设置为 org.apache.spark.serializer.KryoSerializer，因为KryoSerializer比JavaSerializer快，但是有可能会有些Object会序列化失败，这个时候就需要显示的对序列化失败的类进行KryoSerializer的注册，这个时候要配置spark.kryo.registrator参数或者使用参照如下代码：

```java
val conf = new SparkConf().setMaster(...).setAppName(...)
conf.registerKryoClasses(Array(classOf[MyClass], classOf[MyClass2]))
val sc = new SparkContext(conf)
```

## spark.memory.storageFraction (default 0.5)

这个参数设置内存表示 Executor内存中 storage/(storage+execution)，虽然spark-1.6.0+的版本内存storage和execution的内存已经是可以互相借用的了，但是借用和赎回也是需要消耗性能的，所以如果明知道程序中storage是多是少就可以调节一下这个参数。

## spark.locality.wait (default 3s)

spark中有4中本地化执行level，PROCESS_LOCAL->NODE_LOCAL->RACK_LOCAL->ANY,一个task执行完，等待spark.locality.wait时间如果，第一次等待PROCESS的Task到达，如果没有，等待任务的等级下调到NODE再等待spark.locality.wait时间，依次类推，直到ANY。分布式系统是否能够很好的执行本地文件对性能的影响也是很大的。如果RDD的每个分区数据比较多，每个分区处理时间过长，就应该把 spark.locality.wait 适当调大一点，让Task能够有更多的时间等待本地数据。特别是在使用persist或者cache后，这两个操作过后，在本地机器调用内存中保存的数据效率会很高，但是如果需要跨机器传输内存中的数据，效率就会很低。

## spark.speculation (default false)

一个大的集群中，每个节点的性能会有差异，spark.speculation这个参数表示空闲的资源节点会不会尝试执行还在运行，并且运行时间过长的Task，避免单个节点运行速度过慢导致整个任务卡在一个节点上。这个参数最好设置为true。与之相配合可以一起设置的参数有spark.speculation.×开头的参数。参考中有文章详细说明这个参数。





# reference

https://blog.csdn.net/m0_37139189/article/details/100577326

https://blog.csdn.net/m0_37139189/article/details/100582549

https://blog.csdn.net/m0_37139189/article/details/100672783

https://www.cnblogs.com/qiuhong10/p/7762532.html

https://blog.csdn.net/yhb315279058/article/details/51035631


