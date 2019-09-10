---
layout: post
title: "error 记录"
date: 2019-09-09
description: "error 记录"
tag: 工具

---


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



