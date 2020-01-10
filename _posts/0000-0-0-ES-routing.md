---
layout: post
title: "ES routing 机制"
date: 2020-01-10
description: "ES routing 机制"
tag: Elasticsearch

---


## 数据存储到对应的shard（分片）

算法：`shard_num = hash(_routing) % num_primary_shards`

- `_routing` 是一个可变值，默认是文档的 `_id` 的值，可设成自定义值。 

- `num_of_primary_shards` （主分片的数量）

- `shard_num`（文档所在分片的位置）

总结：
在创建索引的时候就确定好主分片的数量，并且永远不会改变这个数量。因为如果数量变化了，那么所有之前路由的值都会无效，文档也再也找不到了。



## 路由机制

![png](/images/posts/all/ES路由查询机制.png)

1. 搜索的请求会被发送到一个节点
2. 接收到这个请求的节点，将这个查询广播到这个索引的每个分片上（可能是主分片，也可能是复本分片）
3. 每个分片执行这个搜索查询并返回结果
4. 结果在通道节点上合并、排序并返回给用户

总结：
因为默认情况下，Elasticsearch使用文档的ID（类似于关系数据库中的自增ID），如果插入数据量比较大，文档会平均的分布于所有的分片上，导致了Elasticsearch不能确定文档的位置，所以它必须将这个请求广播到所有的N个分片上去执行这种操作会给集群带来负担，增大了网络的开销。

## 自定义路由

```sh
PUT 索引名/
{
  "settings": {
    "number_of_shards": 2,           # 分片数
    "number_of_replicas": 0          # 副本数
  }
}


GET _cat/shards/索引名?v   # 查看shard

PUT 索引名/类型/id值?routing=路由值&refresh
{
  "data": "Hello"
}

# hash(路由值)定位到分片，如果分片已存在，则更新Update，否则Create(即使其他分片也有此id也会创建)
```

总结：
- 自定义routing后会导致问题：id不再全局唯一。容易造成负载不均衡。
- 会查询routing计算出来的shard，提高查询速度。


```sh
PUT 索引名/
{
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 0
  },
  "mappings": {
    "_routing": {      # 增删改查接口是否加了routing参数
      "required": true # 设置为true，则强制检查；false则不检查，默认为false
    }
  }
}

GET 索引名/_search?routing=key1,key2  # 多个routing查询
```



# reference

https://www.cnblogs.com/caoweixiong/p/12029789.html




