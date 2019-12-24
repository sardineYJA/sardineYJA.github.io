---
layout: post
title: "SpringBoot 入门"
date: 2018-09-28
description: "SpringBoot 入门"
tag: Java Web

---

# SpringBoot


项目下载：https://start.spring.io/

或新建项目 Spring Initializr

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
    // @RequestMapping("/hello")  // Get,Post都行
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
@ConfigurationProperties(prefix = "person")  // 表示装载配置文件
public class Person {
    private String name;
    private BigDecimal age;
    private String description;
    // Getter & Setter
}
```

读取配置文件字段作为一个类的属性值
```java
@Autowired     // 这里还需 @Autowired
private Person person;
```

## 从多个 yml/properties 配置文件选择某个运行

配置文件优先级：.properties 高于 .yml

从其中选择：application-dev.properties, application-prod.properties...

则 application.properties 配置，选择dev配置文件
```sh
spring.profiles.active=dev
```

如果需要使用命令启动，并选择配置文件：
```sh
java -jar -Dspring.profiles.active=dev YYY.jar
```

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


## JPA(Java Persistence API) 

通过基于JPA的Repository减少数据访问的代码量

Repository——>CrudRepository(增删改查)——>PagingAndSortingRepository(增加分页和排序)——>JpaRepository（继承所有）

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
      ddl-auto: create   # create覆盖，update是追加
    show-sql: true
```

```java
@Entity
@Table(name = "student")  // 表名，非必须，默认类名
public class Student {
    @Id                   // 主键id
    @GeneratedValue
    private Integer id;

    private String name;
    private Integer age;
    // Setter & Getter

}
```

运行自动会创建student表，相关字段

@Entity: 每个持久化POJO类都是一个实体Bean

@Table: 声明此对象映射到数据库的数据表，不是必须


## Jpa操作数据库

需要继承JpaRepository，<Student, Integer>，第二个参数为主键类型
```java
public interface StudentRepository extends JpaRepository<Student, Integer> {
}
```

```java
@Autowired
private StudentRespository studentRespository;

@GetMapping("/student")         // 查询数据库全部
public List<Student> list(){
    return studentRepository.findAll();
}

@GetMapping("/studentAdd")       // 获取url?id和name，并向数据库添加
public Student create(@RequestParam("id") Integer id,
                      @RequestParam("name") String name) {
    Student s = new Student();
    s.setId(id);
    s.setName(name);
    return studentRepository.save(s);
}

@GetMapping("/student/{id}")     // 查询某个id
public Student findById(@PathVariable("id") Integer id) {
    return studentRepository.findById(id).orElse(null);
}
```

并且JPA提供了一系列查询规范，具体可看文档。


## 事务

方法或类前加：@Transactional


## 表单验证

为Student类属性增加限制：
```java
@Min(value = 18, message = "未成年！")
private Integer age;
```

```java
@RequestMapping(value="/studentValid")
public Student studentAdd(@Valid Student s, BindingResult bindingResult) {
    if (bindingResult.hasErrors()) {
        // 验证表单字段
        System.out.println(bindingResult.getFieldError().getDefaultMessage());
        return null;
    }
    return studentRepository.save(s);    // 向数据库中添加
}
```

验证：url/studentValid?age=17


## AOP

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-aop</artifactId>
</dependency>
```

使用方法与Sping一样

```java
@Component
@Aspect  
public class LoggingAspectJ {
    @Pointcut("execution(* com.sxdt.spring.service.*.*(..))")
    public void pointcut(){}     // 重用切入点表达式

    @Before("pointcut()")
    public void beforeMethod(JoinPoint joinPoint) {
        String name = joinPoint.getSignature().getName(); // 方法名
        Object[] args = joinPoint.getArgs();              // 方法参数
        System.out.println("@Before");
    }
}
```

