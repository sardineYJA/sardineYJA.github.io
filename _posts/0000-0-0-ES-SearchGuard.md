---
layout: post
title: "ES7 Search Guard"
date: 2020-05-07
description: "Search Guard"
tag: ELK

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

需要初始化searchguard索引.



## search-guard-ssl 使用

https://github.com/floragunncom/search-guard-ssl

```sh
./gen_root_ca.sh capass changeit                 # CA密码     TS密码
./gen_node_cert.sh 0 changeit capass             # node   KS密码    CA密码
./gen_client_node_cert.sh kirk changeit capass   # 客户端  KS密码    CA密码
```

elasticsearch/config/: truststore.jk, node-0-keystore.jks

plugins/search-guard-6/sgconfig/: truststore.jks, kirk-keystore.jks

证书一次生成，拷贝分发各个节点，之后一台执行即可，生成索引：
```sh
./sgadmin.sh -cn 集群名 -h IP地址 -cd ../sgconfig/ -ks kirk-keystore.jks -kspass 123456 -ts truststore.jks -tspass 123456 -nhnv

# -nhnv 不验证主机名
# -cd   指定存储目录
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
  - CN=kirk, OU=client, O=client, L=Test, C=DE  

searchguard.ssl.http.enabled: false
searchguard.ssl.http.keystore_filepath: node-0-keystore.jks
searchguard.ssl.http.keystore_password: kspass
searchguard.ssl.http.truststore_filepath: truststore.jks
searchguard.ssl.http.truststore_password: tspass
searchguard.allow_all_from_loopback: true
```



## 设置用户和密码

一般使用Kibana管理权限，角色，用户

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


## 删除

1. 删除 plugins 目录下的 search-guard-7

2. elasticsearch.yml 将 search-guard 配置删除



## searchguard 证书

修改 com.floragunn.searchguard.configuration.SearchGuard 类，编译成.class

ES 安装 searchguard 后，反编译 search-guard-6-6.1.1-20.1.jar 替换 .class 重新打包

```sh
SearchGuardIndexSearcherWrapper.class
SearchGuardLicense.class
SearchGuardLicense$Type.class
```


# 其他

## 权限管理等级

Permissions on the cluster level (Community)
Permissions on index level (Community)
Permissions on document level (Enterprise)
Permissions on field level (Enterprise)

Since document types are deprecated in Elasticsearch 6, document type level permissions will be removed in Search Guard 7.


## API

```sh
# GET PUT DELETE
GET /_searchguard/api/internalusers/
GET /_searchguard/api/internalusers/{username}
GET /_searchguard/api/roles/{rolename}
GET /_searchguard/api/rolesmapping/{rolename}
GET /_searchguard/api/actiongroups/{actiongroup}
```


## User cache settings

Search Guard uses a cache to store the roles of authenticated users.

elasticsearch.yml:
`searchguard.cache.ttl_minutes: <integer, ttl in minutes>`

Setting the value to 0 will completely disable the cache.

It is recommended to leave the cache settings untouched for LDAP and Internal User Database. Disabling the cache can severely reduce the performance of these authentication domains.


## Managing the Search Guard index

Search Guard index 名称：`searchguard`，replica shards is set to the number of nodes-1（即每个节点都有）


## searchguard index replica 禁止自动扩展的场景：

- When using a Hot/Warm Architecture
- Running multiple instances of Elasticsearch on the same host machine
- When cluster.routing.allocation.same_shard.host is set to false
- The searchguard index stays constantly yellow


