---
layout: post
title: "Spark 数据倾斜"
date: 2019-09-27
description: "Spark 数据倾斜"
tag: Spark

---


# 数据倾斜


## 数据倾斜表现

- 大部分task都执行特别快，剩下几个task跑得特别慢

- 其他task都执行完了，剩下几个task出现OOM


# 解决方案


## 聚合数据源

每个key聚合出来一条数据：所有的values全部用一种特殊的格式拼接到一个字符串

没有办法对每个key聚合出来一条数据，根据数据字段颗粒度聚合出来多条数据


## 过滤某些key

直接在sql中用where条件，过滤掉某几个key


## 提高 shuffle 操作的 reduce 并行度

将reduce task的数量变多，就可以让每个reduce task分配到更少的数据量，缓解数据倾斜的问题

![png](/images/posts/all/提高shuffle操作的reduce并行度原理.jpg)

shuffle算子(groupByKey、countByKey、reduceByKey）。
在调用的时候，传入进去一个参数。代表了那个shuffle操作的reduce端的并行度。

```java
reduceByKey(func, [numTasks]) 
```


## 使用随机key进行双重聚合

对key进行打散(前面加随机数)，将原先一样的key，变成不一样的key，相当于是将每个key分为多组；

先针对多个组，进行key的`局部聚合`；再去除掉每个key的前缀，然后对所有的key，进行`全局聚合`。

![png](/images/posts/all/使用随机key进行双重聚合原理.jpg)


使用场景：groupByKey、reduceByKey
```java
rdd2 = rdd1.map(lambda x:(str(random.randint(0,10))+"_"+x[0],x[1]))
rdd3 = rdd2.reduceByKey(lambda x,y:x+y)              // 局部聚合
rdd4 = rdd3.map(lambda x:(x[0].split("_")[1],x[1]))
rdd5 = rdd4.reduceByKey(lambda x,y:x+y)              // 全局聚合
```


# 关于两表的join

## reduce join 转化为 map join 

适用场景：两个RDD要进行join，其中一个RDD是数据比较小的。将小的RDD进行collect操作然后设置为broadcast变量，broadcast 出去那个小RDD的数据以后，就会在每个executor的 block manager 中都驻留一份，并确保内存足够存放那个小RDD中的数据。不走shuffle，直接走map，性能也会高很多。

被广播的表需要小于spark.sql.autoBroadcastJoinThreshold所配置的值，默认是10M。

![png](/images/posts/all/broadcast小RDD.png)


但因为被广播的表首先被collect到driver段，然后被冗余分发到每个executor上，所以当表比较大时，采用broadcast join会对driver端和executor端造成较大的压力。


## 对倾斜的 Keys 采样后进行单独的 Join 操作

适用场景：如果两个 RDD 的数据都比较多，且某个key对应的数据量特别多
（导致数据倾斜的key特别多，最好还是不要用下面方法）

1. 采用 SparkRDD 中提供的采样接口 Sample，可以很方便地对全体(如 100 亿条)数掘 进行采样，然后基于采样的数据可以计算出哪个(哪些) Key 的 Values 个数最多 。

2. 把全体数据分成两部分，即把原来的一个 RDD1 变成 RDD11 和 RDD12，其中 RDD11 代表导致数据倾斜的 Key, RDD12 中包含的是不会产生数据倾斜的 Keys。

3. 把 RDDll 和 RDD2 进行 Join 操作，且把 RDD12 和 RDD2 进行 Join 操作， 然后把 Join操作后的结果进行 Union 操作，从而得出和 RDDl 与 RDD2 直接进行 Join 相同的结果。

![png](/images/posts/all/对倾斜的Keys采样后进行单独的Join操作.jpg)


实践：

```python
rdd1 = sc.parallelize((("a",3),("a",2),("n",3),("a",1),
	("n",3),("a",3),("a",45),("m",1),("a",1),("b",23)))
# rdd1是一个二元元组,
# 对rdd1进行随机采样
rdd2 = rdd1.sample(False,0.1,9)
#第二步统计样本中的key排序
rdd3 = rdd2.map(lambda x:(x[0],1))
#第三步进行累加
rdd4 = rdd3.reduceByKey(lambda x,y:x+y)
#第四步反转
rdd5 = rdd4.map(lambda x:(x[1],x[0]))
#第五步找出value值最高的key
targetKey = rdd5.sortByKey(False).take(1)[0][0]
#第六步拆分rdd1,大批数据的rdd
leanRdd = rdd1.filter(lambda x:targetKey==x)
notleanRdd = rdd1.filter(lambda x:targetKey!=x)
waitJoinRdd = sc.parallelize((("a",3), ("a",2), ("n",3), ("a",1), 
	("n",3), ("a",3), ("a",45), ("m",1), ("a",1), ("b",23)))
```

```python
# 分别两个rdd与之join
joinRdd1 = leanRdd.join(waitJoinRdd)
joinRdd2 = notleanRdd.join(waitJoinRdd)
# 合并两个join后的rdd
resultRdd = joinRdd1.union(joinRdd2)
```

改良：对包含倾斜key的rdd，在之前加一个随机数，再需要join的rdd相同的key也加一个随机数，再进行join

```python
# 给leanRdd加随机数
randomNum = str(random.randint(0, 100)
randomedRdd1 = leanRdd.map(lambda x: (str(randomNum) + "-" + x[0], x[1])))
# 过滤出包含相同key的并且顺序加上0-100上的数字或者是一个固定的0-100内得数字
filteredWaitJoinRdd = waitJoinRdd.filter(lambda x: x[0] == targetKey).flatMap(func1)
# join两个rdd
joinRdd1 = randomedRdd1.join(filteredWaitJoinRdd)
joinRdd2 = notleanRdd.join(waitJoinRdd)
# 合并两个join后的rdd
resultRdd = joinRdd1.union(joinRdd2)
```


## 扩容

适用场景：如果两个rdd中倾斜得数据都比较多

1. 选择一个RDD，要用flatMap，进行扩容，将每条数据，映射为多条数据，每个映射出来的数据，都带了一个n以内的随机数，通常来说，会选择10。

2. 将另外一个RDD，做普通的map映射操作，每条数据，都打上一个10以内的随机数。

3. 最后，将两个处理后的RDD，进行join操作。

局限性：

1. 因为两个RDD都很大，所以没有办法去将某一个RDD扩的特别大，一般咱们就是10倍。

2. 如果就是10倍的话，那么数据倾斜问题，的确是只能说是缓解和减轻，不能说彻底解决。


实践：

```python
rdd1 = sc.parallelize((("a", 3), ("a", 2), ("n", 3), ("a", 1), 
	("n", 3), ("a", 3), ("a", 45), ("m", 1), ("a", 1), ("b", 23)))
waitJoinRdd = sc.parallelize((("a", 3), ("a", 2), ("n", 3), ("a", 1),
	("n", 3), ("a", 3), ("a", 45), ("m", 1), ("a", 1), ("b", 23)))
# rdd1每个元素加上个随机数前缀
randomNum = str(random.randint(0, 100)
randomedRdd1 = rdd1.map(lambda x: (randomNum + "-" + x[0], x[1])))
# 待join的每个数字加上一个100以内的顺序数
filteredWaitJoinRdd = waitJoinRdd.flatMap(func1)
# join
resultRdd = randomedRdd1.union(filteredWaitJoinRdd)
```

## hadoop MapReduce 的 Map join


驱动类加载小表的内容，而且无需Reduce阶段
```java
job.addCacheFile(new URL("file://E:/pd.txt"));
job.setNumReduceTasks(0);
```

Mapper类，初始函数setup读取路径文件，切割保存成Map
```java
Map<String, String> pdMap = new HashMap<>();

@Override
protected void setup(Mapper<LongWritable, Text, Text, NullWritable>.Context context) throws IOException, InterruptedException {
	// 获取缓存的文件
	URI[] cacheFiles = context.getCacheFiles();
	String path = cacheFiles[0].getPath().toString();
	
	BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(path), "UTF-8"));
	String line;
	while(StringUtils.isNotEmpty(line = reader.readLine())){
		String[] fields = line.split("\t");
		pdMap.put(fields[0], fields[1]);
	}
	reader.close();
}
```

Mapper类，map函数对另一个表进行读取并一一操作，从Map中找出相应的值

```java
Text k = new Text();
@Override
protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {

	// 获取大表一行
	String line = value.toString();
	String[] fields = line.split("\t");
	String pId = fields[1];
	
	// 从小表中找相应的值，相当于Map端Join
	String pdName = pdMap.get(pId);  
	
	// 拼接写出
	k.set(line + "\t"+ pdName);
	context.write(k, NullWritable.get());
}
```


## Spark 的 Map join

广播小表，大表处理

```java
val little_table = sc.parallelize(Array(("1","华为"),("2","小米"))).collectAsMap()
val little_table_bc = sc.broadcast(little_table)
```

```java
// 大表order_all，使用mapPartition减少创建broadCastMap.value的空间消耗
val res = order_all.mapPartitions(iter =>{
	val map = little_table_bc.value
	val arrayBuffer = ArrayBuffer[(String,String,String)]()

	iter.foreach{case (id,date,sno) =>{
		if(map.contains(id)){
			arrayBuffer.+= ((id, map.getOrElse(id,""), date))
		}
	}}
	arrayBuffer.iterator
})
```


 


# 参考

https://blog.csdn.net/m0_37139189/article/details/100689337

https://www.cnblogs.com/0xcafedaddy/p/7614299.html

