---
layout: post
title: "基于ES7的简易博客搜索"
date: 2020-05-02
description: "基于ES7的简易博客搜索"
tag: Elasticsearch

---

## 项目

注意：版本7mappings下没有`"_doc"`。

```json
PUT /blog
{
  "settings": {
	"number_of_shards": 3,
	"number_of_replicas": 1
  },

  "mappings": {
      "properties": {
        "id":{
          "type": "keyword"
        },
        "title":{
          "type": "text",
          "analyzer": "ik_max_word"
        },
        "createDate":{
          "type": "date",
          "format": "yyyy-MM-dd"
        },
        "tag":{
          "type": "keyword"
        },
        "content":{
          "type": "text",
          "analyzer": "ik_max_word"
        }
      }
  }
}

DELETE /blog

POST /blog/_doc/101
{
  "id": "101",
  "tag": "Some",
  "title": "测试test标题",
  "createDate": "1995-08-11",
  "content": "测试搜索文本，这是很长的一段文字"
}
```

## IndexRequest & DeleteRequest

```java
request = new IndexRequest("index", "doc", "1");  // 索引，类型，文档id  
request = new DeleteRequest("index", "doc", "1"); 

// 需要将对象JSON化，可以Alibaba的fastjson
request.source(JSON.toJSON(entity), XContentType.JSON);

// 可选参数
request.routing("routing");   // 路由值
request.parent("parent");     // parent值
request.timeout(TimeValue.timeValueMinutes(2));                   // 超时
request.setRefreshPolicy(WriteRequest.RefreshPolicy.WAIT_UNTIL);  // 刷新策略
```

## 代码

GitHub仓库中
