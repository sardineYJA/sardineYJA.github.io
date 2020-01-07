---
layout: post
title: "Spark Web Monitoring"
date: 2019-09-17
description: "Spark Web Monitoring"
tag: Spark

---


# Spark UI

官网：http://spark.apache.org/docs/latest/monitoring.html

spark服务本身有提供获取应用信息对方法，方便用户查看应用信息。

Spark服务提供对master，worker，driver，executor，Historyserver进程对运行展示。

对于应用（driver／executor）进程，主要提供 metric 和 rest api 对访问方式以展示运行状态。


## 设置

查看端口监听：netstat -tnlp |grep 18018

Apache 的 Spark Monitoring 将端口默认配置为18080和4040，而 CDH 将端口配置为18088和8088


Spark 的 Master 首页
打开：http://172.16.7.124:8080/

Spark 的 HistoryServer 的端口：spark-env.sh 设置 18080
在18080页面显示的任务：local模式是以local开头，yarn模式是以application开头
打开：http://172.16.7.124:18080

Spark 执行 bin/spark-shell 
打开：http://172.16.7.124:4040


spark-defaults.conf 配置以 spark.eventLog 开头

```sh
spark.eventLog.enabled             true
spark.eventLog.dir                 file:///home/yangja/sparklog
spark.eventLog.compress            true

spark.eventLog.compress                # 默认值为false 
# 设置history-server产生的日志文件是否使用压缩，true为使用，false为不使用。这个参数务可以成压缩哦，不然日志文件岁时间积累会过大
```

spark-env.sh 中的 SPARK_HISTORY_OPTS 配置参数以 spark.history 开头

```sh
spark.history.fs.update.interval       # 默认值10秒 
# 指定刷新日志的时间，更短的时间可以更快检测到新的任务以及任务执行情况，但过快会加重服务器负载

spark.history.ui.maxApplication        # 默认值intMaxValue 
# 指定UI上最多显示的作业的数目

spark.history.ui.port                  # 默认值18080 
# 指定history-server的网页UI端口号

spark.history.fs.cleaner.enabled       # 默认为false 
# 指定history-server的日志是否定时清除，true为定时清除，false为不清除。这个值一定设置成true啊，不然日志文件会越来越大。

spark.history.fs.cleaner.interval      # 默认值为1d 
# 指定history-server的日志检查间隔，默认每一天会检查一下日志文件

spark.history.fs.cleaner.maxAge        # 默认值为7d 
# 指定history-server日志生命周期，当检查到某个日志文件的生命周期为7d时，则会删除该日志文件

spark.history.retainedApplications 　  # 默认值：50 
# 在内存中保存Application历史记录的个数，如果超过这个值，旧的应用程序信息将被删除，当再次访问已被删除的应用信息时需要重新构建页面
```


## Jobs -> Stages -> Tasks

job :job是application的组成单位。 一个 job，就是由一个 rdd 的 action 触发的动作（生成一个 job）

stage : stage 是 job 的组成单位，就是说，一个 job 会被切分成 1 个或 1 个以上的 stage，然后各个 stage 会按照执行顺序依次执行。job 根据Spark的shuffle过程来切分 stage，如某stage有2个shuffle过程，它就被切分成3个stage

task : 一般来说，一个 rdd 有多少个 partition，就会有多少个 task，因为每一个 task 只是处理一个 partition 上的数据。，每一个 task 都会发送到集群中 worker 节点上运行

Spark会根据宽窄依赖区分stage，某个stage作为专门的计算，计算完成后，会等待其他的executor，然后再统一进行计算。


## Spark's REST API

利用接口可创建新的可视化监视工具

history server：`http://<server-url>:18080/api/v1`

running application：`http://localhost:4040/api/v1`

例子：calculate total shuffle statistics

```java
object SparkAppStats {
	case class SparkStage(name:String, shuffleWriteBytes:Long, memoryBytesSpilled:Long, diskBytesSpilled:Long)
	implicit val formats = DefaultFormats
	val url = "http://<host>:4040/api/v1/applications/<app-name>/stages"

	def main(args: Array[String]) {
		val json = fromURL(url).mkString
		val stages: List[SparkStage] = parse(json).extract[List[SparkStage]]
		println("stages count : " + stages.size)
		println("shuffleWriteBytes : " + stages.map(_.shuffleWriteBytes).sum)
		println("memoryBytesSpilled : " + stages.map(_.memoryBytesSpilled).sum)
		println("diskBytesSpilled : " + stages.map(_.diskBytesSpilled).sum)
	}
}
```

例子：calculate total time per job name

```java
val url = "http://<host>:4040/api/v1/applications/<app-name>/jobs"
case class SparkJob(jobId:Int, name:String, submissionTime:Date, completionTime:Option[Date], stageIds:List[Int]) {
	def getDurationMillis:Option[Long] = completionTime.map(_.getTime - submissionTime.getTime)
}

def main(args:Array[String]) {
	val json = fromURL(url).mkString
	parse(json).extract[List[SparkJob]]
			   .filter(j => j.getDurationMillis.isDefined)  // only completed jobs
			   .groupBy(_.name)
			   .mapValues(list => (list.map(_.getDurationMillis.get).sum, list.size))
			   .foreach {case(name, (time, count)) => println(s"TIME:$time\tAVG:${time/count}\tNAME:$name")}
}
```


## Metrics

Metric信息：
服务/进程通过 Metric 将自身运行信息展示出来。 spark 基于 Coda Hale Metrics Library 库展示。需要展示的信息通过配置 source 类，在运行时通过反射实例化并启动 source 进行收集。
然后通过配置 sink 类，将信息 sink 到对应的平台。

官网介绍如下：

Metrics: easy Java API for creating and updating metrics stored in memory

A "Sink" is an interface for viewing these metrics, at given intervals of ad-hoc

Avaliable sinks: Console, CSV, SLF4J, Servlet, JMX, Graphite, Ganglia


We use the Graphite Sink to send all metrics to Graphite

$SPARK_HOME/metrics.properties:
```
*.sink.graphite.class=org.apache.spark.metrics.sink.GraphiteSink
*.sink.graphite.host=<your graphite hostname>
*.sink.graphite.port=2003
*.sink.graphite.period=30
*.sink.graphite.unit=seconds
*.sink.graphite.prefix=<token>.<app-name>.<host-name>
```



# 参考

https://www.slideshare.net/TzachZohar/monitoring-spark-applications-59338130

https://www.jianshu.com/p/864c31b2d1db

https://blog.csdn.net/sinat_34763749/article/details/80944922

https://blog.csdn.net/keyuquan/article/details/79230105



