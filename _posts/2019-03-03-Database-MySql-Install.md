---
layout: post
title: "MySQL 设置及备份"
date: 2019-03-03
description: "设置及备份"
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



##  数据库备份

```sh
#!/bin/sh

####### 文件名为当天时间
time=`date '+%Y-%m-%d %H:%M:%S'`
echo $time
echo '开始备份数据库....'

####### 数据库配置
user=root
password=root123456
dbname=firstfood
mysql_back_path=/home/yangja/sh/mysqlbak

/usr/bin/mysqldump -h127.0.0.1 -u$user -p$password $dbname > $mysql_back_path/$time.sql
echo $mysql_back_path/$time.sql
echo -e '数据库备份完成\n'

find $mysql_back_path -type f -mtime +7 -exec rm {} \;     # 删除7天以上的备份sql
```

测试备份数据库：`30 2 * * * /home/yangja/sh/back_mysql.sh >> /home/yangja/sh/back_mysql.log`




