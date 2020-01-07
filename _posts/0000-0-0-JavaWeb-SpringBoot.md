---
layout: post
title: "SpringBoot 入门使用"
date: 2018-09-28
description: "SpringBoot 入门使用"
tag: Java Web

---

# SpringBoot


项目下载：https://start.spring.io/

或新建项目 Spring Initializr

## 部署运行

命令行：
```sh
mvn spring-boot:run
```

打包运行：
```sh
mvn clean package   # 打包

java -jar XXX.jar   # 部署

java -jar -Dserver.port=8899 XXX.jar   # 修改端口
java -jar -Dspring.profiles.active=dev XXX.jar   # 选择配置文件
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
    return "id=="+id;   // defaultValue 设置默认值
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
    return studentRepository.findAll();  // 返回json

    PageRequest request = PageRequest.of(page, size);
    studentRepository.findAll(request);   // 也可根据页码查询，从0页开始
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
    // 返回类，即返回json数据
}
```

并且JPA提供了一系列查询规范，具体可看文档。


## 事务

方法或类前加：@Transactional


## 表单验证

为Student类属性增加限制：
```java
@Min(value = 18, message = "未成年！")
@NotEmpty(message = "此项必填")
// ... 或者其他限制
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


# 过滤器 Filter

## 简介

处于客户端与服务器资源文件之间的一道过滤网，对JSP、Servlet、静态图片文件或静态HTML文件等进行拦截，可实现URL级别的权限访问控制、过滤敏感词、压缩响应等功能。

Filter的创建和销毁由Web服务器负责。创建时调用init()，读取web.xml。访问URL时，执行doFilter方法。卸载时，调用destroy()。多个Filter组成FilterChain。


## 案例

```java
@WebFilter(filterName = "studentFilter", urlPatterns = "/*")
public class StudentFilter implements Filter {
    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
        System.out.println("Filter_init()");
    }

    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
        System.out.println("Filter_doFilter()");
        // 直接传给下一个过滤器
        filterChain.doFilter(servletRequest, servletResponse);
    }

    @Override
    public void destroy() {
        System.out.println("Filter_destroy()");
    }
}
```

入口类添加@ServletComponentScan，Servlet、Filter、Listener可直接通过@WebServlet、@WebFilter、@WebListener注解自动注册。

```java
@SpringBootApplication
@ServletComponentScan
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }

}
```


# 监听器 Listener

用于监听Web应用中某些对象、信息的创建、销毁、增加、修改等动作的发生，并作出相应处理。

根据`监听对象`分类：
- ServletContext(对应application)
- HttpSession(对应session)
- ServletRequest(对应request)

根据`监听事件`分类：
- 监听对象创建与销毁，如 ServletContextListener
- 监听对象域中属性的增加和删除，如 HttpSessionListener, ServletRequestListener
- 监听绑定到Session上的某个对象的状态，如 ServletContextAttributeListener, HttpSessionAttributeListener

```java
@WebListener
public class StudentListener implements ServletContextListener {
    @Override
    public void contextInitialized(ServletContextEvent sce) {
        System.out.println("ServletContext上下文初始化");
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
        System.out.println("ServletContext上下文销毁");
    }
}
```



