---
layout: post
title: "github与博客"
date: 2018-01-01
description: "github与博客"
tag: Other

---

# github 教程

## github 提交新项目

1. git init    （本地项目初始化）

2. git add .   （目录里要有README.md）

3. git commit -m "提交信息"

4. git remote add origin git@XXXXX.git （使用SSH方式）

5. git push -u origin master


## 配置SSH提交方式

如果提交到github新仓库中，提示权限问题：

> Permission denied (publickey)
fatal: Could not read from remote repository.
Please make sure you have the correct access rights and the repository exists.

只需配置公钥即可：

1. Git Bash Here

2. ssh-keygen -t rsa -C "你的Git对应邮箱地址"，直接全部回车

3. 将../.ssh/id_rsa.pub 文件内容复制 （目录在输出提示）

4. 粘贴到github的setting的SSH中


## .gitignore

在.git同级目录下创建.gitignore

```sh
*.a       # 忽略所有.a结尾的文件
!lib.a    # 但lib.a除外

/TODO     # 仅忽略项目根目录下的TODO文件，不包括 subdir/TODO

build      # 忽略build目录，及下面的文件
```


## 域名解析

1. 获取仓库ip地址：`ping sardineyja.github.io`

2. 解析域名，绑定ip

3. 仓库 --> Settings --> GitHub Pages --> Custom domain



# 博客教程

## 修改访问量标准

pv 表示page view, 即页面浏览量或点击量，每次打开或刷新一个页面，都会增加阅读量

uv 表示unique visitor, 是指独立用户，一台电脑，单个ip为一个阅读量

如需修改，只需将下面 pv 修改成 uv 即可

\_include/footer.html 修改本站总访问量标准

```xml
<!-- 访问统计 -->
<span id="busuanzi_container_site_pv">
	本站总访问量
	<span id="busuanzi_value_site_pv"></span>&nbsp;次
</span>
```

\_layouts/post.html 修改本篇文章访问量标准

```xml
<span id="busuanzi_container_page_pv"><span id="busuanzi_value_page_pv"></span>次</span>
```

## 看板娘修改

参考：https://github.com/sardineYJA/live2d-widget


## 其他修改

- \_include/new-old.html 可修改打赏语句，支付宝/微信二维码图片命名

- \_include/side_panel.html 可修改背景图、人物图命名，

- \_config.yml 可修改左侧栏页面内容。\_include/side-panel.html修改左侧栏布局

- index.html 可修改“博客主页”界面，排版，文章简介展示字符数

- archive.html 可修改“所有文章”界面

- tags.html 可修改“标签”界面

- about.md 可修改“关于我”界面内容




# Markdown 教程

```
Markdown支持6种级别的标题
对应html标签 h1 ~ h6
# h1
## h2
### h3
#### h4
##### h5
###### h6
```

# h1
## h2
### h3
#### h4
##### h5
###### h6

***********************

```
符号>用于段首进行强调
> 文字将被高亮显示
```

> 文字将被高亮显示

***********************

```
[点击跳转至百度](http://www.baidu.com)

![图片标题](https://www.baidu.com/img/bd_logo1.png?where=super)

![png](/images/posts/2019-01-10/output_13_0.png)
```

[点击跳转至百度](http://www.baidu.com)

![图片标题](https://www.baidu.com/img/bd_logo1.png?where=super)

![png](/images/posts/2019-01-10/output_13_0.png)

***********************

```
* 列表1
* 列表2
* 列表3

+ 列表1
+ 列表2
+ 列表3

- 列表1
- 列表2
- 列表3

1. 列表1
2. 列表2
3. 列表3
```

* 列表1
* 列表2
* 列表3

+ 列表1
+ 列表2
+ 列表3

- 列表1
- 列表2
- 列表3

1. 列表1
2. 列表2
3. 列表3

***********************

```
分隔
-------
分隔
*******
分隔
```

分隔
-------

分隔

*******

分隔

***********************

```
*斜体*
_斜体_

**加粗**
__加粗__
```

*斜体*
_斜体_

**加粗**
__加粗__

***********************

```
表头|条目一|条目二
:---:|:---:|:---:
项目|项目一|项目二
代码测试|代码测试一|代码测试二

三个短斜杠左右的冒号用于控制对齐方式
只放置左边冒号表示文字居左
只放置右边冒号表示文字居右
如果两边都放置冒号表示文字居中
```

表头|条目一|条目二
:---:|:---:|:---:
项目|项目一|项目二
代码测试|代码测试一|代码测试二

***********************
