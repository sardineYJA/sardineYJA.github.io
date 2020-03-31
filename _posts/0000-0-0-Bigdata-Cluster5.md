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

VM124      # 三台Worker
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

SPARK_MASTER_HOST=VM126           # VM126 作为 Master
SPARK_MASTER_PORT=7077
```

## 创建目录
```sh
hdfs dfs -mkdir /tmp/SparkJobLog
hdfs dfs -chmod 777 /tmp/SparkJobLog
```

## 启动

```sh
sbin/start-all.sh                   # 在Master那台启动
sbin/start-history-server.sh hdfs://mycluster/tmp/SparkJobLog # mycluster是hdfs-site.xml设置好的
```


## Spark JobHistory 配置目录

spark-env.sh
```sh
# 定期清除日志，生命周期5天，每一天会检查一下日志文件
SPARK_HISTORY_OPTS="-Dspark.history.fs.logDirectory=hdfs://mycluster/tmp/SparkJobLog
    -Dspark.history.ui.port=18080
    -Dspark.history.fs.cleaner.enabled=true
    -Dspark.history.fs.cleaner.maxAge=5d
    -Dspark.history.fs.cleaner.interval=1d"
```
 spark-defaults.conf
```sh
cp spark-defaults.conf.template spark-defaults.conf
vi spark-defaults.conf

spark.eventLog.enabled   true
spark.eventLog.dir       hdfs://mycluster/tmp/SparkJobLog
spark.eventLog.compress  true
```

启动就无需带目录：`sbin/start-history-server.sh`

浏览器查看：http://VM126:18080

测试一下：

```sh
bin/spark-submit \
--class org.apache.spark.examples.SparkPi \
--master spark://VM126:7077 \
--executor-memory 1G \
--total-executor-cores 2 \
examples/jars/spark-examples_2.11-2.4.5.jar 100
```

## 脚本

```sh
#!/bin/bash

################## 设置相关信息 ###################
root_dir=/home/yang/module/
spark_dir=${root_dir}spark-2.4.5-bin-hadoop2.7/
user_name=yang
 
master_VM=VM126           # 启动start-all.sh的VM
history_VM=VM126          # 启动jobhistory的VM

################## 下面尽量不要修改 ####################
# 启动
start_spark(){
    echo -e "\n++++++++++++++++++++ Spark集群启动 +++++++++++++++++++++"
    echo -e "Spark Master -----> ${master_VM}"
    ssh ${user_name}@$master_VM ${spark_dir}sbin/start-all.sh

    echo -e "\n=========> 启动 HistoryServer ============="
    echo -e "Spark HistoryServer -----> ${history_VM}"
    ssh ${user_name}@$history_VM ${spark_dir}sbin/start-history-server.sh

}

# 关闭
stop_spark(){
    echo -e "\n++++++++++++++++++++ Spark集群关闭 +++++++++++++++++++++"
    ssh ${user_name}@$master_VM ${spark_dir}sbin/stop-all.sh

    echo -e "\n=========> 关闭 HistoryServer ============="
    ssh ${user_name}@$history_VM ${spark_dir}sbin/stop-history-server.sh

}

# 获取输入参数个数，如果没有参数，直接退出
pcount=$#
if((pcount==0)); then
    echo no args, example : $0 start/stop;
    exit;

elif [[ "$1" == "start" ]]; then
    echo start;
    start_spark


elif [[ "$1" == "stop" ]]; then
    echo stop;
    stop_spark

else
    echo example : $0 start/stop;
    exit;
fi
```
