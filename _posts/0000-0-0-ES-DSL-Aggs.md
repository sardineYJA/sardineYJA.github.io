---
layout: post
title: "DSL 聚合操作"
date: 2020-09-10
description: "DSL"
tag: ELK

---


# 聚合 aggs 操作

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

