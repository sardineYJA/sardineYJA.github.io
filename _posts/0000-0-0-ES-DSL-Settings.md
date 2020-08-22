---
layout: post
title: "Settings 部分内容"
date: 2020-06-20
description: "Elasticsearch"
tag: ELK

---


# 模板_template

```sh
PUT _template/your-name_tpl
{
  "order" : 1,               # 优先级，越大越优先，多个 template ，那么就会先应用 order 数值小的 template 设置，然后再应用一遍 order 数值高的作为覆盖，最终达到一个 merge 的效果，所以更多时候公用模板autoindex 匹配 * ，order 0，其他模板为1。
  "index_patterns" : [
    "my-index-*"           # 匹配名
  ],
    
  "settings" : {
    "index": {
      "number_of_shards": "2",
      "number_of_replicas": "1",
      "refresh_interval": "5s",
  
      "analysis": {
        "analyzer": {
          "my_analyzer": {
            "type": "custom",
            "tokenizer": "ik_max_word"
          }
        }
      }
    }
  },
    
  "mappings": {
    "doc": {
      "dynamic_templates":       ## 动态映射字段类型
      [                 
        {
          "auto_int": {
            "match": "*_int",
            "match_mapping_type": "string",
            "mapping": {
              "type": "integer"
            }
          }
        },
        # 添加其他的动态模板
      ]
      "properties": {            ## 自定义字段类型
        "ftime": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "uid": {
          "type": "keyword"
        },
        "content": {
          "type": "text",
          "analyzer": "ik_max_word"
        },
        "username": {   ## 默认类型：username.keyword字段实现关键词搜索及数据聚合
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        }
      }
    }
  }, 
  "aliases": {}                # 别名
}
```

## 字段

```sh
"age": {
    "type": "integer",
    "doc_value": false,      ## 不允许聚合，sort、aggregate、access the field from script将会无法使用，可节省磁盘
    "index": false           ## 字段不能够被搜索，也不会分词
}
```
- 如不需要检索、排序和聚合分析, 则可设置 "enable": false
- 如不需要检索, 则可设置 "index": false
- 如不需要排序、聚合分析功能, 则可设置 "doc_values": false / "fielddate": false
- 更新频繁、聚合查询频繁的 keyword 类型的字段, 推荐设置 "eager_global_ordinals": true


## 字段类型

```sh
PUT my_index
{
  "mappings": {
    "_doc": {
      "properties": {
        "username": {   ## 默认类型：username.keyword字段实现关键词搜索及数据聚合
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "name": { 
          "type": "text",
          "fields": {
            "length": {  ## 为name定义的另外一个映射方式，其原始输入值还是name字段。
              "type":     "token_count",     # 定义name.length字段，其类型为token_count
              "analyzer": "standard"        
            }
          }
        }
      }
    }
  }
}
```



## 修改 settings

```sh
POST yang-test-1/_close       # 修改前需关闭index
POST yang-test-1/_open
PUT yang-test-1/_settings
{...}
```


## 修改 mapping

ES 的 mapping 一旦设置了之后是不能修改的，只能新建index，再reindex导入数据。

具体步骤：

1. 获取旧mapping，新建index，利用别名，重新 reindex

2. index_1 别名 A，在搜索的时候就可以在别名中搜索，会自动映射到index_1

3. 修改后的index_1 的 mapping 成新索引 index_2，利用 reindex 同步数据

4. 别名映射从 A->index_1 变成 A->index_2 可以实现无缝切换


```sh
POST _aliases
{
  "actions": [
    {"remove": {"index": "index_1", "alias": "test-alias"}},
    {"add": {"index":"index_2", "alias": "test-alias"}}
  ]
}
```




# 分词器

- standard   （默认）将词汇单元转换成小写形式，并去除停用词和标点符号。中文采用的方法为单字切分。
- whitespace  空格分隔符，仅仅是去除空格，对字符没有lowcase化,不支持中文。
- stop        删除stop words，增加了去除英文中的如the，a等，也可加要设置常用单词，不支持中文。
- keyword     不分词
- ik_max_word 中文分词，最细颗粒
- ik_smart    中文分词，最粗颗粒
- pinyin      拼音分词
- jieba_index    用于索引分词，分词粒度较细
- jieba_search   用于查询分词，分词粒度较粗
- jieba_other    全角转半角、大写转小写、字符分词

> es 启动加载动态词库后，如何词库不可用，实际上暂时不影响词库使用。如果将所有加载动态词库的节点重启一遍，则词库就会不可用了。


## 测试

```sh
GET <index>/<type>/_analyze    # 测试分词器效果，index和type可选
{
  "analyzer": "standard",
  "text": "this is a test 这是中文，中华人民共和国"
}
```

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

- 不指定分词时，会使用默认的standard。

- 明确字段是否需要分词，不需要分词的字段将type设置为keyword，可以节省空间和提高写性能。


## 自定义

```sh
# 测试
POST /myindex/_analyze
{
  "analyzer": "my_analyzer",
  "text": ["This is 中华人民共和国", "<p>I&apos;m so <b>happy</b>!</p>"]
}
```

```sh
PUT /myindex
{
  "settings": {
    "analysis": {

      "filter": {
        "my_stopwords":{
          "type":"stop",
          "stopwords":["a","the","is"]
        },
        "my_pinyin": {
          "type": "pinyin"
        }
      },
      
      "analyzer": {
        "my_ik_max_analyzer":{
          "type":"custom",
          "char_filter":["html_strip","&_to_and"],
          "tokenizer":"ik_max_word",
          "filter":["lowercase","my_stopwords"]  # 转为小写，去停用词
        },
        "my_ik_smart_analyzer": {
          "type":"custom",
          "tokenizer":"ik_smart"
        }
      }
    }
  }
}
```

## ngram

```sh
{
    "settings" : {
        "analysis" : {
            "analyzer" : {
                "my_ngram_analyzer" : {
                    "tokenizer" : "my_ngram_tokenizer"
                }
            },
            "tokenizer" : {
                "my_ngram_tokenizer" : {
                    "type" : "nGram",
                    "min_gram" : "2",
                    "max_gram" : "3",
                    "token_chars": [ "letter", "digit" ]
                }
            }
        }
    },

    "mappings": {
        "doc": {
            "properties": {
                "info": {
                    "type": "text",
                    "analyzer": "my_ngram_analyzer",
                    "search_analyzer": "ik_smart"
                }
            }
        }
    }
}

```
