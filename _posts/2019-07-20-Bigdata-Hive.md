---
layout: post
title: "Hive"
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


## SQL转化为MapReduce

- Antlr定义SQL的语法规则，完成SQL词法，语法解析，将SQL转化为抽象语法树AST Tree

- 遍历AST Tree，抽象出查询的基本组成单元QueryBlock

- 遍历QueryBlock，翻译为执行操作树OperatorTree

- 逻辑层优化器进行OperatorTree变换，合并不必要的ReduceSinkOperator，减少shuffle数据量

- 遍历OperatorTree，翻译为MapReduce任务

- 物理层优化器进行MapReduce任务的变换，生成最终的执行计划


## hive内部表和外部表的区别

- 内部表：加载数据到hive所在的hdfs目录，删除时，元数据和数据文件都删除 

- 外部表：不加载数据到hive所在的hdfs目录，删除时，只删除表结构。


# 安装

## hive

1. 下载：http://archive.apache.org/dist/hive/

2. 解压：`tar -zxvf apache-hive-1.2.1-bin.tar.gz -C /opt/module/`

3. 配置文件：`cp hive-env.sh.template hive-env.sh`
```
配置HADOOP_HOME路径
export HADOOP_HOME=/opt/module/hadoop-2.7.2
配置HIVE_CONF_DIR路径
export HIVE_CONF_DIR=/opt/module/hive/conf
```

4. 必须启动hdfs和yarn

5. 启动hive：`bin/hive`

6. 查看数据库：`show databases;`

如果多开hive窗口会报错，原因是：Metastore默认存储在自带的derby数据库中，推荐使用MySQL存储Metastore


## Metastore元数据配置到MySQL

1. 下载Jar：mysql-connector-java-5.1.37-bin.jar

2. 将其放到hive/lib/目录下

3. 创建hive/conf/hive-site.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
        <property>
                <name>hive.exec.scratchdir</name>
                <value>/tmp/hive</value>
        </property>
        <property>
                <name>hive.metastore.warehouse.dir</name>
                <value>hdfs://172.16.7.124:9000/hive/warehouse</value>
        <description>location to default database for the warehouse</description>
        </property>
        <property>
                <name>javax.jdo.option.ConnectionURL</name>
                <value>jdbc:mysql://172.16.7.124:3306/hiveDB?createDatabaseIfNotExist=true&amp;characterEncoding=UTF-8&amp;useSSL=false</value>
        <description>Hive access metastore using JDBC connectionURL</description>
        </property>
        <property>
                <name>javax.jdo.option.ConnectionDriverName</name>
                <value>com.mysql.jdbc.Driver</value>
        </property>
        <property>
                <name>javax.jdo.option.ConnectionUserName</name>
                <value>root</value>
        </property>
        <property>
                <name>javax.jdo.option.ConnectionPassword</name>
                <value>root123456</value>
        <description>password to access metastore database</description>
        </property>
        <property>
                <name>javax.jdo.option.Multithreaded</name>
                <value>true</value>
        </property>
        <property>
                <name>hive.metasotre.schema.verification</name>
                <value>true</value>
        </property>
</configuration>
```

4. 创建相应目录

```
hdfs dfa -mkdir -p /tmp/hive
hdfs dfs -mkdir -p /hive/warehouse
hdfs dfs -chmod 777 /tmp
hdfs dfs -chmod 777 /hive 
```

5. 必须重启数据库：`service mysql restart`

6. Hive启动：`bin/hive`


## 其他配置

hive-site.xml增加显示当前数据库，表头信息

```xml
<property>
	<name>hive.cli.print.header</name>
	<value>true</value>
</property>

<property>
        <name>hive.cli.print.current.db</name>
        <value>true</value>
</property>
```

Hive运行日志默认存储在：/tmp/yang/hive.log，修改方式

1. 配置文件hive/conf/：cp hive-log4j.properties.template hive-log4j.properties

2. 修改hive.log.dir=/.../hive/logs


HQL中修改参数

```
show databases;      多数命令与MySQL类似

set;                          查看配置信息
set mapred.reduce.tasks;      查看具体某一项
set mapred.reduce.tasks=100;  修改某一项（仅此次有效）  
```



# 操作

## 复杂类型

Hive有三种复杂数据类型Array、Map 和 Struct

```sql
create table test(
        name string,           -- 名字
        friends array<string>, -- ["好友1" , "好友2"]
        children map<string, int>,  -- {"A":10, "B":20}
        address strcut<street:string, city:string> -- {"street":"jiedao", "city":"shenzhen"}
)
row format delimited fields terminated by ',' -- 分隔符
collection items terminated by '_'            -- map struct array 的分隔符
map keys terminated by ':'                    -- map 中的key与value分隔符
lines terminated by '\n';                     -- 行分隔符
```

数据格式：
```
songsong,bingbing_lili,xiao song:18_xiaoxiao song:19,hui long guan_beijing
yangyang,caicai_susu,xiao yang:18_xiaoxiao yang:19,chao yang_beijing
```

导入数据与查看：
```sql
load data local inpath `/data/1.txt` into table test;
select friends[1], children['xiao song'], address.city from test name ="songsong";
```

## 类型转化

隐式类型转换规则

- 任何整数类型都可以隐式地转换为一个范围更广的类型
- 所有整数类型、FLOAT和STRING类型都可以隐式地转换成DOUBLE
- TINYINT、SMALLINT、INT都可以转换为FLOAT
- BOOLEAN类型不可以转换为任何其它的类型

使用CAST操作显示进行数据类型转换

- 例如CAST('1' AS INT)将把字符串'1' 转换成整数1；
- 如果强制类型转换失败，如执行CAST('X' AS INT)，表达式返回空值 NULL。


# 表

```sql
-- 创建表
CREATE [EXTERNAL] TABLE [IF NOT EXISTS] table_name 
[(col_name data_type [COMMENT col_comment], ...)] 
[COMMENT table_comment] 
[PARTITIONED BY (col_name data_type [COMMENT col_comment], ...)] 
[CLUSTERED BY (col_name, col_name, ...) 
[SORTED BY (col_name [ASC|DESC], ...)] INTO num_buckets BUCKETS] 
[ROW FORMAT row_format] 
[STORED AS file_format] 
[LOCATION hdfs_path]
```

- EXTERNAL 创建一个外部表，在建表的同时指定一个指向实际数据的路径（LOCATION），Hive创建内部表时，会将数据移动到数据仓库指向的路径；若创建外部表，仅记录数据所在的路径，不对数据的位置做任何改变。

- COMMENT 为表和列添加注释

- PARTITIONED BY 创建分区表

- CLUSTERED BY 创建分桶表

- SORTED BY 不常用

- STORED AS 指定存储文件类型：SEQUENCEFILE（二进制序列文件）、TEXTFILE（文本）、RCFILE（列式存储格式文件）

- LOCATION ：指定表在HDFS上的存储位置。

## 内部表，外部表

默认创建的表都是所谓的管理表，有时也被称为内部表。
因为这种表，Hive会（或多或少地）控制着数据的生命周期。
Hive默认情况下会将这些表的数据存储在由配置项`hive.metastore.warehouse.dir`
(例如，/user/hive/warehouse)所定义的目录的子目录下。 
当删除一个管理表时，Hive也会删除这个表中数据。管理表不适合和其他工具共享数据。

外部表，Hive并非认为其完全拥有这份数据。删除该表并不会删除掉这份数据，不过描述表的元数据信息会被删除掉。


``` sql
desc formatted 表名;   -- 查看表的类型
alter table 表名 set tblproperties('EXTERNAL'='TRUE');  -- 修改成外部表
-- 注意：('EXTERNAL'='TRUE')和('EXTERNAL'='FALSE')为固定写法，区分大小写！
```

## 分区表

分区表实际上就是对应一个HDFS文件系统上的独立的文件夹，该文件夹下是该分区所有的数据文件。Hive中的分区就是分目录，把一个大的数据集根据业务需要分割成小的数据集。在查询时通过WHERE子句中的表达式选择查询所需要的指定的分区，这样的查询效率会提高很多。

```sql
create table dept_partition(
deptno int, dname string, loc string  -- 字段会增加一个 month
)
partitioned by (month string) -- 创建表时，根据字段分成不同目录。
row format delimited fields terminated by '\t';

load data local inpath '/../2.txt' into table 表名 partition(month='201909');
-- 将数据导入到目标分区

select * from dept_partition where month='201909'
union
select * from dept_partition where month='201908'
-- 多个分区联合查询

alter table 表名 add partition(month="201907");
-- 增加分区

alter table 表名 drop partition(month="201907");
alter table 表名 drop partition(month="201907"), partition(month="201908");
-- 删除分区

show partitions 表名;   -- 查看分区数
desc formatted 表名;    -- 查看分区表结构
```

二级分区表：
```sql
create table dept_partition2(
        deptno int, dname string, loc string
)
partitioned by (month string, day string)
row format delimited fields terminated by '\t';
load data local inpath '/.../3.txt' into table 表名 partition(month='201709', day='13');
```

## 数据直接上传到分区目录

```sql
dfs -mkdir -p /user/hive/warehouse/表名/month=201709/day=12;
dfs -put /.../1.txt  /user/hive/warehouse/表名/month=201709/day=12;
msck repair table 表名;     -- 修复命令 
```

# 其他

## RLIKE

RLIKE子句是Hive中这个功能的一个扩展，其可以通过Java的正则表达式

`select * from person where name RLIKE '[a]';`  名字含a的

## NVL

NVL：给值为NULL的数据赋值，它的格式是NVL(字段, 代替值)
`select nvl(name, -1) from person;` 返回name，空则返回-1

## case 字段 when

```sql
select 
  sum(case sex when '男' then 1 else 0 end) male_count,
  sum(case sex when '女' then 1 else 0 end) female_count
from person;
```

## 排序

order by

sort by : 每个Reducer内部排序，对全局结果集来说不是排序

distribute by : 分区排序，Hive要求DISTRIBUTE BY语句要写在SORT BY语句之前

cluster by : 相当于distribute by和sorts by对同一字段排序。但是排序只能是升序排序，不能指定排序规则为ASC或者DESC。


## 分桶表

分区针对的是数据的存储路径；分桶针对的是数据文件

分区提供一个隔离数据和优化查询的便利方式；分桶是将数据集分解成更容易管理的若干部分的技术

需要设置：
```sql
set hive.enforce.bucketing=true;
set mapreduce.job.reduces=-1;
```

```sql
create table 表名(id int, name string)
clustered by(id) -- 分桶表
into 4 buckets   -- 4个桶
row format delimited fields terminated by '\t';

desc formatted 表名;  -- 查看表结构
load data local inpath '/../1.txt' into table 表名;
```


# 函数

```sql
show functions;     -- 查看自带函数
desc function max;  -- 查看max用法
desc function extended max;  -- 详细信息
```

## 自定义函数

1. 继承org.apache.hadoop.hive.ql.exec.UDF

2. 需要实现evaluate函数，evaluate函数支持重载

3. 打包jar上传

4. hive命令行：add jar /.../Xxx.jar  增加jar

5. 创建function：create [temporary] function 方法名

6. UDF必须要有返回类型，可以返回null，但是返回类型不能为void

```xml
<dependency>
        <groupId>org.apache.hive</groupId>
        <artifactId>hive-exec</artifactId>
        <version>1.2.1</version>
</dependency>
```

```java
public class Lower extends UDF {
        public String evaluate(final String s) {
                if (s==null) {
                        return null;
                }
                return s.toLowerCase();
        }
}
```

测试：
```sql
add jar /../Lower.jar
create temporary function mylower as "com.sxdt.test.Lower";
select mylower(name) from person;
```


# 优化

## fetch

Fetch抓取是指，Hive中对某些情况的查询可以不必使用MapReduce计算。

在hive-default.xml.template文件中hive.fetch.task.conversion默认是more，在全局查找、字段查找、limit查找等都不走mapreduce。

hive.fetch.task.conversion设置成none，然后执行查询语句，都会执行mapreduce程序。

`hive (default)> set hive.fetch.task.conversion=none;`


## 本地模式

Hive可以通过本地模式在单台机器上处理所有的任务。对于小数据集，执行时间可以明显被缩短。

```sql
set hive.exec.mode.local.auto=true;  -- 开启本地mr

-- 设置local mr的最大输入数据量，当输入数据量小于这个值时采用local mr的方式，默认为134217728，即128M
set hive.exec.mode.local.auto.inputbytes.max=50000000;

-- 设置local mr的最大输入文件个数，当输入文件个数小于这个值时采用local mr的方式，默认为4
set hive.exec.mode.local.auto.input.files.max=10;
```

## MapJoin

如果不指定MapJoin或者不符合MapJoin的条件，那么Hive解析器会将Join操作转换成Common Join，
即：在Reduce阶段完成join。容易发生数据倾斜。
可以用MapJoin把小表全部加载到内存在map端进行join，避免reducer处理。

```sql
-- 设置自动选择Mapjoin
set hive.auto.convert.join = true;  -- 默认为true
-- 大表小表的阈值设置（默认25M以下认为是小表）：
set hive.mapjoin.smalltable.filesize=25000000;

```


# reference

https://blog.csdn.net/u010738184/article/details/70893161



