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

output:
  # 输出到logstash中,logstash更换为自己的ip
  logstash:
    hosts: ["XXX.XXX.XXX.XXX:5044"]
```
启动：` nohup ./filebeat -e -c filebeat.yml -d publish &`



过滤：`nohup bin/logstash -f test.conf &`
```sh
input {
	beats {
		port => 5044
	}
}
filter {
	 if "java-logs" in [tags]{ 
	     grok {
	        # 筛选过滤
	        match => {
	           "message" => "(?<date>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\]\[(?<level>[A-Z]{4,5})\]\[(?<thread>[A-Za-z0-9/-]{4,40})\]\[(?<class>[A-Za-z0-9/.]{4,40})\]\[(?<msg>.*)"
	        }
	        remove_field => ["message"]
	     }
	     # 不匹配正则则删除，匹配正则用=~
	     if [level] !~ "(ERROR|WARN|INFO)" {
	         drop {}
	     }
     }
}
output {
    elasticsearch {
        hosts => "XXX.XXX.XXX.XXX:9200"
    }
}
```







