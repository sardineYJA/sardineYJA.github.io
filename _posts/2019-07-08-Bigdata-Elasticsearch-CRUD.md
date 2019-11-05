---
layout: post
title: "Elasticsearch CRUD 操作"
date: 2019-07-08
description: "Elasticsearch"
tag: Bigdata

---

## CRUD 操作

curl测试：`curl -X<VERB> '<PROTOCOL>://<HOST>:<PORT>/<PATH>?<QUERY_STRING>' -d '<BODY>'`

- VERB : GET, POST, PUT, HEAD, DELETE
- PROTOCOL : http 或 https
- HOST : 集群中任意节点的主机名
- PORT : 运行ES HTTP服务的端口
- PATH : 终端路径
- QUERY_STRING : 任意可选的查询字符串参数，例如：?pretty 将格式化地输出JSON返回值
- BODY : 格式的请求体

## Kibana 样例

```sh
GET _cat/indices?v      # 查看索引

GET /_count?pretty      # 个数
{
	"query": {
		"match_all":{}
	}
}
```

## 新增

db为_index，user为_type, 1为_id（没有指定id,将是随机字符串）
```sh
POST /db/user/1
{
	"name":"yang",
	"password":"123",
	"age":"25"
}


GET /db/user/1   # 查询
```

## 查询

查找：`url/<index>/<type>/_search`

index, type 可选择

- took 表示耗时(毫秒）
- hits 表示命中记录
- timed_out 表示是否超时
- score 表示匹配的程序，默认是按照这个字段降序排列

```sh

GET _search    # 查找所有


GET _search    # 查询含有Hello
{
  "query": {
    "query_string": {
      "query": "Hello"
    }
  }
}

GET _search    # 查询含有Hello
{
  "query": {
  	"query_string": {
      "query": "Hello"
    }
  }
}

GET _search   # 查询字段title含有Hello的（fields默认_all）
{
  "query": {
    "query_string": {
      "query": "Hello",
      "fields": ["title"]
    }
  }
}

GET _search   # 查询字段year是1995的
{
	"query": {
		"term": {
			"year": 1995
		}
	}
}


# 查找movices索引movie类型里文档title字段包含“Now”的数据。
GET movies/movie/_search 
{
  "query":{
    "match":{
      "title":"Now"
    }
  }
}


GET /_search        # 常数分数查询
{
  "query": {
    "constant_score": {
      "filter": {
        "term": {
          "year": 1994
        }
      }
    }
  },
  "size": 5      # 指定条数
}
```

# 分词器

## 测试

```sh
GET _mapping    # 查看
```

```sh
GET <index>/<type>/_analyze    # 测试分词器效果，index和type可选
{
  "analyzer": "standard",
  "text": "this is a test 这是中文，中华人民共和国"
}
```

- standard  默认（中文分一字一词）
- whitespace 空格分隔符
- stop 删除stop words
- keyword 不分词
- ik_max_word 中文分词，最细颗粒
- ik_smart 中文分词，最粗颗粒


```sh
GET _search
{
  "query": {
    "query_string": {
        "query": "Hello",
        "analyzer": "standard"     # 查询时指定分词器
    }
  }
}
```

创建 index mapping 时指定 search_analyzer

```sh
PUT /book
{
  "mappings": {
    "doc": {
      "properties": {
        "title": {
          "type": "text",
          "analyzer": "whitespace",       # 分词器
          "search_analyzer": "standard"   # 查询分词器
        }
      }
    }
  }
}
```

- 不指定分词时，会使用默认的standard

- 明确字段是否需要分词，不需要分词的字段将type设置为keyword，可以节省空间和提高写性能


## 自定义分词

```sh
PUT /custom_analyzer
{
	"settings": {
		"analysis": {
			"analyzer": {
				"my_analyzer": {
					"type": "custom",
					"tokenizer": "standard",
					"char_filter": ["html_strip"], # 去html标签和转换html实体
					"filter": ["lowercase"]        # 将字母转化成小写
				}
			}
		}
	}
}
# 测试
POST /custom_analyzer/_analyze
{
	"analyzer": "my_analyzer",
	"text": ["This is 中华人民共和国", "<p>I&apos;m so <b>happy</b>!</p>"]
}
```


# 删除

```sh
DELETE /blog/article/1  # 根据id删除一条记录
DELETE /blog/article    # 删除 type
DELETE /blog            # 删除 index
```

```sh
DELETE _all   # 删除所有，注意
```
为了避免大量删除，elasticsearch.yml 中修改
`action.destructive_requires_name: true`。
设置之后只限于使用特定名称来删除索引，使用_all 或者通配符来删除索引无效。


## 查找匹配后删除

```sh
POST /blog/article/_delete_by_query
{
  "query": {
    "match": {
      "content":"Hello"  # 删除content字段中有Hell的记录
    }
  }
}
```


# reference

https://www.cnblogs.com/zhuzi91/p/8228214.html

https://cloud.tencent.com/developer/article/1391008

https://www.cnblogs.com/xiaobaozi-95/p/9328948.html

