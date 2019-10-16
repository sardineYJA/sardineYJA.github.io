---
layout: post
title: "MySQL 安装及常用语句"
date: 2019-03-03
description: "简单介绍MySQL的常用语句"
tag: Database

---


## 安装

数据库的安装登录需要root用户

1. 查看：rpm -qa\|grep mysql

2. 卸载所有：rpm -e --nodeps mysql-xxx.x86_64

3. 下载：https://dev.mysql.com/downloads/mysql/

4. centos7选择：Red Hat Enterprise Linux 7 / Oracle Linux 7 (x86, 64-bit)，(MySQL-5.6.45-1.el7.x86_64.rpm-bundle.tar)

5. 解压：tar -xvf MySQL-5.6.45-1.el7.x86_64.rpm-bundle.tar

6. 创建mysql用户和组(无需也可安装成功，只是警告mysql用户和mysql组不存在)
```
groupadd -g 1000 mysql        // GID为1000
useradd mysql -g mysql -p mysql
```

7. 安装服务器：`rpm -ivh MySQL-server-5.6.45-1.el7.x86_64.rpm`

8. 查看密码：`cat /root/.mysql_secret`

9. 开启：`service sql start`

10. 安装客户端：`rpm -ivh MySQL-client-5.6.45-1.el7.x86_64.rpm`

11. 登录：`mysql -uroot -pYourPassword`

12. 修改密码：`> set password=password('root123456');`

13. 退出重新登录

14. Centos7 查看`systemctl stop|start|restart|status mysql`


## 设置远程登录

配置只要是root+password，在任何主机都可登录MySQL，否则远程连接提示不允许连接

```SQL
use mysql;
desc user;
select user, host, password from user;
update user set host='%' where host='localhost';
delete from user where host='hadoop101';
delete from user where host='127.0.0.1';
delete from user where host='::1';
flush privileges;	
```

关闭防火墙或开放3306端口，否则远程连接报错：

> 2003 - Can't connect to MySQL server on ' '(10038)


```sh
##Centos7 防火墙打开端口号
firewall-cmd --zone=public --add-port=3306/tcp --permanent
 
#下面3行是参数说明
#–zone                                  #作用域
#–add-port=80/tcp                       #添加端口，格式为：端口/通讯协议
#–permanent                             #永久生效，没有此参数重启后失效
 
#重启防火墙后看看是否生效
firewall-cmd --reload           #重启firewall
firewall-cmd --list-ports       #查看已经开放的端口
 
 
#如果想永久停止防火墙，执行下面操作
systemctl stop firewalld.service         #停止firewall
systemctl disable firewalld.service      #禁止firewall开机启动
 
#查看防火墙状态
firewall-cmd --state            #查看默认防火墙状态（关闭后显示notrunning，开启后显示running）

```

## 免认证登录

> ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using passwor)

问题分析：在安装完数据库之后，没有设置初始密码于是导致使用 mysql -u root -p xxx是无法登录的，因为没有密码，于是需要重新设置密码。

修改mysql的配置文件 /etc/my.cnf   

最后一行添加 `skip-grant-tables` 表示可以跳过权限去登录

重启 mysql 数据库（虚拟机测试，建议直接免认证登录，方便多了）

此时直接命令：mysql 即可登录，而且远程也可直接连接

修改 mysql 表里面的用户，为其设置密码

```sql
use mysql;
update user set password=PASSWORD("root123456") where user='root';
flush privileges;
```

> Unknown column 'password' in 'field list'

错误分析：新版本mysql采用authentication_string替代了password字段

```sql
use mysql;
select user, host, authentication_string from user;    # 查看
select version() from dual;                            # 查看版本
select version();                                      # 查看版本


update user set authentication_string=PASSWORD("root123456") where user='root';
flush privileges;
```

删除 `skip-grant-tables`，重新启动



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

group by 字段：将指定字段值相同的记录作为一个分组
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
select 1 from table;
select anycol(任意一行） from table;
select * from table; 
```

 从作用上来说是没有差别的，都是查看是否有记录，一般是作条件查询用的。
 第一个的1是一常量（可以为任意数值），查到的所有行的值都是它，但从效率上来说，1>anycol>\*，因为不用查字典表。


## 优化

查找表中的第800000条数据后面的20条数据。如何分页。

方法一：直接通过limit start count分页语句：
select * from Product limit 800000, 20;

总结：方便，但是对记录很多的表并不适合直接使用。start越大，速度越慢，效率低。

方法二：利用表的覆盖索引来加速分页查询：
select * from Product where ID > (select ID from Product limit 800000, 1) limit 20

