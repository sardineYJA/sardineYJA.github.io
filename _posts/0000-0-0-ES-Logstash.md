---
layout: post
title: "Logstash 介绍"
date: 2020-05-16
description: "Elasticsearch"
tag: Elasticsearch

---


## 原理简介

数据源 ==> Input Plugin ==> Filter Plugin ==> Output Plugin ==> 目标位置



## 安装Xpack后老是警告

> {:healthcheck_url=>http://logstash_system:xxxxxx@localhost:9200/, :path=>"/"}
[2017-12-18T19:39:14,367][WARN ][logstash.outputs.elasticsearch] Attempted to resurrect connection to dead ES instance, but got an error. {:url=>#<Java::JavaNet::URI:0x90152ca>, :error_type=>LogStash::Outputs::ElasticSearch::HttpClient::Pool::HostUnreachableError, :error=>"Elasticsearch Unreachable: [http://logstash_system:xxxxxx@localhost:9200/][Manticore::SocketException] Connection refused (Connection refused)"}

解决：xpack.monitoring.enabled: false

```sh
node.name: node124

path.logs: /log/logstash
pipeline.batch.size: 8000
pipeline.batch.delay: 5     # 毫秒
pipeline.workers: 10        # cpu数


http.host: "XXX.XXX.XXX.XXX"
xpack.monitoring.enabled: true
xpack.monitoring.elasticsearch.url: "http://XXX.XXX.XXX.XXX:9200"
xpack.monitoring.elasticsearch.username: "logstash_system" 
xpack.monitoring.elasticsearch.password: "changeme"

# 直接关掉
xpack.monitoring.enabled: false

# \n，\t特殊符号才能识别
config.support_escapes: true        
```


# 使用案例


## 启动

```sh
bin/logstash -f cofig/test.conf         # 启动

nohup bin/logstash -f cofig/test.conf   # 后台启动

bin/logstash -f cofig/test.conf -t      # 测试配置文件

bin/logstash -f cofig/test.conf -r      # 修改配置文件无需关闭重启

--path.data PATH         # 需要存储数据时使用此目录，默认值是Logstash主目录下的data目录。

-l, --path.logs PATH     # 将内部日志写入到的目录

--log.level LEVEL   # 设置Logstash的日志级别，可能的值是：
fatal：记录非常严重的错误消息，这通常会导致应用程序中止
error：错误日志
warn：警告日志
info：详细日志信息（这是默认信息）
debug：调试日志信息（针对开发人员）
trace ：记录除调试信息之外的细粒度消息

```

```sh
# 测试输入输出
bin/logstash -e 'input { stdin {} } output { stdout {} }'


# 监控日志文件
input{
    file {
        path => "/usr/local/log/*/*/*.log"
        start_position => "beginning"

        sincedb_path => "/home/yang/test"      # 默认的 $HOME/.sincedb 保存读取的进度
    }    
}

output {
   stdout { 
    codec => json  # json 和 rubydebug 打印格式  
   }
}


# 输出到 ES

output {
	elasticsearch {
		index => "logstash-%{+YYYY.MM.dd}"
		hosts => ["xxx.xxx.xxx.xxx:9200", "..."]
		document_id => "..."
		action => create   # 默认index，使用create必须和document_id一起
		user => admin
		password =>admin
		ssl => false
		sniffing => true
	}
}
```



