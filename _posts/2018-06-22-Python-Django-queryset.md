---
layout: post
title: "Django QuerySet 常见接口"
date: 2018-06-22
description: "介绍Django QuerySet常见接口"
tag: Python

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
get 接口：
try：
	post=Post.objects.get（id=1）
except Post.DoesNotExist：
	pass

create 接口：post=Post.objects.create（title="一起学习Django实战吧"）

get_or_create 接口：根据条件查找，如果没查找到，就调用create创建。

update_or_create 接口：同get_or_create，只是用来做更新操作。

count 接口：用于返回Queryset有多少条记录。

latest 接口：用于返回最新的一条记录，但是需要在Model的Meta中定义：get_latest by=<用来排序的字段>。

earliest接口：同上，返回最早的一条记录。

first / last 接口：从当前 Queryset记录中获取第一条/最后一条。

update 接口：用来根据条件批量更新记录。

delete 接口：同update，根据条件批量删除记录。需要注意的是，update和delete都会触发Django的signal。

values接口：当我们明确知道只需要返回某个字段的值，不需要Model实例时。

values_1ist 接口：同values，但是直接返回的是包含tuple的Queryset。

```

## 条件
```
contains：包含，用来进行相似查询。
icontains：同contains，只是忽略大小写。
exact：精确匹配。
iexact：同exact，忽略大小写。
in：指定某个集合，比如Post.objects.filter（id__in=[1，2，3]）。
gt：大于某个值。
gte：大于等于某个值。
1t：小于某个值。
1te：小于等于某个值。
startswith：以某个字符串开头，与contains类似，只是会产生LIKE'<关键词>%'。
istartswith：同startswith，忽略大小写。
endswith：以某个字符串结尾。
iendswith：同endswith，忽略大小写。
range：范围查询，多用于时间范围，如Post.objects.filter（created_time_range=（2018-05-01，2018-06-011））时间段之内。
```


# 例子
```python
A.objects.create(id=1,name='yang')
A(name='yang', email='').save()
A.objects.get_or_create(...)

Post.objects.all()[:10]
Post.objects.filter(id=1).update(title='更新')
Post.objects.filter(id=1).values('title')

Person.objects.filter(name__iexact="abc")   # 名称为 abc 但是不区分大小写，可以找到 ABC, Abc, aBC，这些都符合条件
Person.objects.filter(name__contains="abc") # 名称中包含 "abc"的人

from django.db.models import Q, F
Post.objects.filter(Q(id=1) | Q(id=2))  # or
Post.objects.filter(Q(id=1) & Q(id=2))  # and

post = Post.objects.get(id=1)
post.pv = F('pv') + 1     # 在数据库层面执行原子性操作
post.save()               # 解决多线程不同步问题
```

