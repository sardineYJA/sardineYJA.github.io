---
layout: post
title: "基于ES7的简易博客搜索SpringBoot部分"
date: 2020-05-05
description: "基于ES7的简易博客搜索"
tag: Elasticsearch

---

## 项目

注意：版本7mappings下没有`"_doc"`。

```json
PUT /blog
{
  "settings": {
	"number_of_shards": 1,
	"number_of_replicas": 0
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


// 查询，就显示title id 字段
GET blog/_search
{
  "size": 200,
  "_source": ["title","id"],
  "query":{
    "match_all":{
    }
  }
}

// 注意：from + size must be less than or equal to: [10000]
// head 查询前50条
```



## 未解决

因为主要是用于搜索，这里用ik_max_word。但是如文章分词"设置"，搜索"设"，却找不到。

Html这里缺少关键字高亮，以及换行符

scrollSearch，未测试，只需要导入10000条以上的数据即可测试


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

