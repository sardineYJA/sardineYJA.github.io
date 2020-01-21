---
layout: post
title: "Junit 和 Lombok"
date: 2018-02-15
description: "Junit 和 Lombok"
tag: Java

---

# Junit

## 注解

1. @Test: 测试方法

2. @Ignore: 被忽略的测试方法：加上之后，暂时不运行此段代码

3. @Before: 每一个测试方法之前运行

4. @After: 每一个测试方法之后运行

5. @BeforeClass: 方法要是静态方法（static 声明），所有测试开始之前运行

6. @AfterClass: 方法要是静态方法（static 声明），所有测试结束之后运行

 
## 依赖

```xml
<dependency>
	<groupId>junit</groupId>
	<artifactId>junit</artifactId>
	<version>RELEASE</version>
</dependency>
 ```

## 编写测试类的原则

1. 测试方法上必须使用@Test进行修饰

2. 测试方法必须使用public void 进行修饰，不能带任何的参数

3. 新建一个源代码目录来存放我们的测试代码，即将测试代码和项目业务代码分开

4. 测试类所在的包名应该和被测试类所在的包名保持一致

5. 测试单元中的每个方法必须可以独立测试，测试方法间不能有任何的依赖

6. 测试类使用Test作为类名的后缀（不是必须）

7. 测试方法使用test作为方法名的前缀（不是必须）



# Lombok

## 简介

Lombok 能以简单的注解形式来简化java代码，提高开发人员的开发效率

缺点：大大降低了源代码的可读性和完整性，降低了阅读源代码的舒适度

## 依赖

```xml
<properties>
    <lombok.version>1.16.12</lombok.version>
</properties>
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <version>${lombok.version}</version>
</dependency>
```

> IDEA 需要安装 Lombok 插件才可使用


# 常使用

## @Data

@Data注解在类上，会为类的所有属性自动生成setter/getter、equals、canEqual、hashCode、toString方法，如为final属性，则不会为该属性生成setter方法。

```java
@Data
@NoArgsConstructor    // 生成无参构造函数
public class Test {
    private String Id;
    private String message;
}
```

## @Getter/@Setter

@Getter/@Setter注解可以为相应的属性自动生成Getter/Setter方法

```java
public class Test {
    @Getter @Setter private String Id;
    @Getter @Setter private String message;
}
```

## @Cleanup

@Cleanup能自动调用close()方法

```java
public class CleanupExample {
  public static void main(String[] args) throws IOException {
    @Cleanup InputStream in = new FileInputStream(args[0]);
    @Cleanup OutputStream out = new FileOutputStream(args[1]);
}
```


## @Slf4j

@Slf4j 相当于定义了日志变量log

```java
@Slf4j
public class Demo {
    // 省略了 private final Logger log = LoggerFactory.getLogger(当前类名.class); 
    public String auth(String s) {
        log.error("没有通过权限验证！");
    }
```


