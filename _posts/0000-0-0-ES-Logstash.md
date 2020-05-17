---
layout: post
title: "Logstash"
date: 2020-05-16
description: "Elasticsearch"
tag: Elasticsearch

---


# Logstash

## 安装Xpack后老是警告：

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


读取过数据，即使重启也不会再读。

```sh
bin/logstash -e 'input { stdin { } } output { stdout {} }'

input{
    file {
        path => "/usr/local/log/*/*/*.log"
        start_position => "beginning"
    }   
}

output {
   stdout { 
    codec => json
   }
}


input {
    stdin {
    }
}

output {
   stdout { 
    codec => rubydebug
   }
}
```

```sh
# 验证配置文件
bin/logstash -f test.conf --config.test_and_exit

# 修改后不需要停止或重启logstash
bin/logstash -f test.conf -r
```

