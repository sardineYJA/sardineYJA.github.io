---
layout: post
title: "Redis的介绍"
date: 2019-03-04
description: "简单介绍Redis安装教程"
tag: 数据库

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


# 安装
window下载安装：https://github.com/microsoftarchive/redis/releases
直接安装msi软件，并增加环境路径

## 启动错误
命令：`redis-server.exe redis.windows.conf`

提示：
> Invalid argument during startup: Failed to open the .conf file: redis.windows.conf CWD=C:\Users\yang

命令：`redis-server.exe`

提示：
> Warning: no config file specified, using the default config. In order to specify a config file use redis-server.exe /path/to/redis.conf
> Creating Server TCP listening socket *:6379: bind: No such file or directory


命令：`redis-server e:\Redis\redis.windows.conf`

提示：
> Creating Server TCP listening socket *:6379: bind: No error
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

> 注意关闭cmd命令即关闭Redis

## 部署Redis
命令：`redis-server --service-install e:\Redis\redis.windows.conf`
提示：
> HandleServiceCommands: system error caught. error code=1073, message = CreateService failed: unknown error
原因：系统服务中已经存在
卸载再安装：`redis-server --service-uninstall`
启动服务：`redis-server --service-start`
停止服务：`redis-server --service-stop`


# 参考：
https://www.cnblogs.com/lixihuan/p/6815730.html
https://www.cnblogs.com/angelyan/p/10449892.html
https://www.cnblogs.com/bigben0123/p/9115597.html


