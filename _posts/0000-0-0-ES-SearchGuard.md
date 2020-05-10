---
layout: post
title: "ES7 Search Guard"
date: 2020-05-07
description: "Search Guard"
tag: Elasticsearch

---


# 安装

## 下载安装

https://docs.search-guard.com/latest/search-guard-versions

```sh
# 安装，文件路径必须绝对
bin/elasticsearch-plugin install -b file:///home/yang/software/search-guard-7-7.6.2-41.0.0.zip
# 生成 plugins/search-guard-7


# 执行脚本：
chmod +x  tools/install_demo_configuration.sh
plugins/search-guard-7/tools/install_demo_configuration.sh
# 安装后发现config/elasticsearch.yml中写入search-guard的内容
```


## 启动访问

- http此时访问不了：http://192.168.243.124:9200/

- https访问时：https://192.168.243.124:9200/

- elasticsearch.yml中修改searchguard.ssl.http.enabled: false（安装后默认true，即https访问），就会可http访问



> Search Guard not initialized (SG11).          

尚未解决，导致后面无法进行？？？





## 设置用户和密码

```sh
./tools/hash.sh -p 123456
# 生成hash码
# $2y$12$aIKpwcArAy8V7PVmPcFi6OfHT3sqN8JCsFpIX5Qp3l65W1xyi913W

# 新建用户
vi ../sgconfig/sg_internal_users.yml
```

```sh
# myself 是用户名
myself:
  hash: "刚才的hash码"
  reserved: true
  backend_roles:
  - "admin"
```

分发新配置到es集群

```sh
# tools/执行
./sgadmin.sh -cd ../sgconfig/ -icl -nhnv \
   -cacert ../../../config/root-ca.pem \
   -cert ../../../config/kirk.pem \
   -key ../../../config/kirk-key.pem 
```


## 删除

1. 删除 plugins 目录下的 search-guard-7

2. elasticsearch.yml 将 search-guard 配置删除





# ssl

下载：
https://git.floragunn.com/search-guard/search-guard-ssl#

```sh
example-pki-scripts/example.sh
cp truststore.jks node-1-keystore.jks %ES_HOME%/config/
vim config/elasticsearch.yml
```

```sh
# 配置ssl，让elasticsearch使用tls加密通讯
searchguard.ssl.transport.enabled: true
searchguard.ssl.transport.keystore_filepath: node-0-keystore.jks
searchguard.ssl.transport.keystore_password: kspass
searchguard.ssl.transport.truststore_filepath: truststore.jks
searchguard.ssl.transport.truststore_password: tspass
searchguard.ssl.transport.enforce_hostname_verification: false
searchguard.ssl.transport.resolve_hostname: false

# 配置 SeachGuard 初始化
searchguard.authcz.admin_dn:
  - CN=cn_name, OU=client, O=client, L=Test, C=DE  

# http配置，这里我只是为了测试方便，配置完，应该设置为true
searchguard.ssl.http.enabled: false
searchguard.ssl.http.keystore_filepath: node-0-keystore.jks
searchguard.ssl.http.keystore_password: kspass
searchguard.ssl.http.truststore_filepath: truststore.jks
searchguard.ssl.http.truststore_password: tspass
searchguard.allow_all_from_loopback: true
```


## 初始化searchguard索引


cp example-pki-scripts/cn_name-keystore.jks %ES_HOME%/plugins/search-guard-5/sgconfig/


$ tools/sgadmin.sh \
> -ts %ES_HOME%/config/trustore.jks \
> -tspass tspass \
> -ks sgconfig/cn_name-keystore.jks \
> -kspass kspass \
> -cd sgconfig/ \
> -icl -nhnv -h localhost


