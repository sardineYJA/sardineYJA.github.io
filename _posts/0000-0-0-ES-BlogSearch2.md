---
layout: post
title: "基于ES7的简易博客搜索SpringBoot部分"
date: 2020-05-05
description: "基于ES7的简易博客搜索"
tag: Elasticsearch

---


## IndexRequest & DeleteRequest

官网：https://www.elastic.co/guide/en/elasticsearch/client/java-rest/7.4/java-rest-high-supported-apis.html

其他以后有空再测试...

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

地址：https://github.com/sardineYJA/blogsearch

待补充...

