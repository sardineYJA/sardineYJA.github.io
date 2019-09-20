---
layout: post
title: "RDD函数"
date: 2019-06-25
description: "介绍一下Spark Core的RDD函数"
tag: 大数据

---

# 简介

spark core

## Transformation

```java
1. map(func)
// 每个元素输入到func中转换
sc.parallelize(1 to 3).map(_*2)
// Array(2, 4, 6)


2. filter(func) 
// 由进过func函数计算返回true的输入元素组成
sc.parallelize(Array("123", "345", "567")).filter(_.contains("3"))
// Array(123, 345)


3. flatMap(func)  
// 与map不同在于每个输入元素可以映射成0或多个输出元素
sc.parallelize(1 to 3).flatMap(1 to _)
// flatMap Array(1, 1,2, 1,2,3)


4. mapPartitions(func)   
// 假设有N个元素，有M个分区，那么map的函数的将被调用N次,而mapPartitions被调用M次,一个函数一次处理所有分区
val rdd1 = sc.parallelize(List(("AA","female"),("BB","male"),("CC","female"),("DD","male")))
def partitionsFun(iter:Iterator[(String, String)]): Iterator[String] ={
  var woman = List[String]()
  while (iter.hasNext) {
    val next = iter.next()
    next match {
      case (_,"female") => woman = next._1 :: woman   // 拼接
      case _ =>
    }
  }
  woman.iterator
}
val result1 = rdd1.mapPartitions(partitionsFun)
result1.collect().foreach{println}


5. mapPartitionsWithIndex(func)
// 类似mapPartitions，但func带有一个整数参数表示分片的索引值
def partitionsFunWithIndex(index:Int, iter:Iterator[(String,String)]): Iterator[String] ={
  var woman = List[String]()
  while (iter.hasNext) {
    val next = iter.next()
    next match {
      case (_,"female") => woman = index + next._1 :: woman
      case _ =>
     }
  }
  woman.iterator
}
val result2 = rdd1.mapPartitionsWithIndex(partitionsFunWithIndex)
result2.collect().foreach{println}


6. sample(withReplacement, fraction, seed) 
// withReplacement表示是否放回；fraction表示抽样比例；seed为随机数种
sc.parallelize(1 to 10).sample(true, 0.5, System.currentTimeMillis())


7. takeSample()   
// 这个是action操作


8. union(otherDataset)
// 求并集，不会去重的
sc.parallelize(1 to 3).union(sc.parallelize(3 to 5))
// Array(1,2,3, 3,4,5)


9. intersection(otherDataset)
// 求交集
sc.parallelize(1 to 3).intersection(sc.parallelize(2 to 5))
// Array(2, 3)


10. distinct([numTasks])      
// 去重,可选的numTasks参数,默认8个
sc.parallelize(List(1,1,2,2)).distinct(2)
// Array(1,2)


11. partitionBy()
// 进行分区
sc.parallelize(Array((1,"a"), (2,"b"), (3,"c"))).partitionBy(
	new org.apache.spark.HashPartitioner(2))
rdd.partitions.size


12. reduceByKey(func, [numTasks]) 
// 相同key的value进行func
rdd.reduceByKey((x,y) => x+y)


13. groupByKey()
// 将相同key的value形成一个sequence
sc.parallelize(1 to 10).map(k => (k,1)).groupByKey()
// Array(key, Iterable[Int])
// 对后续Iterable[Int]求和：.map(t=>t._1, t._2.sum)


14. combineByKey[C](
	createCombiner: V => C,         // 第一次遇到的K，将其V进行运算
	mergerValue: (C, V) => C,       // 当前分区已遇到过的K，将其V与累加器进行运算
	mergerCombiners: (C, C) => C)   // 多个分区合并
// 对相同K，把V合并成一个集合
val scores = Array(("Fred", 88), ("Fred", 95), ("Fred", 91),
                   ("Wilma", 93), ("Wilma", 95), ("Wilma", 98))
val input = sc.parallelize(scores)
val combine = input.combineByKey(
  (v) => (v, 1),                                 // (88, 1)   (93,1)  ...
  (acc:(Int,Int), v) => (acc._1+v, acc._2+1),    // (88+95, 1+1)  (183+91, 2+1)  ...
  (acc1:(Int,Int), acc2:(Int,Int)) => (acc1._1+acc2._1, acc1._2+acc2._2)
)
// Array((Fred,(274,3)), (Wilma,(286,3)))
val result = combine.map{
  case (key, value) => (key, value._1/value._2.toDouble)
}
// Array((Fred,91.33333333333333), (Wilma,95.33333333333333))


15. aggregateByKey(zeroValue:U, [partitioner: Partitioner])(seqOp: (U, V) => U, combOp: (U, U) => U)
// 相同K，V进行seqOp和combOp操作
// 按照K分组，U作为初始值与同分区的V进行SeqOp运算，合并不同分区的V进行comOp运算
val rdd = sc.parallelize(List((1,3),(1,2),(1,4),(2,3),(3,6),(3,8)),3)
rdd.aggregateByKey(0)(math.max(_,_), _+_)
// 六个元素分三个区seqOp:(1,3)--(1,4)(2,3)--(3,8)进行comOp运算：Array((3,8), (1,7), (2,3))
rdd.aggregateByKey(0)(math.max(_,_), math.max(_,_))
// Array((3,8), (1,4), (2,3))


16. foldByKey(zeroValue: V)(func:(V,V) => V):RDD[(K,V)]
// aggregateByKey的简化即seqOp和combOp一样
rdd.foldByKey(0)(math.max(_,_))


17. sortByKey([ascending], [numTasks])    
// 对key排序，truc升序
sc.parallelize(Array((2,"b"), (1,"a"), (3, "c"))).sortByKey(true)


18. sortBy(func, [ascending], [numTasks]) 
// 元素先进行func后再排序，但是元素不变
sc.parallelize(1 to 5).sortBy(x=>x%3)
// Array(3, 1, 4, 2, 5)


19. join(otherDataset, [numTasks])   
// (K,V)和(K,W) => (K,(V,W))
sc.parallelize(Array((1,"a"),(2,"b"))).join(sc.parallelize(Array((1,"c"),(2,4))))
// rray((1,(a,c)), (2,(b,4)))


20. cogroup(otherDataset, [numTasks])
// (K,V)和(K,W)返回(K,(Iterable<V>,Iterable<W>))
sc.parallelize(Array((1,"a"),(2,"b"))).cogroup(sc.parallelize(Array((1,"c"),(2,4))))
// Array((1,(CompactBuffer(a),CompactBuffer(c))), (2,(CompactBuffer(b),CompactBuffer(4))))


21. cartesian(otherDataset)  
// 笛卡尔积
sc.parallelize(1 to 3).cartesian(sc.parallelize(4 to 5))
// Array((1,4), (1,5), (2,4), (2,5), (3,4), (3,5))


22. pipe(command, [envVars]) 
// 执行脚本
rdd.pipe("/home/jiaoben.sh")


23. coalesce(numPartitions)  
// 缩减分区数，用于大数据集过滤后，提高小数据集的执行效率
sc.parallelize(1 to 16,4).coalesce(3).partitions.size
// 3


24. repartition(numPartitions)
// 修改分区数，coalesce只能减少
sc.parallelize(1 to 16,4).repartition(8).partitions.size
// 8


25. repartitionAndSortWithinPartitions(partitioner)
// 与repartition函数不同，它在给定的partitioner内部进行排序，性能比repartition要高


26. glom()   
// 将每个分区形成一个数组
sc.parallelize(1 to 16, 4).glom().collect()
// Array(Array(1,2,3,4), Array(5,6,7,8), Array(9,10,11,12), Array(13,14,15,16))


27. mapValues(func)  
// 只对V操作
sc.parallelize(Array((1,"a"), (2,"b"))).mapValues(_+"T")
// Array((1,aT), (2,bT))


28. subtract() 
// 计算差集
sc.parallelize(3 to 5).subtract(sc.parallelize(1 to 3))
// Array(4, 5)
```

## Action

```java
1. reduce(func)
// 通过func聚集所有元素
sc.makeRDD(1 to 10).reduce(_+_)
// 55

2. collect()
// 在驱动程序中，以数组的形式返回数据集的所有元素

3. count()
// rdd.count() 元素个数

4. first()
// rdd.first() 取第一个元素，take(1)

5. take(n)   
// 取出前n个元素
sc.makeRDD(1 to 10, 2).take(5)
// Array(1,2,3,4,5)

6. takeSample(withReplacement, num, [seed])
// withReplacement表示是否放回；num表示数量；seed为随机数种
sc.parallelize(1 to 10).takeSample(true, 5, System.currentTimeMillis())

7. takeOrder(n)  
// rdd.rakeOrder(3) 升序排序返回前n个

8. top(n)         
// rdd.top(2) 降序排序返回前n个


9. aggregate(zeroValue:U)(seqOp:(U,T)=>U, combOp:(U,U)=>U)
// (没有KV对要求)初始值与当前分区值进行seqOp，每个分区结果与初始值进行combOp
var rdd = sc.makeRDD(1 to 10, 2)
rdd.aggregate(1)({(x:Int, y:Int) => x+y},{(a:Int, b:Int) => a+b})
// 58，两个分区seqOp和一个combOp即在总和上加了三个初始值


10. fold(num)(func)
// aggregate的简化，seqOp与combOp一样
rdd.fold(1)(_+_)

11. saveAsTextFile(path)      
// 保存成文件

12. saveAsSequenceFile(path)  
// 以Hadoop sequencefile格式保存

13. saveAsObjectFile(path)    
// 序列化成对象

14. countByKey()    
// 计算K的个数

15. foreach(func)   
// 每个元素进行func函数
```

```java
// 数值RDD的统计操作
1. count()
2. mean()
3. sum()
4. max()
5. min()
6. variance()        // 方差
7. sampleVariance()  // 采样集的方差
8. stdev()           // 标准差
9. sampleStdev()     // 采样集的方差
```


