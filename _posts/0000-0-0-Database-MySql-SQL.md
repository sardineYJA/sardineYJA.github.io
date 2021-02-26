---
layout: post
title: "MySQL 语句及优化"
date: 2019-03-03
description: "MySQL 语句及优化"
tag: Database

---

# 常用语句

```sql
show engine;           // 查看当前版本的MySQL支持的存储引擎
show variables like 'default_storage_engine';   // 查看当前默认存储引擎
set storage_engine = InnoDB;                    // 临时修改

show variables like 'character%';     // 查看当前MySQL使用的字符集
set character_set_client = utf8;      // 临时修改字符集
show collation;                       // 查看当前MySQL服务实例支持的字符序
show variables like 'collation%';     // 查看当前MySQL使用的字符序

set names gbk;        // 临时修改字符集，相当于下面三条
set character_set_client = gbk;
set character_set_connection = gbk;
set character_set_results = gbk;
```


```sql
show databases;                     // 查看已经有哪些数据库
create database database_name;      // 创建新数据库
use database_name;                  // 选择该数据库作为当前操作的数据库
show create database database_name; // 查看数据库的结构
drop database database_name;        // 删除数据库

use database_name;                  // 操作此数据库
create table table_name(            // 创建新表
user_id int primary key auto_increment;
username varchar(15) not NULL;
password varchar(15) not NULL;
)auto_increment=1;

show tables;                   // 查看当前操作的数据库所有的表
describe table_name;           // 查看该表的结构
show create table table_name;  // 查看创建表的创建语句
drop table table_name;         // 删除该表

select * from table_name;                 // 查看表中的所有记录
select * from score limit 0,3;            // 查看第一行开始的3行
select distinct class_name from classes;  // 查询并去重

// 向表格插入内容
insert into table_name values ( ); 
如：insert into classes values (NULL, '10maths', '10数学');
如：insert into classes (class_id, class_no, class_name) values (NULL, '10maths', '10数学');

// 更新表格内容
update table_name set column_name = 'new_value' where 条件
如：update student set student_name = '张三' where student_id = 1;
如：update score set grade = grade - 5;     // 全部学生成绩-5
如：update score set grade = grade + 9 where student_id = 1 and course_id = 2;  

// 删除表的记录
delete from table_name where 条件
如：delete from score where student_id = 1 and course_id = 2;        
```


```sql
// inner join 内连接：获取两个表中字段匹配关系的记录（inner join和join一样）
// left join  左连接：获取左表所有记录，即使右表没有对应匹配
// right join 右连接：与左连接相反
// full join  全连接：获取两个表所有记录，相互没有对应匹配补null

from 表1 （inner） join 表2 on 表1和表2之间的链接条件

如：select student_id,student_name,classes.class_id,class_name from classes as c join student as s on s.class_id = c.class_id;
```


```sql
where 显示条件;
如：where course_no = 'maths' and grade between 60 and 90;
如：where class_name in('中文'， '英文');  // 值是否在一个集合中
如：where class_id is NULL;               // 使用 is NULL 或 is not NULL,不是=或！=
如：where name regexp '^杨'               // 正则匹配

// "_"匹配任何单个字符； "%"匹配任意数目字符
select * from student where student_name like '张%'；  // 查询姓张
select * from student where student_name like '%三%'； // 查询带'三'字
select * from student where student_name like '_三%'； // 查询第二个为'三'字

// asc升序； desc降序 
select * from score order by grade asc, student_id desc;
```


```sql
// 聚合函数
// 统计score表中course_id = 1的总成绩
select sum(grade) from score where course_id =1;  

avg(grade)        // 计算字段的平均值
max(grade)        // 最大
min(grade)        // 最小
count(student_id) // 计算行数

group by 字段：将指定字段值相同的记录作为一个分组，也可以多个值 group by A,B,C
如：在score表中查询每个学生的平均成绩
select student_no,student_name,avg(grade)
from score inner join student on score.student_id = student.student_id
group by score.student_id;

having 条件：从结果中提取符合条件的分组
如：在score表中查询学生平均成绩高于70的学生记录
select student_no,student_name
from score inner join student on score.student_id = student.student_id
group by score.student_id
having avg(grade)>70;
```


```sql 
# case when then else end
select *,(case when score>=90 then '优秀'
			   when score>=60 then '及格'
			   else '不及格'
		  end)
from mathTable;

```


```sql
select 1 from table;
select anycol(任意一行） from table;
select * from table; 
```
从作用上来说是没有差别的，都是查看是否有记录，一般是作条件查询用的。
第一个的1是一常量（可以为任意数值），查到的所有行的值都是它，但从效率上来说，1>anycol>\*，因为不用查字典表。


随机函数rand()是获取一个0-1之间的数，利用这个函数和order by一起能够数据随机排序（乱序）
```SQL
select * from 表名 order by 2;                  # 表示根据第二列排序，以往直接写列名 
select * from 表名 order by rand();             # 乱序
select * from 表名 order by rand() limit() 3;   # 随机抽取3条
```


```sql
# 表1
("张三", "数学", 34),
("张三", "语文", 58),
("张三", "英语", 58),
("李四", "数学", 45),
("李四", "语文", 87),
("李四", "英语", 45),
("王五", "数学", 76),
("王五", "语文", 34),
("王五", "英语", 89);

# 表2
张三, 34, 58, 58;
李四, 45, 87, 45;
王五, 76, 34, 89;

# 表1转表2，行转列
select name,
	MAX(case courseName when '数学' then score else 0 end) 数学，
	MAX(case courseName when '语文' then score else 0 end) 语文,
	MAX(case courseName when '英语' then score else 0 end) 英语
from tableName
group by name;   # 需要group by
```




# 优化


## 索引

explain显示了mysql如何使用索引来处理select语句以及连接表，可以帮助选择更好的索引和写出更优化的查询语句。


查找表中的第800000条数据后面的20条数据。如何分页。

方法一：直接通过limit start count分页语句：
select * from Product limit 800000, 20;

总结：方便，但是对记录很多的表并不适合直接使用。start越大，速度越慢，效率低。

方法二：利用表的覆盖索引来加速分页查询：
select * from Product where ID > (select ID from Product limit 800000, 1) limit 20


limit千万级分页的时候优化（使用between and）而不是limit m，n。


当只要一行数据时使用 LIMIT 1，你已经知道结果只会有一条结果或者只需要一条数据，加上 LIMIT 1 可以增加性能。


使用JOIN时候，应该用小的结果驱动大的结果（left join 左边表结果尽量小，如果有条件应该放到左边先处理，right join同理反向）。


避免因sql语句不当而致使索引无效的情况，常见的有：

1. 在索引列进行运算或者使用函数导致索引失效

2. 在sql中使用`<> 、not in 、not exist、!=，or，like "%_" 百分号在前，where后使用IS NULL、IS NOT NULL或者使用函数`，会使索引失效。


仅列出需要查询的字段，不要使用select * from ...，节省内存。


## 慢查询日志

```sql
show variables like 'slow_query_log%';  # 查询是否开启慢查询
show variables like 'long_query%';      # 查看慢查询超时时间，默认10s

set global slow_query_log=1;     # 开启
set global long_query_time=4;    # 修改时间

show global status like '%Slow_queries%';  # 查询全部慢查询数量
```

永久开启慢查询记录：vi my.cnf
```sh
slow_query_log =1                           # 开启
slow_query_log_file=/tmp/data/slow.log      # log目录
long_query_time = 10                        # 超时时长
```

