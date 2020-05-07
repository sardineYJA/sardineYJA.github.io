---
layout: post
title: "快速搭建6 —— Elasticsearch快速检索"
date: 2020-04-12
description: "Bigdata"
tag: Bigdata

---

## 下载安装

https://www.elastic.co/cn/downloads/elasticsearch

https://github.com/mobz/elasticsearch-head

https://www.elastic.co/downloads/kibana

https://github.com/medcl/elasticsearch-analysis-ik/releases

https://www.elastic.co/downloads/logstash


## ES

创建目录：data和logs，修改：config/elasticsearch.yml
```sh
cluster.name: es-cluster
node.name: es-124
path.data: /home/yang/module/elasticsearch-7.6.2/data
path.logs: /home/yang/module/elasticsearch-7.6.2/logs

# 避免es使用swap交换分区，测试环境可以false
# 默认true，生产环境建议true
bootstrap.memory_lock: false 

network.host: 192.168.243.124
http.port: 9200
discovery.seed_hosts: ["192.168.243.124:9300", "192.168.243.125:9300", "192.168.243.126:9300"]
cluster.initial_master_nodes: ["192.168.243.124:9300", "192.168.243.125:9300", "192.168.243.126:9300"]

# 设置节点间交互的tcp端口（集群），（默认9300）
transport.tcp.port: 9300
# 增加参数，使head插件可以访问es（端口9100）
http.cors.enabled: true
http.cors.allow-origin: "*"
```

同步节点并开启`bin/elasticsearch -d`

测试：http://192.168.243.124:9200


## head

下载安装：Node.js
```sh
curl --silent --location https://rpm.nodesource.com/setup_10.x | sudo bash -
yum -y install nodejs
```

elasticsearch-head-master 目录下（root用户权限）
```sh
npm install grunt --save
npm install -g cnpm --registry=https://registry.npm.taobao.org
npm install -g grunt-cli

npm install grunt-contrib-clean -registry=https://registry.npm.taobao.org
npm install grunt-contrib-concat -registry=https://registry.npm.taobao.org
npm install grunt-contrib-watch -registry=https://registry.npm.taobao.org 
npm install grunt-contrib-connect -registry=https://registry.npm.taobao.org
npm install grunt-contrib-copy -registry=https://registry.npm.taobao.org 
npm install grunt-contrib-jasmine -registry=https://registry.npm.taobao.org
# 最后一个模块可能安装不成功，但是不影响使用
```

启动：elasticsearch-head-master/grunt server &

测试：http://192.168.243.124:9100/



## kibana

vim config/kibana.yml
```sh
server.port: 5601
server.host: "0.0.0.0"
elasticsearch.hosts: ["http://192.168.243.124:9200"]
kibana.index: ".kibana"
```

启动：bin/kibana &

测试：http://192.168.243.124:5601


## ik 分词

解压到ES的plugins目录下，修改目录名为ik，重启

```sh
unzip elasticsearch-analysis-ik-X.X.X.zip -d ../module/elasticsearch-X.X.X/plugins/ik
```


## logstash

待补充...



## 脚本

```sh
cd /home/yang/module/elasticsearch-head-master/ && grunt server &        ## 启动head
/home/yang/module/kibana-7.6.2-linux-x86_64/bin/kibana &                 ## 启动kibana
```

```sh                    
netstat -tunlp|grep 9100      ## 查看head进程
netstat -tunlp|grep 5601      ## 查看kibana进程
```

```sh
#!/bin/bash

################## 设置相关信息 ###################
root_dir=/home/yang/module/
es_dir=${root_dir}elasticsearch-7.6.2/
user_name=yang

es_VM=(VM124 VM125 VM126) 

################## 下面尽量不要修改 ####################
# 启动
start_es(){
    echo -e "\n++++++++++++++++++++ ES集群启动 +++++++++++++++++++++"
	for i in ${es_VM[*]}
	do
		echo -e "\n=========> 启动 ${i} ES...."
		ssh ${user_name}@$i ${es_dir}bin/elasticsearch -d
	done
}

# 关闭
stop_es(){
	echo -e "\n++++++++++++++++++++ ES集群关闭 +++++++++++++++++++++"

	processname=Elasticsearch                     # 根据进程名找PID
	jps_command=$(whereis jps |awk '{print $2}')  # jps完全路径
	for i in ${es_VM[*]}
	do
		echo -e "\n=========> 关闭 ${i} ES...."
		## 获取进程PID，ssh遍历结点，执行jps需要完全路径
		PID=$(ssh ${user_name}@$i ${jps_command} | grep $processname | awk '{print $1}')
		if [ $? -eq 0 ]; then
		    echo -e "\n process id: $PID"
		else
		    echo -e "\n process $PID not exist"
		fi
		## 杀死进程
		ssh ${user_name}@$i kill -9 ${PID}
		if [ $? -eq 0 ]; then
		    echo -e "\n kill $processname success"
		else
		    echo -e "\n kill $processname fail"
		fi
	done
}

# 获取输入参数个数，如果没有参数，直接退出
pcount=$#
if((pcount==0)); then
    echo no args, example : $0 start/stop;
    exit;

elif [[ "$1" == "start" ]]; then
    echo start;
    start_es


elif [[ "$1" == "stop" ]]; then
    echo stop;
    stop_es

else
    echo example : $0 start/stop;
    exit;
fi
```
