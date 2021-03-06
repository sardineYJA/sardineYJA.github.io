---
layout: post
title: "Docker 构建定制 ELK "
date: 2020-08-04
description: "Docker"
tag: Other

---


## ELK

ELK docker 镜像：`https://www.docker.elastic.co/`

docker 目录：`/var/lib/docker/`

容器启动时所目录：`/usr/share/`

ELK docker images 下载：https://www.docker.elastic.co/

版本区别：
- 无 oss 如：elasticsearch:6.1.1 自带 x-pack
- 有 oss 如：elasticsearch-oss:6.1.1 纯净版（推荐）


## ES


```sh
# 查找
docker search elasticsearch

# 拉取镜像
docker pull docker.elastic.co/elasticsearch/elasticsearch-oss:6.1.1

# 查看所有镜像
docker images

# 删除镜像
docker rmi image_name      

# 运行
docker run -d --name es -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch-oss:6.1.1
# -d 后台运行
# --name 容器名
# -p 指定端口映射，主机端口：容器端口
# -e 设置环境变量
# --privileged=true 使用该参数，container内的root拥有真正的root权限


# 查看运行中的容器
docker ps -a
# -a 显示所有的容器，包括未运行的

# 删除容器
docker rm docker_name

# 进入容器
docker exec -it es /bin/bash
# -i :即使没有附加也保持STDIN 打开
# -t :分配一个伪终端

# 容器默认用户：user:elasticsearch, group:root
su elasticsearch

# 将 docker 容器日志 UTC 时间修改为 UTC+8 时间
docker exec --user root /bin/bash -c "cd / && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime"
# 或者构建镜像时cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
mv localtime localtime_bak
cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
```


## 用户，用户组
```sh
# 容器内部实现创建用户 dy1:dy1 => 1003:1004
groupadd -g 1004 dy1
useradd dy1 -u 1003 -g 1004
# 查看 cat /etc/passwd
```



## 环境

```sh
（这三项容器内部已经修改，适应ES，如果在容器内部修改并不起作用，所以无需修改）
# 单用户可以打开的最大文件数量
echo "* - nofile 655360" >> /etc/security/limits.conf
# 单用户线程数调大
echo "* - nproc 131072" >> /etc/security/limits.conf
echo "* - memlock unlimited" >> /etc/security/limits.conf
# 查看 ulimit -a  # 需要重新登录用户，生效

（这两项容器内部无法修改，在容器外即系统修改后，容器内实时读取系统的配置）
# 文件/etc/sysctl.conf
echo "vm.max_map_count=262144" >> /etc/sysctl.conf
echo "vm.swappiness=0" >> /etc/sysctl.conf
# debian 9  sysctl命令在sbin目录下
/sbin/sysctl -p    # 读取conf文件，生效
```





## 插件安装

```sh
# 拷贝文件，本地->容器
docker cp ./x-pack-6.1.1.zip es:/usr/share/elasticsearch/    

# 拷贝文件，容器->本地
docker cp es:/usr/share/elasticsearch/config/elasticsearch.yml ./

# 可以通过这样的方式修改启动不了无法进入的容器配置

# cp 拷贝进去文件：user:elasticsearch, group:elasticsearch
# cp 出来的文件：user:root, group:root
```

安装插件：
内置插件 ingest-geoip（可对ip进行地理位置分析），ingest-user-agent（识别浏览器的User-Agent）

```sh
## 解压安装插件并修改目录名，需要将文件拷贝进容器

# ik
unzip elasticsearch-analysis-ik-6.1.1.zip -d ./plugins/
mv plugins/elasticsearch plugins/ik

# pinyin
unzip elasticsearch-analysis-pinyin-6.1.1.zip -d ./plugins/
mv plugins/elasticsearch plugins/pinyin

# jieba
unzip elasticsearch-jieba-plugin-6.0.0.zip -d ./plugins/
# 修改 jieba/plugin-descriptor.properties 对于 ES 版本
version=6.1.1
elasticsearch.version=6.1.1

# searchguard
bin/elasticsearch-plugin install file:///..../search-guard-6-6.1.1-20.1.zip

# x-pack
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
chmod +x  plugins/search-guard-6/tools/install_demo_configuration.sh
./install_demo_configuration.sh
# 安装后发现config/elasticsearch.yml中写入search-guard的内容
```

## 修改 elasticsearch.yml

```sh
cluster.name: es-cluster
node.name: es-data-175

# network.host: 0.0.0.0
network.bind_host: 0.0.0.0
network.publish_host: 10.17.76.175

node.master: true 
node.data: true 
node.ingest: true

path.data: /data/node1,/date/node2,/date/node3
path.logs: /raid/log/elasticsearch/

bootstrap.memory_lock: false
bootstrap.system_call_filter: false

discovery.zen.minimum_master_nodes: 1
discovery.zen.ping.unicast.hosts: ["xxx.xxx.xxx.xxx:9300", "..."]
# discovery.zen.ping.unicast.hosts: ["192.168.56.101:19300", "192.168.56.101:29300"]

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

searchguard.restapi.roles_enabled: ["sg_all_access"]
cluster.routing.allocation.same_share.host: true
```

启动报错：

> Demo certificates found but searchguard.allow_unsafe_democertificates is set to false.

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
./sgadmin.sh -cn 集群名 -h IP地址 -p 端口 -cd ../sgconfig/ -ks kirk-keystore.jks -kspass 123456 -ts truststore.jks -tspass 123456 -nhnv

```

```sh
# 修改文件用户，用户组
chown -R dy1:dy1 ./*

# 导出镜像
docker save -o es-oss.tar docker.elastic.co/elasticsearch/elasticsearch-oss:6.1.1
# -o :输出到的文件

# 导入镜像
docker load < /.../es-oss.tar

# 打包容器
docker export container_name > es-node.tar

# 导入容器为镜像
docker import es-node.tar  image_name:tag

# commit 将容器直接保存为镜像
docker commit -a "yang" -m "description" container_name image_name:tag
# -a 提交的镜像作者
# -m 提交时的说明文字


# 以dy1用户启动，-v 挂载目录
docker run -d --name es -u dy1 -p 9200:9200 -p 9300:9300 es/es:1.0 /bin/bash -c "/usr/share/elasticsearch/bin/elasticsearch"
docker run -d --name es -u dy1 -p 9201:9200 -p 9301:9300  -v /raid/data/d1:/test_data1 -v /raid/data/d2:/test_data2 es/es:1.0 /bin/bash -c "/usr/share/elasticsearch/bin/elasticsearch"

# 日志文件路径
docker inspect --format='{{.LogPath}}' container_name
# 直接软链
```


## 一台服务器上运行多个 docker ES 节点

场景：在一个集群中有多台服务器，每个服务器有一个docker es节点或多个。

问题：在一台服务器上运行多个 docker es 节点时（例如在 10.17.76.104 分别在端口 19301 ，19302 启动两个节点），这两个节点无法发现对方，但是集群是正常的而且两个节点也加入到集群中。

两个节点会频繁打印下面的日志

第一台：
[o.e.c.NodeConnectionsService] [docker-es-104_data] failed to connect to node {docker-es-node-104_ingest}{pR5q3bE6T8WDcmXqTXK8VA}{WtitYLlwTJa-lk8ODv0WuQ}{10.17.76.104}{10.17.76.104:19302} (tried [1] times)
org.elasticsearch.transport.ConnectTransportException: [docker-es-node-104_ingest][10.17.76.104:19302] connect_timeout[30s]


第二台：
[o.e.c.NodeConnectionsService] [docker-es-104_ingest] failed to connect to node {docker-es-104_data}{LsTniDUNTdGxEe8nKNPc7A}{KDy4NZ2WTu26vS47TYokKA}{10.17.76.104}{10.17.76.104:19301} (tried [7] times)
org.elasticsearch.transport.ConnectTransportException: [docker-es-104_data][10.17.76.104:19301] connect_timeout[30s]


配置文件，仅端口不同
```sh
cluster.name: test-cluster
node.name: es-data

network.bind_host: 0.0.0.0
network.publish_host: 10.17.76.175 

discovery.zen.ping.unicast.hosts: ["xxx.xxx.xxx.xxx:9300"]

http.port: 19201
transport.tcp.port: 19301
```

```sh
cluster.name: test-cluster
node.name: es-data

network.bind_host: 0.0.0.0
network.publish_host: 10.17.76.175 

discovery.zen.ping.unicast.hosts: ["xxx.xxx.xxx.xxx:9300"]

http.port: 19202
transport.tcp.port: 19302
```

解决办法：
防火墙添加容器网桥的ip和端口，将两个节点的TCP通信端口加上
```sh
iptables -A INPUT -s 172.17.0.0/16 -p tcp --dport 19301 -j ACCEPT      （TCP通信即可）
iptables -A INPUT -s 172.17.0.0/16 -p tcp --dport 19302 -j ACCEPT      （TCP通信即可）
```




## 自定义链DOCKER

查看root执行：iptables-save

docker服务启动时定义的自定义链DOCKER由于某种原因被清掉，重启docker服务及可重新生成自定义链DOCKER

> Error response from daemon: driver failed programming external connectivity on endpoint :  (iptables failed: iptables --wait -t filter -A DOCKER ! -i docker0 -o docker0 -p tcp -d 172.17.0.2 --dport  -j ACCEPT: iptables: No chain/target/match by that name.
(exit status 1))
Error: failed to start containers


## docker 的 es ip

bridge 桥接模式下 Docker Container 不具有一个公有 IP,即和宿主机的 eth0 不处于同一个网段。导致
的结果是宿主机以外的世界不能直接和容器进行通信。（master 无法与容器节点通信，docker es 无法加入外部集群）

network.host将设置network.bind_host和network.publish_host为相同的值。

使用 network.host 参数满足不了需求，ES提供了更高级的配置：
- network.bind_host: 0.0.0.0
- network.publish_host: 10.17.76.175       表示发布地址，是唯一的，用来集群各节点的相互通信



## 容器打包注意事项

> [o.e.d.z.ZenDiscovery] failed to send join request to master
reason [RemoteTransportException[[es-node-03][internal:discovery/zen/join]]; 
nested: IllegalArgumentException can't add node {es-node-04}
found existing node {es-node-03} with the same id but is a different node instance];

对容器打包时，需要将 data/ 目录删除，否则启动在 ZenDiscovery 会有相同 id 导致不能正确形成集群。
（也可以启动后进入容器内删除，再重启）






## docker searchguard admin

> [WARN ][c.f.s.c.ConfigurationLoader] No data for config while retrieving configuration for [config, roles, rolesmapping, internalusers, actiongroups]  (index=searchguard)
> [WARN ][c.f.s.c.ConfigurationLoader] No data for roles while retrieving configuration for [config, roles, rolesmapping, internalusers, actiongroups]  (index=searchguard)
> [WARN ][c.f.s.c.ConfigurationLoader] No data for rolesmapping while retrieving configuration for [config, roles, rolesmapping, internalusers, actiongroups]  (index=searchguard)

需要执行 sgadmin，初始化 searchguard。

之前全部 docker ES 节点容器删掉，就算重新挂载 data 节点目录，发现账号密码全部没有，需要重新执行 sgadmin。





# kibana

```sh
# 拉取镜像
docker pull docker.elastic.co/kibana/kibana-oss:6.1.1

# 启动
docker run --name kibana -p 5601:5601 -d docker.elastic.co/kibana/kibana-oss:6.1.1
# -d: 后台运行容器，并返回容器ID

# 拷贝插件到容器
docker cp ./xxx.zip /usr/share/kibana/

# 进入终端
docker exec -it kibana /bin/bash

# 安装插件
bin/kibana-plugin install file:///usr/share/kibana/search-guard-kibana-plugin-6.1.1-8.zip
bin/kibana-plugin install file:///usr/share/kibana/x-pack-6.1.1.zip
```

修改 kibana.yml
```sh
server.name: kibana
server.host: "0"
server.port: 5601
elasticsearch.url: "http://XXX.XXX.XXX.XXX:9200"
elasticsearch.username: "admin"
elasticsearch.password: "admin"

xpack.monitoring.enabled: true
xpack.security.enabled: false 
xpack.reporting.enabled: false 
searchguard.session.keepalive: true
```
> kibana 第一次启动需要7-8分钟左右


## 用户，用户组

```sh
# root 用户进入 docker
docker exec -it --user root container_name /bin/bash

# 容器内部实现创建用户 dy1:dy1 => 1003:1004
groupadd -g 1004 dy1
useradd dy1 -u 1003 -g 1004
# 查看 cat /etc/passwd

docker run -d --name kibana -u dy1 -p 5601:5601 -d kibana/kibana-auth:6.1.1 /bin/bash  -c "/usr/share/kibana/bin/kibana"
```

