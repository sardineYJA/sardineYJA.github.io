---
layout: post
title: "CentOS 7安装python3"
date: 2018-03-22
description: "介绍新装的CentOS 7安装python3"
tag: Python

---

# 安装配置
centos7 自带有 python，但是却是 python2 版本的 python
```
[root]# whereis python
[root@root ~]# cd /usr/bin/
[root@root bin]# ll python*
lrwxrwxrwx. 1 root root    7 2月   7 09:30 python -> python2
lrwxrwxrwx. 1 root root    9 2月   7 09:30 python2 -> python2.7
-rwxr-xr-x. 1 root root 7136 8月   4 2017 python2.7
```

安装python3依赖
```
yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make
```

安装pip, wget, 下载python
```
#运行这个命令添加epel扩展源
yum -y install epel-release
yum install python-pip
pip install wget
wget https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tar.xz
```

解压编译，在/usr/local/目录下就会有python3目录
```
#解压
xz -d Python-3.6.4.tar.xz
tar -xf Python-3.6.4.tar
#进入解压后的目录，依次执行下面命令进行手动编译
./configure prefix=/usr/local/python3
make && make install
```

修改python命令
```
#将原来的链接备份
mv /usr/bin/python /usr/bin/python.bak
#添加python3的软链接
ln -s /usr/local/python3/bin/python3.6 /usr/bin/python
#测试是否安装成功了
python -V
```

更改yum配置，因为其要用到python2才能执行，否则会导致yum不能正常使用
```
vi /usr/bin/yum
把#! /usr/bin/python修改为#! /usr/bin/python2
vi /usr/libexec/urlgrabber-ext-down
把#! /usr/bin/python 修改为#! /usr/bin/python2
```

修改pip命令 
```
mv /usr/bin/pip /usr/bin/pip.bak 
ln -s /usr/local/python3/bin/pip3 /usr/bin/pip
pip -V
```

# 参考
1. https://blog.csdn.net/lovefengruoqing/article/details/79284573