---
layout: post
title: "基于ES7的简易博客搜索DSL部分"
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



# 查询

```json
// 精确查询 term
GET test-index/_search
{
  "query": {
    "term": {
      "name.keyword": {
        "value": "成龙"
      }
    }
  }
}

// 多内容精确查询
GET test-index/_search
{
  "query": {
    "terms": {
      "name.keyword": [
        "小龙",
        "中龙",
        "大龙"
      ]
    }
  }
}
```

```json
// 匹配查询 match
GET test-index/_search
{
  "query": {
    "match_all":{}
  },
  "from": 0,
  "size": 10,
  "sort": [
    {
      "age": {
        "order": "asc"
      }
    }
  ]
}

GET test-index/_search
{
  "query": {
    "match": {
      "name": "龙"
    }
  }
}

// 词语匹配
GET test-index/_search
{
  "query": {
    "match_phrase": {
      "address": "广州市区"
    }
    "bool": {
       "must": 
       [{
         "range": {
	    "@timestamp": {
	       "gte": "now-1d/d",
	       "lte": "now/d"
	    }
	 }
       }]
    }
  }
}


// 多字段查询
GET test-index/_search
{
  "query": {
    "multi_match": {
      "query": "龙",
      "fields": ["name", "address"]
    }
  }
}
```


```json
// 模糊查询
GET test-index/_search
{
  "query": {
    "fuzzy": {
      "name": "龙"
    }
  }
}
```

```json
// 范围查询
GET test-index/_search
{
  "query": {
    "range": {
      "age": {
        "gte": 30
      }
    }
  }
}

GET test-index/_search
{
  "query": {
    "range": {
      "birthdate": {
        "gte": "now-30y"
      }
    }
  }
}

// now-1h 查询一小时内范围
// now-1d 查询一天内时间范围
// now-1y 查询最近一年内的时间范围
```

```json
// 通配符查询 wildcard
GET test-index/_search
{
  "query": {
    "wildcard": {
      "name.keyword": {
        "value": "*龙"
      }
    }
  }
}
```

```json
// 布尔查询
GET test-index/_search
{
  "query": {
    "bool": {

      "filter": {
        "range": {
          "birthdate": {
            "format": "yyyy",
            "gte": 1990,
            "lte": 2020
          }
        }
      },

      "must": [
        {
          "terms": {
            "address.keyword": [
              "天河区",
              "黄埔区",
              "越秀区"
            ]
          }
        }
      ]

    }
  }
}
```


# 聚合 aggs

```json
// _stats 得到总个数、最高值、最低值、平均值、总和
GET test-index/_search
{
  "size": 0,               // 返回0条数据
  "aggs": {
    "salary_stats": {
      "stats": {
        "field": "salary"
      }
    }
  }
}

// 分别求
GET test-index/_search
{
  "size": 0,
  "aggs": {

    "salary_min": {
      "min": {
        "field": "salary"
      }
    },

    "salary_max": {
      "max": {
        "field": "salary"
      }
    },

    // _avg  _count

    // 统计员工工资百分位
    "salary_percentiles": {
      "percentiles": {
        "field": "salary"
      }
    }

  }
}
```

## 分桶 Bucket 

```json
// 统计各个岁数的人数
GET test-index/_search
{
  "size": 0,
  "aggs": {
    "age_bucket": {
      "terms": {
        "field": "ages",
        "size": "10"
      }
    }
  }
}

// 范围分桶
GET test-index/_search
{
  "aggs": {
    "salary_range_bucket": {
      "range": {
        "field": "salary",
        "ranges": [
          {
            "key": "低级",    // 3000-5000
            "to": 3000
          }, {
            "key": "中级",    // 5000-9000
            "from": 5000,
            "to": 9000
          }, {
            "key": "高级",    // 9000-以上
            "from": 9000
          }
        ]
      }
    }
  }
}

// 时间范围分桶
GET test-index/_search
{
  "aggs": {
    "date_range_bucket": {
      "date_range": {
        "field": "birthdate",
        "format": "yyyy",
        "ranges": [
          {
            "key": "2000-2010的人",
            "from": "2000",
            "to": "2010"
          }, {
            "key": "2010-2020的人",
            "from": "2010",
            "to": "2020"
          }
        ]
      }
    }
  }
}


// 0-12000，区段间隔为3000分桶
GET test-index/_search
{
  "size": 0,
  "aggs": {
    "salary_histogram": {
      "histogram": {
        "field": "salary",
        "extended_bounds": {
          "min": 0,
          "max": 12000
        },
        "interval": 3000
      }
    }
  }
}

// 出生日期分桶
GET test-index/_search
{
  "size": 0,
  "aggs": {
    "birthdate_histogram": {
      "date_histogarm": {
        "format": "yyyy",
        "field": "birthdate",
        "interval": "year"
      }
    }
  }
}
```

```json
// 分桶后再聚合
// 统计每个岁数中工资最高者
GET test-index/_search
{
  "size": 0,
  "aggs": {
    "salary_bucket": {

      "terms": {              // 分桶
        "field": "age",
        "size": "10"
      },

      "aggs": {               // 聚合
        "salary_max_user": {
          "top_hits": {
            "size": 1,
            "sort": [
              {
                "salary": {
                  "order": "desc"
                }
              }
            ]
          }
        }
      }

    }
  }
}
```

