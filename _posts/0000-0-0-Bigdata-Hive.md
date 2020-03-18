---
layout: post
title: "Hive 知识点"
date: 2019-07-20
description: "介绍一下Hive 知识点"
tag: Bigdata

---

# Hive

1. 本质是将HQL转化为MapReduce程序

2. Hive处理的数据存储在HDFS

3. Hive分析数据底层的实现是MapReduce

4. 执行程序运行在Yarn上


## 特点

1. 类SQL语法，避免写MapReduce，减少开发成本，提高效率

2. Hive执行延迟较高，适合对实时性要求不高的场合

3. 对处理小数据没有优势，适合大数据

4. HQL表达能力有限

5. 效率比较低下，调优较难

6. Hive暴力扫描整个数据，因而访问延迟较高


## Hive 架构图

![png](/images/posts/all/Hive架构图.png)

- 用户接口：Client

CLI（hive shell）、JDBC/ODBC(java访问hive)、WEB UI（浏览器访问hive）

- 元数据：Metastore

元数据包括：表名、表所属的数据库（默认是default）、表的拥有者、列/分区字段、表的类型（是否是外部表）、表的数据所在目录等；
默认存储在自带的derby数据库中，推荐使用MySQL存储Metastore

- Hadoop

使用HDFS进行存储，使用MapReduce进行计算

- 驱动器：Driver

1. 解析器（SQL Parser）：将SQL字符串转换成抽象语法树AST，这一步一般都用第三方工具库完成，比如antlr；对AST进行语法分析，比如表是否存在、字段是否存在、SQL语义是否有误。
2. 编译器（Physical Plan）：将AST编译生成逻辑执行计划。
3. 优化器（Query Optimizer）：对逻辑执行计划进行优化。
4. 执行器（Execution）：把逻辑执行计划转换成可以运行的物理计划。对于Hive来说，就是MR/Spark。



## Hive 工作流程

![png](/images/posts/all/Hive工作流程图.jpeg)

1. (执行查询操作)Execute Query：命令行或Web UI之类的Hive接口将查询发送给Driver(任何数据库驱动程序，如JDBC，ODBC等)以执行。

2. (获取计划任务)Get plan：Driver借助查询编译器解析查询，检查语法和查询计划或查询需求。

3. (获取元数据信息)Get Metadata：编译器将元数据请求发送到Metastore(任何数据库)。

4. (发送元数据)：MetaStore将元数据作为对编译器的响应发送出去。

5. (发送计划任务)Send Plan：编译器检查需求并将计划重新发送给Driver。到目前为止，查询的解析和编译已经完成。

6. (执行计划任务)Execute Plan：Driver将执行计划发送到执行引擎。

7. (执行Job任务)Execute Job：在内部，执行任务的过程是MapReduce Job。执行引擎将Job发送到ResourceManager,ResourceManager位于Name节点中，并将job分配给datanode中的NodeManager。在这里，查询执行MapReduce任务。Metadata Ops 在执行的同时，执行引擎可以使用Metastore执行元数据操作。

8. (拉取结果集)Fetch Result：执行引擎将从datanode上获取结果集。

9. (发送结果集至driver)Send Results：执行引擎将这些结果值发送给Driver。

10. (driver将result发送至interface)Send Results Driver：将结果发送到Hive接口。



## SQL转化为MapReduce

- Antlr定义SQL的语法规则，完成SQL词法，语法解析，将SQL转化为抽象语法树AST Tree

- 遍历AST Tree，抽象出查询的基本组成单元QueryBlock

- 遍历QueryBlock，翻译为执行操作树OperatorTree

- 逻辑层优化器进行OperatorTree变换，合并不必要的ReduceSinkOperator，减少shuffle数据量

- 遍历OperatorTree，翻译为MapReduce任务

- 物理层优化器进行MapReduce任务的变换，生成最终的执行计划

总结：`metastore`是一套映射工具，将sql语句转换成对应的job任务区进行执行



## hive内部表和外部表的区别

- 创建内部表时，会将数据移动到数据仓库指向的路径

- 创建外部表，仅记录数据所在的路径， 不对数据的位置做任何改变

- 内部表：加载数据到hive所在的hdfs目录，删除时，元数据和数据文件都删除 

- 外部表：不加载数据到hive所在的hdfs目录，删除时，只删除表结构



## 数据模型

Hive的数据模型主要有：database、table、partition、bucket四部分

![png](/images/posts/all/Hive的数据模型.png)

partition分区是根据某列的值进行粗略的划分，每个分区对应HDFS上的一个目录。

bucket是更加细的划分，按照指定值进行hash，每个桶就是表目录里的一个文件。


## 支持的文件格式

- textfile 存储空间消耗比较大，并且压缩的text 无法分割和合并 查询的效率最低,可以直接存储，加载数据的速度最高

- sequencefile 存储空间消耗最大,压缩的文件可以分割和合并 查询效率高，需要通过text文件转化来加载

- orcfile, rcfile存储空间最小，查询的效率最高 ，需要通过text文件转化来加载，加载的速度最低

- parquet格式是列式存储，有很好的压缩性能和表扫描功能


# 常用配置参数

## hive.fetch.task.conversion=more

hive 拉取模式：
- more 在全局查找、字段查找、limit查找等都不走 mapreduce。
- none 执行查询语句，都会执行 mapreduce 程序。

## hive.exec.mode.local.auto=true

开启本地mr：决定 Hive 是否应该自动地根据输入文件大小，在本地运行。

## hive.auto.convert.join=true

根据输入小表的大小，自动将 Reduce 端的 Common Join 转化为 Map Join，从而加快大表关联小表的 Join 速度。

## hive.map.aggr=true 和 hive.groupby.skewindata=true

开启map端集合，group by 操作支持倾斜的数据（进行合并）。


## hive.mapred.mode=strict

- strict 严格模式，将不允许笛卡尔积。 防止用户执行那些可能意想不到的不好的影响的查询（即耗时巨大）。
- nonstrict 默认非严格模式。


# reference

https://www.jianshu.com/p/b0b77b045fab

https://baijiahao.baidu.com/s?id=1655664783085326263&wfr=spider&for=pc
