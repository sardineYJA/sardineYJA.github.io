---
layout: post
title: "Python 操作 ES"
date: 2020-06-10
description: "python"
tag: Python

---


## urllib 直接操作 ES

```python
username = ""
password = ""
cluster_name = "http://xxx.xxx.xxx.xxx:9200"
headers = {"Content-Type": 'application/json'}

headers.update(urllib3.make_headers(basic_auth=username+":"+password))
url = cluster_name + "/" + index_name + '/_search'
dsl = '{"size":100, "query":{"match_all":{}}}'
data = json.dumps(dsl)
req = urllib.request.Request(method='GET', url=url, data=bytes(data,encoding='utf-8'), headers=headers)
res = urllib.request.urlopen(req, timeout=10)    # 超时单位s
result = json.loads(res.read.decode('utf-8'))
```


## bulk 处理时序列化问题

```sh
POST /test/doc/_bulk
{ "index" : {"_id" : "1", "retry_on_conflict": 3}}
{ "field1" : "value1" }
```
```sh
dsl = [
    { "index" : {"_id" : "1", "retry_on_conflict": 3}},
    { "field1" : "value1" },
    { "index" : {"_id" : "1", "retry_on_conflict": 3}},
    { "field1" : "value1" }
]
```
```python
data = ''
for l in dsl:
    data = data + json.dumps(l) + '\n'
```
> 注意1. 每个json都需要json序列化，不可直接序列化多行json
> 注意2. 每行结束为`\n`





# HTTP Server

## Python3 的 http server

急需一个简单的 Web Server，如：Apache等，使用 Python 可以完成一个简单的内建 HTTP 服务器。

```sh
python -m http.server              # 加&后台启动

nohup python -m http.server 8001   # 如果要保持服务，加nohup以忽略所有挂断信号

# 访问：http://127.0.0.1:9201/ 即可访问目录下内容
```

启动常见错误：
> UnicodeDecodeError: 'utf-8' codec can't decode byte 0xbc in position 0: invalid start byte
原因：计算机名含有中文。



## 用于搭建http server的模块：

- BaseHTTPServer：提供基本的Web服务和处理器类，分别是HTTPServer及BaseHTTPRequestHandler

- SimpleHTTPServer：包含执行GET和HEAD请求的SimpleHTTPRequestHandler类

- CGIHTTPServer：包含处理POST请求和执行的CGIHTTPRequestHandler类



## BaseHTTPRequestHandler 测试

```python
# python3 自带 http.server
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

class TestRequestHandler(BaseHTTPRequestHandler):  # 继承
    def do_GET(self):
        print("do_GET")

    def do_POST(self):
        print("do_POST")

    def do_PUT(self):
        print("do_PUT")

    def do_DELETE(self):
        print("do_DELETE")

# Postman 不同方式访问：http://127.0.0.1:9201/
if __name__ == "__main__":
    print("start......")
    server_address = ('', 9201)
    server = HTTPServer(server_address, TestRequestHandler)
    server.serve_forever()
```

## 设置返回json

```python
def do_GET(self):
    print("do_GET")
    if self.path != '/hello':
        self.send_error(404, "Page not Found!")
        return

    data = {'result_code': '1', 'result_desc': 'Success'}
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(data).encode())  # 返回json
```

## Post 接收数据

```python
def do_POST(self):
    print("do_POST")
    print("==>", self.requestline)     # POST /hello?value=10 HTTP/1.1
    print("==>", self.headers)         # 头部信息
    print("==>", self.command)         # POST

    # 获取body，必须只读取报文长度字符串
    req_datas = self.rfile.read(int(self.headers['content-length']))
    print("==>", req_datas.decode())
```


