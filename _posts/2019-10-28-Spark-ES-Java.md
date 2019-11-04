---
layout: post
title: "Spark 与 ES 交互"
date: 2019-10-28
description: "Spark 与 ES 交互"
tag: Spark

---


## 依赖

```xml
<dependency>
    <groupId>org.elasticsearch</groupId>
    <artifactId>elasticsearch-spark-20_2.11</artifactId>
    <version>5.5.1</version>
</dependency>
```

```java
SparkSession sparkSession = SparkSession.builder().appName("SparkToES")
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        .config("es.nodes", "172.16.7.124")
        .config("es.port", "9200")
        .config("es.index.auto.create", "true")
        .config("es.nodes.wan.only", "true")
        .config("pushdown", "true")
        .master("local[*]")
        .getOrCreate();
JavaSparkContext jsp = new JavaSparkContext(sparkSession.sparkContext());
```

## Spark SQL 方式写入 ES

```java
Blog blog = new Blog(10, "test_title", "test_content");
Encoder<Blog> endcoder = Encoders.bean(Blog.class);
Dataset<Blog> dataset = sparkSession.createDataset(Collections.singletonList(blog), endcoder);
HashMap<String, String> map = new HashMap<>();
map.put("es.mapping.id" , "id");   // 指定id（必须是已有的字段）也可以不指定，不指定ES会自动生成
// Spark SQL 方式写入 ES，某个字段作为id但es已有的话，插入不成功
dataset.write().mode(SaveMode.Append).format("org.elasticsearch.spark.sql").options(map).save("blog/article");
```

## JavaEsSpark 方式写入 ES

```java
Blog blog1 = new Blog(11, "title11", "content11");
Blog blog2 = new Blog(12, "title12", "content12");
JavaRDD<Blog> rdd = jsp.parallelize(ImmutableList.of(blog1, blog2));
Map<String, String> map = new HashMap<>();
map.put("es.mapping.id" , "title");   // 某个字段指定为id也可以不指定，不指定ES会自动生成
// JavaEsSpark 方式写入 ES，某个字段作为id但es已有的话，插入不成功
JavaEsSpark.saveToEs(rdd, "blog/article", map);
```

## Spark SQL 方式读取 ES

```java
// Spark SQL 方式读取 ES
Dataset<Row> blogDataset = sparkSession.read().format("org.elasticsearch.spark.sql").load("blog/article");
blogDataset.show();
blogDataset.createOrReplaceTempView("blog");
sparkSession.sql("select id, title, content from blog").show();
```

## JavaEsSpark 方式读取 ES

```java
// JavaEsSpark 方式读取 ES
String query = "{\"query\":{\"match_all\":{}}}";
JavaPairRDD<String, Map<String, Object>> blogRDD = JavaEsSpark.esRDD(jsp, "blog/article", query);
System.out.println("返回数据个数：" + blogRDD.count());
System.out.println(blogRDD.collectAsMap());
```


