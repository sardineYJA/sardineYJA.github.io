---
layout: post
title: "Logstash 常用解析插件"
date: 2020-05-24
description: "Elasticsearch"
tag: ELK

---

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

![png](/images/posts/all/时间匹配规则表.png)

```sh
# 10位数字的时间戳转换成 2020-05-22T05:30:22.000Z
date {
    # timestamp_mysql 10位数字的时间戳，
    match => ["timestamp_mysql","UNIX"]
    target => "ftime_utc"
}
# 注意转换之后会减掉8小时，可格式化的同时加会8小时
# 进一步格式化 yyyy-MM-dd HH:mm:ss
ruby {  # 自动加8小时
    code => "event.set('ftime', event.get('ftime_utc').time.localtime.strftime('%Y-%m-%d %H:%M:%S'))"
}
```



## ruby 解析

filebeat -> logstash -> elasticsearch 数据链路中，logstash接收时会自动生成@timestamp 表示接收事件时间(可以将@timestamp赋值与logstash_time后期用户kibana展示)，但是往往项目更需要的是message里的时间。
所以常常需要将message解析出时间ftime，并将其减去8小时，覆盖掉@timestamp，@timestamp作为事件发生时间。之所以减少8小时，目的后续 ES 时间范围查询（关键字 range）是以@timestamp为目标字段（now也是UTC时间）
```sh
date {
    match => ["ftime", "YYYY-MM-dd HH:mm:ss"]
    target => "@timestamp"
}
ruby {
    code => "
        event.set('temp_time', event.get('@timestamp').time.localtime - 8*60*60)
        event.set('@timestamp', event.get('temp_time'))
    "
    remove_field => ["temp_time"]
}
```


## 时间处理模块案例

1. 需要解析出 message 的 ftime
2. ftime 是否符合规范格式
3. ftime 需要减少 8 小时后覆盖 @timestamp

```sh
if "process_time" in [tags] {
    # 不存在 ftime 字段，以当前时间为 ftime，理论上应该是 message 上的时间做 ftime
    if ![ftime] {
        ruby {
            # 此时间是东八区时间（即不需要减少8小时）
            code => "event.set('ftime', Time.new.strftime('%Y-%m-%d %H:%M:%S'))"
        }
    }

    # 格式化 ftime，例如2020-05-12 05:12:44.123 去掉后面.123只保留秒即可
    grok {
        match => {"ftime" => "(?<ftime_tmp>([\s\S]{19}))"}
    }
    ruby {
        code => "event.set('ftime', event.get('ftime_tmp'))"
    }

    # 覆盖 @timestamp
    date {
        # ftime 符合格式则覆盖 @timestamp，理论应该是第一种
        match => ["ftime", "yyyy-MM-dd HH:mm:ss", "yyyy-MM-dd HH:mm:sss,SSS", "yyyy-MM-dd HH:mm:ss.SSS"]
        target => "@timestamp"    # 不写默认也是@timestamp，显示方便观看
        timezone => "UTC"
        add_tag => ["need_sub_8"]   # 覆盖后 @timestamp 需要减8小时
    }

    # 覆盖后需要减8小时，没有覆盖则默认@timestamp不用减8小时。即不符合上面格式，如：18 Aug 2020 13:50:23,123
    if "need_sub_8" in [tags] {
        ruby {
            code => "event.set('stamp_tmp', event.get('@timestamp').time.localtime - 8*60*60)"
        }
        ruby {
            code => "event.set('@timestamp', event.get('stamp_tmp'))"
        }
    }

    # 如果存在 ftime，但却是解析失败的值，此时 ftime 为其他乱字符串。则以当前时间为 ftime
    ruby {
        code => "
            tmp = event.get('ftime')
            if tmp.match('sub_time') {     # 这里的值是ftime解析失败后的，可能是其他值
                event.set('ftime', Time.new.strftime('%Y-%m-%d %H:%M:%S'))
            }
        "
    }

    # 删除临时变量
    mutate {
        remove_field => ["ftime_tmp", "stamp_tmp"]
    }
}
```


## 其他语法

```sh
if [ftime] {...}     # 如果字段存在

if ![ftime] {...}    # 如果字段不存在

if ![json_str][key]  # json类型

match 自定义正则表达式 "(?<ftime_tmp>([\s\S]{19}))"    # (?<name>.*) 表示捕获并命名
```


