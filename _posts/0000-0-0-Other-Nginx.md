---
layout: post
title: "Nginx 知识点"
date: 2020-08-17
description: "Nginx"
tag: Other

---

# Nginx

- 高性能的 Web Http 代理 

- 反向代理服务器

- 采用 epoll 模型，异步非阻塞

## 安装

Nginx 安装： 

1. 在线安装执行`apt-get install nginx`

2. 离线安装：
```sh
# 1. 下载
wget http://nginx.org/download/nginx-1.6.2.tar.gz
tar zxvf nginx-1.6.2.tar.gz

# 2. 编译安装
./configure
make && make install

# 3. 验证
./nginx -v
```

## 测试

本地：curl -I 127.0.0.1

浏览器：http://xxx.xxx.xxx.xxx


## 在线安装默认目录

- 配置文件：/etc/nginx/nginx.conf

- 服务器块 (vhost) 配置文件存储：/etc/nginx/sites-available 

- 访问日志：/var/log/nginx/access.log和error.log


## nginx.conf

```sh
# 每个指令必须有分号结束
#user administrator administrators;  # 配置用户或组
#worker_processes 2;                 # 允许生成的进程数，默认为1
#pid /nginx/pid/nginx.pid;           # 指定nginx进程运行文件存放地址
error_log log/error.log debug;       # 制定日志路径，级别。这个设置可以放入全局块，http块，server块，级别以此为：debug|info|notice|warn|error|crit|alert|emerg
events {
    accept_mutex on;                 # 设置网路连接序列化，防止惊群现象发生，默认为on
    multi_accept on;                 # 设置一个进程是否同时接受多个网络连接，默认为off
    #use epoll;                      # 事件驱动模型，select|poll|kqueue|epoll|resig|/dev/poll|eventport
    worker_connections  1024;        # 最大连接数
}
http {
    include       mime.types;               # 文件扩展名与文件类型映射表
    default_type  application/octet-stream; # 默认文件类型，默认为text/plain
    #access_log off;                        # 取消服务日志    
    log_format myFormat '$remote_addr–$remote_user [$time_local] $request $status $body_bytes_sent $http_referer $http_user_agent $http_x_forwarded_for'; #自定义格式
    access_log log/access.log myFormat;     # combined为日志格式的默认值
    sendfile on;                            # 允许sendfile方式传输文件，默认为off，可以在http块，server块，location块。
    sendfile_max_chunk 100k;                # 每个进程每次调用传输数量不能大于设定的值，默认为0，即不设上限。
    keepalive_timeout 65;                   # 连接超时时间，默认为75s，可以在http，server，location块。

    upstream mysvr {   
      server 127.0.0.1:7878;
      server 192.168.10.121:3333 backup;    # 热备
    }

    error_page 404 https://www.baidu.com;   # 错误页

    server {
        keepalive_requests 120;     # 单连接请求上限次数。
        listen       4545;          # 监听端口
        server_name  127.0.0.1;     # 监听地址       
        location  ~*^.+$ {          # 请求的url过滤，正则匹配，~为区分大小写，~*为不区分大小写。
           #root path;                  # 根目录
           #index vv.txt;               # 设置默认页
           proxy_pass  http://mysvr;    # 请求转向mysvr 定义的服务器列表
           deny 127.0.0.1;              # 拒绝的ip
           allow 172.18.5.54;           # 允许的ip           
        } 
    }
}
```


## 日志格式变量

- $remote_addr 与 $http_x_forwarded_for 用以记录客户端的ip地址
- $remote_user        客户端用户名称
- $time_local         访问时间与时区
- $request            请求的url与http协议
- $status             请求状态；成功是200
- $body_bytes_sent    发送给客户端文件主体内容大小
- $http_referer       从那个页面链接访问过来的
- $http_user_agent    客户端浏览器的相关信息


## upstream 

upstream 模块主要负责负载均衡的配置，通过默认的轮询调度方式来分发请求到后端服务器。

```sh
upstream proxy {
    server 172.16.2.123:8888 weight=1 max_fails=4 fail_timeout=10;
    server 172.16.2.124:8888 weight=1 max_fails=4 fail_timeout=10;
    server 172.16.2.125:8888 weight=1 max_fails=4 fail_timeout=10;
    keepalive 64;
}

# weight 节点权重

# max_fails 
# fail_timeout
# max_fails=n 设定 Nginx 与服务器通信的尝试失败的次数。在 fail_timeout 参数定义的时间段内，如果失败的次数达到此值，Nginx 就认为服务器不可用。在下一个 fail_timeout 时间段，服务器不会再被尝试。 max_fails 默认是1。设为0就会停止统计尝试次数，认为服务器是一直可用的。

# keepalive 是长连接的意思。客户端发起 http 请求前需要先与服务端建立TCP连接，每次 TCP 连接都需要三次握手来确定，三次交互不仅会增加消费时间，还会增加网络流量。
```


## server 

server 模块用于进行服务器访问信息的配置，用来定义一个虚拟访问主机，即一个虚拟服务器的配置信息

```sh
server {                                    # 虚拟主机，一个http中可配置多个server
    listen 80;                              # http 为 80 端口，https 为 443 端口
    server_name elk.test.com;               # 指定ip地址或域名，多个配置空格隔开             
    root /nginx/www;                        # server虚拟主机的根目录
    index index.php index.html index.html;  # 用户访问web网站的全局首页
    charset utf-8;
    access_log logs/access.log;
    error_log logs/error.log;
}
```


## location 

location 主要用于配置路由访问信息在路由访问信息配置中关联到反向代理、负载均衡等等各项功能

```sh
server {
    ...
    location / {                      # 表示匹配访问根目录
        root /nginx/www; 
        index index.php index.html;
    }

    location /proxy/ {
        proxy_pass http://proxy/;        
        proxy_redirect off;              # 反向代理配置
        # 其他配置
        proxy_set_header   Host $host; 
        proxy_set_header   X-Real-IP $remote_addr; 
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for; 
        client_max_body_size       10m;     # 允许客户端请求的最大单文件字节数
        client_body_buffer_size    128k;    # 缓冲区代理缓冲用户端请求的最大字节数
        proxy_connect_timeout      300;     # nginx跟后端服务器连接超时时间(代理连接超时)
        proxy_send_timeout         300;     # 后端服务器数据回传时间(代理发送超时)
        proxy_read_timeout         300;     # 连接成功后，后端服务器响应时间(代理接收超时)
        proxy_buffer_size          4k;      # 设置代理服务器（nginx）保存用户头信息的缓冲区大小
        proxy_buffers              32k;     # proxy_buffers缓冲区，网页平均在32k以下的话，这样设置
        proxy_busy_buffers_size    64k;     # 高负荷下缓冲大小（proxy_buffers*2）
        proxy_temp_file_write_size 64k;     # 设定缓存文件夹大小，大于这个值，将从upstream服务器传
    }
}
```



## 端口

80 端口：HTTP（HyperText Transport Protocol)即超文本传输协议开放的，此为上网冲浪使用次数最多的协议。
通过HTTP地址（即常说的“网址”）加“:80”来访问网站，因为浏览网页服务默认的端口号都是80，因此只需输入网址即可，不用输入“:80”了。

443 端口：HTTPS（Secure Hypertext Transfer Protocol）安全超文本传输协议它是一个安全通信通道，它基于HTTP开发，用于在客户计算机和服务器之间交换信息。
它使用安全套接字层(SSL)进行信息交换，简单来说它是HTTP的安全版。




