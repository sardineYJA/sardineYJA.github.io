---
layout: post
title: "SpringBoot 整合 ES"
date: 2019-08-02
description: "Elasticsearch"
tag: Elasticsearch

---



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
    private String title;     // 标题

    @Field(type = FieldType.Keyword)
    private String category;  // 分类

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

```


