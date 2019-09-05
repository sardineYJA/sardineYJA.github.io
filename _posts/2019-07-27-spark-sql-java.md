---
layout: post
title: "Spark SQL Java编程"
date: 2019-07-27
description: "介绍一下Spark java编程"
tag: 大数据

---

# Spark SQL

## SparkSession

```java
SparkSession ssc = SparkSession
        .builder()
        .master("local")
        .appName("SparkSQL")
        .getOrCreate();
```

## 关于 SparkConf 参数

```java
SparkSession sparkSession = SparkSession.builder().appName("ServiceName")
		.config("spark.sql.warehouse.dir", "/user/sxdt/spark-warehouse")
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
// 需要实现 Serializable
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

## RDD 通过反射将类转为 DataFrame

Person类需实现Serializable，Setter和Getter

```java
JavaRDD<Person> personJavaRDD = ssc.read().textFile("D:\\2.txt")
        .javaRDD().map(new Function<String, Person>() {
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
		return RowFactory.create(
				msg_id,
				sp_number,
				errorCode);
	}
});

import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructField;
import org.apache.spark.sql.types.StructType;
List<StructField> fields = new ArrayList<>();
fields.add(DataTypes.createStructField("msg_id", DataTypes.StringType, true));
fields.add(DataTypes.createStructField("sp_number", DataTypes.StringType, true));
fields.add(DataTypes.createStructField("errorCode", DataTypes.StringType, true));
StructType schema = DataTypes.createStructType(fields);
Dataset<Row> successRateDataDataset = sparkSession.createDataFrame(rdd, schema);
```


## Dataset 保存/读取数据库

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


