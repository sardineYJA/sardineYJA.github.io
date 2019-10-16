---
layout: post
title: "数据处理案例"
date: 2019-09-01
description: "数据处理案例"
tag: Bigdata

---


# 粉丝相似度

## 数据

### 数据源

小型数据1000条左右，中型数据250万条左右，大型数据480万条左右

[Small DataSet](https://www.dropbox.com/s/ntzk80l5iiiuh50/Small%20Dataset.txt?dl=0)

[Medium DataSet](https://www.dropbox.com/s/6sxnnadhxbyk7ho/Medium%20Dataset.txt?dl=0)

[Large DataSet](https://www.dropbox.com/s/lrlgz50m88j6fpc/Large%20Dataset.txt?dl=0)

### 数据格式

```
0:98 118 144 826 840 863 889
1:40 66 107 119 152 927
2:19 42 80 284 297 33 592 607 654
3:9 123 657 
......
```

代表意义

```
followee_1:follower_3 follower_8 ....
followee_2:follower_4 follower_5 ....
偶像1：粉丝1 粉丝2 ....
偶像2：粉丝1 粉丝2 ....
....
```

### 需求

判断粉丝相似度：有共同偶像n个，则两两粉丝之间的相似度为n

输入：`K`

输出：
```
user1 : user4 user8 ...(最为相似的前K个用户)
user2 : user5 user9 ...
......
```

### 思路

第一次MapReduce：

将冒号后的粉丝切分，并两两组合成key如：4_8, 4_9...

Map 写出（key, 1）

Reduce 统计（key, num）

```
366-598	5
366-599	3
366-600	5
366-601	1
366-602	4
366-603	6
366-604	4
366-605	4
366-606	4
366-607	4
......
```

第二次MapReduce：

每行切分，分别写两个粉丝的相似度，Map 写出 (336, 602_4) 和 (602, 336_4)

Reduce 对 key 的所有相似度进行排序写出

```
0	327_10 476_8 291_8 920_8 928_8 784_8 ....
1	113_8 118_8 21_8 79_8 808_7 812_7 619_7 ....
2	620_7 875_7 876_7 644_7 677_7 217_7 235_7 ....
......
```

# 共同好友

## 数据

### 数据格式

冒号前是一个用户，冒号后是该用户的所有好友（数据中的好友关系是单向的）

格式：person:friend1,friend2...

```
A:B,C,D,F,E,O
B:A,C,E,K
C:F,A,D,I
D:A,E,F,L
E:B,C,D,M,L
F:A,B,C,D,E,O,M
G:A,C,D,E,F
H:A,C,D,E,O
I:A,O
J:B,O
K:A,C,D
L:D,E,F
M:E,F,G
O:A,H,I,J
```


### 需求

求出哪些人两两之间有共同好友，及他俩的共同好友都有谁

### 思路

第一次MapReduce，Map写出(friend, person)，Reduce(friend, persons)

得到A、B、、等是谁的好友
```
A	I,K,C,B,G,F,H,O,D,
B	A,F,J,E,
C	A,E,B,H,F,G,K,
D	G,C,K,A,L,F,E,H,
...

friend  person1,person2...
```

第二次MapReduce, Map写出(person1-person2, friend)，Reduce统计

等到两两之间的共同好友
```
A-B	E C 
A-C	D F 
A-D	E F 
A-E	D B C 
A-F	O B C D E 
......
```

# 代码

## 代码地址

github：https://github.com/sardineYJA/Hadoop-MapReduce

## 粉丝相似度 spark

```java
public class WeiboFolloerSpark {

    public static void main(String[] args) {

        SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        long startTimeMillis = System.currentTimeMillis();


        // args = new String[] {"D:\\in\\Small Dataset.txt", "D:\\out2"};

        SparkConf sparkConf= new SparkConf()
                .setAppName("WeiboFolloerSpark");
                //.setMaster("local[*]");
        JavaSparkContext jsc = new JavaSparkContext(sparkConf);
        JavaRDD<String> line = jsc.textFile(args[0]);

        // (646-482,1), (646-485,1), ...
        JavaPairRDD<String, Integer> allPairRdd = line
                .repartition(1000)          // 1000个分区100个Task
                .flatMapToPair(new PairFlatMapFunction<String, String, Integer>() {
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

        // 求和 (646-482,3), (646-485,6)
        JavaPairRDD<String, Integer> pairRdd = allPairRdd.reduceByKey(new Function2<Integer, Integer, Integer>() {
            @Override
            public Integer call(Integer v1, Integer v2) throws Exception {
                return v1 + v2;
            }
        });

        // (121,851_2), (851,121_2)
        JavaPairRDD<String, String> pairResult = pairRdd.flatMapToPair(new PairFlatMapFunction<Tuple2<String, Integer>, String, String>() {
            @Override
            public Iterator<Tuple2<String, String>> call(Tuple2<String, Integer> tuple2) throws Exception {
                List<Tuple2<String, String>> list = new ArrayList<>();

                String[] followers = tuple2._1.split("-");
                list.add(new Tuple2<String,String>(followers[0], followers[1]+"_"+tuple2._2.toString()));
                list.add(new Tuple2<String,String>(followers[1], followers[0]+"_"+tuple2._2.toString()));
                return list.iterator();
            }
        });

        // value 进行连接：324_5 357_3 784_4 .....
        JavaPairRDD<String, String> connPairResult = pairResult.reduceByKey(new Function2<String, String, String>() {
            @Override
            public String call(String s, String s2) throws Exception {
                return s + " " + s2;
            }
        });

        // value 切分排序：324_5 357_3 784_4 .....
        JavaPairRDD<String, String> mapResult = connPairResult.mapToPair(new PairFunction<Tuple2<String, String>, String, String>() {
            @Override
            public Tuple2<String, String> call(Tuple2<String, String> t) throws Exception {
                String[] values = t._2.split(" ");
                // 排序
                Map<String, Integer> map = new HashMap<>();
                for (String value : values) {
                    if (value.isEmpty()) {
                        continue;
                    }
                    String[] follower_simi = value.split("_");
                    map.put(follower_simi[0], Integer.valueOf(follower_simi[1].toString()));
                }

                // 对 HashMap 排降序
                List<Map.Entry<String, Integer>> list = new ArrayList<>(map.entrySet());
                list.sort(new Comparator<Map.Entry<String, Integer>>() {
                    @Override
                    public int compare(Map.Entry<String, Integer> o1, Map.Entry<String, Integer> o2) {
                        return o2.getValue().compareTo(o1.getValue());
                    }
                });

                StringBuffer sb = new StringBuffer();
                for (int i = 0; i < list.size(); i++) {
                    sb.append(list.get(i).getKey()).append("_").append(list.get(i).getValue()).append(" ");
                }
                return new Tuple2<>(t._1, sb.toString());
            }
        });

        // key 由 String 转 Integer
        JavaPairRDD<Integer, String> intPairRDD = mapResult.mapToPair(new PairFunction<Tuple2<String, String>, Integer, String>() {
            @Override
            public Tuple2<Integer, String> call(Tuple2<String, String> t) throws Exception {
                return new Tuple2<>(Integer.valueOf(t._1), t._2);
            }
        });

        JavaPairRDD<Integer, String> sortPairRDD = intPairRDD.sortByKey(true);  // 升序
        // 设置为一个分区
        sortPairRDD.coalesce(1).saveAsTextFile(args[1]);

        long endTimeMillis = System.currentTimeMillis();
        System.out.println("Start Time : " + df.format(startTimeMillis));
        System.out.println("End Time : " + df.format(endTimeMillis));
        System.out.println("Spend Time : " + (endTimeMillis - startTimeMillis)/1000.0 + "s");
    }
}
```

修改，打包，将含依赖jar上传

```sh
bin/spark-submit \
--class test.WeiboFolloerSpark \
--master spark://172.16.7.124:7077 \
--executor-memory 4G \
--total-executor-cores 10 \
--driver-cores 2 --driver-memory 1g \
myJar/test-WeiboFolloerSpark-with-dependencies.jar \
hdfs://172.16.7.124:9000/weibo/Small.txt \
hdfs://172.16.7.124:9000/weibo/SmallOut
```
```
hdfs://172.16.7.124:9000/weibo/Large.txt \
hdfs://172.16.7.124:9000/weibo/LargeOut
```


## 相关错误

> WARN TaskSchedulerImpl: Initial job has not accepted any resources; check your cluster UI to ensure that workers are registered and have sufficient resources

原因分析：将spark-submit的内存核数降低一点



> Unsupported major.minor version 52.0

原因分析：IDEA 打包jar使用的是jdk1.8，linux系统安装的也是jdk1.8。之前运行，一段一段时间后spark-submit报错，提示spark环境不可运行jdk1.8，说明spark并没有使用安装的jdk1.8，此时需要在spark-env.sh增加`export JAVA_HOME=`，这样既可保证spark-submit提交运行的是1.8。



> org.apache.spark.rpc.RpcTimeoutException: Futures timed out after [10 seconds]. This timeout is controlled by spark.executor.heartbeatInterval

> java.lang.OutOfMemoryError: GC overhead limit exceeded

> org.apache.spark.rpc.RpcTimeoutException: Futures timed out after [10 seconds]. This timeout is controlled by spark.executor.heartbeatInterval

Spark Web 监控显示

> ExecutorLostFailure (executor driver exited caused by one of the running tasks) Reason: Executor heartbeat timed out after 123186 ms


分析原因：Large.txt 数据过大，发生内存溢出，flatMapToPair的时候两两之间产生new Tuple();数量过于庞大。本人只是用了一台机器测试。

flatMapToPair操作之前调用repartition方法，rdd.repartition(10000)重写分区成10000个，在不增加内存的情况下，通过减少每个Task的大小，以便达到每个Task即使产生大量的对象Executor的内存也能够装得下。


## 增加分区后的错误

> WARN HeartbeatReceiver: Removing executor 0 with no recent heartbeats: 147906 ms exceeds timeout 120000 ms

> ERROR TaskSchedulerImpl: Lost executor 0 on 172.16.7.124: Executor heartbeat timed out after 147906 ms

> WARN TaskSetManager: Lost task 4.0 in stage 1.0 (TID 8, 172.16.7.124, executor 0): ExecutorLostFailure (executor 0 exited caused by one of the running tasks) Reason: Executor heartbeat timed out after 147906 ms

> WARN TaskSetManager: Lost task 1.1 in stage 1.0 (TID 21, 172.16.7.124, executor 1): FetchFailed(null, shuffleId=0, mapId=-1, reduceId=1, message= org.apache.spark.shuffle.MetadataFetchFailedException: Missing an output location for shuffle 0


再增加.persist(StorageLevel.DISK_ONLY()); 进行测试。

```sh
bin/spark-submit \
--class test.WeiboFolloerSpark \
--master spark://172.16.7.124:7077 \
--executor-memory 4G \
--total-executor-cores 10 \
--driver-cores 2 --driver-memory 1g \
myJar/test.WeiboFolloerSpark-p1000-D.jar \
hdfs://172.16.7.124:9000/weibo/Large.txt \
hdfs://172.16.7.124:9000/weibo/lp1000D
```




