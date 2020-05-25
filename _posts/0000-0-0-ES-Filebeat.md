---
layout: post
title: "Filebeat 原理及使用"
date: 2020-05-20
description: "Elasticsearch"
tag: Elasticsearch

---


## 简介

filebeat 是采集目录下日志将其发送出去，但无法对数据进行筛选，logstash拥有众多插件可提供过滤筛选功能

由于 logstash 本身是基于jdk的，所以占用内存较大，而filebeat相较下，占用的内存就不是很多了

Filebeat 组成部分：prospector 和 harvester


## prospector

- prospector 负责管理 harvester 并找到所有要读取的文件来源

- 两种prospector类型：log和stdin

- prospector只能读取本地文件， 没有功能可以连接到远程主机来读取存储的文件或日志


## harvester

- 负责读取单个文件的内容，每个文件启动一个harvester，负责打开和关闭文件


## 文件状态

- 文件状态记录在文件中（默认在/var/lib/filebeat/registry）

- 状态可以记住 harvester 收集文件的偏移量

- Filebeat重启的时候，利用registry记录的状态来进行重建，用来还原到重启之前的状态


## 保证event至少被输出一次

因为filebeat将每个事件的传递状态保存在文件中。在未得到输出方确认时，filebeat会尝试一直发送，直到得到回应。

如果Filebeat在发送事件的过程中关闭，它不会等待输出确认所有收到事件。
发送到输出但在Filebeat关闭前未确认的任何事件在重新启动Filebeat时会再次发送。
这可以确保每个事件至少发送一次，但最终会将重复事件发送到输出。

可修改设置关闭之前的等待事件回应的时间，默认禁用，并且不推荐使用（？？）。
```sh
filebeat.shutdown_timeout: 5s
```



# 测试


## 启动

```sh

./filebeat -e -c test.yml    # 启动

nohup ./filebeat -c test.yml -d publish &   # 后台启动

# -e 是强制输出到控制台，此时不会产生日志文件（注意）

# -c 指定yml配置文件，默认 filebeat.yml

```


## 样例

test.yml:

```sh
filebeat:
  prospectors:
  - type: log
    # 开启监视，不开不采集
    enable: true
    paths:  # 采集日志的路径
    - /var/log/elk/error/*.log
    # 日志多行合并采集，适用于日志中每一条日志占据多行的情况
    multiline.pattern: '^\['      # 多行日志开始一行匹配的pattern
    multiline.negate: true
    multiline.match: after
    # 为每个项目标识,或者分组，可区分不同格式的日志
    tags: ["java-logs"]
    # 这个文件记录日志读取的位置，如果重启可以从记录的位置开始取日志
    registry_file: /usr/share/filebeat/data/registry

output.logstash:
    hosts: ["XXX.XXX.XXX.XXX:5044"]
```

开启logstash：`bin/logstash -f test.conf`
```sh
input {
	beats {
		port => 5044
	}
}
output {
   stdout { 
    codec => rubydebug
   }
}
```

## Nginx 日志测试

```sh
filebeat.prospectors:
- type: log
  enable: true
  paths:
  - /test/Nginx/access.log
  tags: ["access"]
 
- type: log
  enable: true
  paths:
  - /test/Nginx/error.log
  tags: ["error"]
  
filebeat:
  registry_file: my_registry
  registry_file_permissions: 600

logging.level: info
logging.to_files: true
logging.to_syslog: false
logging.files:
  path: /var/log/mybeat.log
  name: mybeat.log
  keepfiles: 7
  permissions: 0644

output.logstash:
    hosts: ["XXX.XXX.XXX.XXX:5044"]     # 指定汇总logstash以及端口
```

## 模板使用

all.yml 文件，启动：./filebeat -c all.yml

```sh
filebeat.config.prospectors:
  enable: true
  path: prospectors.d/*.yml
  reload.enable: true       # 启用动态配置重新加载
  reload.period: 10s        # 检查的间隔时间

filebeat:
  registry_file: my_registry
  registry_file_permissions: 600

logging.level: info
logging.to_files: true
logging.to_syslog: false
logging.files:
  path: /var/log/mybeat.log
  name: mybeat.log
  keepfiles: 7
  permissions: 0644

output.logstash:
    hosts: ["XXX.XXX.XXX.XXX:5044"]     # 指定汇总logstash以及端口
```

prospectors.d/nginx.yml 

```sh
# type 开头即可
- type: log
  enable: true
  paths:
  - /test/Nginx/access.log
  tags: ["access"]
```

## 问题

```sh
reload.enabled: true       # 启用动态配置重新加载
reload.period: 10s        # 检查的间隔时间
```

修改nginx.yml的tags: ["test"]发现并不会自动加载，发送数据logstash还是接收的还是access。
```sh
async.go:235: ERR Failed to publish events caused by: write tcp filebeat的IP:41144  ->  logstash的ip:123800: write: connection reset by peer
output.go:92: ERR Failed to publish events: write tcp filebeat的IP:41144  ->  logstash的ip:123800: write: connection reset by peer
```
原因：reload.enabled 写成了 reload.enable，修改即可以自动重加载



