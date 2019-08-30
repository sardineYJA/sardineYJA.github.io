---
layout: post
title: "MapReduce 编程"
date: 2019-06-15
description: "介绍一下MapReduce 编程"
tag: 大数据

---

# MapReduce项目环境搭建

创建Maven项目，xml依赖以及打包

```xml
<dependencies>
		<dependency>
			<groupId>junit</groupId>
			<artifactId>junit</artifactId>
			<version>RELEASE</version>
		</dependency>
		<dependency>
			<groupId>org.apache.logging.log4j</groupId>
			<artifactId>log4j-core</artifactId>
			<version>2.8.2</version>
		</dependency>
		<dependency>
			<groupId>org.apache.hadoop</groupId>
			<artifactId>hadoop-common</artifactId>
			<version>2.7.2</version>
		</dependency>
		<dependency>
			<groupId>org.apache.hadoop</groupId>
			<artifactId>hadoop-client</artifactId>
			<version>2.7.2</version>
		</dependency>
		<dependency>
			<groupId>org.apache.hadoop</groupId>
			<artifactId>hadoop-hdfs</artifactId>
			<version>2.7.2</version>
		</dependency>
</dependencies>

<build>
	<plugins>
		<plugin>
			<artifactId>maven-compiler-plugin</artifactId>
			<version>2.3.2</version>
			<configuration>
				<source>1.8</source>
				<target>1.8</target>
			</configuration>
		</plugin>
		<plugin>
			<artifactId>maven-assembly-plugin</artifactId>
			<configuration>
				<descriptorRefs>
					<descriptorRef>jar-with-dependencies</descriptorRef>
				</descriptorRefs>
				<archive>
					<manifest>
						<mainClass>mapreduceDemo.WordcountDriver</mainClass>
					</manifest>
				</archive>
			</configuration>
			<executions>
				<execution>
					<id>make-assembly</id>
					<phase>package</phase>
					<goals>
						<goal>single</goal>
					</goals>
				</execution>
			</executions>
		</plugin>
	</plugins>
 </build>

```

注意：`<mainClass>mapreduceDemo.WordcountDriver</mainClass>`换成自己的类（包名+类名）

创建src/main/resources/log4j.properties

```
log4j.rootLogger=INFO, stdout
log4j.appender.stdout=org.apache.log4j.ConsoleAppender
log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
log4j.appender.stdout.layout.ConversionPattern=%d %p [%c] - %m%n
log4j.appender.logfile=org.apache.log4j.FileAppender
log4j.appender.logfile.File=target/spring.log
log4j.appender.logfile.layout=org.apache.log4j.PatternLayout
log4j.appender.logfile.layout.ConversionPattern=%d %p [%c] - %m%n
```

```
log4j.rootCategory=WARN, console
log4j.appender.console=org.apache.log4j.ConsoleAppender
log4j.appender.console.target=System.err
log4j.appender.console.layout=org.apache.log4j.PatternLayout
log4j.appender.console.layout.ConversionPattern=%d{yy/MM/dd HH:mm:ss} %p %c{1}: %m%n
```


如果显示红叉，右键->maven->update project

打包：右键 -> Run as -> maven install，target目录下生成，使用不带依赖的jar

在hadoop测试：`hadoop jar wc.jar  XXXX.WordcountDriver /input /output`
> Exception in thread "main" java.lang.UnsupportedClassVersionError: mapreduceDemo/WordcountDriver : Unsupported major.minor version 52.0

原因：Maven打包的1.8版本，而测试系统jdk是1.7版本

解决：将项目Maven的jdk版本换成1.7，重新打包（建议重装1.8）

# Windows下IDEA本地测试

配置系统环境：新增HADOOP_HOME值为E:\hadoop-2.7.2，在Path增加%HADOOP_HOME%\bin

下载：https://github.com/sardineYJA/sardineYJA.github.io/tree/master/MySource

E:\hadoop-2.7.2\bin下增加：hadoop.dll和winutils.exe（尽量使用Windows下编译的hadoop）

C:\Windows\System32下增加：hadoop.dll（不需要此步骤）

## 问题

`public static void main(String[] args)`少写了static，IDEA的运行按钮不可用，打包到hadoop运行会报空指针错误

本地测试，为配置HADOOP_HOME，运行会空指针错误

> Exception in thread "main" java.lang.NullPointerException

配置，新增hadoop.dll和winutils.exe，本地测试还是报错

> Exception in thread "main" java.lang.UnsatisfiedLinkError: org.apache.hadoop.io.nativeio.NativeIO$Windows.createDirectoryWithMode0(Ljava/lang/String;I)V
at org.apache.hadoop.io.nativeio.NativeIO$Windows.createDirectoryWithMode0(Native Method)

原来hadoop.dll和winutils.exe(也需要相同的版本)，之前用2.6所以不行。windows下编译的hadoop，bin目录有winutils.exe之类的

强制加载hadoop.dll（不是必须此步骤）

```java
static {
	try {
		System.load("E:\\hadoop-2.7.2\\bin\\hadoop.dll");
		System.out.println("load is OK");
	} catch (UnsatisfiedLinkError e) {
		System.err.println("Native code library failed to load.\n" + e);
		System.exit(1);
	}
}
```


# InputFormat 数据输入

## FileInputFormat 切片

1. 简单地按照文件的内容长度进行切片
2. 切片大小默认等于Block大小
3. 切片时不考虑数据集整体，而是逐个针对每一个文件单独切片

## FileInputFormat实现类

### TextInputFormat

1. 每读取一行
2. 键是该行在整个文件中的起始字节偏移量：<LongWritable, Text>
3. 输入到Map的格式<LongWritable, Text, ..., ...>

### KeyValueTextInputFormat

1. 每读取一行，被（第一个）分隔符切分key, value
2. 驱动类设置分隔符：(默认tab)
```java
conf.set(KeyValueLineRecordReader.KEY_VALUE_SEPERATOR, "\t");
// 设置输入格式
job.setInputFormatClass(KeyValueTextInputFormat.class);
```
3. 输入的Map的格式<Text, Text, ..., ...>

### NLineInputFormat

1. 文件总行数/N = 切片数（向上取整）
2. 切片数就是MapTask数
3. <LongWritable, Text, ..., ...>(kv与TextInputFormat一样)
4. 驱动类设置：
```java
// 设置每个切片InputSplit中划分三条记录
NLineInputFormat.setNumLinesPerSplit(job, 3);
// 使用NLineInputFormat处理记录数
job.setInputFormatClass(NLineInputFormat.class);
```


### CombineTextInputFormat 切片
1. 将多个小文件从逻辑上规划到一个切片中
2. 先虚拟存储过程，分半
3. 再切片过程，合并

驱动类添加代码：
```java
// 如果不设置InputFormat，默认TextInputFormat.class
job.setInputFormatClass(CombineTextInputFormat.class);
// 虚拟存储切片最大值设置4M
CombineTextInputFormat.setMaxInputSplitSize(job, 4194304);
```


## 自定义InputFormat

1. 继承FileInputFormat
2. 改写RecordReader
3. 设置Driver
```java
// 设置输入的inputFormat
job.setInputFormatClass(WholeFileInputformat.class);
// 设置输出的outputFormat
job.setOutputFormatClass(SequenceFileOutputFormat.class);
```


# Partition分区

## 自定义Partition
1. 继承Partitioner，重写getPartition()
2. 驱动设置
```java
// 自定义分区CustomPartitioner
job.setPartitionerClass(CustomPartitioner.class)
// 根据自定义Partitioner的逻辑设置相应数量的ReduceTask
job.setNumReduceTasks(5);
```

# 排序

MapTask和ReduceTask默认按照字典排序

MapTask：结果暂存到环形缓冲区，当达到阈值后，对缓冲区的数据进行一次快排，并溢写到磁盘上，当数据处理完毕后对磁盘上所有文件进行归并排序。

ReduceTask：从每个MapTask上远程拷贝相应的数据文件，文件大小超过阈值则溢写到磁盘。磁盘文件数量达到阈值则归并排序合并成大文件。内存文件大小达到阈值则合并溢写到磁盘。所有数据拷贝完毕，对内存和磁盘所有数据进行一次归并排序。

1. 全排序：输出结果只有一个文件，内部有序
2. 部分排序：输出的每个文件内部有序
3. 分组排序：对key进行分组排序


## WritableComparable全排序

1. 实现WritableComparable接口重写compareTo()
2. Mapper输出的Key是自定义排序的类型
3. Reducer输出应该循环，避免相同情况

## WritableComparable区内排序

1. 基于全排序，增加自定义分区Partitioner即可


# Combiner合并

1. 意义在于对每一MapTask的输出进行局部汇总，减少网络传输量
2. Combiner的输出kv与Reducer的输入kv对应

## 方法一
1. 自定义Combiner继承Reducer，重写reduce()
2. 驱动类增加：
```java
job.setCombinerClass(CustomCombiner.class);
```

## 方法二
1. CustomReducer直接作为Combiner
2. 驱动类增加：（说明CustomCombiner其实和CustomReducer一样）
```java
job.setCombinerClass(CustomReducer.class);
```


## GroupingComparator 分组（辅助）排序

分组排序：对Reduce阶段的数据根据某一个或多个字段进行分组

1. 自定义继承WritableComparator
2. 重写compare()
3. 创建一个构造将比较对象的类传给父类
4. 驱动类
```java
// 设置reduce端的分组
job.setGroupingComparatorClass(OrderSortGroupingComparator.class);
```


## WritableComparable与WritableComparator区别

Writable：
接口，进行序列化；
重写：write(), readFields()；
MR执行位置：数据传输/方法间传输；

WritableComparable：
接口，进行序列化、排序，extends Writable, Comparable；
重写：write(), readFields(), compareTo()；
MR执行位置：map()后，缓冲区排序；

WritableComparator：
类，给key分组，将同组的Key传给reduce()执行，implements RawComparator, Configurable；
重写：compare()；
MR执行位置：reduce()执行前；

总结：
WritableComparable 是对Key排序；
WritableComparator 是对Key分组（在接收的key是bean对象时，想让一个或几个字段相同的key进入到同一个reduce）



# OutputFormat

## TextOutputFormat

默认TextOutputFormat

## SequenceFileOutputFormat

## 自定义OutputFormat
可以实现控制最终文件的输出路径和输出格式
1. 继承FileOutputFormat
2. 改写RecordWriter
3. 驱动类
```java
// 自定义输出格式
job.setOutputFormatClass(CustomOutputFormat.class);
```


## Reduce Join
缺点：Reduce断的处理压力过大，容易产生数据倾斜


## Map Join
使用于一张表很小，一张表很大的场景
在Map端缓存多张表，提前处理业务逻辑，增加Map端业务，减少Reduce端数据的压力，尽可能的减少数据倾斜


## 数据清洗
1. 在map()过滤
2. job.setNumReduceTasks(0);


## Mapper 和 Reducer

Mapper :
```java
  public void run(Context context) throws IOException, InterruptedException {
    setup(context);
    try {
      while (context.nextKeyValue()) {
        map(context.getCurrentKey(), context.getCurrentValue(), context);
      }
    } finally {
      cleanup(context);
    }
  }
```

Reducer :
```java
public void run(Context context) throws IOException, InterruptedException {
    setup(context);
    try {
      while (context.nextKey()) {
        reduce(context.getCurrentKey(), context.getValues(), context);
        // If a back up store is used, reset it
        Iterator<VALUEIN> iter = context.getValues().iterator();
        if(iter instanceof ReduceContext.ValueIterator) {
          ((ReduceContext.ValueIterator<VALUEIN>)iter).resetBackupStore();        
        }
      }
    } finally {
      cleanup(context);
    }
  }
```

基类Mapper类和Reducer类中都是只包含四个方法：setup方法，cleanup方法，run方法，map方法。

在run方法中调用了上面的三个方法：setup方法，map方法，cleanup方法。其中setup方法和cleanup方法默认是不做任何操作，且它们只被执行一次。


# 优化


## 数据倾斜

大量的相同key被partition分配到一个分区里，map /reduce程序执行时，reduce节点大部分执行完毕，但是有一个或者几个reduce节点运行很慢，导致整个程序的处理时间很长.

1. 增加jvm内存
2. 增加reduce
3. 自定义分区
4. 重写设计key
5. 使用Combiner合并
6. Join尽量使用Map Join

## 参数调优

mapred-default.xml

```xml
mapreduce.map.memory.mb
一个MapTask可使用的资源上限（单位:MB），默认为1024。如果MapTask实际使用的资源量超过该值，则会被强制杀死。
mapreduce.reduce.memory.mb
一个ReduceTask可使用的资源上限（单位:MB），默认为1024。如果ReduceTask实际使用的资源量超过该值，则会被强制杀死。
mapreduce.map.cpu.vcores	
每个MapTask可使用的最多cpu core数目，默认值: 1
mapreduce.reduce.cpu.vcores	
每个ReduceTask可使用的最多cpu core数目，默认值: 1
mapreduce.reduce.shuffle.parallelcopies	
每个Reduce去Map中取数据的并行数。默认值是5
mapreduce.reduce.shuffle.merge.percent	
Buffer中的数据达到多少比例开始写入磁盘。默认值0.66
mapreduce.reduce.shuffle.input.buffer.percent	
Buffer大小占Reduce可用内存的比例。默认值0.7
mapreduce.reduce.input.buffer.percent	
指定多少比例的内存用来存放Buffer中的数据，默认值是0.0

mapreduce.task.io.sort.mb   	
Shuffle的环形缓冲区大小，默认100m
mapreduce.map.sort.spill.percent   	
环形缓冲区溢出的阈值，默认80%

mapreduce.map.maxattempts	
每个Map Task最大重试次数，一旦重试参数超过该值，则认为Map Task运行失败，默认值：4。
mapreduce.reduce.maxattempts	
每个Reduce Task最大重试次数，一旦重试参数超过该值，则认为Map Task运行失败，默认值：4。
mapreduce.task.timeout	
Task超时时间，经常需要设置的一个参数，该参数表达的意思为：如果一个Task在一定时间内没有任何进入，即不会读取新的数据，也没有输出数据，则认为该Task处于Block状态，可能是卡住了，也许永远会卡住，为了防止因为用户程序永远Block住不退出，则强制设置了一个该超时时间（单位毫秒），默认是600000。如果你的程序对每条输入数据的处理时间过长（比如会访问数据库，通过网络拉取数据等），建议将该参数调大，该参数过小常出现的错误提示是“AttemptID:attempt_14267829456721_123456_m_000224_0 Timed out after 300 secsContainer killed by the ApplicationMaster.”。
```

yarn-default.xml

```xml
yarn.scheduler.minimum-allocation-mb	  	
给应用程序Container分配的最小内存，默认值：1024
yarn.scheduler.maximum-allocation-mb	  	
给应用程序Container分配的最大内存，默认值：8192
yarn.scheduler.minimum-allocation-vcores		
每个Container申请的最小CPU核数，默认值：1
yarn.scheduler.maximum-allocation-vcores		
每个Container申请的最大CPU核数，默认值：32
yarn.nodemanager.resource.memory-mb   	
给Containers分配的最大物理内存，默认值：8192
```




## hdfs小文件处理

小文件的优化方式：

（1）在数据采集的时候，就将小文件或小批数据合成大文件再上传HDFS。

（2）在业务处理之前，在HDFS上使用MapReduce程序对小文件进行合并。

（3）在MapReduce处理时，可采用CombineTextInputFormat提高效率。


1. Hadoop Archive：是一个高效地将小文件放入HDFS块中的文件存档工具，能将多个小文件打包成HAR文件，减少了NameNode的内存使用。
2. Sequence File：由一系列的二进制key/value组成，如果key为文件名，value为文件内容，则可以将大批小文件合并成一个大文件。
3. CombineFileInputFormat：是一种新的InputFormat，用于将多个文件合并成一个单独的Split，并且它会考虑数据的存储位置。
4. 开启JVM重用：一个Map运行在一个JVM上，开启重用该Map在JVM上运行完毕后，JVM继续运行其他Map，设置`mapreduce.job.jvm.numtasks`值在10-20之间。



# MapReduce 流程

InputFormat；
FileInputFormat；
TextInputFormat（默认）；
KeyValueTextInputFormat；
NLineInputFormat；
CombineTextInputFormat；

   ↓

RecordReader 自定义InputFormat

   ↓

Mapper: map(), setup(), cleanup()

   ↓

WirtableComparable 排序

   ↓

Combiner 合并
   
   ↓

GroupingComparator 分组

   ↓

Reducer: reduce(), setup(), cleanup()

   ↓

OutputFormat；
TextOutputFormat（默认）；
SequenceFileOutputFormat；

   ↓

RecordWriter 自定义OutputFormat

   ↓

Partitioner 分区


# 参考

[代码地址](https://github.com/sardineYJA/Hadoop-MapReduce)

