---
layout: post
title: "Docker 基础使用"
date: 2019-12-02
description: "Docker 基础使用"
tag: Other

---


## 容器基本使用

```sh
docker info          # 查看信息

docker run ubuntu:15.10 echo "Hello"            # 没有ubuntu:15.10镜像则会下载

docker run -i -t ubuntu:15.10 /bin/bash         # 运行交互式的容器
# -t: 在新容器内指定一个伪终端或终端。
# -i: 允许你对容器内的标准输入 (STDIN) 进行交互。


# 以进程方式运行的容器，后台模式
docker run -d ubuntu:15.10 /bin/sh -c "while true; do echo hello world; sleep 1; done"

docker ps -a                      # 查看运行容器

docker logs (容器id或name)        # 查看容器内的标准输出

docker start/stop (容器id或name)  # 停止容器
```

```sh
docker run -itd --name ubuntu-test ubuntu /bin/bash

docker attach (容器id或name)   # 进入（已在后台）容器
# attach 命令在退出容器时，会导致容器的停止

docker exec -it (容器id或name)  /bin/bash   # 进入（已在后台）容器
# exec 命令在退出容器时，不会导致容器的停止
```

```sh
# 容器目录：/var/lib/docker/containers

ls -l|grep "^d"|wc -l   # 查看目录数量 

docker export (容器id或name) > ubuntu.tar   # 导出容器

# docker import 从容器快照文件中再导入为镜像
cat ubuntu.tar | docker import - test/ubuntu:v1
docker images

docker rm -f (容器id或name)   # 删除容器

docker container prune   # 清理掉所有处于终止状态的容器 
# 慎用，会删掉某些 
```


## 错误

> docker: Error response from daemon: driver failed programming external connectivity on endpoint

原因：docker container prune 使用此命令后，某些东西被删，重启docker即可。

```sh
systemctl status docker
```


## Web应用

```sh
docker pull training/webapp  # 载入镜像
docker run -d -P training/webapp python app.py
# -P 随机端口，-p 指定端口，例如：-p 5000:5000
# 运行一个 Python Flask 应用来运行一个web应用

docker ps   # 查看应用端口
# 打开Web:http://172.16.7.124:32768
```


## 镜像

```sh
docker pull ubuntu         # 载入ubuntu镜像

docker images              # 查看所有镜像

docker rmi (镜像名)        # 删除镜像
```


## 网络

```sh
docker network ls    # Docker 网络列表

docker network create -d bridge test-net
# -d 网络类型：bridge, overlay

# 建立两个容器并连接到 test-net 网络:
docker run -itd --name test1 --network test-net ubuntu /bin/bash
docker run -itd --name test2 --network test-net ubuntu /bin/bash

docker exec -it test1 /bin/bash    # 进入test1容器
apt-get update                     # 安装ping
apt install iputils-ping
ping test2       # ping 证明 test1 容器和 test2 容器建立了互联关系 
```

## 用户仓库

```sh
# https://hub.docker.com/ 注册账号
docker login      # 登录
docker logout     # 退出

docker push username/ubuntu:18.04  # 将自己的镜像推送到 Docker Hub
```

## Dockerfile

```sh
待补充...
```



# ELK

ELK docker 镜像：`https://www.docker.elastic.co/`

docker 目录：`/var/lib/docker/`

容器启动时所目录：`/usr/share/`

ELK docker images 下载：https://www.docker.elastic.co/

版本区别：
- 无 oss 如：elasticsearch:6.1.1 自带 x-pack
- 有 oss 如：elasticsearch-oss:6.1.1 纯净版，无安装插件（推荐）


## ES


```sh
# 查找
docker search elasticsearch

# 拉取镜像
docker pull docker.elastic.co/elasticsearch/elasticsearch-oss:6.1.1

# 查看
docker images

# 运行
docker run -d --name es -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch-oss:6.1.1
# -d 后台运行
# --name 容器名
# -p 指定端口映射，主机端口：容器端口
# -e 设置环境变量
# --privileged=true 使用该参数，container内的root拥有真正的root权限


# 查看运行中的容器
docke ps -a
# -a 显示所有的容器，包括未运行的

# 进入容器
docker exec -it es /bin/bash
# -i :即使没有附加也保持STDIN 打开
# -t :分配一个伪终端
```


```sh
# 拷贝文件，本地->容器
docker cp ./x-pack-6.1.1.zip es:/usr/share/elasticsearch/    

# 拷贝文件，容器->本地
docker cp es:/usr/share/elasticsearch/config/elasticsearch.yml ./

# 可以通过这样的方式修改启动不了无法进入的容器配置
```

```sh
## 解压安装插件并修改目录名，需要将文件拷贝进容器
unzip elasticsearch-analysis-ik-6.1.1.zip -d ./plugins/
mv plugins/elasticsearch plugins/ik

unzip elasticsearch-analysis-pinyin-6.1.1.zip -d ./plugins/
mv plugins/elasticsearch plugins/pinyin

bin/elasticsearch-plugin install file:///..../search-guard-6-6.1.1-20.1.zip

bin/elasticsearch-plugin install file:///..../x-pack-6.1.1.zip
```



```sh
# search-guard-ssl 生成证书
./gen_root_ca.sh capass changeit                 # CA密码     TS密码
./gen_node_cert.sh 0 changeit capass             # node   KS密码    CA密码
./gen_client_node_cert.sh kirk changeit capass   # 客户端  KS密码    CA密码

# 分发到目录
elasticsearch/config/: truststore.jk, node-0-keystore.jks
plugins/search-guard-6/sgconfig/: truststore.jks, kirk-keystore.jks

# 执行脚本：
chmod +x  plugins/search-guard-7/tools/install_demo_configuration.sh
./install_demo_configuration.sh
# 安装后发现config/elasticsearch.yml中写入search-guard的内容
```

修改 elasticsearch.yml
```sh
cluster.name: es-cluster
node.name: es-data-175
network.host: 0.0.0.0

node.master: true 
node.data: true 
node.ingest: true

path.data: /data/node1,/date/node2,/date/node3
path.logs: /raid/log/elasticsearch/

bootstrap.memory_lock: false
bootstrap.system_call_filter: false

discovery.zen.minimum_master_nodes: 1
discovery.zen.ping.unicast.hosts: ["xxx.xxx.xxx.xxx:9300", "..."]

http.port: 9200
transport.tcp.port: 9300

## 加入跨域配置
http.cors.enabled: true        
http.cors.allow-origin: "*"

# xpack 
xpack.monitoring.enabled: true
xpack.security.enabled: false   
xpack.graph.enabled: false
xpack.ml.enabled: false
xpack.watcher.enabled: false


# 配置 SeachGuard 初始化
searchguard.authcz.admin_dn:
  - CN=kirk, OU=client, O=client, L=Test, C=DE  

# 配置ssl
searchguard.ssl.transport.enabled: true
searchguard.ssl.transport.keystore_filepath: node-0-keystore.jks
searchguard.ssl.transport.keystore_password: kspass
searchguard.ssl.transport.truststore_filepath: truststore.jks
searchguard.ssl.transport.truststore_password: tspass
searchguard.ssl.transport.enforce_hostname_verification: false
searchguard.ssl.transport.resolve_hostname: false

searchguard.ssl.http.enabled: false
searchguard.ssl.http.keystore_filepath: node-0-keystore.jks
searchguard.ssl.http.keystore_password: kspass
searchguard.ssl.http.truststore_filepath: truststore.jks
searchguard.ssl.http.truststore_password: tspass
searchguard.allow_all_from_loopback: true

searchguard.restapi.roles_enabled: ["sg_all_access"]
cluster.routing.allocation.same_share.host: true
```

启动报错：

>  Demo certificates found but searchguard.allow_unsafe_democertificates is set to false.

增加参数：
```sh
searchguard.allow_unsafe_democertificates: true
searchguard.allow_default_init_sgindex: true
```



```sh
# 重启
docker restart es

curl -X GET "http://xxx.xxx.xxx.xxx:9200" -H "Content-Type:application/json" -u "admin:admin"

# 访问集群提示：Search Guard not initialized (SG11).则需要执行   
./sgadmin.sh -cn 集群名 -h IP地址 -cd ../sgconfig/ -ks kirk-keystore.jks -ts truststore.jks -nhnv


# 查看日志
docker logs es                # 查看日志
docker logs -f --tail=200 es  # 实时查看日志
# -f : 跟踪日志输出
```

```sh
# 导出镜像
docker save -o es-oss.tar docker.elastic.co/elasticsearch/elasticsearch-oss:6.1.1
# -o :输出到的文件

# 导入镜像
docker load < /.../es-oss.tar

# 打包容器
docker export > es-node.tar

# 导入容器为镜像
docker import es-node.tar  es/es:1.0

# 启动
docker run -d --name es -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" es/es:1.0 /bin/bash -c "/usr/share/elasticsearch/bin/elasticsearch"
```


## kibana

```sh
# 拉取镜像
docker pull docker.elastic.co/kibana/kibana:6.1.1

# 启动
docker run --name kibana -p 5601:5601 -d docker.elastic.co/kibana/kibana:6.1.1

# 拷贝插件到容器
docker cp ./xxx.zip /usr/share/kibana/

# 进入终端
docker exec -it kibana /bin/bash

# 安装插件
bin/kibana-plugin install file:///usr/share/kiban/search-guard-kibana-plugin-6.1.1-8.zip
bin/kibana-plugin install file:///usr/share/kiban/x-pack-6.1.1.zip
```

修改 kibana.yml
```sh
server.name: kibana
server.host: "0"
elasticsearch.url: "http://XXX.XXX.XXX.XXX:9200"
elasticsearch.username: "admin"
elasticsearch.password: "admin"

xpack.monitoring.enabled: true
xpack.security.enabled: false 
xpack.reporting.enabled: false 
searchguard.session.keepalive: true
```
> kibana 第一次启动需要7-8分钟左右

