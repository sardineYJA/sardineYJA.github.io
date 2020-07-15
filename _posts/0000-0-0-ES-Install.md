---
layout: post
title: "ES 及插件安装"
date: 2019-07-07
description: "Elasticsearch"
tag: ELK

---


# 单节点安装

1. 解压：tar -zxvf elasticsearch-5.2.2.tar.gz -C ../module/

2. 创建目录：data和logs

3. 修改配置文件：config/elasticsearch.yml

```sh
# 集群名字
cluster.name: my-application
# 节点名字
node.name: elasticsearch-101
# 数据与日志存储目录
path.data: /home/yangja/module/elasticsearch-5.2.2/data
path.logs: /home/yangja/module/elasticsearch-5.2.2/logs
# ------------- Memory --------------
bootstrap.memory_lock: false
bootstrap.system_call_filter: false
# 本机ip地址
network.host: 172.16.7.124 
# 设置集群中master节点的初始列表，可以通过这些节点来自动发现新加入集群的节点
discovery.zen.ping.unicast.hosts: ["172.16.7.124:9300"]
# 设置节点间交互的tcp端口（集群），（默认9300）
transport.tcp.port: 9300
# 监听端口（默认9200），（Web界面）
http.port: 9200
# 增加参数，使head插件可以访问es（端口9100）
http.cors.enabled: true        ## 加入跨域配置
http.cors.allow-origin: "*"
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

11. 启动：bin/elasticsearch -d (-d后台运行)

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

vi /etc/security/limits.d/XX-nproc.conf 

```sh
* soft nproc 1024
#修改为
* soft nproc 4096
```

重启生效，`ulimit -a`查看 max user processes 是否改变。


> max virtual memory areas vm.max_map_count [65530] likely too low, increase to at least [262144]

解决：切换到root用户修改配置sysctl.conf

vi /etc/sysctl.conf 
```sh
vm.max_map_count=262144
```
并执行命令：sysctl -p


> memory locking requested for elasticsearch process but memory is not locked

避免es使用swap交换分区设置，bootstrap.memory_lock: true 

但是会报上面错误，测试环境可直接修改false

修改：/etc/security/limits.conf
```sh
* soft memlock unlimited
* hard memlock unlimited
```

修改：/etc/sysctl.conf
```sh
vm.swappiness=0
```


## 内存

vi jvm.options，一般来说默认1g太少了对于业务来说
```
-Xms1g
-Xmx1g
```

# 安装 Elasticsearch head 插件

插件下载：https://github.com/mobz/elasticsearch-head

nodejs下载：https://nodejs.org/dist/

安装nodejs：tar -zxvf node-v6.9.2-linux-x64.tar.gz -C ../module/

配置nodejs环境变量 vi /etc/profile
```sh
export NODE_HOME=/home/yangja/module/node-v6.9.2-linux-x64
export PATH=$PATH:$NODE_HOME/bin
# 执行
source /etc/profile 
# 查看node和npm版本
node -v
npm -v
```
head插件：unzip elasticsearch-head-master.zip -d ../module/

查看当前head插件目录下有无node_modules/grunt目录，没有的话，（root用户）
执行命令创建：npm install grunt --save

安装head插件：npm install -g cnpm --registry=https://registry.npm.taobao.org

安装grunt：npm install -g grunt-cli

编辑vim Gruntfile.js
```java
// 文件93行添加hostname:'0.0.0.0'
options: {
        hostname:'0.0.0.0',
        port: 9100,
        base: '.',
        keepalive: true
      }
```

检查head根目录下是否存在base文件夹
没有：将 \_site下的base文件夹及其内容复制到head根目录下base

```
mkdir base
cp _site/base/* base/
```

elasticsearch-head/目录下启动grunt server：grunt server &

提示grunt的模块没有安装，安装即可

```sh
npm install grunt-contrib-clean -registry=https://registry.npm.taobao.org
npm install grunt-contrib-concat -registry=https://registry.npm.taobao.org
npm install grunt-contrib-watch -registry=https://registry.npm.taobao.org 
npm install grunt-contrib-connect -registry=https://registry.npm.taobao.org
npm install grunt-contrib-copy -registry=https://registry.npm.taobao.org 
npm install grunt-contrib-jasmine -registry=https://registry.npm.taobao.org
# 最后一个模块可能安装不成功，但是不影响使用
```

打开web界面：http://172.16.7.124:9100


启动集群插件后发现集群未连接，关闭修改重启

在elasticsearch-5.2.2/config/elasticsearch.yml，增加
```
http.cors.enabled: true
http.cors.allow-origin: "*"
```



# 安装Kibana

下载：`wget https://artifacts.elastic.co/downloads/kibana/kibana-5.2.2-linux-x86_64.tar.gz`

解压：`tar -zxvf kibana-5.2.2-linux-x86_64.tar.gz -C ../module`

修改配置文件：vim config/kibana.yml

```
server.port: 5601
server.host: "0.0.0.0"
elasticsearch.url: "http://172.16.7.124:9200"
kibana.index: ".kibana"
```

启动：bin/kibana

打开Web：http://172.16.7.124:5601

## 问题

>  Status changed from yellow to red - This version of Kibana requires Elasticsearch v6.3.2 on all nodes. I found the following incompatible nodes in your cluster: v5.2.2 @ 172.16.7.124:9200 (172.16.7.124)

安装Kibana6.3.2，与es版本不匹配，后面全部版本修改为5.2.2


# 安装 Graph

官网：https://www.elastic.co/cn/downloads/graph

## Install Graph into Elasticsearch

```
bin/plugin install license
bin/plugin install graph
```

## Install Graph into Kibana

```
bin/kibana plugin --install elasticsearch/graph/latest
```

## Start Elasticsearch and Kibana

```
bin/elasticsearch
bin/kibana
```

## Navigate to Kibana

```
http://172.16.7.124:5601/app/graph
```

## 问题

ES 的bin目录下plugin已经修改成elasticsearch-plugin

查看可在线安装的插件：'./elasticsearch-plugin install -h' 

查看官网：

> From version 5.0 onward, Graph is part of X-Pack. For more information, see Graphing connections in your data.



# 中文分词

## ik 分词

ik 分词模式：ik_max_word（最细颗粒，穷尽所有可能）和 ik_smart（最粗颗粒）

下载与ES版本一致：https://github.com/medcl/elasticsearch-analysis-ik/releases

解压到ES的plugins目录下，修改目录名为ik，重启

```
wget ...

yum -y install unzip

unzip elasticsearch-analysis-ik-5.2.2.zip -d ../module/elasticsearch-5.2.2/plugins/ik
```

## pinyin 分词 

地址：https://github.com/medcl/elasticsearch-analysis-pinyin/releases


# reference

https://www.cnblogs.com/zhuzi91/p/8228214.html

https://cloud.tencent.com/developer/article/1391008

