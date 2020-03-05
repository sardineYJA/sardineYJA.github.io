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

DataFrame多了数据的结构信息，即schema。RDD是分布式的Java对象的集合。DataFrame是分布式的Row对象的集合。

DataFrame除了提供了比RDD更丰富的算子以外，更重要的特点是提升执行效率、减少数据读取以及执行计划的优化，比如filter下推、裁剪等。

DD强调的是不可变对象，每个RDD都是不可变的。DataFrame由于有类型信息所以是可变的

![png](/images/posts/all/RDD&DataFrame.png)



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


