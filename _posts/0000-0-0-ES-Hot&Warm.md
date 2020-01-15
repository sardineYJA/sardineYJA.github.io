---
layout: post
title: "ES 笔记"
date: 2020-01-15
description: "ES 笔记"
tag: Elasticsearch

---


# 规划设置

## 数据建模

- 尽可能Denormalize数据（非范式化），从而获取最佳性能。
- 使用Nested类型的数据，查询速度会慢几倍。
- 使用Parent/Child关系，查询速度会慢几百倍。

## 单个分片大小

- Search 20G
- Logging 40G

## Node的内存与存储数据的比率:

- 搜索类的比例建议为 1：16

- 日志类为 1：48-1：96 之间

## 数据的总量：

假设总数据量1T，设置一个副本，2T总数据量。

每台64G内存，一半即可且不可超过32G。

如果搜索类的项目，每个节点31X16=496G，加上预留空间。

所以每个节点最多400G数据，至少需要5个数据节点。

如果是日志类项目，每个节点31X50=1550GB，2个数据节点即可。


# 提高写入性能

## 客户端：多线程，批量写

- 通过性能测试，确定最佳文档数量
- 多线程：需要观察是否有 HTTP429 返回，实现Retry以及线程数量的自动调节

## 服务器端

- 降低IO操作：使用ES自动生成的文档Id。
- 降低CPU和存储开销：减少不必要的分词。
- 调整Bulk线程池和队列，线程数配置CPU数+1，避免过多的上下文切换。

## 关闭无关功能

- 只需要聚合不需要搜索，Index 设置成false。
- 不需要算分，Norms 设置成false。
- 不要对字符串使用默认的dynamic mapping。字段数量过多，会对性能产生比较大的影响。
- Index_options 控制在创建倒排索引时，哪些内容会被添加到倒排索引中。优化这些设置，一定程度可以节约CPU。
- 关闭_source，减少IO操作（适合指标型数据）。

## 追求极致的写入速度

- 牺牲可靠性：将副本分片设置为0，写入完毕再调整回去。

- 牺牲搜索实时性：增加 Refresh Interval 的时间，因为频繁 refresh 产生过多 segment 文件，但增加时间会降低搜索的实时性。同时增大`indices.memory.index_buffer_size`（默认10%，自动触发refresh），也会降低 refresh 的频率。

- 牺牲可靠性：修改 Translog 的配置。

## 修改 Translog

降低写磁盘的频率，但是会降低容灾能力：

- Index.translog.durability：默认是request，每个请求都落盘。设置成async，异步写入。

- Index.translog.sync_interval 设置为60s，每分钟执行一次。

- Index.translog.flush_threshod_size：默认512mb，可以适当调大。当translog 超过该值，会触发flush。



## 例子

```sh
PUT demo_index
{
	"settings": {
		"index": {
			"refresh_interval": "30s",
			"number_of_shards": "2"
		},
		"routing": {
			"allocation": {
				"total_shards_per_node": "3"
			}
		},
		"translog": {
			"sync_interval": "30s",
			"durability": "async"
		},
		"number_of_replicas": 0
	},

	"mappings": {
		"dynamic": false,
		"properties": {}
	}
}
```


# Lucene

- 在Lucene中，单个倒排索引文件被称为Segment。Segment 是自包含的，不可变更的。

- 多个Segments汇总在一起，称为Lucene的Index，其对应的就是ES中的Shard当有新文档写入时，并且执行Refresh，就会会生成一个新Segment。Lucene中有一个文件，用来记录所有Segments信息，叫做Commit Point。查询时会同时查询所有Segments，并且对结果汇总。

- 删除的文档信息，保存在“.del”文件中，查询后会进行过滤。

- Segment 会定期Merge，合并成一个，同时删除已删除文档。


## Merge 优化

- 降低segment分段数量/频率：增大参数 `refresh_interval` 和 `indices.memory.index_buffer_size`。

- 降低最大分段大小，避免较大的分段继续参与Merge，节省系统资源。参数`Index.merge.policy.segments_per_tier`表示越小需要越多的合并操作，`Index.merge.policy.max_merged_segment`表示Segment大小限定。

- 当Index不再有写入，建议进行force merge，可提高查询速度和减少内存开销。命令：`POST 索引名/_forcemerge?max_num_segments=1`。查看：`GET _cat/segments/索引名?v`。一般越少越好，但Force Merge会占用大量的网络、IO和CPU。如果不能在业务高峰期之前做完，就需要考虑增大最终的分段数：`Shard大小/Index.merge.policy.max_merged_segment大小`。




# 冷热架构 Hot-Warm Architecture

## 应用

- 热数据节点处理所有新输入的数据，并且存储速度也较快，以便确保快速地采集和检索数据。

- 冷节点的存储密度则较大，如需在较长保留期限内保留日志数据，不失为一种具有成本效益的方法。

- ES集群的索引写入及查询速度主要依赖于磁盘的IO速度，冷热数据分离的关键为使用SSD磁盘存储热数据，提升查询效率。

- 若全部使用SSD，成本过高，且存放冷数据较为浪费，因而使用普通SATA磁盘与SSD磁盘混搭。

## 配置

elasticsearch.yml 配置:`node.attr.{attribute}: {value}`

```sh
node.attr.hotwarm_type: hot    # 热节点
# 将节点标记成Hot或Warm
node.attr.hotwarm_type: warm   # 冷节点
```

创建模板或索引时指定属性：
```sh
# 表示索引可以分配在包含多个值中其中一个的节点上。
index.routing.allocation.include.{attribute}　

# 表示索引要分配在包含索引指定值的节点上（通常一般设置一个值）。
index.routing.allocation.require.{attribute}

# 表示索引只能分配在不包含所有指定值的节点上。
index.routing.allocation.exclude.{attribute} 
```


## 索引指定冷热节点

```sh
PUT /2019-12-01.log
{
  "settings": {
    "index.routing.allocation.require.hotwarm_type": "hot", # 热节点
  }
}
```

## 迁移至冷节点

```sh
PUT 2019-12-01.log/_settings 
{ 
  "settings": { 
    "index.routing.allocation.require.hotwarm_type": "warm"  # 冷节点
  } 
}
```

## 脚本迁移

```sh
#!/bin/bash
Time=$(date -d "1 week ago" +"%Y-%m-%d")   # 一周前的日期
Hostname=$(hostname)
arr=("mt" "mo")
for var in ${arr[@]}      # hot数据（保留7天）迁移到 cold
do
    curl -H "Content-Type: application/json" -XPUT http://$Hostname:9200/$var_$Time/_settings?pretty -d'
    { 
       "settings": { 
             "index.routing.allocation.require.hotwarm_type": "warm"
        } 
    }'
done
```



# reference

https://www.cnblogs.com/caoweixiong/p/11988457.html

