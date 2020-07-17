---
layout: post
title: "Spark 消费 kafka 写 ES"
date: 2020-07-16
description: "Elasticsearch"
tag: ELK

---


# Spark 消费 kafka


## 本地运行spark 读取 kafka

Couldn't find leader offsets for Set([ndp-topic,0], [ndp-topic,1], [ndp-topic,2])

解决方案：要在kafka集群的hosts要配到spark的Driver的hosts里面去（所以修改windown的hosts，C:\Windows\System32\drivers\etc）



## SparkContext 序列化问题

Spark程序中的map、filter等算子内部引用了类成员函数或变量导致需要该类所有成员都需要支持序列化，又由于该类某些成员变量不支持序列化，最终引发Task无法序列化问题 。

> org.apache.spark.SparkException: Task not serializable

解决：将 sc（SparkContext）和 sparkConf（SparkConf）两个成员变量使用“@transent”标注



## auto.offset.reset 消费进度

Kafka 单独写 consumer：

- earliest：自动将偏移重置为最早的偏移量

- latest：自动将偏移量重置为最新的偏移量（默认）

- none：如果consumer group没有发现先前的偏移量，则向consumer抛出异常


SparkStreaming：

- smallest：简单理解为从头开始消费，其实等价于上面的 earliest

- largest：简单理解为从最新的开始消费，其实等价于上面的 latest



## Spark ES 参数

```sh

es.nodes                 ES节点
es.port                  ES端口
es.index.auto.create     true 自动创建index
es.resource              index_name/doc 具体索引

es.batch.size.bytes               es批量API的批量写入的大小（以字节为单位）
es.batch.write.refresh            批量更新完成后是否调用索引刷新
es.read.field.as.array.include    读es的时候，指定将哪些字段作为数组类型
es.index.read.missing.as.empty    true 允许读到ES空值
es.nodes.wan.only                 false，在此模式下，连接器禁用发现，并且所有操作通过声明的es.nodes连接（设为false即不用域名访问）

es.mapping.id             id   分配id，如果不指定此参数将随机生成
es.write.operation        upsert
es.update.script.inline   ctx._source.location = params.location
es.update.script.params   location:100

es.net.ssl                             true
es.net.ssl.keystore.location           D:\\node-0-keystore.jks 
es.net.ssl.keystore.pass               changeit
es.net.ssl.keystore.type               JKS
es.net.ssl.truststore.location         D:\\truststore.jk(file:///全路径)
es.net.ssl.truststore.pass             changeit
es.net.ssl.cert.allow.self.signed      false
es.net.ssl.protocol                    TLSv1.2       官网上是TLS,必须带版本号，否则报错

es.net.http.auth.user      admin    // 访问es的用户名
es.net.http.auth.pass      admin    // 访问es的密码
```


## Spark Writing to dynamic/multi-resources

参考：https://www.elastic.co/guide/en/elasticsearch/hadoop/6.1/spark.html

```sh
# stringDStream 数据中都有 index 字段
EsSparkStreaming.saveJsonToEs(stringDStream,"spark-{index}/doc", map)
```




## sparkStreaming消费kafka消息的频率设置参数

控制sparkstreaming启动时，积压问题并设置背压机制，自适应批次的record变化，来控制任务的堆积：

```java
// 1.确保在kill任务时，能够处理完最后一批数据，再关闭程序，不会发生强制kill导致数据处理中断，没处理完的数据丢失
sparkConf.set("spark.streaming.stopGracefullyOnShutdown", "true");

// 2.开启后spark自动根据系统负载选择最优消费速率
sparkConf.set("spark.streaming.backpressure.enabled", "true");

// 3.开启的情况下，限制第一次批处理应该消费的数据，因为程序冷启动 队列里面有大量积压，防止第一次全部读取，造成系统阻塞
sparkConf.set("spark.streaming.backpressure.initialRate", "1000");

// 4.限制每秒每个消费线程读取每个kafka分区最大的数据量
sparkConf.set("spark.streaming.kafka.maxRatePerPartition", "1000");
```

- 只有（4）激活的时候，每次消费的最大数据量，就是设置的数据量，如果不足这个数，就有多少读多少
- 只有（2）+（4）激活的时候，每次消费读取的数量最大==设置的值，最小是spark根据系统负载自动推断的值，消费的数据量会在这两个范围之内变化根据系统情况，但第一次启动会有多少读多少数据。
- 开启（2）+（3）+（4）同时激活的时候，跟上一个消费情况基本一样，但第一次消费会得到限制。
