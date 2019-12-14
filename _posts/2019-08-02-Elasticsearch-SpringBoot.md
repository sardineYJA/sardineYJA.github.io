---
layout: post
title: "SpringBoot 整合 ES"
date: 2019-08-02
description: "Elasticsearch"
tag: Elasticsearch

---

## 依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-elasticsearch</artifactId>
</dependency>
<dependency>
    <groupId>junit</groupId>
    <artifactId>junit</artifactId>
</dependency>
```

> 适合6.0版本以上ES，6.0版本以下ES不适用于SpringBoot的依赖

配置文件：application.yml / application.properties
```sh
spring:
  data:
    elasticsearch:
      cluster-name: my-application
      cluster-nodes: 172.16.7.124:9300
      repositories:
        enabled: true
```

```java
@Document(indexName = "item", type = "docs", shards = 1, replicas = 0)
public class Item {
    @Id
    private Long id;

    @Field(type = FieldType.Text, analyzer = "ik_max_word")
    private String title;     // 标题，text：存储数据时候，会自动分词，并生成索引

    @Field(type = FieldType.Keyword)
    private String category;  // 分类，keyword：存储数据时候，不会分词建立索引

    @Field(type = FieldType.Keyword)
    private String brand;     // 品牌

    @Field(type = FieldType.Double)
    private Double price;     // 价格

    @Field(index = false, type = FieldType.Keyword)
    private String images;    // 图片地址
}
```

## 测试

```java
@RunWith(SpringRunner.class)
@SpringBootTest(classes = DemoApplication.class)   // main函数
public class EsDemo {

    @Autowired
    private ElasticsearchTemplate elasticsearchTemplate;

    @Test
    public void testCreateIndex() {
        // 创建索引
        elasticsearchTemplate.createIndex(Item.class);
    }

    @Test
    public void testDeleteIndex() {
        // 删除索引
        elasticsearchTemplate.deleteIndex(Item.class);
    }
}
```


## Repository接口

```java
// Item:为实体类
// Long:为Item实体类中主键的数据类型
public interface ItemRepository extends ElasticsearchRepository<Item, Long> {}
```

插入：
```java
@Autowired
private ItemRepository itemRepository;

@Test
public void insert() {   // 插入数据
    Item item = new Item(1L, "小米", " 手机",
            "小米", 3499.00, "http://.../3.jpg");
    itemRepository.save(item);
}

@Test
public void insertList() {  // 批量插入
    List<Item> list = new ArrayList<>();
    list.add(new Item(2L, "坚果手机R1", " 手机", "锤子", 3699.0, "http://../13123.jpg"));
    list.add(new Item(3L, "华为META10", " 手机", "华为", 4499.0, "http://../13123.jpg"));
    itemRepository.saveAll(list);
}
```

查询：

```java
public void testQueryAll() {
	// 查询全部，descending()降序，ascending()升序
	Iterable<Item> list = this.itemRepository.findAll(Sort.by("price").ascending())
	for (Item item: list) {
		System.out.println(item);
	}
}
```

```java
@Test
public void testMatchQuery() {
	// 创建对象，匹配字符串查询matchQuery
	NativeSearchQueryBuilder queryBuilder = new NativeSearchQueryBuilder();
	queryBuilder.withQuery(QueryBuilders.matchQuery("title", "小米"));
	// 查询，search 默认就是分页查找
	Page<Item> page = this.itemRepository.search(queryBuilder.build());
	for (Item item: page) {
		System.out.println(item);
	}
}
```

```java
@Test
public void testTermQuery(){
	
    NativeSearchQueryBuilder builder = new NativeSearchQueryBuilder();

    
    // 匹配int/long/double/float/....等类型查找
    builder.withQuery(QueryBuilders.termQuery("price",998.0));
    
    // 布尔查询
	builder.withQuery(
		QueryBuilders.boolQuery().must(QueryBuilders.matchQuery("title","华为"))
								 .must(QueryBuilders.matchQuery("brand","华为"))
	);

	// 模糊查询
	builder.withQuery(QueryBuilders.fuzzyQuery("title","faceoooo"));

	// 分页查询
	builder.withQuery(QueryBuilders.termQuery("category", "手机"));
    int page = 0;  // 起始页
    int size = 2;  // 页数
    builder.withPageable(PageRequest.of(page,size));

    // 排序
	builder.withSort(SortBuilders.fieldSort("price").order(SortOrder.ASC));


    Page<Item> page = this.itemRepository.search(builder.build());
}
```


## 聚合

```java
@Test
public void testAgg() {
	NativeSearchQueryBuilder queryBuilder = new NativeSearchQueryBuilder();
	queryBuilder.withSourceFilter(new FetchSourceFilter(new String[]{""}, null));

	// 添加一个新的聚合，按品牌分组
	queryBuilder.addAggregation(
		AggregationBuilders.terms("brands")  // 聚合名称
							.field("brand")  // 聚合字段
							);
	// 查询，需要把结果转，AggregatedPage：聚合查询的结果类
	AggregatedPage<Item> aggPage = (AggregatedPage<Item>) this.itemRepository.search(queryBuilder.builder());
	
	StringTerms agg = (StringTerms) aggPage.getAggregation("brands");
	List<StringTerms.Bucket> buckets = agg.getBuckets();
	for (StringTerms.Bucket bucket: buckets)	{
		bucket.getKeyAsString();  
		bucket.getDocCount();   // 每个品牌的数量
	}
} 
```



```java
//（1）统计某个字段的数量
ValueCountBuilder vcb=  AggregationBuilders.count("count_uid").field("uid");

//（2）去重统计某个字段的数量（有少量误差）
CardinalityBuilder cb= AggregationBuilders.cardinality("distinct_count_uid").field("uid");

//（3）聚合过滤
FilterAggregationBuilder fab= AggregationBuilders.filter("uid_filter").filter(QueryBuilders.queryStringQuery("uid:001"));

//（4）按某个字段分组
TermsBuilder tb=  AggregationBuilders.terms("group_name").field("name");

//（5）求和
SumBuilder  sumBuilder=	AggregationBuilders.sum("sum_price").field("price");

//（6）求平均
AvgBuilder ab= AggregationBuilders.avg("avg_price").field("price");

//（7）求最大值
MaxBuilder mb= AggregationBuilders.max("max_price").field("price"); 

//（8）求最小值
MinBuilder min=	AggregationBuilders.min("min_price").field("price");

//（9）按日期间隔分组
DateHistogramBuilder dhb= AggregationBuilders.dateHistogram("dh").field("date");

//（10）获取聚合里面的结果
TopHitsBuilder thb=  AggregationBuilders.topHits("top_result");

//（11）嵌套的聚合
NestedBuilder nb= AggregationBuilders.nested("negsted_path").path("quests");

//（12）反转嵌套
AggregationBuilders.reverseNested("res_negsted").path("kps ");
```

## 嵌套聚合

```java
// 添加一个新的聚合，聚合类型为terms，聚合名称为brands，聚合字段为brand
queryBuilder.addAggregation(
    AggregationBuilders.terms("brands").field("brand")
    .subAggregation(AggregationBuilders.avg("priceAvg").field("price")) 
    // 在品牌聚合桶内进行嵌套聚合，求平均值
);
```


# reference

https://blog.csdn.net/chen_2890/article/details/83895646

