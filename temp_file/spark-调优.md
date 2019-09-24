

## job 对CPU利用率很低

可以尝试减少每个executor占用CPU core的数量，增加并行的executor数量，同时配合增加分片，整体上增加了CPU的利用率，加快数据处理速度。


## job 容易内存溢出

增大分片数量，从而减少了每片数据的规模，同时还减少并行的executor数量，这样相同的内存资源分配给数量更少的executor，相当于增加了每个task的内存分配。


## 数据量特别少，有大量的小文件生成

减少文件分片，没必要创建那么多task。这种情况，如果只是最原始的input比较小，一般都能被注意到；
但是，如果是在运算过程中，比如应用某个reduceBy或者某个filter以后，数据大量减少，这种低效情况就很少被留意到。


## executor的数量增加

分配到每个executor的内存数量减小，在内存里直接操作的越来越少，spill over到磁盘上的数据越来越多，自然性能就变差了。


## Slave, Worker, executor

调整并行的executor的数量两种方式：

1. 每个worker内始终跑一个executor，但是调整单台slave上并行的worker的数量。
比如，SPARK_WORKER_INSTANCES可以设置每个slave的worker的数量，但是在改变这个参数的时候，比如改成2，
一定要相应设置SPARK_WORKER_CORES的值，让每个worker使用原有一半的core，这样才能让两个worker一同工作。

2. 每台slave内始终只部署一个worker，但是worker内部署多个executor。
我们是在YARN框架下采用这个调整来实现executor数量改变的，
一种典型办法是，一个host只跑一个worker，然后配置spark.executor.cores为host上CPU core的N分之一，
同时也设置spark.executor.memory为host上分配给Spark计算内存的N分之一，这样这个host上就能够启动N个executor。


## Standalone集群 和 Yarn集群

在Standalone模式下:
- 每个节点使用的最大内存数：`SPARK_WORKER_INSTANCES * SPARK_WORKER_MEMORY`
- 每个节点的最大并发task数：`SPARK_WORKER_INSTANCES * SPARK_WORKER_CORES`

在YARN模式下：
- 集群task并行度：`SPARK_EXECUTOR_INSTANCES * SPARK_EXECUTOR_CORES`
- 集群内存总量：`(executor个数) * (SPARK_EXECUTOR_MEMORY + spark.yarn.executor.memoryOverhead) + (SPARK_DRIVER_MEMORY + spark.yarn.driver.memoryOverhead)`

重点强调：Spark对 Executor 和 Driver 额外添加堆内存大小
- Executor端：由spark.yarn.executor.memoryOverhead设置，默认值executorMemory * 0.07与384的最大值。
- Driver端：由spark.yarn.driver.memoryOverhead设置，默认值driverMemory * 0.07与384的最大值。



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

2. 持久化RDD：优化内存的占用和消耗，持久化RDD占用的内存越少，task执行的时候，创建的对象，就不至于频繁的占满内存，频繁发生GC。

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


## 内存回收信息打印

spark-env.sh中设置，来获取每一次内存回收的信息。
```sh
SPARK_JAVA_OPTS="-verbose:gc -XX:+PrintGCDetails -XX:+PrintGCTimeStamps $ SPARK_JAVA_OPTS"
```


## GC 时间

GC默认情况下有一个限制，默认是GC时间不能超过2%的CPU时间。
但是如果大量对象创建，就会导致大量的GC时间，从而出现`OutOfMemoryError: GC overhead limit exceeded`
可以通过设置`-XX:-UseGCOverheadLimit`关闭。


## Executor内存

executor的内存大小通过`spark.executor.memory`参数配置，默认是512M。
'spark.storage.memoryFraction'参数配置，默认是0.6。
即默认每个executor的内存是512M，其中512M*0.6=307.2M用于RDD缓存，其余 512M*0.4=204.8用于Task任务计算。


优化：

- 如果executor报OOM内存不足，需要考虑增大spark.executor.memory。

- 如果频繁Full GC，可能是executor中用于Task任务计算的内存不足:
需要考虑降低spark.storage.memoryFraction的比例，即减小用于缓存的内存大小，增大用于Task任务计算的内存大小(对象创建的空间)。
需要考虑优化RDD中的数据结构，减小数据占用的内存大小。

- 如果频繁Minor GC, 需要考虑增大年轻代内存的大小。

```sh
bin/spark-submit \
--executor-memory 24G \
--total-executor-cores 4 \
--driver-cores 2 \
--driver-memory 8g \
```


## 开启推测机制

推测机制，如果集群中，某一台机器的几个task特别慢，推测机制会将任务分配到其他机器执行，最后Spark会选取最快的作为最终结果。

在spark-default.conf 中添加：`spark.speculation true`

推测机制与以下几个参数有关：
1. spark.speculation.interval 100：检测周期，单位毫秒；
2. spark.speculation.quantile 0.75：完成task的百分比时启动推测；
3. spark.speculation.multiplier 1.5：比其他的慢多少倍时启动推测。



# 参考

https://blog.csdn.net/m0_37139189/article/details/100577326




