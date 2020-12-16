---
layout: post
title: "Docker 进阶"
date: 2019-12-04
description: "Docker"
tag: Other

---


## docker hub

```sh
# https://hub.docker.com/ 默认
docker login  [url -u username -p password]    # 登录，可加 仓库地址 
docker logout [url]    # 退出

docker push ubuntu/ubuntu:18.04  # 将自己的镜像推送到 Docker Hub
```


## Dockerfile

使用 Dockerfile 快速构建自定义的镜像





