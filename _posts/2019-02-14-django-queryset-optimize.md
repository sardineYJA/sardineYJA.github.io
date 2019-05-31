---
layout: post
title: "关于QuerySet的优化"
date: 2019-02-14
description: "介绍关于QuerySet的优化"
tag: Web框架

---

# 介绍

## 懒加载
QuerySet本质是懒加载的对象，如下请两句不会产生数据库查询，只是返回一个QuerySet对象，等你真正使用它时才会执行查询。
```python
posts = Post.objects.all()                 # 返回QuerySet对象
available_posts = posts.filter(status=1)   # 返回QuerySet对象
print(available_posts)                     # 数据库查询
```


## defer接口
特点：把不需要展示的字段做延迟加载。拿到的记录不包含content部分，用到时才会加载。
```python
posts = Post.objects.all().defer('content')
for post in posts:             # 此时执行数据库查询 
	print(post.content)        # 此时执行数据库查询，此时才加载content
```
注意：上面代码产生N+1问题。


## only接口
与defer接口相反，只获取某个内容，其他值在获取时会产生额外的查询。


## select_related接口
解决外键产生的N+1问题，解决一对多问题。
```python
posts = Post.objects.all()
for post in posts:      # 产生数据库查询
	print(post.owner)   # 产生额外的数据库查询，owner(关联表)

# 解决
posts = Post.objects.all().select_related('category')
for post in posts:      # 产生数据库查询,cotegory数据也会一次性查询出来
	print(post.category)
```


## prefetch_related接口
解决外键产生的N+1问题，解决多对多问题。
```python
posts = Post.objects.all().prefetch_related('tag')
for post in posts:      # 产生两条查询，分别查询post和tag
	print(post.tag.all())
```


## 数据库优化
添加索引
```python
title = models.CharField(max_length=100, blank=True, db_index=True, verbose_name=u'标题')
```

## QuerySet会被缓存
```python
news = News.objects.get(id=1)
news.channel   # 此时的channel对象会从数据库取出
news.channel   # 这时的channel是缓存的版本，不会造成数据库访问

# 方法的调用每次都会触发数据库查询
news = News.objects.get(id=1)
news.authors.all()   # 执行查询
news.authors.all()   # 再次执行查询
```


## 使用iterator()
获取大量数据时，使用iterator()
```python
news_list = News.objects.filter(title__contains='..')
for news in news_list.iterator():
    print(news)
```

## 使用原生的SQL
```python
cl = Channel.objects.raw('SELECT * FROM channel WHERE id = 1')
print(cl)
# <RawQuerySet: 'SELECT * FROM channel WHERE id = 1'>
for c in cl:
    print(c)
```

## QuerySet.values()和values_list()
不要获取你不需要的数据，当只需要一个字段的值，返回list或者dict.
```python
# values
news_list = News.objects.values('title').filter(channel__id=1)
print(news_list)
# [{'title': ''}, ...]

# values_list
news_list = News.objects.values_list('title').filter(channel__id=1)
print(news_list)
# [('新闻标题',),('新闻标题', ) ...]
```


# 直接使用外键的值
```python
# 获取频道的id
news.channel_id
new.channel.id     # 不要这样
```


## 使用 QuerySet.count()
如果你只是想要获取有多少数据，不要使用 len(queryset) 。

## 使用 QuerySet.exists()
如果你只是想要知道是否至少存在一个结果，不要使用 if querysets 。


# 参考
1. 《Django企业开发实战》
2. https://www.the5fire.com/django-database-access-optimization.html
