---
layout: post
title: "Spark GraphX"
date: 2019-09-18
description: "Spark GraphX"
tag: Spark

---

# Spark GraphX

Spark GraphX是Spark的一个模块，主要用于进行以图为核心的计算还有分布式图的计算。

GraphX他的底层计算也是RDD计算，他和RDD共用一种存储形态，在展示形态上可以以数据集来表示，也是以图的形式来表示。


## 数据抽象：

- Spark Core : RDD

- Spark SQL : DataFrame, DataSet

- Spark Streaming : DStream

- Spark GraphX : RDPG （Resilient Distributed Property Graph）



## RDPG

顶点：RDD[(VertexId, VD)]

(VertexId, VD) 表示顶点，VertexID表示顶点的ID，是Long类型的别名，VD是顶点的属性，是一个类型参数，可以是任何类型

边：RDD[Edge[ED]]

Edge用来具体表示一个边，Edge里面包含一个ED类型参数来设定的属性，一个源顶点的ID和一个目标顶点的ID

三元组：RDD[EdgeTriplet[VD, ED]]

EdgeTriplet[VD, ED]表示三元组，三元组包含了一个边、边的属性、源顶点ID、源顶点属性、目标顶点ID、目标顶点属性。VD和ED是类型参数，VD表示顶点的属性，ED表示边的属性

图：Graph[VD, ED]



# 例子

![png](/images/posts/all/GraphX例子.PNG)


```xml
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-graphx_2.11</artifactId>
    <version>${spark.version}</version>
    <scope>provided</scope>
</dependency>
```

```java
import org.apache.spark.graphx.{Edge, Graph, VertexId}
import org.apache.spark.rdd.RDD
import org.apache.spark.{SparkConf, SparkContext}
import org.slf4j.LoggerFactory

object HelloWorld {

  val logger = LoggerFactory.getLogger(HelloWorld.getClass)

  def main(args: Array[String]) {

    val conf = new SparkConf().setMaster("local[3]").setAppName("WC")
    val sc = new SparkContext(conf)

    // Create an RDD for the vertices
    val users: RDD[(VertexId, (String, String))] =
      sc.parallelize(Array((3L, ("rxin", "student")), (7L, ("jgonzal", "postdoc")),
        (5L, ("franklin", "prof")), (2L, ("istoica", "prof"))))
    // Create an RDD for edges
    val relationships: RDD[Edge[String]] =
      sc.parallelize(Array(Edge(3L, 7L, "collab"),    Edge(5L, 3L, "advisor"),
        Edge(2L, 5L, "colleague"), Edge(5L, 7L, "pi")))

    val defaultUser = ("John Doe", "Missing")
    // Build the initial Graph
    val graph = Graph(users, relationships, defaultUser)

    // Count all users which are postdocs
    val verticesCount = graph.vertices.filter { case (id, (name, pos)) => pos == "postdoc" }.count
    println(verticesCount)

    // Count all the edges where src > dst
    val edgeCount = graph.edges.filter(e => e.srcId > e.dstId).count
    println(edgeCount)
    sc.stop()
  }
}
```


# GraphX图的构建

## 对于顶点的构建：

```java
// 对于RDD[(VertexId, VD)]这种版本：
     val users: RDD[(VertexId, (String, String))] = sc.parallelize(Array((3L, ("rxin", "student")), (7L, ("jgonzal", "postdoc")),(5L, ("franklin", "prof")), (2L, ("istoica", "prof"))))
// 对于VertexRDD[VD]这种版本：是上面版本的优化版本。
     val users1:VertexRDD[(String, String)] = VertexRDD[(String, String)](users)
```

## 对于边的构建：

```java
// 对于RDD[Edge[ED]]这种版本：
    val relationships: RDD[Edge[String]] = sc.parallelize(Array(Edge(3L, 7L, "collab"),    Edge(5L, 3L, "advisor"),Edge(2L, 5L, "colleague"), Edge(5L, 7L, "pi")))
// 对于EdgeRDD[ED]这种版本：也是边的优化版本。
    val relationships1:EdgeRDD[String] = EdgeRDD.fromEdges(relationships)
```

## 对于Graph图的构建：

```java
//1、通过Graph类的apply方法进行构建如下：Graph[VD: ClassTag, ED: ClassTag]

val graph = Graph(users,relationships) 

def apply[VD: ClassTag, ED: ClassTag](
    vertices: RDD[(VertexId, VD)],
    edges: RDD[Edge[ED]],
    defaultVertexAttr: VD = null.asInstanceOf[VD],
    edgeStorageLevel: StorageLevel = StorageLevel.MEMORY_ONLY,
    vertexStorageLevel: StorageLevel = StorageLevel.MEMORY_ONLY): Graph[VD, ED]
    
// 2、通过Graph类提供fromEdges方法来构建，对于顶点的属性是使用提供的默认属性。

val graph2 = Graph.fromEdges(relationships,defaultUser)

def fromEdges[VD: ClassTag, ED: ClassTag](
    edges: RDD[Edge[ED]],
    defaultValue: VD,
    edgeStorageLevel: StorageLevel = StorageLevel.MEMORY_ONLY,
    vertexStorageLevel: StorageLevel = StorageLevel.MEMORY_ONLY): Graph[VD, ED]


// 3、通过Graph类提供的fromEdgeTuples方法类构建，对于顶点的属性是使用提供的默认属性，对于边的属性是相同边的数量。

val relationships: RDD[(VertexId,VertexId)] = sc.parallelize(Array((3L, 7L),(5L, 3L),(2L, 5L), (5L, 7L)))
val graph3 = Graph.fromEdgeTuples[(String,String)](relationships,defaultUser)

def fromEdgeTuples[VD: ClassTag](
    rawEdges: RDD[(VertexId, VertexId)],
    defaultValue: VD,
    uniqueEdges: Option[PartitionStrategy] = None,
    edgeStorageLevel: StorageLevel = StorageLevel.MEMORY_ONLY,
    vertexStorageLevel: StorageLevel = StorageLevel.MEMORY_ONLY): Graph[VD, Int]

```


# GraphX图的转换

## GraphX 图的基本信息转换

1. graph.numEdges  返回当前图的边的数量
2. graph.numVertices  返回当前图的顶点的数量
3. graph.inDegrees    返回当前图每个顶点入度的数量，返回类型为VertexRDD[Int]
4. graph.outDegrees   返回当前图每个顶点出度的数量，返回的类型为VertexRDD[Int]
5. graph.degrees      返回当前图每个顶点入度和出度的和，返回的类型为VertexRDD[Int]

## GraphX 图的转换操作

```java
def mapVertices[VD2: ClassTag](map: (VertexId, VD) => VD2) (implicit eq: VD =:= VD2 = null): Graph[VD2, ED]
// 对当前图每一个顶点应用提供的map函数来修改顶点的属性，返回一个新的图

def mapEdges[ED2: ClassTag](map: Edge[ED] => ED2): Graph[VD, ED2]  
// 对当前图每一条边应用提供的map函数来修改边的属性，返回一个新图

def mapTriplets[ED2: ClassTag](map: EdgeTriplet[VD, ED] => ED2): Graph[VD, ED2]  
// 对当前图每一个三元组应用提供的map函数来修改边的属性，返回一个新图
```





