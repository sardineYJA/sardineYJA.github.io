---
layout: post
title: "Spark SQL Java编程"
date: 2019-07-27
description: "介绍一下Spark java编程"
tag: 大数据

---

# Spark SQL

## SparkSession

SparkSession是spark2.0新引入的概念，提供了对Hive功能的内置支持。

parkSession内部封装了sparkContext，所以计算实际上是由sparkContext完成的。

```java
SparkSession ssc = SparkSession
        .builder()
        .master("local")
        .appName("SparkSQL")
        .getOrCreate();
```

```java
Dataset<Row> dataset = ssc.read().json("D:\\person.json");
dataset.show();
dataset.select("age").show();

//  创建临时表
dataset.createOrReplaceTempView("person");
Dataset<Row> result = ssc.sql("select * from person");
result.show(true);    // 右对齐
result.show(false);   // 左对齐

//创建全局临时视图
dataset.createGlobalTempView("user");
//全局临时视图绑定到系统保存的数据库“global_temp”
Dataset<Row> globalUser = ssc.sql("SELECT * FROM global_temp.user");
ssc.newSession().sql("SELECT * FROM global_temp.user").show();
```

## 关于 SparkConf 参数

```java
SparkSession sparkSession = SparkSession.builder().appName("ServiceName")
		.config("spark.sql.warehouse.dir", "/user/sxdt/spark-warehouse")
        .config("spark.streaming.backpressure.enabled","true")
        .config("spark.streaming.kafka.maxRatePerPartition","3000000")
		.config("spark.testing.memory", "2147480000")
		.master("local[*]")
		.enableHiveSupport()
		.getOrCreate();

		.config("es.index.auto.create", "true")
		.config("es.nodes", "183.238.157.218")
		.config("es.port", "42284")
		.config("es.nodes.wan.only", "true")
		.config("pushdown", "true")

SparkConf sparkConf = new SparkConf()
        .setAppName("SparkApplication")
        .setMaster("local")
        .set("spark.cores.max", "10");

// SparkSession.builder.config的配置对应SparkConf

// conf/spark-defaults.conf
spark.master                     spark://master:7077
spark.eventLog.enabled           true
spark.eventLog.dir               file:///home/yangja/sparklog
spark.eventLog.dir               hdfs://namenode:8021/directory
spark.eventLog.compress          true

spark.app.name, name        // AppName
spark.executor.memory, 1g   // 执行内存
spark.driver.cores, 1       // driver的cpu核数
spark.driver.memory, 512m   // driver的内存
spark.executor.memory, 512m // 每个executor内存
```

## 例子

```json
{"name":"yang"}
{"name":"liu", "age":20}
{"name":"chen", "age":25}
```

```java
// 需要实现 Serializable，toString, setXxx, getXxx
public class Person implements Serializable {
    public String name;
    public Integer age;
    public Person(String name, Integer age) {
        this.name = name;
        this.age = age;
    };
    @Override
    public String toString() {
        return name+" "+age;
    }
    public String getName() {
        return name;
    }
    public Integer getAge() {
        return age;
    }
    public void setName(String name) {
        this.name = name;
    }
    public void setAge(Integer age) {
        this.age = age;
    }
}
```


## Encoder

RDD 序列化是使用 Serializable

DataSet 使用的Encoder来实现对象的序列化和在网络中的传输

encoder 有个动态的特性, Spark 在执行比如 sorting 之类的操作时无需再把字节反序列化成对象

```java
// Person 类无需实现 Serializable
Encoder<Person> encoder = Encoders.bean(Person.class);    // Person对应的Encoder

Person person = new Person("yang", 24); 
Dataset<Person> d1 = ssc.createDataset(Collections.singletonList(person), encoder);
d1.show();

Dataset<Person> d2 = ssc.read().json("D:/test/person.json").as(encoder);
d2.show();
```


## RDD 通过反射将类转为 DataFrame

Person类需实现Serializable，Setter和Getter

```java
Dataset<String> line = ssc.read().textFile("D:/test/2.txt");  
line.show();  // 读取Dataset，但只有一列，列值为 row，下面进行结构化

JavaRDD<String> stringJavaRDD = line.javaRDD(); //javaRDD() 将Dataset转JavaRDD ==> [row, row, ...]
JavaRDD<Person> personJavaRDD = stringJavaRDD.map(new Function<String, Person>() {
    @Override
    public Person call(String s) throws Exception {
        String[] sp = s.split(" ");
        Person p = new Person(sp[0], Integer.valueOf(sp[1]));
        return p;
    }
});

List<Person> pList = personJavaRDD.collect();
for (Person person : pList) {
    System.out.println(person.name+" : "+person.age);
}
Dataset<Row> pf = ssc.createDataFrame(personJavaRDD, Person.class);
pf.show();
Dataset<Row> pl = ssc.createDataFrame(pList, Person.class);
pl.show();
```


## RDD 通过 StructField 方法转 DataFrame 

```java
JavaRDD<Row> javaRdd = rdd.map(new Function<String, Row>() {
	@Override
	public Row call(String v1) throws Exception {
		String str[] = v1.split(":");

		if(str.length < 38) {
			return null;
		}
		String msg_id = str[1];
		String sp_number = str[5];
		String errorCode = str[35];
		return RowFactory.create(id,number,code);
	}
});

import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructField;
import org.apache.spark.sql.types.StructType;
List<StructField> fields = new ArrayList<>();
fields.add(DataTypes.createStructField("id", DataTypes.StringType, true));
fields.add(DataTypes.createStructField("number", DataTypes.StringType, true));
fields.add(DataTypes.createStructField("code", DataTypes.StringType, true));
StructType schema = DataTypes.createStructType(fields);
Dataset<Row> successRateDataDataset = sparkSession.createDataFrame(rdd, schema);
```


## Dataset 保存/读取

```java
dataset.select("name", "age").write().save("D:/1.parquet");
dataset.select("name", "age").write().format("json").save("D:/1.json");
dataset.write().format("json").mode(SaveMode.Append).save("D:/1.json");
```

保存模式

```
SaveMode.ErrorIFExists(default)  将DataFrame保存到(数据源)时,.如果数据已经存在,则抛出异常
SaveMode.Append                  如果数据存在,则追加
SaveMode.Overwrite               如果数据存在则覆盖
SaveMode.Ignore                  如果数据存在,则忽略,不影响原先数据,也不会保存现在的数据
```

数据库

```
driverClassName=oracle.jdbc.OracleDriver
url=jdbc:oracle:thin:@172.16.7.14:1521:ora10ha
username=root
password=123456
```

```java
Properties jdbcpro = new Properties();
jdbcpro.setProperty("user", PropertiesUtil.user);
jdbcpro.setProperty("password", PropertiesUtil.password);
jdbcpro.setProperty("driver", PropertiesUtil.driver);
String url = PropertiesUtil.url;
// 读取数据
Dataset<Row> dataset = sparkSession.sql(yourSQL);
// 数据库参数只需user,password,driver,url四个即可
dataset.write().mode(SaveMode.Append).jdbc(url, "table_name", jdbcpro); // 保存到数据库
sparkSession.read().jdbc(url, "yourSQL", jdbcpro).createOrReplaceTempView(tableName); // 读取
```



