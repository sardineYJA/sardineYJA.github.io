---
layout: post
title: "安装 Python3 及 virtualenv"
date: 2018-03-22
description: "CentOS7 安装 Python3 及 virtualenv"
tag: Python

---

# CentOS7 安装配置

## centos7 自带有 python2

```sh
whereis python
cd /usr/bin/
ll python*
lrwxrwxrwx. 1 root root    7 2月   7 09:30 python -> python2
lrwxrwxrwx. 1 root root    9 2月   7 09:30 python2 -> python2.7
-rwxr-xr-x. 1 root root 7136 8月   4 2017 python2.7
```

## 安装python3依赖

```sh
yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make
```

## 安装pip, wget, 下载python

```sh
#运行这个命令添加epel扩展源
yum -y install epel-release
yum install python-pip
pip install wget
wget https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tar.xz
```

## python3 安装 pip

```sh
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py 
apt-get install python3-distutils
python3 get-pip.py
```

## 解压编译，在/usr/local/目录下就会有python3目录

```sh
#解压
xz -d Python-3.6.4.tar.xz
tar -xf Python-3.6.4.tar
#进入解压后的目录，依次执行下面命令进行手动编译
./configure prefix=/usr/local/python3
make && make install
```

## 修改python命令

```sh
#将原来的链接备份
mv /usr/bin/python /usr/bin/python.bak
#添加python3的软链接
ln -s /usr/local/python3/bin/python3.6 /usr/bin/python
#测试是否安装成功了
python -V
```

## 更改yum配置，因为其要用到python2才能执行，否则会导致yum不能正常使用

```sh
vi /usr/bin/yum
把#! /usr/bin/python修改为#! /usr/bin/python2
vi /usr/libexec/urlgrabber-ext-down
把#! /usr/bin/python 修改为#! /usr/bin/python2
```

## 修改pip命令 

```sh
mv /usr/bin/pip /usr/bin/pip.bak 
ln -s /usr/local/python3/bin/pip3 /usr/bin/pip
pip -V
```




# virtualenv 虚拟环境

## 安装

```sh
pip install virtualenv
```

## 新建虚拟环境

```sh
C:\>virtualenv testenv                            # 默认版本
C:\>virtualenv -p D:\\Python27\\python testenv    # 指定2.7
# 默认情况下，虚拟环境会依赖系统环境中的site packages，
# 就是说系统中已经安装好的第三方package也会安装在虚拟环境中，
# 如果不想依赖这些package，那么可以加上参数 --no-site-packages建立虚拟环境
 
virtualenv --no-site-packages [虚拟环境名称]
C:\testenv\Scripts>activate                       # 激活
(testenv) C:\testenv\Scripts>                     # 注意终端发生了变化
(testenv) C:\testenv\Scripts>pip3 list
(testenv) C:\testenv\Scripts>deactivate           # 关闭当前虚拟环境
C:\testenv\Scripts>
```

## 导出每个包版本/安装所需包

```sh
(venv) $ pip freeze > requirements.txt      # 导出
(venv) $ pip install -r requirements.txt    # 安装
```

requirements.txt文本,其中第一行可指定源，
最后一行表示从当前的setup.py中查找其他依赖项：

```sh
-i http://pypi.doubanio.com/simple/
Django==2.0
django-ranged-response==0.2.0
django-simple-captcha==0.5.11
fasttext==0.8.22
-e .
```


# reference

https://www.jb51.net/article/129027.htm

https://blog.csdn.net/lovefengruoqing/article/details/79284573


