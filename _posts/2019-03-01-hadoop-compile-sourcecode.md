---
layout: post
title: "Hadoop编译源码"
date: 2019-03-01
description: "简单介绍Hadoop编译源码过程"
tag: 大数据

---

# 准备
1. hadoop-2.7.2-src.tar.gz
2. jdk-8u144-linux-x64.tar.gz
3. apache-ant-1.9.9-bin.tar.gz（build工具，打包用的）
4. apache-maven-3.0.5-bin.tar.gz
5. protobuf-2.5.0.tar.gz（序列化的框架）

# jar包安装
1. JDK解压、配置环境变量 JAVA_HOME和PATH，验证java-version
```
[root]# tar -zxf jdk-8u144-linux-x64.tar.gz -C /opt/module/
[root]# vi /etc/profile
#JAVA_HOME：
export JAVA_HOME=/opt/module/jdk1.8.0_144
export PATH=$PATH:$JAVA_HOME/bin
[root]#source /etc/profile
java -version
```

2. Maven解压、配置MAVEN_HOME和PATH
解压
```
[root]# tar -zxvf apache-maven-3.0.5-bin.tar.gz -C /opt/module/
[root]# vi conf/settings.xml
[root]# vi /etc/profile
#MAVEN_HOME
export MAVEN_HOME=/opt/module/apache-maven-3.0.5
export PATH=$PATH:$MAVEN_HOME/bin
[root]#source /etc/profile
mvn -version
```

3. settings.xml文件修改：
```
mirror
        id nexus-aliyun id
        mirrorOf central mirrorOf
        name Nexus aliyun name
        url http://maven.aliyun.com/nexus/content/groups/public url
mirror
```

4. ant解压、配置ANT_HOME和PATH
```
[root]# tar -zxvf apache-ant-1.9.9-bin.tar.gz -C /opt/module/
[root]# vi /etc/profile
#ANT_HOME
export ANT_HOME=/opt/module/apache-ant-1.9.9
export PATH=$PATH:$ANT_HOME/bin
[root]# source /etc/profile
ant -version
```

5. 安装glibc-headers和g++命令如下
```
[root@hadoop101 apache-ant-1.9.9]# yum install glibc-headers
[root@hadoop101 apache-ant-1.9.9]# yum install gcc-c++
```

6. 安装make和cmake
```
[root@hadoop101 apache-ant-1.9.9]# yum install make
[root@hadoop101 apache-ant-1.9.9]# yum install cmake
```

7. 解压protobuf ，进入到解压后protobuf主目录，然后相继执行命令
```
[root@hadoop101 software]# tar -zxvf protobuf-2.5.0.tar.gz -C /opt/module/
[root@hadoop101 opt]# cd /opt/module/protobuf-2.5.0/
[root@hadoop101 protobuf-2.5.0]#./configure 
[root@hadoop101 protobuf-2.5.0]# make 
[root@hadoop101 protobuf-2.5.0]# make check 
[root@hadoop101 protobuf-2.5.0]# make install 
[root@hadoop101 protobuf-2.5.0]# ldconfig 
[root@hadoop101 hadoop-dist]# vi /etc/profile
#LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/opt/module/protobuf-2.5.0
export PATH=$PATH:$LD_LIBRARY_PATH
[root@hadoop101 software]# source /etc/profile
protoc --version
```

8. 安装openssl库
`[root@hadoop101 software]# yum install openssl-devel`

9. 安装 ncurses-devel库
`[root@hadoop101 software]# yum install ncurses-devel`

# 编译源码
1. 解压源码到/opt/目录
`[root]# tar -zxvf hadoop-2.7.2-src.tar.gz -C /opt/`

2. 通过maven执行编译命令，等待时间30分钟左右，最终成功是全部SUCCESS。
`[hadoop-2.7.2-src]#mvn package -Pdist,native -DskipTests -Dtar`
 
3. 成功的64位hadoop包在/opt/hadoop-2.7.2-src/hadoop-dist/target下

# 参考
1. 尚硅谷大数据教程