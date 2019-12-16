---
layout: post
title: "SpringBoot 添加 html"
date: 2018-09-29
description: "SpringBoot 添加 html"
tag: Java

---

## 简介

@RestController = @Controller + @ResponseBody

@RestController 不能返回jsp，html页面。

@Controller 返回到指定页面，需要返回JSON，XML或自定义mediaType内容到页面，则需要在对应的方法上加上 @ResponseBody 注解。



## SpringBoot 跳转 html

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-thymeleaf</artifactId>
</dependency>
```


```sh
spring:
  thymeleaf:
    prefix: classpath:/templates/
```


```java
@Controller
public class FileUploadController {
    @RequestMapping("file")
    public String file() {
        return "/fileUpload"; // 跳到templates/fileUpload.html
    }
}
```

resources/templates/fileUpload.html
```xml
<form action="upload" method="post">
    <p>选择文件: <input type="file" name="fileName"/></p>
    <p><input type="submit" value="提交"/></p>
</form>
```

## SpringBoot ES 搜索框

resources/templates/search.html
```xml
<form action="searchTitle" method="get">
    <p>输入搜索：<input type="text" name="title"/></p>
    <p><input type="submit" value="搜索"/></p>
</form>
```

```java
@Controller
public class SearchController {

    @RequestMapping("search")
    public String search() {
        return "search";  // 跳转 search.html
    }

    @Autowired
    private ItemRepository itemRepository;

    @RequestMapping("searchTitle")  // 查询标题含有搜索文本的数据
    public String SearchTitle(@RequestParam(value = "title") String title) {
        NativeSearchQueryBuilder queryBuilder = new NativeSearchQueryBuilder();
        queryBuilder.withQuery(QueryBuilders.matchQuery("title", title));
        Page<Item> page = this.itemRepository.search(queryBuilder.build());
        for (Item item: page) {
            System.out.println(item);
        } 
        return "search";   // 重新返回到 search.html
    }
}
```

## Model 向 html 传递数据

show.html
```xml
<html xmlns:th="http://www.thymeleaf.org">
    <p th:text="'用户ID：' + ${id}"/>
    <p th:text="'用户名：' + ${name}"/>
</html>
```


```java
@RequestMapping("show")
public String show(Model model) {
    model.addAttribute("id", "1");
    model.addAttribute("name", "yang");
    return "show";   // 将model传递个show.html
}
```
