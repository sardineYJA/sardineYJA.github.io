---
layout: post
title: "Redis 简介与安装"
date: 2019-03-04
description: "简单介绍Redis安装教程"
tag: Database

---

## 介绍

- NoSQL技术，基于内存的数据库，并且提供一定的持久化功能。

- Redis和MongoDB是当前使用最广泛的NoSQL（Not Only SQL非关系型的数据库）。

- Redis使用ANSI C语言编写、支持网络、可基于内存亦可持久化的日志型、Key-Value数据库。


## 持久化

- 方式一：RDB(Redis DataBase)，功能核心函数rdbSave(生成RDB文件)和rdbLoad（从文件加载内存）

- 方式二：AOF(Append-only file)，每当执行服务器(定时)任务或者函数时flushAppendOnlyFile 函数都会被调用


## 通信协议

- RESP 是redis客户端和服务端之前使用的一种通讯协议

- 特点：实现简单、快速解析、可读性好


## 支持的数据格式

- String
- Hash
- List
- Set
- sorted set


## 持久化

- RDB方式（Redis DataBase）Redis默认的持久化方式。按照一定的时间周期策略把内存的数据以快照的形式保存到硬盘的二进制文件。

- AOF方式（Append-only file）Redis会将每一个收到的写命令都通过Write函数追加到文件最后，类似于MySQL的binlog。当Redis重启是会通过重新执行文件中保存的写命令来在内存中重建整个数据库的内容。

比较：

- aof文件比rdb更新频率高，优先使用aof还原数据

- aof比rdb更安全也更大

- rdb性能比aof好

- 如果两个都配了优先加载AOF



## 快速

- 纯内存操作

- 单线程操作，避免了频繁的上下文切换

- 采用了非阻塞I/O多路复用机制


## 缺点

- 缓存雪崩问题：缓存层宕掉或Redis恰好将这部分数据全部删光

- 缓存击穿问题：缓存不存在对应的value（恶意的请求会大量不命中），并发量很大去访问DB


## 解决雪崩问题

- 对于“对缓存数据设置相同的过期时间，导致某段时间内缓存失效，请求全部走数据库”情况：

解决方法：在缓存的时候给过期时间加上一个随机值，这样就会大幅度的减少缓存在同一时间过期

- 对于“Redis挂掉了，请求全部走数据库”情况：

解决方法：实现Redis的高可用(Redis 集群)，尽量避免Redis挂掉这种情况发生


## 解决击穿问题

- 用布隆过滤器(BloomFilter)或压缩filter提前拦截，不合法就不让请求到数据库层

- 从数据库找不到时，也将这个空对象设置到缓存里边去。下次再请求的时候，就可以从缓存里边获取了，并设置一个较短的过期时间。



## 过期策略及内存淘汰策略

redis采用的是定期删除+惰性删除策略。

`定期删除`：redis默认每个100ms检查，是否有过期的key，有过期key则删除。但不是每个100ms将所有的key检查一次，而是随机抽取进行检查(如果每隔100ms,全部key进行检查，redis岂不是卡死)。因此，如果只采用定期删除策略，会导致很多key到时间没有删除。

`惰性删除`：是说在获取某个key的时候，redis会检查一下，这个key如果设置了过期时间那么是否过期了？如果过期了此时就会删除。

如果定期删除没删除key，也没即时去请求key，redis的内存会越来越高。那么就应该采用内存淘汰机制。

`内存淘汰机制`：redis.conf配置文件中，`maxmemory-policy volatile-lru`

- volatile-lru：从已设置过期时间的数据集（server.db[i].expires）中挑选最近最少使用的数据淘汰
- volatile-ttl：从已设置过期时间的数据集（server.db[i].expires）中挑选将要过期的数据淘汰
- volatile-random：从已设置过期时间的数据集（server.db[i].expires）中任意选择数据淘汰
- allkeys-lru：从数据集（server.db[i].dict）中挑选最近最少使用的数据淘汰
- allkeys-random：从数据集（server.db[i].dict）中任意选择数据淘汰
- no-enviction（驱逐）：禁止驱逐数据，新写入操作会报错


## 分布式锁

setnx 命令：若给定的 key 已存在，则不再如何动作。不存在 key 则将 key 值设置为 value。

del key命令：释放锁。

解决死锁：

- 通过 redis 的 expire()给锁设定最大持有时间，超时 redis 则会释放锁。

- 使用 setnx key "当前时间+持有时间" （没有则创建）和 getset key "当前时间+持有时间"（获取旧值设置新值）。


setnx之后执行expire之前进程意外crash或重启维护：

解决：setnx和expire合成一条指令来用的



## 有大量的key需要设置同一时间过期

如果大量的key过期时间设置的过于集中，到过期的那个时间点，redis可能会出现短暂的卡顿现象。
一般需要在时间上加一个随机值，使得过期时间分散一些。


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


## 部署 Redis

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

## 命令

```sh
# 选择 db，默认 0
select 1     # 切换 db 1   默认0-15共16个

set key1 value1    # 设置key
get key1           # 获取key

exists key1        # 是否存在 key

del key1           # 删除一个key

mset key1 value1 key2 value2   # 一次设置多个值

mget key1 key2                 # 一次获取多个值


```




# reference

https://www.cnblogs.com/lixihuan/p/6815730.html

https://www.cnblogs.com/angelyan/p/10449892.html

https://www.cnblogs.com/bigben0123/p/9115597.html

https://www.runoob.com/redis/redis-backup.html

https://blog.csdn.net/weixin_34320159/article/details/85088333

https://www.cnblogs.com/jasontec/p/9699242.html