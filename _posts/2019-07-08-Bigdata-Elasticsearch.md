---
layout: post
title: "Elasticsearch 全文检索"
date: 2019-07-08
description: "Elasticsearch"
tag: Bigdata

---

# Elasticsearch

Elasticsearch是一个实时分布式搜索和分析引擎。它用于全文搜索、结构化搜索、分析。


## 全文检索

指计算机索引程序通过扫描文章中的每一个词，对每一个词建立一个索引，指明该词在文章中出现的次数和位置，当用户查询时，检索程序就根据事先建立的索引进行查找，并将查找的结果反馈给用户的检索方式。这个过程类似于通过字典中的检索字表查字的过程。全文搜索搜索引擎数据库中的数据。


## lucene

jar包，里面包含了封装好的各种建立倒排索引，以及进行搜索的代码，包括各种算法。用java开发的时候，引入lucene jar，然后基于lucene的api进行去进行开发就可以了。



## 类型

Index 索引（相当于数据库）：包含一堆有相似结构的文档数据

Type 类型（相当于表）：每个索引里都可以有一个或多个type，type是index中的一个逻辑数据分类，一个type下的document，都有相同的field

Document 文档（相当于行）：文档是es中的最小数据单元，一个document可以是一条客户数据

Field 字段（列）：Field是Elasticsearch的最小单位。一个document里面有多个field，每个field就是一个数据字段。


# 单节点安装

1. 解压：tar -zxvf elasticsearch-5.2.2.tar.gz -C ../module/

2. 创建目录：data和logs

3. 修改配置文件：config/elasticsearch.yml

```sh
# ------------ Cluster --------------
cluster.name: my-application
# ------------- Node ----------------
node.name: elasticsearch-101
# ------------- Paths ---------------
path.data: /home/yangja/module/elasticsearch-5.2.2/data
path.logs: /home/yangja/module/elasticsearch-5.2.2/logs
# ------------- Memory --------------
bootstrap.memory_lock: false
bootstrap.system_call_filter: false
# ------------- Network -------------
network.host: 172.16.7.124 
# ------------ Discovery ------------
discovery.zen.ping.unicast.hosts: ["172.16.7.124"]
```

4. cluster.name如果要配置集群需要两个节点上的elasticsearch配置的cluster.name相同，都启动可以自动组成集群，
这里如果不改cluster.name则默认是cluster.name=my-application，

5. nodename随意取但是集群内的各节点不能相同

6. 修改后的每行前面不能有空格，修改后的“:”后面必须有一个空格

7. 切换root，vi /etc/security/limits.conf

```
* soft nofile 65536
* hard nofile 131072
* soft nproc 2048
* hard nproc 4096
```

8. vi /etc/security/limits.d/90-nproc.conf

```
* soft nproc 1024
#修改为
* soft nproc 2048
```

9. vi /etc/sysctl.conf 

```
添加下面配置：
vm.max_map_count=655360
```

10. 执行命令：sysctl -p

11. 启动：bin/elasticsearch

12. 测试：curl http://172.16.7.124:9200

13. 打开Web界面：http://172.16.7.124:9200


## 问题

> org.elasticsearch.bootstrap.StartupException: java.lang.RuntimeException: can not run elasticsearch as root

因为Elasticsearch5.0之后，不能使用root账户启动，先创建一个elasticsearch组和账户es：
```sh
groupadd elasticsearch
useradd es -g elasticsearch -p 123456
chown -R es:elasticsearch elasticsearch-5.2.2/
```


> ERROR: bootstrap checks failed
max file descriptors [4096] for elasticsearch process is too low, increase to at least [65536]

切换到root，vi /etc/security/limits.conf
```sh
*        hard    nofile           65536
*        soft    nofile           65536
```
`此文件修改后需要重新登录用户，才会生效`


> ERROR: bootstrap checks failed
max file descriptors [4096] for elasticsearch process likely too low, increase to at least [65536]
max number of threads [1024] for user [lishang] likely too low, increase to at least [2048]

解决：切换到root用户，编辑limits.conf 添加类似如下内容

vi /etc/security/limits.conf 

```sh
* soft nofile 65536
* hard nofile 131072
* soft nproc 4096
* hard nproc 4096
```


> max number of threads [1024] for user [lish] likely too low, increase to at least [2048]

解决：切换到root用户，进入limits.d目录下修改配置文件。

vi /etc/security/limits.d/90-nproc.conf 

```sh
* soft nproc 1024
#修改为
* soft nproc 4096
```


> max virtual memory areas vm.max_map_count [65530] likely too low, increase to at least [262144]

解决：切换到root用户修改配置sysctl.conf

vi /etc/sysctl.conf 
```sh
vm.max_map_count=655360
```
并执行命令：sysctl -p




# reference

https://www.cnblogs.com/zhuzi91/p/8228214.html

