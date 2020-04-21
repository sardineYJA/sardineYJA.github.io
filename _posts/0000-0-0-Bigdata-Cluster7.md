---
layout: post
title: "快速搭建7 —— Sogou数据测试"
date: 2020-04-19
description: "Bigdata"
tag: Bigdata

---

## 数据

数据来源：http://www.sogou.com/labs/resource/q.php

```java
public class ReadWebLog {

    private static String readFileName;
    private static String writeFileName;

    public static void main(String args[]) {
        // args = new String[2];    // 测试
        // args[0]="E:\\test\\SogouQ.reduced";
        // args[1]="E:\\test\\weblog.log";

        if (args.length < 2) {
            System.out.println("no args, exit...");
            System.exit(0);
        }
        readFileName = args[0];
        writeFileName = args[1];
        readFile(readFileName);
    }

    public static void readFile(String fileName) {

        try {
            FileInputStream fis = new FileInputStream(fileName);
            InputStreamReader isr = new InputStreamReader(fis, "GBK");
            BufferedReader br = new BufferedReader(isr);
            int count = 0;  // 显示行号
            while (br.readLine() != null) {
                String line = br.readLine();
                count++;
                Thread.sleep(300);
                String str = new String(line.getBytes("UTF8"), "GBK");
                System.out.println("row:" + count + ">>>>>>>>" + line);
                writeFile(writeFileName, line);
            }
            isr.close();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static void writeFile(String fileName, String conent) {
        try {
            FileOutputStream fos = new FileOutputStream(fileName, true);
            OutputStreamWriter osw = new OutputStreamWriter(fos);
            BufferedWriter bw = new BufferedWriter(osw);
            bw.write("\n");
            bw.write(conent);
            bw.close();
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

maven项目打包：
```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-jar-plugin</artifactId>
            <configuration>
                <archive>
                    <manifest>
                        <mainClass>dataformat.ReadWebLog</mainClass>
                    </manifest>
                </archive>
            </configuration>
        </plugin>
    </plugins>
</build>
```

打包weblog.jar，重新格式化数据，写进log


## 数据流

Flume 检测并将数据写进 Kafka，测试（删除了写进Hbase的步骤）

首先开启Zookeeper, Kafka, Flume

```sh
# VM124，先启动聚合的节点
bin/flume-ng agent --conf conf -f conf/flume-conf.properties -n agent1 -Dflume.root.logger=INFO,console
# VM125 
bin/flume-ng agent --conf conf -f conf/flume-conf.properties -n agent2 -Dflume.root.logger=INFO,console
# VM126
bin/flume-ng agent --conf conf -f conf/flume-conf.properties -n agent3 -Dflume.root.logger=INFO,console


# 创建topic
bin/kafka-topics.sh --zookeeper localhost:2181 --create --topic weblogs --replication-factor 1 --partitions 1
# 查看topic
bin/kafka-topics.sh --zookeeper localhost:2181 --list
bin/kafka-topics.sh --describe --zookeeper localhost:2181 --topic weblogs
```

模拟日志逐渐写入

```sh
#/bin/bash
echo "start log"
java -jar /.../weblog.jar /.../SogouQ.reduced /home/yang/datas/weblog-flume.log
java -jar ./weblog.jar ./SogouQ.reduced ../datas/weblog-flume.log
```


测试消费从flume传过来的信息

```sh
#/bin/bash
echo "flume agent1 start"
bin/kafka-console-consumer.sh --zookeeper VM124:2181,VM125:2181,VM126:2181 --topic weblogs  --from-beginning
```

数据格式：访问时间 用户ID [查询词] 该URL在返回结果中的排名 用户点击的顺序号 用户点击的URL
```
00:01:31    9418217515675722    [特种部队的大跳]   9 6 games.qq.com/a/20070801/000058.htm
...
```


## Spark

测试的是Maven项目 Scala 版本 2.12

```xml
<dependencies>
    <!--Spark sql-->
    <dependency>
        <groupId>org.apache.spark</groupId>
        <artifactId>spark-sql_2.11</artifactId>
        <version>2.2.0</version>
    </dependency>
    <!--structured streaming-->
    <dependency>
        <groupId>org.apache.spark</groupId>
        <artifactId>spark-sql-kafka-0-10_2.11</artifactId>
        <version>2.2.0</version>
    </dependency>
</dependencies>
```


log4j.properties 测试时为了减少 INFO 的输出

```sh
log4j.rootLogger=WARN, stdout
log4j.appender.stdout=org.apache.log4j.ConsoleAppender
log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
log4j.appender.stdout.layout.ConversionPattern=%d %p [%c] - %m%n
log4j.appender.logfile=org.apache.log4j.FileAppender
log4j.appender.logfile.File=target/spring.log
log4j.appender.logfile.layout=org.apache.log4j.PatternLayout
log4j.appender.logfile.layout.ConversionPattern=%d %p [%c] - %m%n
```

StructuredStreaming 读取 Kafka

```java
object ReadStreaming {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .master("local[*]")
      .appName("Readstreaming")
      .getOrCreate()

    val df = spark
      .readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", "192.168.243.124:9092,192.168.243.125:9092")
      .option("subscribe", "weblogs")    // topic
      .load()

    import spark.implicits._
    val lines = df.selectExpr("CAST(value AS STRING)").as[String] // 每行转为String

    // lines.writeStream.format("console").start().awaitTermination()  // 打印每条数据

    // 数据以\t隔开，但是两个order是以空格隔开，所以这里是5个字段非6个
    val value = lines.map(_.split("\t")).map(x=>(x(0),x(1),x(2),x(3),x(4)))
    value.writeStream.format("console").start().awaitTermination()
  }
}
```

```java
val spark = SparkSession.builder()
      .master("local[2]")
      .appName("streaming").getOrCreate()

val df = spark
  .readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "master:9092")
  .option("subscribe", "weblogs")
  .load()

// 统计每个关键字搜索的次数
import spark.implicits._
val lines = df.selectExpr("CAST(value AS STRING)").as[String]
val weblog = lines.map(_.split(",")).map(x => Weblog(x(0), x(1), x(2), x(3), x(4), x(5)))
val titleCount = weblog.groupBy("searchname").count().toDF("titleName", "webcount")

// 结果保存到mysql
val url = "jdbc:mysql://master:3306/weblog?useSSL=false"
val username = "root"
val password = "123456"
val writer = new JdbcSink(url, username, password)
val weblogcount = titleCount.writeStream
  .foreach(writer)
  .outputMode("update")
  .start()

weblogcount.awaitTermination()
```
