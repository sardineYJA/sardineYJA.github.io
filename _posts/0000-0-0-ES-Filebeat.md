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


## 滚动rolling日志依然正确读取文件

- close_inactive 当被监控的文件多长时间没有变化后就关闭文件句柄(file handle)。官方建议将这个参数设置为一个比文件最大更新间隔大的值。默认值为5min.
- scan_frequency 指定Filebeat搜索新文件的频率(时间间隔)。当发现新的文件被创建时，Filebeat会为它再启动一个 harvester 进行监控。默认为10s。

综合以上两个机制，当logback完成日志切割后(即重命名)，此时老的harvester仍然在监控重命名后的日志文件，但是由于该文件不会再更新，因此会在close_inactive时间后关闭这个文件的 harvester。当scan_frequency时间过后，Filebeat会发现目录中出现了新文件，于是为该文件启动 harvester 进行监控。这样就保证了切割日志时也能不丢不重的传输数据。(不重是通过为每个日志文件保存offset实现的)


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

> 注意：修改all.yml是不会重加载的，需要重启


## 增加输出字段

配置文件中增加字段，并通过环境变量配置ip地址，在es索引中增加“host_ip"字段，值为客户端的真实IP。（默认输出host字段，但却是服务器的hostname）
配置增加以下部分：
```sh
paths:
  - /test/Nginx/access.log
fields_under_root: true
fields:
  host_ip: ${serverIP}
#serverIP 为系统环境变量 192.168.xxx.xxx
```

> 注意：fields_under_root: true 表示新增字段在全局下，如果没有fields_under_root则新增加的字段会作为数组值添加到fields这个字段里。
> 注意：系统环境变量需要 source /etc/profile，获取不到${serverIP} 启动报错：missing field accessing 'filebeat.prospectors.0.fields.ip'

# 配置
```sh
filebeat.prospectors:    # 每一个prospectors，起始于一个破折号"-"
- type: log              # 默认log，从日志文件读取每一行。stdin，从标准输入读取
  enabled: true          # 每个prospectors的开关，默认true
  paths:                 # 日志文件路径列表，可用通配符，不递归
    -/var/log/*.log
  tags: ["Nginx"]        # 标记tag，可用于分组
  fields:                # 添加附件字段，可以使values，arrays，dictionaries
    key: value

  include_lines: ['^ERR','^WARN']  # 匹配行，后接一个正则表达式列表，默认无，如果启用，则filebeat只输出匹配行
  exclude_lines: ["^DBG"]          # 排除行，后接一个正则表达式的列表，默认无
  exclude_files: [".gz$"]          # 排除文件，后接一个正则表达式的列表，默认无

  multiline.pattern:  ^\[       # 多行匹配模式，后接正则表达式，默认无
  multiline.negate: false       # 定义上边pattern匹配到的行是否用于多行合并，也就是定义是不是作为日志的一部分
  multiline.match: after        # 定义多行内容被添加到模式匹配行之后还是之前，默认无，可以被设置为after或者before
  multiline.max_lines: 500      # 单一多行匹配聚合的最大行数，超过定义行数后的行会被丢弃，默认500
  multiline.timeout: 5s         # 多行匹配超时时间，超过超时时间后的当前多行匹配事件将停止并发送，然后开始一个新的多行匹配事件，默认5秒
  
  tail_files: false        # 定义是从文件开头读取日志还是结尾。true从现在开始收集，之前已存在的不管
  close_renamed: false     # 当文件被重命名或被轮询时关闭重命名的文件处理。注意：潜在的数据丢失。默认false
  close_removed: true      # 如果文件不存在，立即关闭文件处理。如果后面文件又出现了，会在scan_frequency之后继续从最后一个已知position处开始收集，默认true
 
  encoding: plain          # 编码，默认无，plain(不验证或者改变任何输入) latin1, utf-8, utf-16be-bom, gb18030 ...
  ignore_older: 0          # 排除更改时间超过定义的文件，时间字符串可以用2h表示2小时，5m表示5分钟，默认0
  document_type: log       # 该type会被添加到type字段，对于输出到ES来说，这个输入时的type字段会被存储，默认log
  scan_frequency: 10s      # prospector扫描新文件的时间间隔，默认10秒
  max_bytes: 10485760      # 单文件最大收集的字节数，单文件超过此字节数后的字节将被丢弃，默认10MB，需要增大，保持与日志输出配置的单文件最大值一致即可



# filebeat 全局配置
filebeat:
  registry_file: ${path.data}/my_registry    # 注册表文件，只写文件名会创建在默认的${path.data}
  registry_file_permissions: 600             # 注册表文件权限
  registry_flush: 3s   # 刷新时间，默认为0实时刷新，filebeat处理一条日志就实时的将信息写入到registry文件中，这在日志量大的时候会频繁读写registry文件，可考虑适当增加这个值来降低磁盘开销
  spool_size: 2048     # 后台事件计数阈值，超过后强制发送，默认2048
  idle_timeout: 5s     # 后台刷新超时时间，超过定义时间后强制发送，不管spool_size是否达到，默认5秒
  config_dir:          # 定义filebeat配置文件目录，必须指定一个不同于filebeat主配置文件所在的目录


# 日志
logging.level: info            # error, warning, info, debug
logging.metrics.enabled: true  # 定期记录filebeat内部性能指标，默认true
logging.metrics.period: 30s    # 记录内部性能指标的周期，默认30秒

logging:
  to_files: true         # 输出所有日志到file，默认true
  files:                 # 日志输出的文件配置
    path: /var/log/filebeat        # 配置日志输出路径，默认在家目录的logs目录
    name: filebeat_log             # 日志文件名
    rotateeverybytes: 10485760     # 日志轮循大小，默认10MB
    keepfiles: 7                   # 日志轮循文件保存数量，默认7
```
