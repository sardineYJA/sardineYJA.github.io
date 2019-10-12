---
layout: post
title: "Java 反射机制"
date: 2018-02-27
description: "Java 反射机制"
tag: Java

---


## 简介

JAVA反射机制是在运行状态中，对于任意一个类，都能够知道这个类的所有属性和方法；对于任意一个对象，都能够调用它的任意一个方法和属性；这种动态获取的信息以及动态调用对象的方法的功能称为java语言的反射机制。


Class对象的由来是将class文件读入内存，并为之创建一个Class对象。

![png](/images/posts/all/Java反射原理解析.png)


## 获取Class对象的三种方式：
* Object ——> new 类名().getClass();
* 任何数据类型（包括基本数据类型）都有一个“静态”的class属性，类名.class;
* 通过Class类的静态方法：Class.forName（String  className）(常用)

```java
Class c1 = new Student().getClass();
Class c2 = Studnet.class;
Class c3 = Class.forName("包名.Student");
```


通过反射可以执行私有方法，并且获取私有变量
```java
Class c = Class.forName("java.lang.String");

c.getConstructors();         // 获取所有公有构造方法
c.getDeclaredConstructors(); // 所有的构造方法(包括：私有、受保护、默认、公有)

c.getFields();               // 获取所有公有的字段
c.getDeclaredFields();       // 获取所有的字段(包括私有、受保护、默认的)

c.getMethods();              // 获取所有的”公有“方法
c.getDeclaredMethods();      // 获取所有的方法，包括私有的


// 获取私有构造方法，并调用
Constructor con = c.getDeclaredConstructor(char.class);
con.setAccessible(true);     //暴力访问(忽略掉访问修饰符)
Object obj = con.newInstance('男'); //调用构造方法

// 获取私有字段，并调用
Field f = c.getDeclaredField("password");
f.setAccessible(true);//暴力反射，解除私有限定
f.set(obj, "123456");

// 获取私有的方法，并调用
Method m = c.getDeclaredMethod("sayHello", String.class);
m.setAccessible(true);      // 解除私有限定
m.invoke(obj, "Hi");        // 调用方法
```



# reference

https://blog.csdn.net/sinat_38259539/article/details/71799078






