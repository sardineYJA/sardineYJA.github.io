---
layout: post
title: "openssl 证书生成"
date: 2020-11-17
description: "openssl"
tag: Other

---


## genrsa 生成私钥

```sh
openssl genrsa [args] [numbits]

args1 对生成的私钥文件是否要使用加密算法进行对称加密: 
    -des : CBC模式的DES加密 
    -des3 : CBC模式的3DES加密 
    -aes128 : CBC模式的AES128加密 
    -aes192 : CBC模式的AES192加密 
    -aes256 : CBC模式的AES256加密 

args2 对称加密密码
    -passout passwords
    其中passwords为对称加密(des、3des、aes)的密码

args3 输出文件
    -out file : 输出证书私钥文件 

[numbits]: 密钥长度，理解为私钥长度
```

例如：生成一个2048位的RSA私钥，并用des3加密(密码为123456)，保存为server.key

```sh
openssl genrsa -des3 -passout pass:123456 -out server.key 2048
```


## req 生成证书请求和生成自签名证书

```sh
openssl req [args] outfile

args1 是输入输入文件格式：-inform arg
    -inform DER 使用输入文件格式为DER
    -inform PEM 使用输入文件格式为PEM

args2 输出文件格式:-outform arg   
    -outform DER 使用输出文件格式为DER
    -outform PEM 使用输出文件格式为PEM

args3 是待处理文件 
    -in inputfilepath

args4 待输出文件
    -out outputfilepath

args5 用于签名待生成的请求证书的私钥文件的解密密码
    -passin passwords    

args6 用于签名待生成的请求证书的私钥文件
    -key file

args7 指定输入密钥的编码格式 -keyform arg  
    -keyform  DER
    -keyform  NET
     -keyform  PEM

args8 生成新的证书请求 
    -new

args9 输出一个X509格式的证书,签名证书时使用 
    -x509

args10 使用X509签名证书的有效时间  
    -days

args11 生成一个bits长度的RSA私钥文件，用于签发【生成私钥、并生成自签名证书】 
    -newkey rsa:bits 

args12 设置HASH算法-[digest]【生成私钥指定的hash摘要算法】
    -md5
    -sha1  # 高版本浏览器开始不信任这种算法
    -md2
    -mdc2
    -md4

args13 指定 openssl 配置文件，很多内容不容易通过参数配置，可以指定配置文件
    -config filepath  

args14 显示格式txt【用于查看证书、私钥信息】
    -text

args15 指定证书所有人主体信息
    -subj '/C=<country>/ST=<province>/L=<locality>/O=<organiation>/OU=<organiation-unit>/CN=<common-name>/emailAddress=<email>'
    # 果证书用于网站，则其中的CN域必须指定为网站域名，其他域不是必填项。
```

案例：利用私钥生成证书请求csr
```sh
openssl req -new -key server.key -out server.csr
```

案例：利用私钥生成自签名证书
```sh
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt
```


## x509 证书处理工具，显示证书的内容，转换其格式，给CSR签名等

```sh
openssl x509 [args]
```

```sh
args1 是输入输入文件格式：-inform arg
    -inform DER 使用输入文件格式为DER
    -inform PEM 使用输入文件格式为PEM

args2 输出文件格式:-outform arg   
    -outform DER 使用输出文件格式为DER
    -outform PEM 使用输出文件格式为PEM

args3 是待处理X509证书文件 
    -in inputfilepath

args4 待输出X509证书文件
    -out outputfilepath

args5 表明输入文件是一个"请求签发证书文件(CSR)"，等待进行签发
    -req            

args6 签名证书的有效时间  
    -days

args7 指定用于签发请求证书的根CA证书 
    -CA arg 

args8 根CA证书格式(默认是PEM)     
    -CAform arg     

args9 指定用于签发请求证书的CA私钥证书文件    
    -CAkey arg      

args10 指定根CA私钥证书文件格式(默认为PEM格式)
    -CAkeyform arg  

args11 指定序列号文件(serial number file)    
    -CAserial arg   

args12 如果序列号文件(serial number file)没有指定，则自动创建它 
    -CAcreateserial 

args13 设置HASH算法-[digest]【生成私钥指定的hash摘要算法】
    -md5
    -sha1  # 高版本浏览器开始不信任这种算法
    -md2
    -mdc2
    -md4
```

案例：使用根CA证书[ca.crt]和私钥[ca.key]对"请求签发证书"[server.csr]进行签发，生成x509格式证书
```sh
openssl x509 -req -days 3650 -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out serverx509.crt
```


## 查看信息
```sh
# 查看私钥信息
openssl rsa -text -noout -in ca.key

# 查看证书签名请求信息
openssl req -text -noout -in server.csr

# 查看证书信息
openssl x509 -text -noout -in server.crt
```


## filebeat 与 logstash 证书设置案例

```sh
# 生成 ca 私钥
openssl genrsa 2048 > ca.key
# 使用 ca 私钥建立 ca 证书
openssl req -new -x509 -nodes -days 1000 -key ca.key -subj /CN=elkCA\ CA/OU=Development\ group/O=HomeIT\ SIA/DC=elk/DC=com > ca.crt


# 生成服务器 csr 证书请求文件
openssl req -newkey rsa:2048 -days 1000 -nodes -keyout server.key -subj /CN=server.t.com/OU=Development\ group/O=Home\ SIA/DC=elk/DC=com > server.csr
# 使用 ca 证书与私钥签发服务器证书
openssl x509 -req -in server.csr -days 1000 -CA ca.crt -CAkey ca.key -set_serial 01 > server.crt


# 生成客户端 csr 证书请求文件
openssl req -newkey rsa:2048 -days 1000 -nodes -keyout client.key -subj /CN=client.t.com/OU=Development\ group/O=Home\ SIA/DC=elk/DC=com > client.csr
# 使用 ca 证书与私钥签发客户端证书
openssl x509 -req -in client.csr -days 1000 -CA ca.crt -CAkey ca.key -set_serial 01 > client.crt
```

server.t.com 服务器域名，配置在 logstash 的 input 字段中

client.t.com 客户端域名，配置在 filebeat.yml 文件中


## logstash 的 input config
```sh
input {
  beats {
    port => 5045
    ssl => true
    ssl_certificate_authorities => ["/ssl/ca.crt"]
    ssl_certificate => "/ssl/server.crt"
    ssl_key => "/ssl/server.key"
    ssl_verify_mode => "force_peer"
  }
}
```

参数：

- certificate_authorities: Configures Filebeat to trust any certificates signed by the specified CA. If certificate_authorities is empty or not set, the trusted certificate authorities of the host system are used.

- certificate and key: Specifies the certificate and key that Filebeat uses to authenticate with Logstash.



## filebeat 的 output config
```sh
output.logstash:
  hosts: ["server.t.com:5045"]
  # Optional SSL. By default is off.
  # List of root certificates for HTTPS server verifications
  ssl.certificate_authorities: ["/ssl/ca.crt"]
  # Certificate for SSL client authentication
  ssl.certificate: "/ssl/client.crt"
  # Client Certificate Key
  ssl.key: "/ssl/client.key"
```

参数：

- ssl: When set to true, enables Logstash to use SSL/TLS.

- ssl_certificate_authorities: Configures Logstash to trust any certificates signed by the specified CA.

- ssl_certificate and ssl_key: Specify the certificate and key that Logstash uses to authenticate with the client.

- ssl_verify_mode: Specifies whether the Logstash server verifies the client certificate against the CA. You need to specify either peer or force_peer to make the server ask for the certificate and validate it. If you specify force_peer, and Filebeat doesn’t provide a certificate, the Logstash connection will be closed.


修改 /etc/hosts，将域名与对应的 ip 加上，同时 filebeat 的 output 地址只能为域名形式。

测试：`curl -v --cacert ca.crt https://server.t.com:5045`


## 错误案例

>x509: cannot validate certificate for <IP address> because it doesn’t contain any IP SANsedit

原因：This happens because your certificate is only valid for the hostname present in the Subject field.

三种解决方案：
1. Create a DNS entry for the hostname mapping it to the server’s IP.
2. Create an entry in /etc/hosts for the hostname. Or on Windows add an entry to C:\Windows\System32\drivers\etc\hosts.
3. Re-create the server certificate and add a SubjectAltName (SAN) for the IP address of the server. This make the server’s certificate valid for both the hostname and the IP address.




# Reference

https://www.elastic.co/guide/en/beats/filebeat/6.1/configuring-ssl-logstash.html

http://mjpclab.site/linux/openssl-self-signed-certificate

https://segmentfault.com/a/1190000014963014
