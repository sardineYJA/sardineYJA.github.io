---
layout: post
title: "Elasticsearch 全文检索"
date: 2019-07-08
description: "Elasticsearch"
tag: Bigdata

---

# Elasticsearch

Elasticsearch是一个实时分布式搜索和分析引擎。它用于全文搜索、结构化搜索、分析。


## 全文检索

指计算机索引程序通过扫描文章中的每一个词，对每一个词建立一个索引，指明该词在文章中出现的次数和位置，当用户查询时，检索程序就根据事先建立的索引进行查找，并将查找的结果反馈给用户的检索方式。这个过程类似于通过字典中的检索字表查字的过程。全文搜索搜索引擎数据库中的数据。


## lucene

jar包，里面包含了封装好的各种建立倒排索引，以及进行搜索的代码，包括各种算法。用java开发的时候，引入lucene jar，然后基于lucene的api进行去进行开发就可以了。



## 类型

Index 索引（相当于数据库）：包含一堆有相似结构的文档数据

Type 类型（相当于表）：每个索引里都可以有一个或多个type，type是index中的一个逻辑数据分类，一个type下的document，都有相同的field

Document 文档（相当于行）：文档是es中的最小数据单元，一个document可以是一条客户数据

Field 字段（列）：Field是Elasticsearch的最小单位。一个document里面有多个field，每个field就是一个数据字段。


# 单节点安装

1. 解压：tar -zxvf elasticsearch-5.2.2.tar.gz -C ../module/

2. 创建目录：data和logs

3. 修改配置文件：config/elasticsearch.yml

```sh
# ------------ Cluster --------------
cluster.name: my-application
# ------------- Node ----------------
node.name: elasticsearch-101
# ------------- Paths ---------------
path.data: /home/yangja/module/elasticsearch-5.2.2/data
path.logs: /home/yangja/module/elasticsearch-5.2.2/logs
# ------------- Memory --------------
bootstrap.memory_lock: false
bootstrap.system_call_filter: false
# ------------- Network -------------
network.host: 172.16.7.124 
# ------------ Discovery ------------
discovery.zen.ping.unicast.hosts: ["172.16.7.124"]
```

4. cluster.name如果要配置集群需要两个节点上的elasticsearch配置的cluster.name相同，都启动可以自动组成集群，
这里如果不改cluster.name则默认是cluster.name=my-application，

5. nodename随意取但是集群内的各节点不能相同

6. 修改后的每行前面不能有空格，修改后的“:”后面必须有一个空格

7. 切换root，vi /etc/security/limits.conf

```
* soft nofile 65536
* hard nofile 131072
* soft nproc 2048
* hard nproc 4096
```

8. vi /etc/security/limits.d/90-nproc.conf

```
* soft nproc 1024
#修改为
* soft nproc 2048
```

9. vi /etc/sysctl.conf 

```
添加下面配置：
vm.max_map_count=655360
```

10. 执行命令：sysctl -p

11. 启动：bin/elasticsearch -d (-d后台运行)

12. 测试：curl http://172.16.7.124:9200

13. 打开Web界面：http://172.16.7.124:9200


创建一个索引myfulltext：curl -XPUT http://172.16.7.124:9200/myfulltext


## 问题

> org.elasticsearch.bootstrap.StartupException: java.lang.RuntimeException: can not run elasticsearch as root

因为Elasticsearch5.0之后，不能使用root账户启动，先创建一个elasticsearch组和账户es：
```sh
groupadd elasticsearch
useradd es -g elasticsearch -p 123456
chown -R es:elasticsearch elasticsearch-5.2.2/
```


> ERROR: bootstrap checks failed
max file descriptors [4096] for elasticsearch process is too low, increase to at least [65536]

切换到root，vi /etc/security/limits.conf
```sh
*        hard    nofile           65536
*        soft    nofile           65536
```
`此文件修改后需要重新登录用户，才会生效`


> ERROR: bootstrap checks failed
max file descriptors [4096] for elasticsearch process likely too low, increase to at least [65536]
max number of threads [1024] for user [lishang] likely too low, increase to at least [2048]

解决：切换到root用户，编辑limits.conf 添加类似如下内容

vi /etc/security/limits.conf 

```sh
* soft nofile 65536
* hard nofile 131072
* soft nproc 4096
* hard nproc 4096
```


> max number of threads [1024] for user [lish] likely too low, increase to at least [2048]

解决：切换到root用户，进入limits.d目录下修改配置文件。

vi /etc/security/limits.d/90-nproc.conf 

```sh
* soft nproc 1024
#修改为
* soft nproc 4096
```


> max virtual memory areas vm.max_map_count [65530] likely too low, increase to at least [262144]

解决：切换到root用户修改配置sysctl.conf

vi /etc/sysctl.conf 
```sh
vm.max_map_count=655360
```
并执行命令：sysctl -p


# 安装 Elasticsearch head 插件

插件下载：https://github.com/mobz/elasticsearch-head

nodejs下载：https://nodejs.org/dist/

安装nodejs：tar -zxvf node-v6.9.2-linux-x64.tar.gz -C ../module/

配置nodejs环境变量 vi /etc/profile
```sh
export NODE_HOME=/home/yangja/module/node-v6.9.2-linux-x64
export PATH=$PATH:$NODE_HOME/bin
# 执行
source /etc/profile 
# 查看node和npm版本
node -v
npm -v
```
head插件：unzip elasticsearch-head-master.zip -d ../module/

查看当前head插件目录下有无node_modules/grunt目录，没有的话，
执行命令创建：npm install grunt --save

安装head插件：npm install -g cnpm --registry=https://registry.npm.taobao.org

安装grunt：npm install -g grunt-cli

编辑vim Gruntfile.js
```java
// 文件93行添加hostname:'0.0.0.0'
options: {
        hostname:'0.0.0.0',
        port: 9100,
        base: '.',
        keepalive: true
      }
```

检查head根目录下是否存在base文件夹
没有：将 \_site下的base文件夹及其内容复制到head根目录下base

```
mkdir base
cp _site/base/* base/
```

elasticsearch-head/目录下启动grunt server：grunt server -d

提示grunt的模块没有安装，安装即可

```sh
npm install grunt-contrib-clean -registry=https://registry.npm.taobao.org
npm install grunt-contrib-concat -registry=https://registry.npm.taobao.org
npm install grunt-contrib-watch -registry=https://registry.npm.taobao.org 
npm install grunt-contrib-connect -registry=https://registry.npm.taobao.org
npm install grunt-contrib-copy -registry=https://registry.npm.taobao.org 
npm install grunt-contrib-jasmine -registry=https://registry.npm.taobao.org
# 最后一个模块可能安装不成功，但是不影响使用
```

打开web界面：http://172.16.7.124:9100


启动集群插件后发现集群未连接，关闭修改重启

在elasticsearch-5.2.2/config/elasticsearch.yml，增加
```
http.cors.enabled: true
http.cors.allow-origin: "*"
```


# 项目

## 依赖

```xml
<dependencies>
	<dependency>
		<groupId>org.elasticsearch</groupId>
		<artifactId>elasticsearch</artifactId>
		<version>5.2.2</version>
	</dependency>

	<dependency>
		<groupId>org.elasticsearch.client</groupId>
		<artifactId>transport</artifactId>
		<version>5.2.2</version>
	</dependency>
</dependencies>
```

## 连接测试

- ElasticSearch 服务默认端口9300
- Web 管理平台端口9200
- Head 插件端口9100

下面：blog相当于数据库，article相当于表

```java
// 设置连接集群名称
Settings settings = Settings.builder().put("cluster.name", "my-application").build();
// 连接集群
PreBuiltTransportClient client = new PreBuiltTransportClient(settings);
client.addTransportAddress(new InetSocketTransportAddress(
		InetAddress.getByName("172.16.7.124"), 9300));
// 打印集群名称
System.out.println(client.toString());

// 创建索引
// client.admin().indices().prepareCreate("blog").get();

// 删除索引
client.admin().indices().prepareDelete("blog").get();

// 关闭连接
// client.close();
```

## 数据源插入到文档

```java
// json -> 新建文档
String json = "{" + "\"id\":\"1\"," + "\"title\":\"基于Lucene的搜索服务器\","
		+ "\"content\":\"它提供了一个分布式多用户能力的全文搜索引擎，基于RESTful web接口\"" + "}";
// 创建文档
IndexResponse indexResponse = client.prepareIndex("blog", "article", "1").setSource(json).execute().actionGet();


// map -> 新建文档
Map<String, Object> map = new HashMap<String, Object>();
map.put("id", "2");
map.put("title", "基于Lucene的搜索服务器");
map.put("content", "它提供了一个分布式多用户能力的全文搜索引擎，基于RESTful web接口");
// 创建文档
indexResponse = client.prepareIndex("blog", "article", "2").setSource(map).execute().actionGet();


// 通过es自带类构件json
XContentBuilder builder = XContentFactory.jsonBuilder().startObject()
		.field("id", "3")
		.field("title", "基于Lucene的搜索服务器")
		.field("content", "它提供了一个分布式多用户能力的全文搜索引擎，基于RESTful web接口")
		.endObject();
// 创建文档
indexResponse = client.prepareIndex("blog", "article", "3").setSource(builder).execute().actionGet();


// 打印返回结果
System.out.println("index:" + indexResponse.getIndex());
System.out.println("type:" + indexResponse.getType());
System.out.println("id:" + indexResponse.getId());
System.out.println("version:" + indexResponse.getVersion());
System.out.println("result:" + indexResponse.getResult());
```

## 查询文档

```java
// 查询文档-单个索引
GetResponse response = client.prepareGet("blog", "article", "1").get();
System.out.println(response.getSourceAsString());

// 查询文档-多个索引
MultiGetResponse mresponse = client.prepareMultiGet()
		.add("blog", "article", "1")
		.add("blog", "article", "2", "3", "1")
		.add("blog", "article", "2")
		.get();
for (MultiGetItemResponse item: mresponse) {
	GetResponse getResponse = item.getResponse();
	if(getResponse.isExists()) {
		System.out.println(getResponse.getSourceAsString());
	}
}
```

## 更新文档

```java
// 创建更新数据的请求对象
UpdateRequest updateRequest = new UpdateRequest();
updateRequest.index("blog");
updateRequest.type("article");
updateRequest.id("3");

updateRequest.doc(XContentFactory.jsonBuilder().startObject()
	// 对没有的字段添加, 对已有的字段替换
	.field("title", "基于Lucene的搜索服务器")
	.field("content", "它提供了一个分布式多用户能力的全文搜索引擎，基于RESTful web接口。大数据前景无限")
	.field("createDate", "2017-8-22").endObject());

// 获取更新后的值
UpdateResponse indexResponse = client.update(updateRequest).get();

// 打印返回的结果
System.out.println("index:" + indexResponse.getIndex());
System.out.println("type:" + indexResponse.getType());
System.out.println("id:" + indexResponse.getId());
System.out.println("version:" + indexResponse.getVersion());
System.out.println("create:" + indexResponse.getResult());
```

设置查询条件, 查找不到则添加IndexRequest内容，查找到则按照UpdateRequest更新

```java
// 设置查询条件，查找不到则添加(第一次执行，添加下面内容)
IndexRequest indexRequest = new IndexRequest("blog", "article", "5")
	.source(XContentFactory.jsonBuilder().startObject()
		.field("title", "搜索服务器")
		.field("content","它提供了一个分布式多用户能力的全文搜索引擎，基于RESTful web接口。Elasticsearch是用Java开发的，并作为Apache许可条款下的开放源码发布，是当前流行的企业级搜索引擎。设计用于云计算中，能够达到实时搜索，稳定，可靠，快速，安装使用方便。")
		.endObject());

// 设置更新，查找到更新下面的设置(第二次执行，增加字段)
UpdateRequest upsert = new UpdateRequest("blog", "article", "5")
	.doc(XContentFactory.jsonBuilder().startObject()
		.field("user", "yangja")
		.endObject())
	.upsert(indexRequest);  // 找不到则添加IndexRequest内容

client.update(upsert).get();
```

## 删除文档数据

```java
// 删除文档数据
DeleteResponse indexResponse = client.prepareDelete("blog", "article", "5").get();

// 打印返回的结果
System.out.println("index:" + indexResponse.getIndex());
System.out.println("type:" + indexResponse.getType());
System.out.println("id:" + indexResponse.getId());
System.out.println("version:" + indexResponse.getVersion());
System.out.println("found:" + indexResponse.getResult());
```

## 条件查询


```java
// 查询所有
SearchResponse searchResponse = client.prepareSearch("blog")
	.setTypes("article")
	.setQuery(QueryBuilders.matchAllQuery())
	.get();


// 对所有字段分词查询
SearchResponse searchResponse = client.prepareSearch("blog")
	.setTypes("article")
	.setQuery(QueryBuilders.queryStringQuery("全文"))
	.get();


// 通配符查询 wildcardQuery，*任意多个字符，?单个字符
SearchResponse searchResponse = client.prepareSearch("blog")
	.setTypes("article")
	.setQuery(QueryBuilders.wildcardQuery("content", "*全*"))
	.get();


// 词条查询 TermQuery
// field查询
SearchResponse searchResponse = client.prepareSearch("blog")
	.setTypes("article")
	.setQuery(QueryBuilders.termQuery("content", "全"))
	.get();


// 模糊查询fuzzy
SearchResponse searchResponse = client.prepareSearch("blog")
	.setTypes("article")
	.setQuery(QueryBuilders.fuzzyQuery("title", "lucene"))
	.get();


// 打印
SearchHits hits = searchResponse.getHits();   // 获取命中次数，查询结果有多少对
System.out.println("查询结果有：" + hits.getTotalHits() + "条");

Iterator<SearchHit> iterator = hits.iterator();
while(iterator.hasNext()) {
	SearchHit searchHit = iterator.next();
	System.out.println(searchHit.getSourceAsString());
}
```



# 中文查询

ik 分词模式：ik_max_word（最细颗粒，穷尽所有可能） 和 ik_smart（最粗颗粒）

下载与ES版本一致：https://github.com/medcl/elasticsearch-analysis-ik/releases

解压到ES的plugins目录下，修改目录名为ik，重启



# reference

https://www.cnblogs.com/zhuzi91/p/8228214.html

