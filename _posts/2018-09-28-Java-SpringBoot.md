---
layout: post
title: "SpringBoot 入门"
date: 2018-09-28
description: "SpringBoot 入门"
tag: Java

---

# SpringBoot


项目下载：https://start.spring.io/

## 运行

命令行：
```sh
mvn spring-boot:run
```

打包运行：
```sh
mvn clean package
java -jar XXX.jar
```

网址：http://localhost:8080

## 测试案例

```java
@RestController
public class HelloController {
    @GetMapping("/hello")
    public String say() {
        return "Hello, Spring Boot!";
    }
}
```

## 配置文件

新建application.yml，换端口和根地址
```sh
server:
  port: 18080
  servlet:
    context-path: /root
```

打开：http://localhost:18080/root/hello


## 读取配置文件自定义字段

yml文件增加：
```sh
minMoney: 10
description: 测试自定义配置字段
```

读取：
```java
@Value("${minMoney}")
private BigDecimal minMoney;

@Value("${description}")
private String description;
```

## 读取多个字段

yml文件增加：
```sh
person:
  name: yang
  age: 25
  description: ${person.name}是男，${person.age}岁
```

```java
@Component
@ConfigurationProperties(prefix = "person")
public class Person {
    private String name;
    private BigDecimal age;
    private String description;
    // Getter & Setter
}
```

读取配置文件字段作为一个类的属性值
```java
@Autowired
private Person person;
```

## 多个XXX.yml配置文件读取

选择某个yml进行运行：

java -jar -Dspring.profiles.active=... YYY.jar


## 警告

出现警告：

> Spring Boot Configuration Annotation Processor not found in classpath

解决：

```xml
<dependency>
     <groupId>org.springframework.boot</groupId>
     <artifactId>spring-boot-configuration-processor</artifactId>
     <optional>true</optional>
</dependency>
```

