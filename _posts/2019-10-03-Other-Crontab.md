---
layout: post
title: "crontab 定时任务"
date: 2019-10-03
description: "crontab 定时任务"
tag: Other

---


# 定时任务

```sh
systemctl status crond   # 状态

crontab -l   # 查看定时任务

crontab -e   # 编辑任务
``` 

## 格式

格式：`分钟 小时 日期 月份 周 命令`

范围：0-59 0-23 1-31 1-12 0-7 command


特殊字符：
```
*(星号) 代表任何时刻都接受。

,(逗号) 代表分隔时段的意思。

-(减号) 代表一段时间范围内。

/n(斜线) 那个 n 代表数字，每隔 n 单位间隔
```

案例：
```sh
5 10 1 5 * command     # 每年的五月一日 10:5 执行一次

0 3,6 * * * command    # 每天的三点，六点各执行一次

20 8-11 * * * command  # 每天的8:20, 9:20,10:20,11:20各执行一次

*/5 * * * * command    # 每五分钟执行一次

0 10 * * 1 command     # 每周一的十点执行一次
```

测试每分钟：`* * * * * date >> /home/yangja/sh/date.txt` 



# 数据库备份

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


