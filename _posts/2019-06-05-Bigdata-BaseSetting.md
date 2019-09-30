---
layout: post
title: "搭建大数据基础环境"
date: 2019-06-05
description: "简单介绍一下搭建大数据基础环境"
tag: Bigdata

---

# 环境配置

## 主机名修改

修改主机名
```
vi /etc/sysconfig/network
HOSTNAME=hadoop101
```

配置集群dns解析
```
vi /etc/hosts
192.168.34.101 hadoop101
192.168.34.102 hadoop102
192.168.34.103 hadoop103
```

## 防火墙关闭

```
firewall-cmd --state
systemctl stop firewalld.service
systemctl disable firewalld.service
```

## 创建具备root权限的用户

创建用户：`useradd 用户名`

创建并分组：`useradd -g 组名 用户名`

设置密码：`passwd 用户名`

检查用户：`id 用户名`

修改用户分组：`usermod -g 用户组 用户名`



## 安装JDK，配置路径
1. 查询是否安装Java软件：`[hadoop101 opt]$ rpm -qa | grep java`

2. 如果安装的版本低于1.7，卸载该JDK：`[hadoop101 opt]$ sudo rpm -e 软件包`

3. 查看JDK安装路径：`[hadoop101 ~]$ which java`

4. 解压JDK：`[hadoop101 software]$ tar -zxvf jdk-8u144-linux-x64.tar.gz -C /opt/module/`

5. 配置JDK环境变量：`[hadoop101 software]$ sudo vi /etc/profile`

```
#JAVA_HOME
export JAVA_HOME=/opt/module/jdk1.8.0_144
export PATH=$PATH:$JAVA_HOME/bin
```

6. 让修改后的文件生效：`[hadoop101 jdk1.8.0_144]$ source /etc/profile`

7. 测试JDK是否安装成功：`[@hadoop101 jdk1.8.0_144]# java -version`


## 已安装的JDK，配置路径
（之前测试系统的jdk是1.7就直接使用，建议自己安装jdk1.8）

```
在linux下,如何找java的安装路径
$ whereis java
java: /usr/bin/java /usr/share/java /usr/lib/jvm/java-8-openjdk-amd64/bin/java /usr/share/man/man1/java.1.gz
$ ls -lrt /usr/bin/java
/usr/bin/java -> /etc/alternatives/java
$ ls -lrt /etc/alternatives/java
/etc/alternatives/java -> /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java
```

```
编写配置文件vi /etc/profile
##JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk-1.7.0.221-2.6.18.0.el7_6.x86_64/jre
export PATH=$JAVA_HOME/bin:$PATH
```


## 远程拷贝

scp（secure copy）安全拷贝：scp -r /test  root@hadoop102:/opt/test

rsync -rvl(r递归,v显示过程,l拷贝符号连接) /test  root@hadoop102:/opt/test


## SSH无密登录设置

1. 生成公钥和私钥：`ssh-keygen -t rsa`(多次直接回车)

2. 将公钥拷贝到目标机器上：ssh-copy-id 192.xxx.xxx.xxx

3. 登录：ssh 192.xxx.xxx.xxx

