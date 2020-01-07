---
layout: post
title: "数据库读写分离"
date: 2019-10-14
description: "数据库读写分离"
tag: Database

---

# 概述

## 原理

通过数据冗余将数据库读写操作分散到不同的节点上

* 数据库搭建主从服务器，一主一从或一主多从

* 主机负责写操作，从机负责读操作

* 主机通过复制将数据同步到从机，每天数据库服务器都存储了所有的数据

* 业务服务器将写操作发送给数据库主机，将读操作发送给数据库从机


![png](/images/posts/all/数据库读写分离基本架构图.png)


## 适用场景

* 并发量大，单机已不能满足请求

* 读远大于写

* 数据实时性要求不那么严格的业务



# 问题

## 主从复制延迟问题

![png](/images/posts/all/解决主从复制延迟问题.png)


## 读写操作分配机制问题

如何将读写操作区分开来，然后访问不同的数据库服务器？

方案一：客户端程序代码封装实现

![png](/images/posts/all/客户端程序代码封装实现-架构图.png)

![png](/images/posts/all/客户端程序代码封装实现-读写操作分配机制问题.png)

方案二：服务端中间件封装

![png](/images/posts/all/服务端中间件封装-架构图.png)

![png](/images/posts/all/服务端中间件封装-读写操作分配机制问题.png)



# Mysql 主从数据库同步的实现

## 结构图

![png](/images/posts/all/主从数据库同步的实现结构图.jpg)

## binlog 线程、I/O 线程和 SQL 线程

* binlog 线程 ：负责将`主服务器`上的数据更改写入二进制文件（binary log）中。

* I/O 线程 ：负责从`主服务器`上读取二进制日志文件，并写入`从服务器`的中继日志（relay log）中。

* SQL 线程 ：负责读取中继日志并重放其中的 SQL 语句。

## 配置文件

主数据库：编辑 /etc/my.cnf，配置开启Binary log

```sh
# 在[mysqld]标签下面增加以下代码：
server-id=1
log-bin=master-bin
log-bin-index=master-bin.index
```

重启服务，登录查看状态：`show master status;`。
可以查看到File和Position，从数据库需要用到。

从数据库：编辑 /etc/my.cnf

```sh
# 在[mysqld]标签下面增加以下代码：
server-id=2   # 不能和主数据库相同
read-only=on  # 设置该数据库为只读状态
relay-log=slave-relay-bin
relay-log-index=slave-relay-bin.index
```
重新启动


## 关联数据库

从数据库：
```sql
change master to master_host='主数据库IP', master_port=3306,
master_user='用户名', master_password='密码',
master_log_file='File二进制文件名', master_log_pos=Position二进制文件的端口;
```

启动slave同步：

```sql
start slave;
show salve status \G;  # 查看状态
```

数据同步是根据二进制的日志文件进行的，一开始的状态两个数据库必须保持数据库名字相同，和表的名字相同，否则会出现找不到数据库的错误。


# reference

https://blog.csdn.net/X5fnncxzq4/article/details/83747407

https://blog.csdn.net/starlh35/article/details/78735510
