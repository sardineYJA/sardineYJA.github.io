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


## logstash 输出到 ES
```sh
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

# 插件解析

## 易错点

- 插件里不能使用 if 判断语句，if 里面可以有mutate，grok插件

- 注意括号的使用，例如 grok 匹配字符串 "message" => {""}，匹配规则不要用大括号，正确 "message" => ""

- 所有插件都支持 add_field, add_tag等参数选项（执行顺序为最后）


## kv 解析

```sh
kv {
	source => "message"      # 解析后都为字符串
	field_split => ","       # (键值对) 与 (键值对) 之间的切割符号
	value_split => ":"       # (键) 与 (值) 之间的切割符

	allow_duplicate_values => false   # 只有唯一的键值对保留，默认true(所有保留)
	default_keys => ["key1", "value1", "key2", "value2"]    # 默认键值对
	exclude_keys => ["key1", "key2"]          # 解析时不保留的键值对
	include_keys => ["key1", "key2"]          # 解析时只保留的键值对（默认的也会保留）

	prefix => "pre_"     # 解析后在key加前缀
}

```

## json 解析

```sh
json {
	source => "message" 
	skip_on_invalid_json => false # 是否允许跳过无效json，默认false
                                  # true，无效json不会_jsonparsefailure，但是还是会读取到message
}
```



## grok 字符串匹配

```sh
filter {
	grok { 
	  	match => { "message" => "Duration: %{NUMBER:duration}" }

	  	# 匹配多模式
	  	match => { "message" => [ "Duration: %{NUMBER:duration}", "Speed: %{NUMBER:speed}" ] }

	}
}
```

内置匹配规则：https://github.com/elastic/logstash/blob/v1.4.2/patterns/grok-patterns



## mutate 插件常用解析

注意：以下排序是按照执行顺序，如果更换顺序影响逻辑建议多个mutate分开使用

```sh
filter {
	mutate {
		coerce => { "field1" => "default_value" }  # 设置默认值

		rename => { "oldname" => "newname" }   # 修改字段名

		update => { "fieldname" => "newvalue" } # 修改字段值，如果不存在字段则不操作

		replace => { "message" => "%{fieldname}newvalue" }  # 修改字段值
 
		convert => { "fieldname" => "integer" }   # 仅限integer, float, string, boolean
		
		gsub => [
          #  匹配 / 全转换成 _
          "fieldname", "/", "_"
        ]

        uppercase => [ "fieldname" ]      # 转换成大写

        lowercase => [ "fieldname" ]      # 转换成小写

		strip => ["field1", "field2"]  # 去收尾空格

		split => { "fieldname" => "," }  # 切割字符串成数组

		join => { "arrayfieldname" => "," }    # 数组连接成字符串

		copy => { "source_field" => "dest_field" } # 复制
	}
}
```


## date 解析

Logstash在处理数据的时候，会自动生成一个字段@timestamp，默认该字段存储的是Logstash收到消息/事件(event)的时间。（少8小时时间差）

```sh
# 利用 ruby 加上8小时
ruby {
	code => "
		event.set('temp_time', event.get('@timestamp').time.localtime + 8*60*60)
		event.set('@timestamp', event.get('temp_time'))
	"
	remove_field => ["temp_time"]
}
```


```sh
# [22/May/2020:13:30:22 +0800]

filter {
	grok {
		match => {
			"message" => "\[%{HTTPDATE:timestamp}\]"
		}
	}
	date {
		match => ["timestamp", "dd/MMM/yyy:HH:mm:ss Z"]
		target => "ftime"   # 默认@timestamp，最好修改一下
	}
}

# 结果："ftime" => 2020-05-22T05:30:22.000Z   (自动减8小时，且不是字符串格式了)
# 如果不减时间修改：+0800 变成 +0000

# 进一步格式化 yyyy-MM-dd HH:mm:ss
ruby {
	code => "event.set('format_time', event.get('ftime').time.localtime.strftime('%Y-%m-%d %H:%M:%S'))"
}
# 结果 "format_time" => "2020-05-22 13:30:22"  (自动加回8小时，且是字符串)
```


```sh
# [2020-09-11T01:33:04+08:00]

filter {
	grok {
		match => {
			"message" => "%{TIMESTAMP_ISO8601:localtime}"
		}
	}
	date {
		match => ["localtime", "yyyy-MM-dd'T'HH:mm:ssZZ"]
		target => "ftime"
	}
}
# 结果："ftime" => 2020-09-10T17:33:04.000Z   (自动减8小时，且不是字符串格式了)
```


