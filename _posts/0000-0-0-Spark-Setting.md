---
layout: post
title: "Spark 环境配置"
date: 2019-06-20
description: "介绍一下Spark环境配置"
tag: Spark

---

# spark

基于内存计算的大数据并行分析引擎

# 环境准备

1. 安装JDK，建议安装1.8版本的JDK

2. 下载解压spark:http://spark.apache.org/downloads.html

`tar -zxvf spark-2.1.1-bin-hadoop2.7.tgz -C /opt/`

3. 主机名修改


# 配置单机版

1. 配置系统的环境变量:vi /etc/profile
```
## SPARK_HOME
export SPARK_HOME=/../spark
export PATH=$PATH:$SPARK_HOME/bin
```

2. cp spark-env.sh.template spark-env.sh
```
export JAVA_HOME=/.../java
export SPARK_HOME=/.../spark
export SPARK_MASTER_IP=XXX.XX.XX.XXX  #自己ip
```
修改pid目录位置：export SPARK_PID_DIR=/.../spark/pids

3. cp slaves.template slaves
```
localhost
```

4. 启动：`sbin/start-all.sh`

5. 查看 jps 出现：Master，Worker

6. 浏览器查看：`http://master01:8080`

# 测试

```
bin/spark-submit \
--class org.apache.spark.examples.SparkPi \
--master spark://xxx.xxx.xxx.xxx:7077 \
--executor-memory 1G \
--total-executor-cores 2 \
examples/jars/spark-examples_2.11-2.1.1.jar 100
```
```
bin/spark-submit \
--class org.apache.spark.examples.SparkPi \
--master spark://172.16.7.124:7077 \
--executor-memory 1G \
--total-executor-cores 2 \
examples/jars/spark-examples_2.11-2.1.1.jar 100
```

# 减少输出信息

vi conf/log4j.properties
```
log4j.rootCategory=INFO, console
改成：
log4j.rootCategory=WARN, console
```

# 测试 spark-shell

1. 先创建1.txt文本

2. 统计单词数量
```
sc.textFile("/home/yangja/tmp/1.txt").flatMap(_.split(" ")).map((_,1)).reduceByKey(_+_).saveAsTextFile("/home/yangja/tmp/out")
```

# spark程序

## IDEA安装Scala

0. 安装后xml则可以不写依赖
1. 关闭项目 --> configure --> plugins --> 搜索Scala --> 安装
2. File --> Project Structure --> Global Libraries --> + --> Scala

## 新建maven项目

1. 加上spark依赖，以及打包插件

```xml
	<dependencies>
        <dependency>
            <groupId>org.apache.spark</groupId>
            <artifactId>spark-core_2.11</artifactId>
            <version>2.1.1</version>
        </dependency>
    </dependencies>

    <build>
        <finalName>wordcount</finalName>
        <plugins>

            <plugin>
                <groupId>net.alchim31.maven</groupId>
                <artifactId>scala-maven-plugin</artifactId>
                <version>3.2.2</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>compile</goal>
                            <goal>testCompile</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>

            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-assembly-plugin</artifactId>
                <version>3.0.0</version>
                <configuration>
                    <archive>
                        <manifest>
                            <mainClass>test.WordCount</mainClass>
                        </manifest>
                    </archive>
                    <descriptorRefs>
                        <descriptorRef>jar-with-dependencies</descriptorRef>
                    </descriptorRefs>
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

2. wordcount例子代码

```java
package test

import org.apache.spark.{SparkConf, SparkContext}

object WordCount {
  def main(args: Array[String]) {
    //创建SparkConf()并设置App名称
    val conf = new SparkConf().setAppName("WC")
    //创建SparkContext，该对象是提交spark App的入口
    val sc = new SparkContext(conf)
    //使用sc创建RDD并执行相应的transformation和action
    sc.textFile(args(0))
      .flatMap(_.split(" "))
      .map((_, 1))
      .reduceByKey(_+_, 1)
      .sortBy(_._2, false)
      .saveAsTextFile(args(1))
    //停止sc，结束该任务
    sc.stop()
  }
}
```

3. 打包：右侧栏Maven --> 选择clean和package --> Run Maven Build

4. 上传含依赖的jar，运行：

```
bin/spark-submit \
--class test.WordCount \
--master spark://172.16.7.124:7077 \
--executor-memory 1G \
--total-executor-cores 2 \
myJar/swc.jar \
/home/yangja/tmp/1.txt \
/home/yangja/tmp/output
```

## 本地测试

1. 修改Master为本地，以及输入输出路径
```java
val conf = new SparkConf().setAppName("WC").setMaster("local")
val inputFilePath:String = "D:\\1.txt"
val outputFilePath:String = "D:\\output"
```

2. 运行发现，即使不用hdfs，还是需要hadoop
> java.lang.NullPointerException

3. 将hadoop解压到E:\hadoop-2.7.2

4. Run --> Edit configurations --> Environment variables 
添加：HADOOP_HOME=E:\hadoop-2.7.2

5. 运行发现bin目录下并没有winutils.exe文件
> java.io.IOException: Could not locate executable E:\hadoop-2.7.2\bin\winutils.exe in the Hadoop binaries.

6. 下载放进去




# 配置Standalone集群模式

## 配置流程

1. ../conf目录下增加配置文件
cp slaves.template slaves
cp spark-env.sh.template spark-env.sh

2. slaves 中增加：
```
slave01
slave02
```

3. spark-env.sh 中增加：
```
SPARK_MASTER_HOST=master01
SPARK_MASTER_PORT=7077
```

4. 配置文件同步到其他节点
5. 启动：`sbin/start-all.sh`
6. 浏览器查看：`http://master01:8080`

## 问题

1. 提示异常：“JAVA_HOME not set”，则 spark-config.sh 需要增加：
`export JAVA_HOME=/.../jdk1.8.0_144`，同步配置文件。

2. hdfs写入权限问题：`org.apache.hadoop.security.AccessControlException`，
需要在hdfs-site.xml 关闭权限验证：


```xml
<property>
    <name>dfs.permissions</name>
    <value>false</value>
</property>
```



# 配置JobHistory Server

1. cp spark-defaults.conf.template spark-defaults.conf

2. 开启Log, vi spark-defaults.conf:
```sh
spark.master             spark://master01:7077
spark.eventLog.enabled   true
spark.eventLog.dir       hdfs://master01:9000/directory 或 file:///home/yangja/sparklog
spark.eventLog.compress  true
```
3. vi spark-env.sh 添加：
```sh
export SPARK_HISTORY_OPTS="-Dspark.history.ui.port=4000
-Dspark.history.retainedApplications=3
-Dspark.history.fs.logDirectory=hdfs://master01:9000/directory"
```
4. 注意hdfs://master01:9000/directory 目录要先在hadoop上创建好

5. 同步配置文件到其他节点

6. 启动集群：`../sbin/start-all.sh`

7. 启动JobHistory：`../sbin/start-history-server.sh`

8. 浏览器查看：`http://master01:4000`




# spark on yarn 集群

## spark-env.sh

注意路径必须在hdfs先创建，否则运行spark程序会报错

cleaner.enabled 日志是否定时清除，true为定时清除，默认为false

cleaner.maxAge 日志生命周期2天

cleaner.interval 日志检查间隔，默认每一天会检查一下日志文件

```sh
## 指定hadoop的conf配置文件
HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
## 此配置是所有模式中historyserver必须配置的
SPARK_HISTORY_OPTS="-Dspark.history.fs.logDirectory=hdfs://master01:9000/spark/log 
    -Dspark.history.ui.port=18080
    -Dspark.history.fs.cleaner.enabled=true
    -Dspark.history.fs.cleaner.maxAge=2d
    -Dspark.history.fs.cleaner.interval=1d"
```


## slaves

```
spark1
spark2
```

## spark-defaults.conf

```sh
## 打开日志收集功能
spark.eventLog.enabled           true
## 定义历史日志收集在hdfs上的路径 
spark.eventLog.dir               hdfs://master01:9000/spark/log
spark.yarn.historyServer.address http://spark3:18080
```

## yarn-site.xml

修改hadoop的yarn-site.xml配置文件，添加
```xml
<property>
    <name>yarn.log-aggregation-enable</name>
    <value>true</value>
</property>
<property>
    <name>yarn.log.server.url</name>
    <value>http://spark3:19888/jobhistory/logs/</value>
</property>
```

## 同步启动

同步其他节点

重新启动hadoop中的yarn模块相关进程

spark on yarn 模式:它调用是hadoop中的yarn资源框架，而spark的sbin目录下脚本，是为standalone模式服务的，所以不需要启动spark（但是 start-history-server.sh 需要启动）

## spark.eventLog.dir 和 spark.history.fs.logDirectory  区别

设置了 spark.eventLog.dir ，start-history-server.sh 启动后面不带地址，还是使用默认地址

设置 spark.history.fs.logDirectory 能不带参数启动

## spark.yarn.historyServer.address 和 spark.history.ui.port 区别

启动：spark.yarn.historyServer.address 设置的端口并没有生效，需要spark.history.ui.port设置才生效。

如果不设置spark.yarn.historyServer.address，虽然直接在history-server中能直接看，但是在完成任务那里点击“History”，不会链接到history-server。在任务的"Environment"中也没看到这个属性。但是设置了，"Environment"中可以看到这个属性，那么大胆的认为，这个属性在任务运行中会记录下来，后面才可以链接。

spark-env.sh 里面的 SPARK_HISTORY_OPTS 才是设置 history-server 启动的配置。

spark-defaults.conf 任务中让 yarn RM 知道这些配置，给后面的链接用。


