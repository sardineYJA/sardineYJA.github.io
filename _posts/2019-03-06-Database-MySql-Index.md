---
layout: post
title: "MySQL 索引"
date: 2019-03-06
description: "MySQL 索引"
tag: Database

---


# 简介

没有索引时，需要全表检索，即使很早检索到数据也必须搜完所有表。

加完索引后，会建立一个索引文件，这个索引文件会将索引字段的磁盘地址构建一个二叉树的数据结构进行存储，搜索时会进行二分查找，一旦查找到数据就无需继续查找。

一般数据库`默认`都会为`主键、外键`生成索引。


# 使用

## ALTER 创建索引

索引表名table_name ；索引名称index_name

```SQL
1.PRIMARY  KEY（主键索引）
ALTER  TABLE  `table_name`  ADD  PRIMARY  KEY (  `column`  ) 

2.UNIQUE(唯一索引)
ALTER  TABLE  `table_name`  ADD  UNIQUE  (`column` ) 

3.INDEX(普通索引)
ALTER  TABLE  `table_name`  ADD  INDEX  index_name (  `column`  )

4.FULLTEXT(全文索引)
ALTER  TABLE  `table_name`  ADD  FULLTEXT ( `column` )

5.多列索引
ALTER  TABLE  `table_name`  ADD  INDEX index_name (  `column1`,  `column2`,  `column3`  )
```

## CREATE 创建索引

```sql
1.UNIQUE(唯一索引)
CREATE UNIQUE INDEX index_name ON `table_name` (`column` ) 

2.INDEX(普通索引)
CREATE INDEX index_name ON `table_name` (  `column`  )

3.多列索引
CREATE INDEX index_name ON `table_name` (  `column1`,  `column2`,  `column3` )
```

## 删除索引

```SQL
1.PRIMARY  KEY（主键索引）
ALTER  TABLE  `table_name`  DROP PRIMARY KEY

3.INDEX(普通索引)或UNIQUE(唯一索引)
ALTER  TABLE  `table_name`  DROP INDEX index_name
DROP INDEX index_name ON `talbe_name`
```

## 查看表的索引

```SQL
show index from table_name;
show keys from table_name;
```


# 特点

## 普通索引

最基本的索引，没有任何限制

## 唯一索引

索引`列的值`必须唯一，但允许有空值（注意和主键不同）。如果是组合索引，则列值的组合必须唯一，创建方法和普通索引类似。


## 全文索引(FULLTEXT)

大容量的数据表，生成全文索引是一个非常消耗时间非常消耗硬盘空间的做法。


## 单列索引、多列索引

`多个单列索引`与`单个多列索引`的查询效果不同，因为执行查询时，MySQL只能使用一个索引，会从多个索引中选择一个限制最为严格的索引。

## 组合索引（最左前缀）

平时用的SQL查询语句一般都有比较多的限制条件，所以为了进一步榨取MySQL的效率，就要考虑建立组合索引。针对title和time建立一个组合索引：

```SQL
ALTER TABLE article ADD INDEX index_title_time (title(50),time(10));
```

建立这样的组合索引，其实是相当于分别建立了下面两组组合索引：

```
--title,time
--title
```

没有time这样的组合索引是因为MySQL组合索引“最左前缀”的结果。
简单的理解就是只从最左面的开始组合。


## explain 检查语句索引是否生效

`explain select * form `table_name`  where id=10`

```
table：显示这一行的数据是关于哪张表的

type：这是重要的列，显示连接使用了何种类型。从最好到最差的连接类型为const、eq_reg、ref、range、indexhe和ALL

possible_keys：显示可能应用在这张表中的索引。如果为空，没有可能的索引。可以为相关的域从WHERE语句中选择一个合适的语句

key： 实际使用的索引。如果为NULL，则没有使用索引。很少的情况下，MYSQL会选择优化不足的索引。这种情况下，可以在SELECT语句中使用USE INDEX（indexname）来强制使用一个索引或者用IGNORE INDEX（indexname）来强制MYSQL忽略索引

key_len：使用的索引的长度。在不损失精确性的情况下，长度越短越好

ref：显示索引的哪一列被使用了，如果可能的话，是一个常数

rows：MYSQL认为必须检查的用来返回请求数据的行数

Extra：关于MYSQL如何解析查询的额外信息。Using temporary和Using filesort，意思MYSQL根本不能使用索引，结果是检索会很慢
```


# 优化

虽然索引大大提高了查询速度，同时却会降低更新表的速度，如对表进行INSERT、UPDATE和DELETE。
因为更新表时，MySQL不仅要保存数据，还要保存一下索引文件。建立索引会占用磁盘空间的索引文件。
一般情况这个问题不太严重，但如果你在一个大表上创建了多种组合索引，索引文件的会膨胀很快。
索引只是提高效率的一个因素，如果你的MySQL有大数据量的表，就需要花时间研究建立最优秀的索引，或优化查询语句。

## 索引不会包含有NULL值的列

只要列中包含有NULL值都将不会被包含在索引中，复合索引中只要有一列含有NULL值，那么这一列对于此复合索引就是无效的。所以在数据库设计时不要让字段的默认值为NULL。

## 使用短索引

对串列进行索引，如果可能应该指定一个前缀长度。例如，如果有一个CHAR(255)的列，如果在前10个或20个字符内，多数值是惟一的，那么就不要对整个列进行索引。短索引不仅可以提高查询速度而且可以节省磁盘空间和I/O操作。

例：`CREATE INDEX index_name ON table_name(column_name(10))`

## 索引列排序

MySQL查询只使用一个索引，因此如果where子句中已经使用了索引的话，那么order by中的列是不会使用索引的。
因此数据库默认排序可以符合要求的情况下不要使用排序操作；尽量不要包含多个列的排序，如果需要最好给这些列创建复合索引。

## like语句操作

一般情况下不鼓励使用like操作，如果非使用不可，如何使用也是一个问题。
like “%aaa%” 不会使用索引而like “aaa%”可以使用索引。

## 不要在列上进行运算

例如：`select * from users where YEAR(adddate)<2007`，将在每个行上进行运算，这将导致索引失效而进行全表扫描，因此我们可以改成：`select * from users where adddate < '2007-01-01'`。

## 其他

MySQL只对一下操作符才使用索引：<,<=,=,>,>=,between,in,以及某些时候的like(不以通配符%或_开头的情形)。理论上每张表里面最多可创建16个索引。


# reference

https://blog.csdn.net/qq_36570733/article/details/79170651

https://blog.csdn.net/qq_36628908/article/details/80853034

https://blog.csdn.net/aa1215018028/article/details/80982208

