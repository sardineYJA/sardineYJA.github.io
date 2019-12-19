---
layout: post
title: "Lombok 的使用"
date: 2019-11-11
description: "Lombok 的使用"
tag: Java

---

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

