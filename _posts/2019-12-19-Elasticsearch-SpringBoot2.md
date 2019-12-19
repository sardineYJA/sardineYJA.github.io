---
layout: post
title: "SpringBoot 整合 ES 的 HighLevelClient"
date: 2019-12-19
description: "Elasticsearch"
tag: Elasticsearch

---


# high-level-client

InetSocketTransportAddress  --> transportClient  --> RestHighLevelClient

ES 7版本建议使用 high-level-client。


## 依赖


```xml
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>fastjson</artifactId>
    <version>1.2.56</version>
</dependency>

<!-- elasticsearch7.4.1 新版本引入 -->
<dependency>
	<groupId>org.elasticsearch.client</groupId>
	<artifactId>elasticsearch-rest-high-level-client</artifactId>
	<version>${es.version}</version>
	<exclusions>
		<exclusion>
			<groupId>org.elasticsearch.client</groupId>
			<artifactId>elasticsearch-rest-client</artifactId>
		</exclusion>
		<exclusion>
			<groupId>org.elasticsearch</groupId>
			<artifactId>elasticsearch</artifactId>
		</exclusion>
	</exclusions>
</dependency>
<dependency>
	<groupId>org.elasticsearch.client</groupId>
	<artifactId>elasticsearch-rest-client</artifactId>
	<version>${es.version}</version>
</dependency>
<dependency>
	<groupId>org.elasticsearch</groupId>
	<artifactId>elasticsearch</artifactId>
	<version>${es.version}</version>
</dependency>
```

```
es.search.node=172.16.7.93
es.search.port=9200
```

## 封装 Client

```java
@Component
@Data
@ConfigurationProperties(prefix = "es.search")   // 加载配置到属性
public class EsClientUtil implements Serializable{

    private static final long serialVersionUID = 8827734706520399883L;
    private RestClientBuilder restClientBuilder;
    private RestHighLevelClient client;

    //客户端与之通信的一个或多个服务节点,用于client
    private String node;
    //es端口
    private int port = 9200;

    //链接超时时长(默认1000)
    private static final int CONNECT_TIME_OUT = 1000;
    //socket超时时间(默认30000)
    private static final int SOCKET_TIME_OUT = 400000;
    //链接请求超时时间(默认500)
    private static final int CONNECTION_REQUEST_TIME_OUT = 5000;
    private static final int MAX_CONNECT_NUM = 100;
    private static final int MAX_CONNECT_PER_ROUTE = 100;
    private static boolean uniqueConnectTimeConfig = true;
    private static boolean uniqueConnectNumConfig = true;



    public RestHighLevelClient getClient() {
        if (client == null) {
            synchronized (RestHighLevelClient.class) {
                if (client == null) {
                    buildClient();
                }
            }
        }
        return client;
    }

    private void buildClient(){
        restClientBuilder = RestClient.builder(new HttpHost(node, port, "http"));
        if (uniqueConnectTimeConfig) {
            setConnectTimeOutConfig();
        }
        if (uniqueConnectNumConfig) {
            setMutiConnectConfig();
        }
        client = new RestHighLevelClient(restClientBuilder);
    }

    /**
     * 主要关于异步httpclient的连接延时配置
     */
    private void setConnectTimeOutConfig() {
        restClientBuilder.setRequestConfigCallback(new RestClientBuilder.RequestConfigCallback() {
            @Override
            public RequestConfig.Builder customizeRequestConfig(RequestConfig.Builder requestConfigBuilder) {
                requestConfigBuilder.setConnectTimeout(CONNECT_TIME_OUT);
                requestConfigBuilder.setSocketTimeout(SOCKET_TIME_OUT);
                requestConfigBuilder.setConnectionRequestTimeout(CONNECTION_REQUEST_TIME_OUT);
                return requestConfigBuilder;
            }
        });
    }

    /**
     * 主要关于异步httpclient的连接数配置
     */
    private void setMutiConnectConfig() {
        restClientBuilder.setHttpClientConfigCallback(new RestClientBuilder.HttpClientConfigCallback() {
            @Override
            public HttpAsyncClientBuilder customizeHttpClient(HttpAsyncClientBuilder httpAsyncClientBuilder) {
                httpAsyncClientBuilder.setMaxConnTotal(MAX_CONNECT_NUM);
                httpAsyncClientBuilder.setMaxConnPerRoute(MAX_CONNECT_PER_ROUTE);
                return httpAsyncClientBuilder;
            }
        });
    }
}
```


```java
@Autowired
private EsClientUtil esClientUtil;

private RestHighLevelClient client;

client = esClientUtil.getClient();
```



## 插入或更新一个对象

```java
public void insertOrUpdateOne(String index, EsEntity entity) {
    IndexRequest request = new IndexRequest(index);
    request.id(entity.getId());
    request.source(JSON.toJSONString(entity.getData()), XContentType.JSON);
    client.index(request, RequestOptions.DEFAULT);
}
```


## 批量插入

```java
public void insertBatch(String index, List<EsEntity> list) {
    BulkRequest request = new BulkRequest();
    list.forEach(item -> request.add(new IndexRequest(index).id(item.getId())
            .source(JSON.toJSONString(item.getData()), XContentType.JSON)));
    client.bulk(request, RequestOptions.DEFAULT);
}
```


## 批量删除

```java
public <T> void deleteBatch(String index, Collection<T> idList) {
    BulkRequest request = new BulkRequest();
    idList.forEach(item -> request.add(new DeleteRequest(index, item.toString())));
    client.bulk(request, RequestOptions.DEFAULT);
}
```


## 搜索

```java
public <T> List<T> search(String index, SearchSourceBuilder builder, Class<T> c) {
    SearchRequest request = new SearchRequest(index);
    request.source(builder);
    try {
        SearchResponse response = client.search(request, RequestOptions.DEFAULT);
        SearchHit[] hits = response.getHits().getHits();
        List<T> res = new ArrayList<>(hits.length);
        for (SearchHit hit : hits) {
            res.add(JSON.parseObject(hit.getSourceAsString(), c));
        }
        return res;
    } catch (Exception e) {
        throw new RuntimeException(e);
    }
}
```


## 条件删除

```java
public void deleteByQuery(String index, QueryBuilder builder) {
    DeleteByQueryRequest request = new DeleteByQueryRequest(index);
    request.setQuery(builder);
    //设置批量操作数量,最大为10000
    request.setBatchSize(10000);
    request.setConflicts("proceed");
    try {
        client.deleteByQuery(request, RequestOptions.DEFAULT);
    } catch (Exception e) {
        throw new RuntimeException(e);
    }
}
```


## SearchSourceBuilder

```java
// 创建封装查询条件参数对象，所有的查询条件都会封装到此类
SearchSourceBuilder sourceBuilder = new SearchSourceBuilder();
sourceBuilder.size(1000);
sourceBuilder.from(0);
sourceBuilder.timeout(new TimeValue(60, TimeUnit.SECONDS));
sourceBuilder.fetchSource(feilds, null);  // 获取指定的字段, String[] feilds
sourceBuilder.sort("price", SortOrder.DESC);

//创建请求对象，如果不传参数，这将针对所有索引运行，这里搜索多个索引, String[] indices
SearchRequest searchRequest = new SearchRequest(indices,sourceBuilder);

client.search(searchRequest, RequestOptions.DEFAULT).getHits();  // Client 查询
```


# reference

https://www.cnblogs.com/wuyoucao/p/11269923.html

