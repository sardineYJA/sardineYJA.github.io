---
layout: post
title: "Spark java编程1"
date: 2019-07-25
description: "介绍一下Spark java编程1"
tag: 大数据

---

## Spark Core

```java
SparkConf sparkConf = new SparkConf()
        .setAppName("SparkApplication")
        .setMaster("local");

JavaSparkContext jsc = new JavaSparkContext(sparkConf);
// jsc.setLogLevel("INFO");

JavaRDD<Integer> rddInt = jsc.parallelize(Arrays.asList(1,2,3,4));
JavaRDD<String> lines = jsc.textFile("D:\\1.txt");
System.out.println(lines.collect());
lines.foreach(v->System.out.println(v));


// map [[1, a], [2, b], [3, c], ...]
JavaRDD<List<String>> rdd1 = lines.map(line -> Arrays.asList(line.split(" ")));

// map
JavaRDD<String[]> rdd2 = lines.map(new Function<String, String[]>() {
    @Override
    public String[] call(String s) throws Exception {
        return s.split(" ");
    }
});

// flatMap [1, a, 2, b, 3, c, 4, d, 5, e, 1, aa, 2, bb, 3, cc]
JavaRDD<String> rdd3 = lines.flatMap(new FlatMapFunction<String, String>() {
    @Override
    public Iterator<String> call(String s) throws Exception {
        return Arrays.asList(s.split(" ")).iterator();
    }
});

// mapToPair
JavaPairRDD<Integer, String> rdd4 = lines.mapToPair(new PairFunction<String, Integer, String>() {
    @Override
    public Tuple2<Integer, String> call(String s) throws Exception {
        String[] ts = s.split(" ");
        return new Tuple2(ts[0], ts[1]);
    }
});

// filter
JavaRDD<String> filterRdd = list.filter(
    new Function<String, Boolean>() {
        @Override
        public Boolean call(String s) throws Exception {
            return s.contains("a");
        }
    });

// reduce
Integer totalAge = dataAgeInt.reduce(new Function2<Integer, Integer, Integer>() {
    @Override
    public Integer call(Integer x, Integer y) throws Exception {
        return x+y;
    }
});

// mapToPair
PairFunction<String, String, String> myPairFunc = new PairFunction<String, String, String>() {
    @Override
    public Tuple2<String, String> call(String s) throws Exception {
        return new Tuple2<>(s, s);
    }
};
JavaPairRDD<String, String> pariRdd = rdd.mapToPair(myPairFunc);

// 设置为一个分区
rdd.coalesce(1).saveAsTextFile("D://rdd");
```

##累加器、广播变量

```java
final Accumulator lineNum = jsc.accumulator(0);
lineNum.add(1);
System.out.println(lineNum.value);   // 必须放action后面

System.out.println(pariRdd1.groupByKey().collect());               // 分组
System.out.println(pariRdd1.subtract(pariRdd2).collect());         // 差集
System.out.println(pariRdd1.join(pariRdd2).collect());             // 内连接
System.out.println(pariRdd1.leftOuterJoin(pariRdd2).collect());    // 左连接
System.out.println(pariRdd1.rightOuterJoin(pariRdd2).collect());   // 有连接
```


## Wordcount

```java
JavaPairRDD<String, Integer> result = jsc.textFile("D:\\1.txt")
        .flatMap(s -> Arrays.asList(s.split(" ")).iterator())
        .mapToPair(s -> new Tuple2<>(s,1))
        .filter(t -> StringUtils.isNoneBlank(t._1))
        .reduceByKey((v1,v2) -> (v1+v2));
System.out.println(result.collect());

```

## Spark SQL

```json
{"name":"yang"}
{"name":"liu", "age":20}
{"name":"chen", "age":25}
```

```java
import java.io.Serializable;
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
SparkSession ssc = SparkSession
        .builder()
        .master("local")
        .appName("SparkSQL")
        .getOrCreate();

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

## Spark Streaming

```java
SparkConf sparkConf = new SparkConf().setAppName("SparkApplication").setMaster("local");
JavaStreamingContext jssc = new JavaStreamingContext(sparkConf, new Duration(2000));
JavaDStream lines = jssc.socketTextStream("172.16.7.124", 9999);
lines.print();
jssc.start();
jssc.awaitTermination();
// jssc.stop();
```