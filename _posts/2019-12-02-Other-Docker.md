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






# reference

https://www.runoob.com/docker/docker-container-connection.html
