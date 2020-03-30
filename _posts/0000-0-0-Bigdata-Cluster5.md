---
layout: post
title: "快速搭建5 —— Spark分析数据"
date: 2020-03-30
description: "Bigdata"
tag: Bigdata

---


# Spark

## 配置

解压spark-2.4.5-bin-hadoop2.7.tgz

## slaves

```sh
cp slaves.template slaves
vi slaves

VM124
VM125
VM126
```

## spark-env.sh

```sh
cp spark-env.sh.template spark-env.sh
vi spark-env.sh

export JAVA_HOME=/home/yang/module/jdk1.8.0_241

export SPARK_PID_DIR=/home/yang/module/spark-2.4.5-bin-hadoop2.7/pids

export HADOOP_CONF_DIR=/home/yang/module/hadoop-2.7.2/etc/hadoop
export SPARK_CONF_DIR=/home/yang/module/spark-2.4.5-bin-hadoop2.7/conf

SPARK_MASTER_HOST=VM124
SPARK_MASTER_PORT=7077

# 定期清除日志，生命周期5天，每一天会检查一下日志文件
SPARK_HISTORY_OPTS="-Dspark.history.fs.logDirectory=hdfs://VM124:9000/tmp/SparkJobLog 
    -Dspark.history.ui.port=18080
    -Dspark.history.fs.cleaner.enabled=true
    -Dspark.history.fs.cleaner.maxAge=5d
    -Dspark.history.fs.cleaner.interval=1d"


```

## spark-defaults.conf

```sh
cp spark-defaults.conf.template spark-defaults.conf
vi spark-defaults.conf

spark.eventLog.enabled   true
spark.eventLog.dir       hdfs://VM124:9000/tmp/SparkJobLog # 或 file:///home/yang/sparklog
spark.yarn.historyServer.address http://VM124:18080
```

创建目录
```sh
hdfs dfs -mkdir /tmp/SparkJobLog
hdfs dfs -chmod 777 /tmp/SparkJobLog
```

## 同步其他节点


## 启动

```sh
sbin/start-all.sh
sbin/start-history-server.sh
```

浏览器查看：http://VM124:4000




## hadoop hdfs-site.xml 关闭权限验证

```xml
<property>
    <name>dfs.permissions</name>
    <value>false</value>
</property>
```

## hadoop yarn-site.xml

```xml
<property>
    <name>yarn.log-aggregation-enable</name>
    <value>true</value>
</property>
<property>
    <name>yarn.log.server.url</name>
    <value>http://VM124:19888/jobhistory/logs/</value>
</property>
```




```sh
spark.master             spark://master01:7077
spark.eventLog.enabled   true
spark.eventLog.dir       hdfs://VM124:9000/tmp/SparkJobLog
spark.eventLog.compress  true
```

```sh
export HADOOP_CONF_DIR=/home/yang/module/hadoop-2.7.2/etc/hadoop
export SPARK_CONF_DIR=/home/yang/module/spark-2.4.5-bin-hadoop2.7/conf

export SPARK_HISTORY_OPTS="-Dspark.history.ui.port=4000
-Dspark.history.retainedApplications=3
-Dspark.history.fs.logDirectory=hdfs://VM124:9000/tmp/SparkJobLog"
```

bin/spark-submit \
--class org.apache.spark.examples.SparkPi \
--master spark://VM124:7077 \
--executor-memory 1G \
--total-executor-cores 2 \
examples/jars/spark-exam 100

