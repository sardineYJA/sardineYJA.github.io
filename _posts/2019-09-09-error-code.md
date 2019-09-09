---
layout: post
title: "error 记录"
date: 2019-09-09
description: "error 记录"
tag: 工具

---

## 数据库

```sql
select 1 from table;
select anycol(任意一行） from table;
select * from table; 
```
 从作用上来说是没有差别的，都是查看是否有记录，一般是作条件查询用的。第一个的1是一常量（可以为任意数值），查到的所有行的值都是它，但从效率上来说，1>anycol>\*，因为不用查字典表。


## src资源文件xml编译

在练习spring时，需要在src目录下创建xml文件。

如果使用的是Eclipse，Eclipse的src目录下的xml等资源文件在编译的时候会自动打包进输出到classes文件夹。Hibernate和Spring有时会将配置文件放置在src目录下，编译后要一块打包进classes文件夹，所以存在着需要将xml等资源文件放置在源代码目录下的需求。

IDEA的maven项目中，默认src目录下的xml等资源文件并不会在编译的时候一块打包进classes文件夹，而是直接舍弃掉。

如下：在IDEA是无法读取到src/applicationContext.xml的

```java
// 实例化IOC对象
ApplicationContext ctx = new ClassPathXmlApplicationContext("applicationContext.xml");
```

解决一：建立src/main/resources文件夹，将xml等资源文件放置到这个目录中。maven工具默认在编译的时候，会将resources文件夹中的资源文件一块打包进classes目录中。

解决二：pom文件增加下面内容，将xml文件放到src/main/java目录下

```xml
<build>
    <resources>
        <resource>
            <directory>src/main/java</directory>
            <includes>
                <include>**/*.xml</include>
            </includes>
        </resource>
    </resources>
</build>
```

`<directory>src/main/java</directory>`资源文件的路径

`<include>**/*.xml</include>`需要编译打包的文件类型是xml文件，如果有其它资源文件也需要打包，可以修改或添加通配符


## 依赖不起作用，受scope影响

> java.lang.NoClassDefFoundError: org/apache/spark/api/java/function/Function
  java.lang.ClassNotFoundException: org.apache.spark.api.java.function.Function

发现xml依赖是scope范围的影响，可直接注释掉，或者IDEA中run -> edit configurations -> include dependencies with "provided" scope 勾选

## oracle依赖不起作用

> java.lang.ClassNotFoundException: oracle.jdbc.OracleDriver

xml即使写了oracle数据库的依赖依然没用，oracle并不提供到中央仓库，可下载后手动加载到本地仓库


## 类需要实现Serializable接口

> java.io.NotSerializableException: MySparkSQL.Person
Serialization stack:

## 缺少org.apache.spark.Logging

Spark 1.5.2升级到2.0之后，运行测试代码spark-stream-kafka报以下错误

下载jar导入项目

> java.lang.NoClassDefFoundError: org/apache/spark/Logging

## 5


