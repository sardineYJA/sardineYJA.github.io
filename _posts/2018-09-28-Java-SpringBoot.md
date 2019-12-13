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
    // @PostMapping("/hello")
    // @RequestMapping("/hello")
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

## 获取url上的参数值

方法一：url/test/11
```java
@RequestMapping("/test/{id}")
public String test(@PathVariable("id") Integer id) {
    return "id=="+id;
}
```

方法二：url/test?id=11
```java
@RequestMapping("/test")
public String kan(@RequestParam(value = "id", required = false, defaultValue = "99") Integer id) {
    return "id=="+id;
}
```


## 数据库

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
</dependency>
```

application.yml配置

```sh
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://172.16.7.124:3306/test?characterEncoding=utf-8
    username: root
    password: root123456
  jpa:
    hibernate:
      ddl-auto: create   # update是追加
    show-sql: true
```

```java
@Entity
public class Student {
    @Id
    @GeneratedValue
    private Integer id;

    private String name;
    private Integer age;
    // Setter & Getter

}
```

运行自动会创建student表


## Jpa操作数据库

```java
public interface StudentRespository extends JpaRepository<Student, Integer> {
}
```

```java
@Autowired
private StudentRespository studentRespository;

@GetMapping("/student")
public List<Student> list(){
    return studentRespository.findAll();
}

@GetMapping("/studentAdd")
public Student create(@RequestParam("id") Integer id,
                      @RequestParam("name") String name) {
    Student s = new Student();
    s.setId(id);
    s.setName(name);
    return studentRespository.save(s);
}

@GetMapping("/student/{id}")
public Student findById(@PathVariable("id") Integer id) {
    return studentRespository.findById(id).orElse(null);
}
```


## 事务

方法前：@Transactional
