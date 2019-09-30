---
layout: post
title: "Ubuntu设置代理"
date: 2018-08-03
description: "Ubuntu设置代理"
tag: Other

---


## 设置方法

/etc/shadowsocks/config.json
```json
{
	"server":"代理服务器ip地址",
	"server_port":443,
	"local_address":"127.0.0.1",
	"local_port":1080,
	"password":"密码",
	"timeout":300,
	"method":"aes-256-gcm",
	"fast_open":false,
	"workers":1
}
```

shell脚本：
```sh
#!/bin/bash
#shadow.sh
sslocal -c /etc/shadowsocks/config.json
```

google浏览器需要安装代理插件：

代理协议：SOCKS5；
代理服务器：127.0.0.1；
代理端口：1080；


火狐浏览器可直接在浏览器设置：

手动代理配置：HTTP代理：127.0.0.1：端口8123：为所有协议使用相同代理服务器
