---
layout: post
title: "快速搭建1 —— 集群环境准备"
date: 2020-03-15
description: "Bigdata"
tag: Bigdata

---

## 项目流程

![png](/images/posts/all/用户行为分析项目数据流程图.jpg)

## 节点功能

![png](/images/posts/all/大数据功能节点图.jpg)


# 虚拟机

## 准备

- 系统：CentOS-7-x86_64-DVD-1810.iso

- 用户密码：root，123456

- 考虑测试开启多个jps进程，后续可以将内存提升1台4G, 2台3G


## 网络修改

- 网络选择：NAT 模式

- 查看ip：`ip addr`，发现没有ip，同时也不可以上网

- 修改：`vi /etc/sysconfig/network-scripts/ifcfg-ens33`，`ONBOOT=yes`即可上网

## 拟网络编辑器

VMnet8 (即NAT模式)，编辑->虚拟网络编辑器中，一般主机，VMnet1，VMnet8它们ip前两位一样,没必要则无需修改.为了方便，此版本作为备份。


# 服务器

## 准备

- 拷贝一台服务

- 修改成静态ip：`vi /etc/sysconfig/network-scripts/ifcfg-ens33`，重启`service network restart`
```sh
ONBOOT=yes
BOOTPROTO=static
IPADDR=XXX.XXX.XXX.124
NETMASK=255.255.255.0
GATEWAY=XXX.XXX.XXX.2
DNS1=XXX.XXX.XXX.2
PREFIX=24
```

- 修改主机名：`vi /etc/sysconfig/network`成`HOSTNAME=VM124`

- 配置DNS解析
```sh
vi /etc/hosts
XXX.XXX.XXX.124 VM124
XXX.XXX.XXX.125 VM125
XXX.XXX.XXX.126 VM126
...
```

- 防火墙关闭
```sh
firewall-cmd --state  # service firewalld status
systemctl stop firewalld.service
systemctl disable firewalld.service
```

- 创建具备root权限的用户
```sh
useradd -g root yang
passwd yang
id yang     ## 检测用户
```


## 补充需要安装

- rsync安装：`yum -y install rsync`

- ifconfig安装：`yum search ifconfig`

- nc安装：`yum -y install nc`

- ntp安装：`yum -y install ntp`    集群时间同步

- wget安装：`yum -y install wget`

- unzip安装：`yum -y install unzip`

- pasmisc安装：`yum -y install psmisc`    HA高可用需要命令

- java安装：https://www.oracle.com/java/technologies/javase/javase-jdk8-downloads.html
```sh
tar -zxvf jdk-8u144-linux-x64.tar.gz -C /opt/module/
vi /etc/profile
## JAVA_HOME
export JAVA_HOME=/home/yang/module/jdk1.8.0_241
export PATH=$PATH:$JAVA_HOME/bin
source /etc/profile
```


## 切换用户

- 切换yang用户，接下来所有的操作使用yang用户

- /home/yang目录下创建module，sofware, sh等目录

- 以此再复制两台，修改静态ip，主机名



## SSH 无密登录

生成公钥和私钥：ssh-keygen -t rsa(多次直接回车)

将公钥拷贝到目标机器上：ssh-copy-id 192.xxx.xxx.xxx

登录：ssh 192.xxx.xxx.xxx

注意1：自身也发自己公钥一次方便后续脚本运行

注意2：其他机器也要生成，并相互发送，否则后续HA可能NameNode故障转移会失败（如：namenode1故障，namenode2需要ssh namenodde1）


## 同步脚本

创建：xsync文件

```sh
#!/bin/bash

all_VM=(VM125 VM126)   # 只需增加所需同步的服务器

#################### 下面尽量不要修改 ################
# 没有参数直接退出
pcount=$#
if((pcount==0)); then
echo no args;
exit;
fi

# 获取文件名称
p1=$1
fname=`basename $p1`
echo fname=$fname

# 获取上级目录到绝对路径
pdir=`cd -P $(dirname $p1); pwd`
echo pdir=$pdir

# 获取当前用户名称
user=`whoami`

# 循环
for i in ${all_VM[*]}
do        
	echo -------------- rsync ==》 $i --------------
	rsync -rvl $pdir/$fname $user@$i:$pdir
done
```

修改权限：`chmod 777 xsync`

全局使用：将xsync移动到/usr/local/bin目录下


## 集群同步时间

待补充...



