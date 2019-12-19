---
layout: post
title: "Singleton 单例模式"
date: 2019-11-12
description: "Singleton 单例模式"
tag: Java

---

## 简介

1. 单例类只能有一个实例。
2. 单例类必须自己创建自己的唯一实例。
3. 单例类必须给所有其他对象提供这一实例。


## 懒汉式

- 是否 Lazy 初始化：是
- 是否多线程安全：否

```java
public class Singleton {  
    private static Singleton instance;  
    private Singleton (){}  
  
    public static Singleton getInstance() {  
        if (instance == null) {  
            instance = new Singleton();   // 第一次调用才初始化，避免内存浪费。
        }  
        return instance;  
    }  
}
```

```java
// 改成线程安全，但加锁会影响效率。
// 因为加锁其实只需要在第一次初始化的时候用到，之后的调用都没必要再进行加锁。
public static synchronized Singleton getInstance()
```


## 饿汉式

- 是否 Lazy 初始化：否
- 是否多线程安全：是
- 基于 classloader 机制避免了多线程的同步问题

```java
public class Singleton {  
    private static Singleton instance = new Singleton();  // 类加载时就初始化，浪费内存。 
    private Singleton (){}  
    public static Singleton getInstance() {  
        return instance;   // 没有加锁，执行效率会提高。
    }  
}
```


## 双重校验锁

- 是否 Lazy 初始化：是
- 是否多线程安全：是

```java
public class Singleton {
    private volatile static Singleton singleton; // 注意这里加volatile
    public Singleton() {}

    public static Singleton getSingleton() {
        if (singleton == null) {   // 后续的所有调用都会避免加锁而直接返回
            synchronized(Singleton.class) {
                if (singleton == null) {
                    singleton = new Singleton();
                }
            }
        }
        return singleton;
    }
}
```
volatile 使用原因：读取volatile类型的变量时总会返回最新写入的值。


# reference

https://www.cnblogs.com/xz816111/p/8470048.html

https://www.runoob.com/design-pattern/singleton-pattern.html
