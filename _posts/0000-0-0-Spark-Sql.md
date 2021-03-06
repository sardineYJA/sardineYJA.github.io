---
layout: post
title: "Spark SQL"
date: 2019-07-01
description: "介绍一下Spark SQL"
tag: Spark

---

# Spark SQL

将数据的计算任务通过SQL的形式转换成了RDD的计算，类似于Hive通过SQL的形式将数据的计算任务转换成了MapReduce。

Hive ---> MapReduce

Spark SQL ---> RDD


## 分布式弹性数据集

DataSet 包括RDD,DataFrame(RDD),两者是并列的

1. 都是弹性数据集，为处理超大型数据提供便利

2. 三者都有惰性机制

3. 都会根据spark内存情况自动缓存运算

4. 都有partition的概念


## SparkSession与SparkContext

在老的版本中，Spark SQL提供两种SQL查询起始点：

一个叫SQLContext，用于Spark自己提供的SQL查询；

一个叫HiveContext，用于连接Hive的查询；

SparkSession是Spark最新的SQL查询起始点，实质上是SQLContext和HiveContext的组合。

所以在SQLContext和HiveContext上可用的API在SparkSession上同样是可以使用的。

SparkSession内部封装了sparkContext，所以计算实际上是由sparkContext完成的。


## 查询

```json
{"name":"yang"}
{"name":"liu", "age":20}
{"name":"chen", "age":25}
```

DSL风格

```java
// spark作为SparkSession的变量名

// 读取json文件
val df = spark.read.json("1.json")

// 显示
df.show()
df.show(5)   // 显示前5条

// 过滤
df.filter($"age" > 20).show()

// 分组
df.groupBy("age").count().show()

// 结构
df.printSchema()
```

SQL风格

```java
// 创建临时表
df.createOrReplaceTempView("persons")
// sql 语句
spark.sql("select * from persons").show()

// Session退出临时表失效，可使用全局表
df.createGlobalTempView("people")
spark.sql("select * from global_temp.people").show()

spark.newSession().sql("select * from global_temp.people").show()
```

## 添加spark sql 依赖

```xml
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-sql_2.11</artifactId>
    <version>${spark.version}</version>
    <scope>provided</scope>
</dependency>
```

```java
import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.sql.SparkSession

object TestSql {

  def main(args:Array[String]): Unit = {

    val conf = new SparkConf().setAppName("SQL").setMaster("local")
    val sc = new SparkContext(conf)

    val spark = SparkSession
      .builder()   
      .appName("Spark Test SQL")
      .config("spark.some.config.option", "some-value")
      .getOrCreate()

    // 用于将DataFrame隐式转换成RDD, 使df能够使用RDD中的方法
    import spark.implicits._

    val df = spark.read.json("D:\\test\\1.json")

    df.show()

    df.filter($"age" > 21).show()

    df.createOrReplaceTempView("persons")

    spark.sql("SELECT * FROM persons where age > 21").show()

    spark.stop()
  }
}
```

使用SparkSession，会报错却可以正确运行：

> java.io.IOException: Could not locate executable E:\hadoop-2.7.2\bin\winutils.exe in the Hadoop binaries.

解决 Run --> Edit configurations --> Environment variables 

添加：HADOOP_HOME=E:\hadoop-2.7.2


如果需要Hive支持

```java
val spark = SparkSession
      .builder()   
      .appName("Spark Test SQL")
      .config("spark.some.config.option", "some-value")
      .enableHiveSupport()
      .getOrCreate()
```


## 创建 DataFrames

```java
1. 数据源
val df = spark.read.json(path)

2. RDD转换
val df = sc.testFile("1.txt")
		   .map(_.split(","))
		   .map(paras => (paras(0), paras(1).trim().toInt) )
		   .toDF("name", "age")
```

## 创建 DataSet

Dataset是具有强类型的数据集合，需提供对应的类型信息

Dataset不使用Java序列化或者Kryo，而是使用专用的编码器（Encoder ）来序列化对象和跨网络传输通信。如果这个编码器和标准序列化都能把对象转字节，那么编码器就可以根据代码动态生成，并使用一种特殊数据格式，这种格式下的对象不需要反序列化回来，就能允许Spark进行操作，如过滤、排序、哈希等。

```java
case class Person(name: String, age: Long)
Seq(Person("yang", 33)).toDS().show()

Seq(1,2,3).toDS()

spark.read.json(path).as[Person].show()
```


## 转换

```java
1. DataFrame/DataSet 转 RDD
val rdd1 = testDF.rdd
val rdd2 = testDS.rdd

2. RDD 转 DataFrame
import spark.implicits._
val testDF = rdd.map(line => (line._1, line._2)).toDF("col1", "col2")

3. RDD 转 DataSet
import spark.implicits._
case clas Coltest(col1:String, col2:Int) extends Serializable
val testDS = rdd.map(line => (Coltest(line._1, line._2))).toDS

4. DataSet 转 DataFrame
import spark.implicits._
val testDF = testDS.toDF

5. DataFrame 转 DataSet
import spark.implicits._
case class Coltest(col1:String, col2:Int) extends Serializable
val testDS = testDF.as[Coltest]
```

在使用一些特殊的操作时，一定要加上 import spark.implicits._ 不然toDF、toDS无法使用


## 用户自定义UDF函数

```java
spark.udf.register("addName", (x:String) => "Name："+x)
spark.sql("Select addName(name), age from people").show()
// Name:yang   23
```

## 自定义聚合函数

弱类型(DataFrame)用户自定义聚合函数：
通过继承UserDefinedAggregateFunction来实现用户自定义聚合函数

```java

```

强类型(DataSet)用户自定义聚合函数：
通过继承Aggregator来实现用户自定义聚合函数

```java

```

## 数据源

```java
// Spark SQL的默认数据源为Parquet格式
sqlContext.read.load("1.parquet")

// json, parquet, jdbc, orc, libsvm, csv, text
spark.read.format("json").load("1.json")

testDF.write.format("parquet").save("1.parquet")

```



## 实例操作

tbStock         订单表 （foreign key时间）

tbStockDetailDS 货物表 （foreign key单号）

tbDate          时间表

``` java
// tbStock 表的读取
case class tbStock(ordernumber:String, locationid:String, dateid:String) extends Serializable
val tbStockRdd = spark.sparkContext.textFile("/home/yangja/tmp/tbStock.txt")
val tbStockDS = tbStockRdd.map(_.split(",")).map(attr => tbStock(attr(0), attr(1), attr(2))).toDS
tbStockDS.show()
+------------+----------+---------+
| ordernumber|locationid|   dataid|
+------------+----------+---------+
|BYSL00000893|      ZHAO|2007-8-23|
```

```java
// tbStockDetail 表的读取
case class tbStockDetail(ordernumber:String, rownum:Int, itemid:String,number:Int, price:Double, amount:Double) extends Serializable
val tbStockDetailRdd = spark.sparkContext.textFile("/home/yangja/tmp/tbStockDetail.txt")
val tbStockDetailDS = tbStockDetailRdd.map(_.split(",")).map(attr => tbStockDetail(attr(0),attr(1).trim().toInt,attr(2),attr(3).trim().toInt,attr(4).trim().toDouble, attr(5).trim().toDouble)).toDS
tbStockDetailDS.show()
+------------+------+--------------+------+-----+------+
| ordernumber|rownum|        itemid|number|price|amount|
+------------+------+--------------+------+-----+------+
|BYSL00000893|     0|FS527258160501|    -1|268.0|-268.0|
```

```java
// tbDate 表的读取
case class tbDate(dateid:String, years:Int, theyear:Int, month:Int, day:Int, weekday:Int, week:Int, quarter:Int, period:Int, halfmonth:Int) extends Serializable
val tbDateRdd = spark.sparkContext.textFile("/home/yangja/tmp/tbDate.txt")
val tbDateDS = tbDateRdd.map(_.split(",")).map(attr => tbDate(attr(0),attr(1).trim().toInt, attr(2).trim().toInt,attr(3).trim().toInt, attr(4).trim().toInt, attr(5).trim().toInt, attr(6).trim().toInt, attr(7).trim().toInt, attr(8).trim().toInt, attr(9).trim().toInt)).toDS
tbDateDS.show()
+---------+------+-------+-----+---+-------+----+-------+------+---------+
|   dateid| years|theyear|month|day|weekday|week|quarter|period|halfmonth|
+---------+------+-------+-----+---+-------+----+-------+------+---------+
| 2003-1-1|200301|   2003|    1|  1|      3|   1|      1|     1|        1|
```

```java
// 注册表
tbStockDS.createOrReplaceTempView("tbStock")

tbDateDS.createOrReplaceTempView("tbDate")

tbStockDetailDS.createOrReplaceTempView("tbStockDetail")
```


统计所有订单中每年的销售单数、销售总额

```java
spark.sql("...").show
```

```sql
select c.theyear, count(distinct a.ordernumber), sum(b.amount) 
from tbStock a 
  join tbStockDetail b on a.ordernumber = b.ordernumber 
  join tbDate c on a.dateid = c.dateid 
group by c.theyear 
order by c.theyear 
```

统计每年每个订单的总销售额

```sql
select a.dateid, a.ordernumber, sum(b.amount) as sumofamount 
from tbStock a 
  join tbStockDetail b on a.ordernumber=b.ordernumber 
group by a.dateid, a.ordernumber
```

统计每年最大金额订单的销售额

```sql
select theyear, max(c.SumOfAmount) as SumOfAmount 
from (select a.dateid, a.ordernumber, sum(b.amount) as SumOfAmount 
      from tbStock a 
        join tbStockDetail b on a.ordernumber = b.ordernumber 
      group by a.dateid, a.ordernumber) c 
  join tbDate d on c.dateid = d.dateid 
group by theyear 
order by theyear DESC

```

统计每年每个货品的销售额

```sql
select c.theyear, b.itemid, sum(b.amount) as SumOfAmount 
from tbStock a 
  join tbStockDetail b on a.ordernumber = b.ordernumber 
  join tbDate c on a.dateid = c.dateid 
group by c.theyear, b.itemid
```

统计每年单个货品中的最大金额

```sql
select d.theyear, max(d.SumOfAmount) as MaxOfAmount 
from (select c.theyear, b.itemid, SUM(b.amount) as SumOfAmount 
      from tbStock a 
        join tbStockDetail b on a.ordernumber = b.ordernumber 
        join tbDate c on a.dateid = c.dateid 
      group by c.theyear, b.itemid ) d 
group by d.theyear
```

> 统计后，我还想输出d.itemid，发现不行，原因：d有个3个字段，theyear用来分组，SumOfAmount进行聚合函数，itemid不可再输出了。就比如聚合函数是sum的时候，可能有几个itemid不同的行因theyear相同合成一行了。

统计每年最畅销的货品（即将上面的结果加上itemid字段输出），需要join每年每个货品的销售额来得到itemid

```sql
SELECT DISTINCT e.theyear, e.itemid, f.maxofamount 
FROM (SELECT c.theyear, b.itemid, SUM(b.amount) AS sumofamount 
      FROM tbStock a 
        JOIN tbStockDetail b ON a.ordernumber = b.ordernumber 
        JOIN tbDate c ON a.dateid = c.dateid 
      GROUP BY c.theyear, b.itemid 
      ) e         -- e 统计每年每个货品的销售额

      JOIN (SELECT d.theyear, MAX(d.sumofamount) AS maxofamount 
          FROM (SELECT c.theyear, b.itemid, SUM(b.amount) AS sumofamount 
                FROM tbStock a 
                  JOIN tbStockDetail b ON a.ordernumber = b.ordernumber 
                  JOIN tbDate c ON a.dateid = c.dateid 
                GROUP BY c.theyear, b.itemid 
                ) d  -- d 统计每年每个货品的销售额
          GROUP BY d.theyear 
          ) f                  -- f 统计每年单个货品中的最大金额
      ON e.theyear = f.theyear AND e.sumofamount = f.maxofamount 
ORDER BY e.theyear"
```



