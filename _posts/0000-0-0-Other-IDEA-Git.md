---
layout: post
title: "IDEA, Pycharm 常用操作"
date: 2019-12-01
description: "常用操作"
tag: Other

---


# IDEA 交互 Github 项目

## 配置

安装 .ignore 插件，重启后

File → Settings → Version Control → Git，选择Git的路径，点击Test，看看是否成功

File → Settings → Version Control → GitHub，登录的GitHub账号

## 上传项目

0. 右键项目，new → 添加maven项目的.gitignore文件 

1. VCS → Import into Version Control → Create Git Repository，配置好后，项目文件名称会变红。

2. 右键项目 → Git → Add，把项目提交到本地仓库，项目文件名称会变绿。

3. 右键项目 → Git → Commit Directory，提交到本地Git。 现在，本地Git已Commit完了，项目文件从暂存区真正进入版本库中，项目文件名称会变白。

4. VCS → Import into Version Control → Share Project on GitHub，上传项目到GitHub中。


## 更新文件

先commit，之后 VCS --> Git --> Push 



## 文件颜色

- 红色，未加入版本控制
- 绿色，已经加入控制暂未提交
- 白色，加入，已提交，无改动
- 蓝色，加入，已提交，有改动
- 灰色，版本控制已忽略文件


## 修改 .gitignore 文件

```sh
# 删除缓存 注意有个点
git rm -r --cache .

# 查看状态
git status

# 将文件修改提交到本地暂存区
git add .gitignore

# 提交本地库
git commit -m "update .gitignore"

# 上传服务器
git push origin master
```


## IDEA 下载仓库项目

github 点击仓库的 clone or download --> 复制仓库地址

VCS --> Checkout from Version Control --> Git --> 仓库地址 --> clone 

> 下载后自动会创建项目，但是下载速度太慢了，还不下载直接导入



# Pycharm

## pycharm 调试快捷键

```sh
Ctrl + Shift + F8    查找全部断点

F7                   单步进入

F8                   单步不进入

Shift + F8           跳出

F9                   下一个断点
```





# Shell


## vim 删除空格：

删除空格行：`:g/^$/d`

删除行首空格：`:%s/^\s*//g`

删除行尾空格：`:%s/\s*$//g`


## 命令

```sh
ps -ef | grep elasticsearch

-e 所有用户所有进程 -f 详细信息，-a 是当前用户所有进程

端口：lsof -i :5601   # 查看kibana进程

```

