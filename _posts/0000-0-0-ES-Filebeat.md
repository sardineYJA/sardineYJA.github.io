---
layout: post
title: "Filebeat"
date: 2020-05-17
description: "Elasticsearch"
tag: Elasticsearch

---


## 简介

filebeat作用是采集特定目录下的日志，并将其发送出去，但无法对数据进行筛选。
logstash拥有众多插件可提供过滤筛选功能，由于logstash本身是基于jdk的，所以占用内存较大，而filebeat相较下，占用的内存就不是很多了。

Filebeat：prospector 和 harvester

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

可修改设置关闭之前的等待事件回应的时间，默认禁用，并且不推荐使用。
```sh
filebeat.shutdown_timeout: 5s
```

## 测试


filebeat.yml:

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
启动：` nohup ./filebeat -e -c filebeat.yml -d publish &`


启动过程中不要使用-e参数，-e是强制输出到syslog，此时不会产生日志问价。
日志等级：debug, info, warning, error, critical

过滤：`nohup bin/logstash -f test.conf &`
```sh
input {
	beats {
		port => 5044
	}
}
```

```sh
filebeat.prospectors:
- type: log
  enable: true
  paths:
  - /test/access.log
  tags: ["access"]
 
- type: log
  enable: true
  paths:
  - /test/error.log
  tags: ["error"]
  
filebeat:
  registry_file: my_registry
  registry_file_permissions: 600

logging.level: warning
logging.to_files: true
logging.to_syslog: false
logging.files:
  path: /var/log/mybeat.log
  name: mybeat.log
  keepfiles: 7
  permissions: 0644
```






