---
layout: post
title: "Django QuerySet常见接口"
date: 2019-02-13
description: "介绍Django QuerySet常见接口"
tag: Web框架

---

# 接口
## 支持链式
```
all 接口：相当于SELECT*FROM table_name 语句，用于查询所有数据。
filter 接口：根据条件过滤数据，常用的条件基本上是字段等于、不等于、大于、小于。
exclude 接口：同filter，只是相反的逻辑。
reverse 接口：把Queryset中的结果倒序排列。
distinct 接口：用来进行去重查询，产生SELECT DISTINCT的SQL查询。
none 接口：返回空的Queryset。
```

## 不支持链式
```
```

# 常见参数
```

``` 

# 例子
```
```

