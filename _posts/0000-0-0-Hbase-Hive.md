---
layout: post
title: "Hbase 结合 Hive"
date: 2019-09-10
description: "Hbase 系列"
tag: HBase

---


## Hbase 与 Hive

通过关联，可以借助Hive来分析HBase表中的数据。Hbase数据库的缺点在于—-语法格式异类，没有类sql的查询方式，因此在实际的业务当中操作和计算数据非常不方便，但是Hive就不一样了，Hive支持标准的sql语法，于是我们就希望通过Hive这个客户端工具对Hbase中的数据进行操作与查询，进行相应的数据挖掘。


## 环境变量

$ export HBASE_HOME=/.../hbase
$ export HIVE_HOME=/../hive

将hbase/lib的`hbase-*.jar`复制到hive/lib和hadoop/lib下，（可根据报错，选择将某些jar复制过去）


## hive-site.xml

```xml
<property>
    <name>hive.zookeeper.quorum</name>
    <value>172.16.7.124</value>
</property>
```


## 在Hive中创建表同时关联Hbase表

创建Hive表，关联HBase表，插入数据到Hive表的同时能够影响HBase

```sql
create external table hive_hbase_student(rowkey int, name string, sex string, age int) 
stored by 'org.apache.hadoop.hive.hbase.HBaseStorageHandler'
with serdeproperties ("hbase.columns.mapping"=":key,info:name,info:sex,info:age")
tblproperties("hbase.table.name"="hbase_hive_student");
```

第一种情况：hive和hbase表都不存在

第二种情况：hive表存在（有数据），hbase表不存在

第三种情况：hive表不存在，hbase表存在（有数据）



## 导入数据

注：不能将数据直接load进Hive所关联HBase的那张表中

通过临时表导入：
```sql
create table temp(rowkey int, name string, sex string, age int)
row format delimited fields terminated by '\t';

load data local inpath '/../1.txt' into table temp;

insert into table hive_hbase_student select * from temp;
```



