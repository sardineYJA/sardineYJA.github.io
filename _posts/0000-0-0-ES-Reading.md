---
layout: post
title: "《Elasticsearch源码解析与优化实战》笔记"
date: 2021-03-01
description: "Elasticsearch"
tag: ELK

---

## 背景

抽空复习一下 Elasticsearch 知识点


# 10 索引恢复流程


## 恢复阶段

- INIT            恢复尚未启动
- INDEX           恢复Lucene文件，以及在节点间复制索引数据
- VERIFY_INDEX    验证索引，当前分片是否损坏
- TRANSLOG        启动engine，重放translog，建立Lucene索引
- FINALIZE        清理工作，refresh 将缓冲数据写入文件但不刷盘
- DONE            完毕


## 索引恢复配置

```sh
# 恢复过程中，主副分片节点之间传输数据速率默认40MB/s，设置0则不限速
indices.recovery.max_bytes_per_sec

# 由于集群状态同步导致recovery失败时，重试recovery前的等待时间，默认为500ms
indices.recovery.retry_delay_state_sync

# 由于网络问题导致recovery失败时，重试recovery前的等待时间，默认为5s
indices.recovery.retry_delay_network

# 用于某些恢复请求的RPC超时时间，默认为15min。例如：prepare translog、clean files等
indices.recovery.internal_action_timeout

# 与上面的用处相同，但是超时更长，默认为前者的2倍
indices.recovery.internal_action_long_timeout 

# 不活跃的recovery超时时间，默认值等于indices.recovery.internal_action_long_timeout
indices.recovery.recovery_activity_timeout 
```


## 副分片恢复

核心思想：从主分片拉取 Lucene 分段和 translog 进行恢复


## recovery 速度优化

- 配置项 cluster.routing.allocation.node_concurrent_recoveries 决定了单个节点执行副分片recovery时的最大并发数（进/出），默认为2，适当提高此值可以增加recovery并发数。

```sh
PUT _cluster/settings
{
  "transient": {
    "cluster": {
      "routing": {
        "allocation.node_concurrent_recoveries": 20
      }
    }
  }
}
```

- 配置项 indices.recovery.max_bytes_per_sec 决定节点间复制数据时的限速，可以适当提高此值或取消限速。

- 配置项 cluster.routing.allocation.node_initial_primaries_recoveries 决定了单个节点执行主分片recovery时的最大并发数，默认为4。由于主分片的恢复不涉及在网络上复制数据，仅在本地磁盘读写，所以在节点配置了多个数据磁盘的情况下，可以适当提高此值。

- 在重启集群之前，先停止写入端，执行sync flush，让恢复过程有机会跳过phasel。

- 适当地多保留些translog，配置项 index.translog.retention.size 默认最大保留512MB，index.translog.retention.age 默认为不超过12小时。调整这两个配置可让恢复过程有机会跳过phase1。

- 合并Lucene分段，对于冷索引甚至不再更新的索引执行_forcemerge，较少的Lucene分段可以提升恢复效率，例如，减少对比，降低文件传输请求数量。




# 18 写入速度优化

## translog flush 间隔调整
```sh
# translog 默认持久化策略，每个请求都 flush
index.translog.durability: request

# 接受一定概率数据丢失：主分片写成功，未复制副分片而主机断电
# 导致数据既没有刷到 Lucene, translog 也没有刷盘，恢复时 translog 中没有此数据，数据丢失
# 可设置成周期性和大小性策略
index.translog.durability: async   # async 表示 translog 按 sync_interval 时间周期进行
index.translog.sync_interval: 120s # 默认 5 s
index.translog.flush_threshold_size: 1024mb  # 默认512MB, 超过则 refresh, 产生新 Lucene 分段
```

## 索引刷新间隔 refresh_interval
```sh
# refresh 会产生新的 Lucene 即segement段，导致频繁 segment merge，实时搜索性不高则可增大
index.refresh_interval: 120s  # 默认1s，即1s才可被搜索
```

## 段合并
```sh
GET _cat/segments/索引名?v                  # segment大小（默认5G），内存，数量
POST 索引名/_forcemerge?max_num_segments=1  # 合并成一个（根据具体情况）
GET _tasks?actions=*merge&detailed=true      
```
> 强制合并并不会受到默认大小的限制（5G），segment合并不会均等的将一个segment分到多个，而是直接将此segment合并到另一segment

merge完成，旧的segments就会被删除：
1. 新的segment会被flush到磁盘
2. 生成新的commit point文件，包含新的segment名称，并排除掉旧的segment和那些被合并过的小的segment
3. 接着新的segment会被打开用于搜索
4. 最后旧的segment会被删除掉

合并一个大的segment会消耗比较多的io和cpu资源，同时也会搜索性能造成影响。

一个索引它的segment数量越少，它的搜索性能就越高，可以强制合并每个shard上只有一个segment。


## indexing buffer
除了 refresh_interval，另一个生成新 segment 的就是，indexing buffer 为 doc 建立索引时，当缓冲满会刷入磁盘，生成一个新 segment。
```sh
indices.memory.index_buffer_size       # 默认整个堆的10%=节点上share个数*每个share indexing buffer
indices.memory.min_index_buffer_size   # 默认 48MB
indices.memroy.max_index_buffer_size   # 默认无限制
```
例如：elasticsearch.yml
```sh
indices.memory.index_buffer_size: 30%
```

## 自动生成 doc id
写入 doc 指定 id，则 ES 会先读取原 doc 的版本号，以判断是否需要更新。通过自动生成 id，避免此过程。


## 延迟分配
通过这个参数控制延迟多长时间后才开始分配unassigned的分片。
解决问题：如果节点离开后马上又回来（如网络不好，重启等），在这个短时间内会进行两次Rebalancing操作。
```sh
PUT _all/_settings
PUT index_name/_settings
{
  "settings": {
    "index.unassigned.node_left.delayed_timeout": "5m"
  }
}
```

## 磁盘使用
磁盘利用率达到85%时，主节点将不再分配分片至该节点上
```sh
# 查看磁盘利用率：
GET _cat/allocation?v

# 如果磁盘空间比较大，而85%利用率有些浪费，可以通过设置
# cluster.routing.allocation.disk.watermark.low
# cluster.routing.allocation.disk.watermark.high
POST _cluster/settings
{
    "transient": { 
     "cluster.routing.allocation.disk.watermark.low":"90%"   
    }
}
```

## 模板配置
```sh
{
    "template": "*",
    "order": 0,
    "settings": {
        "index.merge.policy.max_merged_segment": "2gb", # 单个segment最大容量
        "index.merge.policy.segments_per_tier": "24",   # 每层允许出现的索引段数量的上限
        "index.number_of_replicas": "1",
        "index.number_of_shards": "5",
        "index.optimize_auto_generated_id": "true",
        "index.refresh_interval": "120s",
        "index.translog.durability": "saync",
        "index.translog.flush_threshold_size": "1000mb",
        "index.translog.sync_interval": "120s",
        "index.unassigned.node_left.delayed_timeout": "5d"
    }
}
```


# 19 搜索速度的优化

## 优化日期搜索
```sh
"@timestamp": {
    "gte": "now-1h/m",
    "lte": "now/m"
}
```
now 一直在变化，增加/m进行四舍五入，可利用查询缓存。当多个相同时间范围查询，则查询缓存可以加快查询速度。


## 预热全局序号 global ordinals
全局序号是一种数据结构，用于keyword字段进行terms聚合。提前告诉ES哪些字段将用于terms聚合。
可通过配置映射在刷新 refresh 时告诉  ES 预先加载全局序数。
```sh
PUT index
{
    "mappings": {
        "type": {
            "properties": {
                "num": {
                    "type": "keyword",
                    "eager_global_ordinals": true
                }
            }
        }
    }
}
```

## execution hint
terms 聚合机制：
- 通过直接使用字段值来聚合每个桶的数据（map）
- 通过使用字段的全局序号并为每个全局序号分配一个bucket（global_ordinals）

当查询的结果集很小的情况下，可以使用map的模式不去构建字典。
```sh
GET /_search
{
    "aggs": {
        "tags": {
            "terms": {
                "field": "tags",
                "execution_hit": "map"
            }
        }
    }
}
```


## 限制搜索请求的分片数
```sh
# 默认情况下，ES 会拒绝超过 1000 个分片的搜索请求
action.search.shard_count 
```


## 自适应副本选择ARS
```sh
# 6.1 版本开始支持，7.0 默认开启
PUT _cluster/settings
{
    "transient": {
        "cluster.routing.use_adaptive_replica_selection": true
    }
}
```

默认协调节点将搜索请求轮询发到分片的每个副本上。但是容易造成将请求分发到负载较高的节点上。

ES 能够将请求路由选择到非高负载节点上的副本分片，避免某个副本有较高延迟导致长尾效应。



# 20 磁盘使用量优化

## 索引映射参数
```sh
analyzer
normalizer
boost
coerce
copy_to
doc_values      # 聚合和排序（默认开启除analyzed的字符串外）
dynamic
enabled
fielddata
eager_global_ordinals
format
ignore_above
ignore_malformed
index_options    # 设 freqs 不存储频率和位置，用于不需要短语匹配的 text
index            # 控制是否被索引，false则不被查询到
fields
norms            # 设 false 则不关心评分
null_value
position_increment_gap
properties
search_analyzer
similarity
store
term_vector

https://www.elastic.co/guide/en/elasticsearch/reference/6.1/mapping-params.html
```

1. 禁用特性提高性能

2. 不使用默认的字符串映射（同时索引为text和keyword），可考虑只需一种



# 21 综合应用实践

## 规划

1. 节点数越多，节点间的连接数和通信量倍增，主节点管理压力大

2. 分片不宜超过 50G，过多分片增加主节点负担，集群重启恢复时间长

3. 内存推荐 31G，多个数据盘进行 raid

4. master 独立部署，没有存储数据，离线也不产生没分配分片

5. 为系统 cache 保留一半物理内存，关闭 swap

## 坏盘下线

```sh
PUT _cluster/settings
{
    "transient": {     # 将分片迁移出去
        "cluster.routing.allocation.exclude_name": "node-name"
    }
}
GET _cat/shards?v

# 维护完成后，取消排除
PUT _cluster/settings
{
    "transient": {
        "cluster.routing.allocation.exclude_name": ""
    }
}
```

##  使用全局模板

```sh
{
    "template": "*",
    "order": 0,
    ......
}
```
order 越小优先级越小，匹配多个模板时合并模板，有冲突则优先级高生效。


## 避免热索引分片不均

新节点加入，可能导致热点数据集中写到新节点上，增大该节点的压力。目的使索引的分片在节点上分布均匀。
```sh
PUT test-index/_settings
{
    "index": {
        "routing.allocation.total_shards_per_node": "2"
    }
}
```

## 优化

1. 临时副本数可设1，副本调整只涉网络传输，代价较小

2. 空闲时间对不再更新的索引 force merge

3. Shrink 降低索引分片数量

4. close 索引，关闭的索引除 




## 延迟分片

某个数据节点需要下线，会导致重新分配副分片，可以调整节点离线后分片重新分配的延迟时间：
```sh
"index.unassigned.node_left.delayed_timeout": "5d"
```










# 22 故障诊断

## profile 定位慢查询原因
```sh
GET mytest/_search
{
    "profile": true,       # 开启
    "query": { ... }
}
```

## 分片诊断不可分配原因
```sh
GET _cluster/allocation/explain
{
  "index": "test-index",
  "shard": 0,
  "primary": false
}
```

## 将某个索引的在A节点上的分片移走
```sh
PUT /test-index/_settings
{
    "index.routing.allocation.exclude._name": "node-name-A"
}
```

## 繁忙线程堆栈
```sh
# 获取 pid 的所有线程 cpu 使用情况
top -H -b -n 1 -p $pid  
# -p 查看进程详情
# -H 线程
# -b 以批处理模式启动top命令
# -n 设置迭代数量

# 查看 pid 所有线程堆栈
jstack $pid
```



## 问题
> jstack命令执行报错：
Unable to open socket file: target process not responding or HotSpot VM not loaded
The -F option can be used when the target process is not responding

解决：需要su切换到进程的用户才可执行命令


## 查看每个数据节点总分段所占内存总量
```sh
GET _cat/nodes?v&h=name,segments.memory
```

## 查看磁盘I/O
```sh
iostat -xd 3   # 每3s打印一次

iotop          # 查看具体pid进程的I/O
```




