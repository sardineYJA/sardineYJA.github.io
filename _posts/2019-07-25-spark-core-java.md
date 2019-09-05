---
layout: post
title: "Spark Core Java编程"
date: 2019-07-25
description: "介绍一下Spark java编程"
tag: 大数据

---

# Spark Core


## SparkConf 和 JavaSparkContext

```java
SparkConf sparkConf = new SparkConf()
        .setAppName("SparkApplication")
        .setMaster("local[*]");

JavaSparkContext jsc = new JavaSparkContext(sparkConf);
// jsc.setLogLevel("INFO");

JavaRDD<Integer> rddInt = jsc.parallelize(Arrays.asList(1,2,3,4));
JavaRDD<String> lines = jsc.textFile("D:\\1.txt");
System.out.println(lines.collect());
lines.foreach(v->System.out.println(v));
```

## 函数

```java
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

// 设置为一个分区，保存为一个文件
rdd.coalesce(1).saveAsTextFile("D://rdd");
```


```java
System.out.println(pariRdd1.groupByKey().collect());               // 分组
System.out.println(pariRdd1.subtract(pariRdd2).collect());         // 差集
System.out.println(pariRdd1.join(pariRdd2).collect());             // 内连接
System.out.println(pariRdd1.leftOuterJoin(pariRdd2).collect());    // 左连接
System.out.println(pariRdd1.rightOuterJoin(pariRdd2).collect());   // 有连接
```


# 例子


## 累加器、广播变量

```java

final Accumulator lineNum = jsc.accumulator(0);
lineNum.add(1);
System.out.println(lineNum.value);   // 必须放action后面才可以

```

## Wordcount

```java
JavaPairRDD<String, Integer> result = jsc.textFile("D:/test/1.txt")
                .flatMap(s -> Arrays.asList(s.split(" ")).iterator())
                .mapToPair(s -> new Tuple2<>(s, 1))
                .filter(t -> !t._1.isEmpty())
                .reduceByKey((v1, v2) -> (v1+v2));
```

```java
JavaRDD<String> lines = jsc.textFile("D:/test/1.txt");
JavaRDD<String> rdd = lines.flatMap(new FlatMapFunction<String, String>() {
    @Override
    public Iterator<String> call(String s) throws Exception {
        return Arrays.asList(s.split(" ")).iterator();
    }
});

JavaRDD<String> notEmtryRdd = rdd.filter(new Function<String, Boolean>() {
    @Override
    public Boolean call(String s) throws Exception {
        return !s.isEmpty();
    }
});

JavaPairRDD<String, Integer> javaPairRDD = notEmtryRdd.mapToPair(new PairFunction<String, String, Integer>() {
    @Override
    public Tuple2<String, Integer> call(String s) throws Exception {
        return new Tuple2<>(s, 1);
    }
});

JavaPairRDD<String, Integer> result = javaPairRDD.reduceByKey(new Function2<Integer, Integer, Integer>() {
    @Override
    public Integer call(Integer v1, Integer v2) throws Exception {
        return v1 + v2;
    }
});
```


## aggregate 的使用

```java
class RddAvg implements Serializable {
    private Integer total;
    private Integer num;
    public RddAvg(Integer total, Integer num) {
        this.total = total;
        this.num = num;
    }
    public double avg() {
        return total / num;
    }
    // RddAvg 是初始参数，Integer 传入的运算参数，RddAvg 返回值
    Function2<RddAvg, Integer, RddAvg> avgSeqOp = new Function2<RddAvg, Integer, RddAvg>() {
        @Override
        public RddAvg call(RddAvg v1, Integer v2) {
            v1.total += v2;
            v1.num += 1;
            return v1;
        }
    };
    // RddAvg 是初始参数，Integer 传入的运算参数，RddAvg 返回值
    Function2<RddAvg,RddAvg,RddAvg> avgCombOp = new Function2<RddAvg, RddAvg, RddAvg>() {
        @Override
        public RddAvg call(RddAvg v1, RddAvg v2) {
            v1.total += v2.total;
            v1.num += v2.num;
            return v1;
        }
    };
}
```

```java
// aggregate
JavaRDD<Integer> javaRDD = jsc.parallelize(Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)).coalesce(2);
Integer aggregate = javaRDD.aggregate(10,
        new Function2<Integer, Integer, Integer>() {
            @Override
            public Integer call(Integer v1, Integer v2) throws Exception {
                return v1 + v2;
            }
        },
        new Function2<Integer, Integer, Integer>() {
            @Override
            public Integer call(Integer v1, Integer v2) throws Exception {
                return v1 + v2;
            }
        });
System.out.println(aggregate);   // 85(2个seqOp，1个combOp)

// aggregate 将类作为初始参数进行运算
RddAvg rddAvg = new RddAvg(0,0);
RddAvg resultRddAvg = javaRDD.aggregate(rddAvg, rddAvg.avgSeqOp, rddAvg.avgCombOp);
System.out.println(resultRddAvg.avg());
```

## 自定义排序

```java
// 需要实现 Serializable
class CustomComComparator implements Serializable, Comparator<Integer> {
    @Override
    public int compare(Integer o1, Integer o2) {
        return o1.compareTo(o2);
    }
}

JavaRDD<Integer> javaRDD = jsc.parallelize(Arrays.asList(1, 4, 9, 2, 5, 6, 7, 8, 3, 10));
// sortBy 降序 分区
JavaRDD<Integer> integerJavaRDD = javaRDD.sortBy(new Function<Integer, Integer>() {
    @Override
    public Integer call(Integer v1) throws Exception {
        return v1;
    }
}, false, 1);
System.out.println(integerJavaRDD.collect());

// 需实现Serializable排序或取出num个
List<Integer> integers = javaRDD.takeOrdered(10, new CustomComComparator());
System.out.println(integers);
```

```java
// parallelizePairs
List<Tuple2<String, Integer>> list = new LinkedList<>();
list.add(new Tuple2<>("yang", 22));
list.add(new Tuple2<>("liu", 55));
list.add(new Tuple2<>("huang",43));
JavaPairRDD pairRDD = jsc.parallelizePairs(list);
System.out.println(pairRDD.collect());

// sortByKey
JavaPairRDD sortPairRDD = pairRDD.sortByKey(true); // 升序
System.out.println(sortPairRDD.collect());
// 自定义排序，需要实现Serializable
JavaPairRDD sortPairRDD2 = pairRDD.sortByKey(new CustomComComparatorS());
System.out.println(sortPairRDD2.collect());
```

## 每行切分后，返回多个Tuple2

```java
JavaRDD<String> line = jsc.textFile("D:/in/Small Dataset.txt");
JavaRDD<Tuple2<String, Integer>> rdd = line.flatMap(new FlatMapFunction<String, Tuple2<String, Integer>>() {
    @Override
    public Iterator<Tuple2<String, Integer>> call(String s) throws Exception {
        String[] followee_followers = s.split(":");
        String[] followers = followee_followers[1].split(" ");

        List<Tuple2<String, Integer>> list = new ArrayList<>();

        for (int i = 0; i < followers.length - 1; i++)
            for (int j = i+1; j < followers.length; j++) {
                list.add(new Tuple2<>(followers[i] + "-" + followers[j], 1));
            }
        return list.iterator();
    }
});

JavaPairRDD<String , Integer> allPairRdd = rdd.mapToPair(new PairFunction<Tuple2<String, Integer>, String, Integer>() {
    @Override
    public Tuple2<String, Integer> call(Tuple2<String, Integer> t) throws Exception {
        return t;
    }
});
```

上面两个等效于下面

```java
JavaPairRDD<String, Integer> tt = line.flatMapToPair(new PairFlatMapFunction<String, String, Integer>() {
    @Override
    public Iterator<Tuple2<String, Integer>> call(String s) throws Exception {
        String[] followee_followers = s.split(":");
        String[] followers = followee_followers[1].split(" ");
        List<Tuple2<String, Integer>> list = new ArrayList<>();

        for (int i = 0; i < followers.length - 1; i++)
            for (int j = i+1; j < followers.length; j++) {
                list.add(new Tuple2<>(followers[i] + "-" + followers[j], 1));
            }
        return list.iterator();
    }
});
```

