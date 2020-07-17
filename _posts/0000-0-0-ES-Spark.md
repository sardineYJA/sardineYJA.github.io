---
layout: post
title: "Spark 消费 kafka 写 ES"
date: 2020-07-16
description: "Elasticsearch"
tag: ELK

---

# Spark 消费 kafka

手动报错 kafka offset 到 ES

```xml
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-core_2.10</artifactId>
    <version>1.6.2</version>
</dependency>
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-sql_2.10</artifactId>
    <version>1.6.2</version>
</dependency>
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-streaming_2.10</artifactId>
    <version>1.6.2</version>
</dependency>
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>fastjson</artifactId>
    <version>1.2.47</version>
</dependency>
<dependency>
    <groupId>org.elasticsearch</groupId>
    <artifactId>elasticsearch-spark-20_2.10</artifactId>
    <version>6.1.1</version>
</dependency>
```

```java
val kafka_params = Map(
	"metadata.broker.list" -> "xxx.xxx.xxx.xxx:9092,xxx.xxx.xxx.xxx:9092"
	"group.id" -> "yangjingan"
	)
val topic = Set("topic_name")

// es 读取 offset
val es_read_conf = new Configuration()
es_read_conf.set("es.nodes", es_addr)
es_read_conf.set("es.port", es_port)
es_read_conf.set("es.net.http.auth.user", es_user)
es_read_conf.set("es.net.http.auth.pass", es_pass)
es_read_conf.set("es.index.read.missing.as.empty", "true")
es_read_conf.set("es.resource", "your_index/doc")
es_read_conf.set("es.query", "{\"query\":{your_dsl}}")

// es 更新 offset 
val es_update_offset_params = Map(
		"es.nodes" -> es_addr,
		"es.port" -> es_port,
		"es.net.http.auth.user" -> es_user,
		"es.net.http.auth.pass" -> es_pass,
		"es.index.auto.create" -> "true",
		"es.mapping.id" -> "id",           // 这里的id指后面传入的Map里的id，将其作为后面doc的_id
		"es.write.operation" -> "upsert", 
		// "es.update.script.inline" -> "ctx._source.offsets=10"  // 这样无法动态
	)


// 数据 写 ES
val es_write_params = Map(
		"es.nodes" -> es_addr,
		"es.port" -> es_port,
		"es.net.http.auth.user" -> es_user,
		"es.net.http.auth.pass" -> es_pass,
		"es.index.auto.create" -> "true"
	)
```

```java
val conf = new SparkConf().setMaster("local")
// 限流设置
conf.set("spark.streaming.stopGracefullyOnShutdown", "true");
conf.set("spark.streaming.backpressure.enabled", "true");
conf.set("spark.streaming.backpressure.initialRate", "1000");
conf.set("spark.streaming.kafka.maxRatePerPartition", "1000");

val sc = new SparkContext(conf)
sc.setLogLevel("WARN")
val ssc = new StreamingContext(sc, Seconds(5))
```

广播变量存储offset
```java
val id_offset_map = mutable.Map.empty[String, String]
val broadcast_map = broadcast.Broadcast[mutable.Map[String, String]] = sc.broadcast(id_offset_map)

// 从 ES 获取 offset
val offset_rdd = sc.newAPIHadoopRDD(
	es_read_conf,
	classOf[EsInputFormat[Text, MapWritable]],
	classOf[Text],
	classOf[MapWritable]
	)
if (offset_rdd.count == 0) {
	// 在ES初始创建保存offset的index
	EsSpark.saveToEs(sc.makeRDD(Seq(Map("topic"-> topic_name, "offset"->Map("0"->0)))), index_name, es_write_params)
} else if (offset_rdd.count >= 2) {
	sys.exit(0)
}


/***
{
	"topic": "your_topic",
	"offset": {
		"0": 100,    # 分区号和offset
		"1": 200
	}
}
***/
// 再次从 ES 获取 offset，并解析，保存到 广播变量
val offset_rdd2 = sc.newAPIHadoopRDD(
	es_read_conf,
	classOf[EsInputFormat[Text, MapWritable]],
	classOf[Text],
	classOf[MapWritable]
	)
offset_rdd2.foreach(rdd => {
	broadcast_map.value += ("id" -> rdd._1.toString)
	val value = rdd._2.keySet().iterator()
	while (value.hasNext()) {
		val a = value.next()
		if (a.toString == "offset") {
			broadcast_map.value += ("offset" -> rdd._2.get(a).toString)
		}
	}
})
val topic_id = broadcast_map.value.get("id").iterator.next()
val topic_offset = broadcast_map.value.get("offset").iterator.next()
```

格式化 offset

```java
val offset_json = JSON.parseObject(topic_offset.replace("=",":"))
var offset_list: List[(String, Int, Long)] = List()
for (p <- offset_json.size()) {
	offset_list = offset_list.+:((topic_name, p, offset_json.get(p).toString.toLong))
}  // List((topic_name, 0, 21L), (topic_name, 1, 45L))
```
```java
def setFromOffsets(list:List[(String, Int, Long)]): Map[TopicAndPartition, Long] = {
	var fromOffsets: Map[TopicAndPartition, Long] = Map()
	for (offset <- list) {
		val tp = TopicAndPartition(offset._1, offset._2)
		fromOffsets += (tp -> offset._3)
	}
	fromOffsets
} 
```

写 ES

```java
val fromOffsets = setFromOffsets(offset_list)
val messageHandler = (mam:MessageAndMetadata[String, String]) => (mam.topic, mam.message())
val messages: InputDString[(String, String)] = KafkaUtils.createDirectStream[String, String, StringDecoder, StringDecoder, (String,String)](
	ssc,
	kafka_params,
	fromOffsets,
	messageHandler
	)
messages.foreachRDD(batch => {    // 每batch_time 处理一次
	EsSpark.saveJsonToEs(batch, "spark-{index}/doc", es_write_params)
	// 更新offset
	val offsetsList = batch.asInstanceOf[HasOffsetRanges].offsetRanges
	offsetsList.foreach(x => {
		println(x.topic, x.partions, x.fromOffset, x.untilOffset)
		val update_script = "ctx._source['offset']['" + x.partions + "'] = " + x.untilOffset.toString
		val conf: Map[String, String] = es_update_offset_params + ("es.update.script.inline" -> update_script)
		val n = sc.makeRDD(Seq(Map("id" -> topic_id)))
		EsSpark.saveToEs(n, offset_index_name, conf)
	})
})

// EsSparkStreaming.saveJsonToEs(messages.map(_._2), "spark-{index}/doc", es_write_params)
```




# 问题

## 本地运行spark 读取 kafka

> Couldn't find leader offsets for Set([ndp-topic,0], [ndp-topic,1], [ndp-topic,2])

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
