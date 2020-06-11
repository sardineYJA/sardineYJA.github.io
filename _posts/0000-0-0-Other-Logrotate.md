---
layout: post
title: "Logrotate 日志滚动切割工具"
date: 2020-06-11
description: "Logrotate"
tag: Other

---

## 简介

Logrotate 是基于CRON来运行的，其脚本是/etc/cron.daily/logrotate，日志轮转是系统自动完成的。

Linux系统默认安装logrotate工具，它默认的配置文件在：
- `/etc/logrotate.conf`
- `/etc/logrotate.d/`


## 切割介绍

比如以系统日志/var/log/message做切割来简单说明下：
第一次执行完rotate之后，原本的messages会变成messages.1，而且会制造一个空的messages给系统来储存日志；
第二次执行之后，messages.1会变成messages.2，而messages会变成messages.1，又造成一个空的messages来储存日志！

```sh
/usr/sbin/logrotate -f /etc/logrotate.d/mysql-server
/usr/sbin/logrotate -d -f /etc/logrotate.d/mysql-server
# -d, --debug ： debug模式，测试配置文件是否有错误
# -f, --force ： 强制转储文件
# -v, --verbose ：显示转储过程
```

## 参数

- weekly         默认每一周执行一次rotate轮转工作：daily、weekly、monthly、yearly

- rotate 4       保留日志文件个数，默认保留四个，0 指没有备份

- create         自动创建新的日志文件，新的日志文件具有和原来的文件相同的权限；因为日志被改名,因此要创建一个新的来继续存储之前的日志

- dateext        切割后的日志文件以当前日期为格式结尾，如xxx.log-20131216,如注释掉,切割出来是按数字递增,xxx.log.1格式

- compress       是否通过gzip压缩转储以后的日志文件，如xxx.log-20131216.gz ；如果不需要压缩，注释掉就行

- missingok      如果日志丢失，不报错继续滚动下一个日志

- sharedscripts  运行postrotate脚本，作用是在所有日志都轮转后统一执行一次脚本。如果没有配置这个则每个日志轮转后都会执行一次脚本

- postrotate     在logrotate转储之后需要执行的指令，例如重新启动 (kill -HUP) 某个服务！必须独立成行


## mysql 日志滚动

/etc/logrotate.d/mysql-server

```sh
/var/log/mysql.log /var/log/mysql/mysql.log /var/log/mysql/mysql-slow.log {
        daily
        rotate 7
        missingok
        create 640 mysql adm
        compress
        sharedscripts
        postrotate
                test -x /usr/bin/mysqladmin || exit 0
                MYADMIN="/usr/bin/mysqladmin --defaults-file=/etc/mysql/debian.cnf"
                if [ -z "`$MYADMIN ping 2>/dev/null`" ]; then
                  if killall -q -s0 -umysql mysqld; then
                    exit 1
                  fi
                else
                  $MYADMIN flush-logs
                fi
        endscript
}
```

## 关于配置文件权限

手动切割：`/usr/sbin/logrotate -vf /etc/logrotate.d/mysql-server`

> Ignoring /etc/logrotate.d/mysql-server because of bad file mode

只有文件权限是 0644 的时候，配置文件才会被读取！

```sh
chmod 644 /etc/logrotate.d/mysql-server
chown root:root /etc/logrotate.d/mysql-server
```

## 滚动失败

> error: skipping "/var/log/xxx.log" because parent
directory has insecure permissions (It's world writable or writable by
group which is not "root") Set "su" directive in config file to tell
logrotate which user/group should be used for rotation.


原因：
一番试错发现对应日志文件（xxxlog）的父文件夹有“w”的组权限。
暂时没能google到为什么组权限有“w”就不安全。

解决方法：
方法一：去掉对应日志父目录的`w`组权限 ---- chmod g-w。
方法二：在对应的logrotate配置文件中添加 `su <dir_user> <dir_group>`。

## filebeat 获取 mysql-slow.log 权限拒接

默认路径：/var/log/mysql/mysql-slow.log，filebeat 还需要 mysql/ 目录的 o+rx 权限


