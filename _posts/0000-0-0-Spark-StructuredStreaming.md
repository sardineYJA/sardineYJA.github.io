---
layout: post
title: "Structured Streaming"
date: 2020-02-27
description: "Structured Streaming"
tag: Spark

---

## Structured Streaming

结构化流是一种基于Spark SQL引擎的可扩展且容错的流处理引擎。解决了Spark Streaming存在的代码升级，DAG图变化引起的任务失败，无法断点续传的问题

Structured Streaming将实时流抽象成一张无边界的表，输入的每一条数据当成输入表的一个新行，同时将流式计算的结果映射为另外一张表，完全以结构化的方式去操作流式数据。

输入的流数据是以batch为单位被处理，每个batch会触发一次流式计算，计算结果被更新到Result Table。

![png](/images/posts/all/StructuredStreaming结构化流式处理.png)


## 外部存储

Result Table的结果写出到外部存储介质有三种Output模式：

- Append模式：只有自上次触发后在Result Table表中附加的新行将被写入外部存储器。重点模式，一般使用它。

- Complete模式： 将整个更新表写入到外部存储。每次batch触发计算，整张Result Table的结果都会被写出到外部存储介质。

- Update模式：只有自上次触发后在Result Table表中更新的行将被写入外部存储器。注意，这与完全模式不同，因为此模式不输出未更改的行。



## StructuredStreaming & SparkStreaming 区别

- StructuredStreaming使用的数据类型是DataFrame和Dataset。SparkStreaming是DStream(RDD序列)。

- StructedStreaming是基于Event time（事件时间）聚合，而SparkStreaming是基于Process time （处理时间）。事件时间是嵌入在数据本身中的时间，即事件发生时间，而处理时间是指Spark接收数据的时间。


## 测试

待补充

# reference

https://blog.csdn.net/MrZhangBaby/article/details/88352179