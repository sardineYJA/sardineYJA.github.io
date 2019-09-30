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


Hive通过给用户提供的一系列交互接口，接收到用户的指令(SQL)，使用自己的Driver，结合元数据(MetaStore)，将这些指令翻译成MapReduce，提交到Hadoop中执行，最后，将执行返回的结果输出到用户交互接口。


Hive暴力扫描整个数据，因而访问延迟较高，Hive不适合在线数据查询。但是用于MapReduce，Hive可以并行访问数据，在大数据量体现优势。


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


