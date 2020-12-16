---
layout: post
title: "Docker 基础使用"
date: 2019-12-02
description: "Docker 基础使用"
tag: Other

---


## 查看命令

```sh
docker info 

docker images

# 元数据信息
docker inspect image_name 或 container_name

# 查看容器的端口映射情况
docker port container_name

docker ps -a

# 容器内进程
docker top container_name  

# 查看docker run参数
pip3 install runlike
runlike -p container_name

# 重新导入相同名称和 tag 的镜像，原镜像 tag 会变成 none:
# 一次性删掉所有 none 的镜像
docker images|grep none|awk '{print $3}'|xargs docker rmi

# 获取容器 ip
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container_name_or_id

```



## 查看日志

```sh
# 查看日志
docker logs es                # 查看日志
docker logs -f --tail=200 es  # 实时查看日志
# -f : 跟踪日志输出

# 看指定时间后的日志，只显示最后100行
docker logs -f -t --since="2018-02-08" --tail=100 CONTAINER_ID

# 查看最近30分钟的日志
docker logs --since 30m CONTAINER_ID

# 查看某时间之后的日志
docker logs -t --since="2018-02-08T13:23:37" CONTAINER_ID

# 查看某时间段日志
docker logs -t --since="2018-02-08T13:23:37" --until "2018-02-09T12:23:37" CONTAINER_ID
```


## 基本使用

```sh
# 对镜像再进行标签 tag
docker tag es/es:6.1.1 es/es:latest

docker attach (容器id或name)   # 进入（已在后台）容器
# attach 命令在退出容器时，会导致容器的停止

docker exec -it (容器id或name)  /bin/bash   # 进入（已在后台）容器
# exec 命令在退出容器时，不会导致容器的停止

ls -l|grep "^d"|wc -l   # 查看目录数量 

docker rm -f (容器id或name)   # 删除容器

docker container prune   # 清理掉所有处于终止状态的容器 
# 慎用，会删掉某些 
```

> docker: Error response from daemon: driver failed programming external connectivity on endpoint

原因：docker container prune 使用此命令后，某些东西被删，重启docker即可。

```sh
systemctl status docker
```


## -v 和 --mount 区别

- -v 宿主机上没有这个文件，会自动创建，

- --mount 宿主机中没有这个文件会报错找不到这个文件，并创建失败


## -v 挂载目录注意事项

1. 目录顺序，-v 挂载宿主机目录:容器目录
2. 挂载宿主机目录或容器目录不存在时都会自动创建
3. 挂载宿主机目录或容器目录的文件，权限，所属用户uid和所属用户组gid保持一致，无论修改挂载宿主机目录或容器目录而另一边都会随着改变
4. 如果挂载时，挂载宿主机目录或容器目录只存在一边，另一边创建时都会以此创建相同的权限，uid和gid
5. 容器销毁了，在宿主机上新建的挂载目录不会因此而消失
6. 如果挂载某个文件（不是目录），宿主机修改vi文件，导致inode改变，而容器内文件却没有改变。解决：1.最后挂载配置文件的目录而不是文件；2.修改文件使用echo重定向方式





## 打包

```sh
# 镜像 -> tar
docker save -o es-oss.tar docker.elastic.co/elasticsearch/elasticsearch-oss:6.1.1
# -o :输出到的文件

# tar -> 镜像
docker load < /.../es-oss.tar

# 容器 -> tar
docker export container_name > xxx.tar

# 容器 tar -> 镜像
docker import xxx.tar  image_name:tag

# 容器 -> 镜像
docker commit -a "yang" -m "description" container_name image_name:tag
# -a 提交的镜像作者
# -m 提交时的说明文字
```



## Web应用

```sh
docker pull training/webapp  # 载入镜像
docker run -d -P training/webapp python app.py
# -P 随机端口，-p 指定端口，例如：-p 5000:5000
# 运行一个 Python Flask 应用来运行一个web应用

# 打开Web:http://172.16.7.124:32768
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




## docker 网络模式

- bridge 桥接模式
- host 模式
- container 模式
- none 模式

启动容器 -net 参数指定，默认桥接模式（即172.17.0.1网关）


