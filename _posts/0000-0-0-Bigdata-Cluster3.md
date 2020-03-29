---
layout: post
title: "快速搭建3 —— HBase和Hive"
date: 2020-03-25
description: "Bigdata"
tag: Bigdata

---

# HBase

## 配置

解压：hbase-1.3.2-bin.tar.gz

```sh
vi conf/hbase-env.sh
export JAVA_HOME=/home/yang/module/jdk1.8.0_241
export HBASE_MANAGES_ZK=false
```

```sh
# 注释掉下面两句，否则启动时会有警告
# Configure PermSize. Only needed in JDK7. You can safely remove it for JDK8+
export HBASE_MASTER_OPTS="$HBASE_MASTER_OPTS -XX:PermSize=128m -XX:MaxPermSize=128m -XX:ReservedCodeCacheSize=256m"
export HBASE_REGIONSERVER_OPTS="$HBASE_REGIONSERVER_OPTS -XX:PermSize=128m -XX:MaxPermSize=128m -XX:ReservedCodeCacheSize=256m"
```

hbase-site.xml
```xml
<!-- 设置hbase的根目录，为NameNode所在位置 -->
<property>
	<name>hbase.rootdir</name>
	<value>hdfs://mycluster/hbase</value>  <!-- hdfs-site.xml -->
</property>
<!-- 使hbase运行于完全分布式 -->
<property>
	<name>hbase.cluster.distributed</name>
	<value>true</value>
</property>
<!-- Zookeeper集群的地址列表 -->
<property>
	<name>hbase.zookeeper.quorum</name>
	<value>VM124,VM125,VM126</value>
</property>
<!-- zookeeper保存属性信息的文件，默认为/tmp 重启会丢失 -->
<property>
	<name>hbase.zookeeper.property.dataDir</name>
	<value>/home/yang/module/hbase-1.3.2/zkDate</value>
</property>
<!-- 临时文件存放目录 -->
<property>
    <name>hbase.tmp.dir</name>
    <value>/home/yang/module/hbase-1.3.2/tmp</value>
</property>
```

修改 regionservers
```
VM124
VM125
VM126
```

创建conf/backup-masters，并写入`VM125`，实现高可用

将hadoop中hdfs-site.xml和core-site.xml拷贝到hbase的conf下


## 启动

启动 zookeeper 和 hdfs

```sh
bin/start-hbase.sh
bin/stop-hbase.sh
# Web
http://VM124:16010  # 1.0之后 端口发生改变
```


## 脚本

```sh
#!/bin/bash

################## 设置相关信息 ###################
root_dir=/home/yang/module/
hbase_dir=${root_dir}hbase-1.3.2/
user_name=yang
 
hbase_VM=VM124                 # 启动start-hbase.sh的VM

################## 下面尽量不要修改 ####################
# 启动
start_hbase(){
	echo -e "\n++++++++++++++++++++ HBase集群启动 +++++++++++++++++++++"
	ssh ${user_name}@$hbase_VM ${hbase_dir}bin/start-hbase.sh
}

# 关闭
stop_hbase(){
	echo -e "\n++++++++++++++++++++ HBase集群关闭 +++++++++++++++++++++"
	ssh ${user_name}@$hbase_VM ${hbase_dir}bin/stop-hbase.sh
}



# 获取输入参数个数，如果没有参数，直接退出
pcount=$#
if((pcount==0)); then
	echo no args, example : $0 start/stop;
	exit;

elif [[ "$1" == "start" ]]; then
	echo start;
	start_hbase


elif [[ "$1" == "stop" ]]; then
	echo stop;
	stop_hbase

else
	echo example : $0 start/stop;
	exit;
fi
```



# Mysql

详见MySQL篇文章...


# Hive

## 配置

建议：hive-1.2版本

解压apache-hive-2.1.1-bin.tar.gz

```sh
cp hive-env.sh.template hive-env.sh
vi hive-env.sh
export HADOOP_HOME=/home/yang/module/hadoop-2.7.2
export HBASE_HOME=/home/yang/module/hbase-1.3.2
export HIVE_CONF_DIR=/home/yang/module/hive-2.1.1-bin/conf


cp hive-log4j2.properties.template hive-log4j2.properties
vi hive-log4j2.properties
# 日志目录需要提前创建
hive.log.dir=/home/yang/module/hive-2.1.1-bin/logs
```

## 利用mysql放Hive的元数据

下载：https://dev.mysql.com/downloads/connector/j/5.1.html

mysql-connector-java-5.1.48-bin.jar将其放到lib/目录下

创建conf/hive-site.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
            <name>hive.exec.scratchdir</name>
            <value>/tmp/hive</value>
    </property>
    <property>
            <name>hive.metastore.warehouse.dir</name>
            <value>hdfs://VM124:9000/hive/warehouse</value>
    <description>location to default database for the warehouse</description>
    </property>
    <property>
            <name>javax.jdo.option.ConnectionURL</name>
            <value>jdbc:mysql://VM124:3306/hivedb?createDatabaseIfNotExist=true&amp;characterEncoding=UTF-8&amp;useSSL=false</value>
    <description>Hive access metastore using JDBC connectionURL</description>
    </property>
    <property>
            <name>javax.jdo.option.ConnectionDriverName</name>
            <value>com.mysql.jdbc.Driver</value>
    </property>
    <property>
            <name>javax.jdo.option.ConnectionUserName</name>
            <value>root</value>
    </property>
    <property>
            <name>javax.jdo.option.ConnectionPassword</name>
            <value>123456</value>
    <description>password to access metastore database</description>
    </property>
    <property>
            <name>javax.jdo.option.Multithreaded</name>
            <value>true</value>
    </property>
    <property>
            <name>hive.metasotre.schema.verification</name>
            <value>true</value>
    </property>
    <property>
    		<name>hbase.zookeeper.quorum</name>   
			<value>VM124,VM125,VM126</value>
  	</property>
  	<!-- 增加显示当前数据库，表头信息 -->
  	<property>
			<name>hive.cli.print.header</name>
			<value>true</value>
	</property>

	<property>
	        <name>hive.cli.print.current.db</name>
	        <value>true</value>
	</property>
</configuration>
```


## 启动

先启动 zookeeper，hdfs，yarn

高版本需要在bin/目录下hive元数据库初始化：`./schematool -dbType mysql -initSchema`

创建相应的目录
```sh
hdfs dfs -mkdir -p /tmp/hive
hdfs dfs -chmod 777 /tmp/hive
hdfs dfs -mkdir -p /hive/warehouse
hdfs dfs -chmod 777 /hive 
```

启动：bin/hive

