---
layout: post
title: "Logstash 介绍"
date: 2020-05-16
description: "Elasticsearch"
tag: ELK

---


## 原理简介

数据源 ==> Input Plugin ==> Filter Plugin ==> Output Plugin ==> 目标位置

![png](/images/posts/all/Logstash架构图.png)

```sh
# Queue 介绍
queue.type:persisted # 默认是memory
queue.max_bytes:4gb  # 队列存储最大数据量，默认1G
## In Memory ： 无法处理进程Crash、机器宕机等情况，会导致数据丢失
## Persistent Queue In Disk：可处理进程Crash等情况，保证数据不丢失，保证数据至少消费一次，充当缓冲区，可以替代kafka等消息队列的作用
```


## 配置

```sh
node.name: node124

path.logs: /log/logstash

## 增大接收数量
pipeline.batch.size: 8000        # 每次发送的事件数
pipeline.workers: 12             # pipeline线程数
pipeline.output.workers: 6       # 实际output时的线程数
pipeline.batch.delay: 6          # 发送延时 毫秒

# \n，\t特殊符号才能识别
config.support_escapes: true       

## ES 监控
http.host: "XXX.XXX.XXX.XXX"
xpack.monitoring.enabled: true  
xpack.monitoring.elasticsearch.url: "http://XXX.XXX.XXX.XXX:9200"
xpack.monitoring.elasticsearch.username: "admin" 
xpack.monitoring.elasticsearch.password: "admin"
```


# 使用案例

## 启动

```sh
bin/logstash -f config/test.conf &       # 后台启动

bin/logstash -f config/test.conf -t      # 测试配置文件

bin/logstash -f config/test.conf -r      # 修改配置文件无需关闭重启

--path.logs PATH    # 将内部日志写入到的目录

--path.data PATH    # 多个logstash需要不同data目录，启动时指定则不用每次修改logstash.yml

--log.level LEVEL   # 设置Logstash的日志级别，可能的值是：
fatal：记录非常严重的错误消息，这通常会导致应用程序中止
error：错误日志
warn：警告日志
info：详细日志信息（这是默认信息）
debug：调试日志信息（针对开发人员）
trace：记录除调试信息之外的细粒度消息
```

```sh
# 测试输入输出
bin/logstash -e 'input { stdin {} } output { stdout {} }'


# 监控日志文件
input{
    file {
        path => "/usr/local/log/*/*/*.log"
        start_position => "beginning"

        sincedb_path => "/home/yang/test"      # 默认的 $HOME/.sincedb 保存(重启)读取的进度
    }    
}

output {
   stdout { 
    codec => json  # json 和 rubydebug 打印格式  
   }
}

```

## 输出到 ES

```sh
output {
	elasticsearch {
		index => "logstash-%{+YYYY.MM.dd}"
		hosts => ["xxx.xxx.xxx.xxx:9200", "..."]
		document_id => "..."
		action => index   # 默认index
		user => admin
		password =>admin
		ssl => false
		sniffing => true        # 表示可发现所有节点，不局限于 hosts
	}
}
```

aciton 三种：

- index: 不指定document_id则随机，指定id如ES已存在则更新doc，不存在则创建。（写入的效率降低，因为额外增加了查询该document_id 是否存在的过程。）

- create: 必须指定document_id，ES不存在此id则创建成功，存在则返回失败。（只适合用在像是用户创建之后就不能再更新的场景。）

- update: 必须指定document_id，ES不存在此id则返回失败，存在则更新doc。



# log4j2.properties

## 以 logstash 的日志配置为参考

默认是基于时间的触发策略，但不是每天一个log的意思，只有触发logstash-plain.log写操作（如重启，修改conf），才会进行滚动判断，如果几天没有写操作，可能就不会有那几天的log文件。

```sh
status = error
name = LogstashPropertiesConfig


# 控制台输出，logstash启动关闭会打印在console，与log文件内容一样

appender.console.type = Console
appender.console.name = plain_console
appender.console.layout.type = PatternLayout
appender.console.layout.pattern = [%d{ISO8601}][%-5p][%-25c] %m%n

appender.json_console.type = Console
appender.json_console.name = json_console
appender.json_console.layout.type = JSONLayout
appender.json_console.layout.compact = true
appender.json_console.layout.eventEol = true


## 滚动文件

appender.rolling.type = RollingFile
appender.rolling.name = plain_rolling
appender.rolling.fileName = ${sys:ls.logs}/logstash-${sys:ls.log.format}.log
appender.rolling.filePattern = ${sys:ls.logs}/logstash-${sys:ls.log.format}-%d{yyyy-MM-dd}.log
appender.rolling.policies.type = Policies
appender.rolling.policies.time.type = TimeBasedTriggeringPolicy
appender.rolling.policies.time.interval = 1
appender.rolling.policies.time.modulate = true
appender.rolling.layout.type = PatternLayout
appender.rolling.layout.pattern = [%d{ISO8601}][%-5p][%-25c] %-.10000m%n


appender.json_rolling.type = RollingFile
appender.json_rolling.name = json_rolling
appender.json_rolling.fileName = ${sys:ls.logs}/logstash-${sys:ls.log.format}.log
appender.json_rolling.filePattern = ${sys:ls.logs}/logstash-${sys:ls.log.format}-%d{yyyy-MM-dd}.log
appender.json_rolling.policies.type = Policies
appender.json_rolling.policies.time.type = TimeBasedTriggeringPolicy
appender.json_rolling.policies.time.interval = 1
appender.json_rolling.policies.time.modulate = true
appender.json_rolling.layout.type = JSONLayout
appender.json_rolling.layout.compact = true
appender.json_rolling.layout.eventEol = true

rootLogger.level = ${sys:ls.log.level}
rootLogger.appenderRef.console.ref = ${sys:ls.log.format}_console
rootLogger.appenderRef.rolling.ref = ${sys:ls.log.format}_rolling
```

待测试...

```sh
# 新增
appender.rolling.policies.size.type = SizeBasedTriggeringPolicy
appender.rolling.policies.size.size = 50MB
appender.rolling.strategy.type = DefaultRolloverStrategy
appender.rolling.strategy.max = 30
```

```sh
# 基于时间的触发策略（TriggeringPolicy）
appender.rolling.policies.time.type = TimeBasedTriggeringPolicy
# filePattern中配置的文件重命名规则是test1-%d{yyyy-MM-dd-HH-mm}，
# 最小的时间粒度是mm，即分钟，TimeBasedTriggeringPolicy指定的size是1，结合起来就是每2分钟生成一个新文件。
# 如果改成%d{yyyy-MM-dd-HH}，最小粒度为小时，则每2个小时生成一个文件。
# %d{yyyy-MM-dd-HH}不能有空格，如%d{yyyy-MM-dd HH-mm}则不会滚动。
appender.rolling.policies.time.interval = 2
# 是否对保存时间进行限制。若modulate=true，则保存时间将以0点为边界进行偏移计算。
# 比如，modulate=true，interval=4hours，
# 那么假设上次保存日志的时间为03:00，则下次保存日志的时间为04:00，之后的保存时间依次为08:00，12:00，16:00
appender.rolling.policies.time.modulate = true

# 基于日志文件大小的触发策略
appender.rolling.policies.size.type = SizeBasedTriggeringPolicy
appender.rolling.policies.size.size = 100MB

# 文件保存的覆盖策略，生成分割（保存）文件的个数
appender.rolling.strategy.type = DefaultRolloverStrategy
appender.rolling.strategy.max = 5
```



