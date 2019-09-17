---
layout: post
title: "集群关闭问题"
date: 2019-09-17
description: "集群关闭问题"
tag: 大数据

---

# Spark 关闭问题

停止spark : sbin/stop-all.sh

>no org.apache.spark.deploy.worker.Worker to stop
 no org.apache.spark.deploy.master.Master to stop


因为Spark程序在启动后会在 /tmp 创建临时文件，系统每隔一段时间就会清除 /tmp 目录下的内容

```
/tmp/spark-你的用户名-org.apache.spark.deploy.master.Master-1.pid 
/tmp/spark-你的用户名-org.apache.spark.deploy.worker.Worker-1.pid
/tmp/spark-你的用户名-org.apache.spark.deploy.history.HistoryServer-1.pid
```

关闭的时候会去寻找是否还有这类的文件，若没有则会报以上的错误。若有，停止pid，并删除相关.pid文件


文件格式查看：cat sbin/spark-daemon.sh

pid="$SPARK_PID_DIR/spark-$SPARK_IDENT_STRING-$command-$instance.pid


重新创建文件，再关闭。还不行，jps，再 kill -9 进程号。

修改目录位置：conf/spark-env.sh文件加上export SPARK_PID_DIR=/.../spark/pids




# hadoop 关闭问题


文件格式查看：cat sbin/hadoop-daemon.sh
```
pid=$HADOOP_PID_DIR/hadoop-$HADOOP_IDENT_STRING-$command.pid
/tmp/hadoop-你的用户名-namenode.pid
/tmp/hadoop-你的用户名-secondarynamenode.pid
/tmp/hadoop-你的用户名-datanode.pid
```

文件格式查看：cat sbin/yarn-daemon.sh
```
pid=$YARN_PID_DIR/yarn-$YANR_IDENT_STRING-$command.pid
/tmp/yarn-你的用户名-resourcemanager.pid
/tmp/yarn-你的用户名-nodemanager.pid
```

文件格式查看：cat sbin/mr-jobhistory-daemon.sh
```
pid=$HADOOP_MAPRED_PID_DIR/mapred-$HADOOP_MAPRED_IDENT_STRING-$command.pid
/tmp/mapred-你的用户名-historyserver.pid
```


修改 hadoop-env.sh，增加：export HADOOP_PID_DIR=/.../pids
/home/yangja/tmp
修改 yarn-env.sh，增加：export YARN_PID_DIR=/.../pids

修改 mapred-env.sh，增加：export HADOOP_MAPRED_PID_DIR=/.../pids



## 集群启动/关闭时：

> Error: JAVA_HOME is not set and could not be found.

可能是因为JAVA_HOME环境没配置正确，还有一种情况是即使各结点都正确地配置了JAVA_HOME，但在集群环境下还是报该错误，解决方法是显示地重新声明一遍JAVA_HOME

hadoop-env.sh、yarn-env.sh、mapred-env.sh增加`export JAVA_HOME=/.../jdk1.8.0_144`

## 启动节点需要登录密码

启动namenode, datanode, secondarynamenode 分别都需要输入登录密码

生成秘钥：如果本地环境有则不需要 ssh-keygen -t rsa -P “” 

本地的公钥导入私钥就可以 
cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys

如果不是root用户，应该在hom目录下：/home/yangja/.ssh



# 参考

https://www.cnblogs.com/simplestupid/p/4693513.html

