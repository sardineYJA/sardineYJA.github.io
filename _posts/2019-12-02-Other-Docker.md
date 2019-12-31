---
layout: post
title: "Docker 基础使用"
date: 2019-12-02
description: "Docker 基础使用"
tag: Other

---


## 测试

```sh
docker info          # 查看信息

docker run ubuntu:15.10 echo "Hello"            # 没有ubuntu:15.10镜像则会下载

docker run -i -t ubuntu:15.10 /bin/bash         # 运行交互式的容器
# -t: 在新容器内指定一个伪终端或终端。
# -i: 允许你对容器内的标准输入 (STDIN) 进行交互。


# 以进程方式运行的容器，后台模式
docker run -d ubuntu:15.10 /bin/sh -c "while true; do echo hello world; sleep 1; done"

docker ps -a                     # 查看运行容器

docker logs (容器id或name)        # 查看容器内的标准输出

docker start/stop (容器id或name)  # 停止容器
```

```sh
docker pull ubuntu         # 载入镜像

docker run -itd --name ubuntu-test ubuntu /bin/bash

docker attach (容器id或name)   # 进入（已在后台）容器
# attach 命令在退出容器时，会导致容器的停止

docker exec -it (容器id或name)  /bin/bash   # 进入（已在后台）容器
# exec 命令在退出容器时，不会导致容器的停止
```

```sh
# 容器目录/var/lib/docker/containers
docker export (容器id或name) > ubuntu.tar   # 导出容器




```


# reference

https://www.runoob.com/docker/docker-container-usage.html


