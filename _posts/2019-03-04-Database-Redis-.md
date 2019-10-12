---
layout: post
title: "Redis的介绍"
date: 2019-03-04
description: "简单介绍Redis安装教程"
tag: Database

---
# 简介

## 介绍
NoSQL技术，这是一种基于内存的数据库，并且提供一定的持久化功能。Redis和MongoDB是当前使用最广泛的NoSQL（Not Only SQL非关系型的数据库）。Redis是一个开源的使用ANSI C语言编写、支持网络、可基于内存亦可持久化的日志型、Key-Value数据库。在项目中使用redis，主要是从两个角度去考虑:性能和并发。性能：在碰到需要执行耗时特别久，且结果不频繁变动的SQL，就特别适合将运行结果放入缓存。这样，后面的请求就去缓存中读取，使得请求能够迅速响应。并发：在大并发的情况下，所有的请求直接访问数据库，数据库会出现连接异常。这个时候，就需要使用redis做一个缓冲操作，让请求先访问到redis，而不是直接访问数据库。

## 单线程redis快的原因
1. redis是单线程工作模型
2. 纯内存操作
3. 单线程操作，避免了频繁的上下文切换
4. 采用了非阻塞I/O多路复用机制

## 缺点
1. 缓存和数据库双写一致性问题
2. 缓存雪崩问题
3. 缓存击穿问题
4. 缓存的并发竞争问题


# Windows安装
window下载安装：https://github.com/microsoftarchive/redis/releases

直接安装msi软件，并增加环境路径

## 启动错误
命令：`redis-server.exe redis.windows.conf`

提示：
> Invalid argument during startup: Failed to open the .conf file: redis.windows.conf CWD=C:\Users\yang

命令：`redis-server.exe`

提示：
> Warning: no config file specified, using the default config. In order to specify a config file use redis-server.exe /path/to/redis.conf
> Creating Server TCP listening socket :6379: bind: No such file or directory


命令：`redis-server e:\Redis\redis.windows.conf`

提示：
> Creating Server TCP listening socket :6379: bind: No error

解决：
```
redis-cli.exe
shutdown
exit
```

此时启动命令可以：
```
reids-server
redis-server.exe
redis-server e:\Redis\redis.windows.conf
```

> 注意关闭cmd窗口即关闭Redis

新的窗口连接: `redis-cli -h 127.0.0.1 -p 6379`

## 部署Redis
命令：`redis-server --service-install e:\Redis\redis.windows.conf`

提示：
> HandleServiceCommands: system error caught. error code=1073, message = CreateService failed: unknown error

原因：系统服务中已经存在
```
redis-server --service-uninstall      // 卸载再安装
redis-server --service-start          // 启动服务
redis-server --service-stop           // 停止服务
```


# Linux安装

介绍：https://github.com/antirez/redis

安装gcc：yum -y install gcc gcc-c++

## 安装tcl

> You need tcl 8.5 or newer in order to run the Redis test

下载：`wget http://downloads.sourceforge.net/tcl/tcl8.6.1-src.tar.gz`

解压：`tar -xzvf tcl8.6.1-src.tar.gz  -C ../module`  

进入目录：`cd  /tcl8.6.1/unix/`

编译：
```sh
./configure 
make  
make install  
```

## 安装redis

下载：`wget http://download.redis.io/releases/redis-3.2.12.tar.gz`

解压：`tar -zxvf redis-3.2.12.tar.gz -C ../module`

进入目录redis-3.2.12：`make`

进入目录redis-3.2.12/src：`make test`

> [exception]: Executing test client: NOREPLICAS Not enough good slaves to write..
NOREPLICAS Not enough good slaves to write.

虽然报错，却可以运行：`src/redis-server redis.conf`

新窗口连接：`src/redis-cli`

完整的命令：redis-cli -h ip地址 -p 端口号 -a 密码


## 修改成后台运行

修改redis.conf，将daemonize属性改为yes

启动：`src/redis-server redis.conf`

查看：`netstat -anotp|grep 6379`


## 性能测试

启动：`src/redis-benchmark`

```
100000 requests completed in 3.14 seconds   #100000个请求完成于 3.14 秒
50 parallel clients                         #每个请求有50个并发客户端
3 bytes payload                             #每次写入3字节
keep alive: 1                               #保持1个连接
```

命令：`./redis-benchmark -h localhost -p 6379 -c 100 -n 100000`

参数解析

```
-h    设置检测主机IP地址，默认为127.0.0.1
-p    设置检测主机的端口号，默认为6379
-s<socket>    服务器套接字(压倒主机和端口)
-c    并发连接数
-n    请求数
-d    测试使用的数据集的大小/字节的值(默认3字节)
-k    1：表示保持连接(默认值)0：重新连接
-r    SET/GET/INCR方法使用随机数插入数值，设置10则插入值为rand:000000000000 - rand:000000000009
-P    默认为1(无管道)，当网络延迟过长时，使用管道方式通信(请求和响应打包发送接收)
-q    简约信息模式，只显示查询和秒值等基本信息。
--csv    以CSV格式输出信息
-l    无线循环插入测试数据，ctrl+c停止
-t<tests>    只运行<tests>测试逗号分隔的列表命令，如：-t ping,set,get    
-I    空闲模式。立即打开50个空闲连接和等待。
```

## 其他





# reference

https://www.cnblogs.com/lixihuan/p/6815730.html

https://www.cnblogs.com/angelyan/p/10449892.html

https://www.cnblogs.com/bigben0123/p/9115597.html

https://www.runoob.com/redis/redis-backup.html

https://blog.csdn.net/weixin_34320159/article/details/85088333
