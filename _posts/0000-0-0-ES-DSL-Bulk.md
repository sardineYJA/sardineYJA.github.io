---
layout: post
title: "Bulk 批量处理"
date: 2020-06-19
description: "DSL"
tag: ELK

---


# bulk API

bulk api可以在单个请求中一次执行多个索引或者删除操作，使用这种方式可以极大的提升索引性能。

## 格式

```sh
action and meta_data \n   ## 操作类型：index，create，update，delete 以及 metadata：_index, _type, _id
optional source \n        ## 可选的数据体
```

> 一行一行写，前一行是Action，后一行是内容，每行结束为\n.

1. index 和 create  第二行是 source 数据体
2. delete 没有第二行
3. update 第二行可以是 doc，upsert 或者是 script
4. 只能 POST


```sh
POST _bulk
{ "index" : { "_index" : "test", "_type" : "type1", "_id" : "1" } }
{ "field1" : "value1" }
{ "delete" : { "_index" : "test", "_type" : "type1", "_id" : "2" } }
{ "create" : { "_index" : "test", "_type" : "type1", "_id" : "3" } }
{ "field1" : "value3" }
{ "update" : {"_id" : "1", "_type" : "type1", "_index" : "test"} }
{ "doc" : {"field2" : "value2"} }
```

## index 和 create 区别

id 已存在情况下，index 是将第二篇文章覆盖第一篇，create 是在第二篇插入的时候抛出一个已经存在的异常

在批量请求的时候最好使用 create 方式进行导入。假如批量导入一个大小为500MB 的文件，中途突然网络中断，可能其中有5万条数据已经导入，那么第二次尝试导入的时候，如果选用 index 方式，那么前5万条数据又会重复导入，增加了很多额外的开销，如果是 create 的话，elasticsearch 针对 bulk 操作机制是忽略已经存在的（当然在 bulk 完成后会返回哪些数据是重复的），这样就不会重复被导入了。


## 批量处理同一索引和类型

```sh
# /{index}/_bulk
# /{index}/{type}/_bulk

POST /test/doc/_bulk
{ "index" : {"_id" : "1", "retry_on_conflict": 3}}
{ "field1" : "value1" }

# 最简单插入多条数据
POST /index_name/doc/_bulk
{"index": {}}
{"field" : "value", "field" : "value"}
{"index": {}}
{"field" : "value", "field" : "value"}
```



## update 操作

更新数据的方法：

- doc
- upsert
- doc_as_upsert
- script
- params ，lang ，source

```sh
POST _bulk
{ "update" : {"_id" : "1", "_type" : "type1", "_index" : "index1", "retry_on_conflict" : 3} }
{ "doc" : {"field" : "value"} }
{ "update" : { "_id" : "0", "_type" : "type1", "_index" : "index1", "retry_on_conflict" : 3} }
{ "script" : { "source": "ctx._source.counter += params.param1", "lang" : "painless", "params" : {"param1" : 1}}, "upsert" : {"counter" : 1}}
{ "update" : {"_id" : "2", "_type" : "type1", "_index" : "index1", "retry_on_conflict" : 3} }
{ "doc" : {"field" : "value"}, "doc_as_upsert" : true }
{ "update" : {"_id" : "3", "_type" : "type1", "_index" : "index1", "_source" : true} }
{ "doc" : {"field" : "value"} }
{ "update" : {"_id" : "4", "_type" : "type1", "_index" : "index1"} }
{ "doc" : {"field" : "value"}, "_source": true}
```


## script 使用 

```sh
{
  "query": {
    "match": {
      "_id": "A001"
    }
  },
  "script": {
    "inline": "ctx._source['name'] = params.name; ctx._source['tags'] = params.tags",
    "params": {
      "name": "",
      "tags": []
    }
  }
}
```


## curl 批量

```sh
curl -XPOST "http://xxx.xxx.xxx.xxx:9200/test/doc/_bulk" -H "Content-Type:application/json" -u admin:admin -d '{"index":{"_id":"1"}}
{"name": "John" }
{"index":{"_id":"2"}}
{"name": "Yang" }
'
```

--data-binary 参数可以加载文件

```sh
$ cat requests
{ "index" : { "_index" : "test", "_type" : "type1", "_id" : "1" } }
{ "field1" : "value1" }
$ curl -s -H "Content-Type: application/x-ndjson" -XPOST localhost:9200/_bulk --data-binary "@requests"
```


