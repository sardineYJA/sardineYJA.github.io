---
layout: post
title: "代理模式"
date: 2019-05-26
description: "简单介绍代理模式"
tag: Java

---
# 简介

在使用Spring框架的过程中，其实就是为了使用IOC/DI和AOP，面向切面编程，这两个是Spring的灵魂。主要用到的设计模式有工厂模式和代理模式。

IOC就是典型的工厂模式，通过sessionfactory去注入实例。

AOP就是典型的代理模式的体现。

## 静态代理

静态代理在使用时,需要定义接口或者父类,被代理对象与代理对象一起实现相同的接口或者是继承相同父类

总而言之，将目标对象作为参数传进代理对象中，对目标对象的方法进行装饰

缺点:因为代理对象需要与目标对象实现一样的接口,所以会有很多代理类,一旦接口增加方法,目标对象与代理对象都要维护

## 动态代理

代理对象,不需要实现接口

代理对象的生成,是利用JDK的API,动态的在内存中构建代理对象(需要指定创建代理对象/目标对象实现的接口的类型)

## 实例

```java
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
// 接口
interface InterfaceUserDao {
    void write();
}

// 目标对象，接口实现
class UserDao implements InterfaceUserDao {
    public void write() {
        System.out.println("write is OK");
    }
}
```

测试静态代理：

```java
// 代理对象，静态代理
class UserDaoProxy implements InterfaceUserDao {
    private InterfaceUserDao target;
    public UserDaoProxy(InterfaceUserDao target) {
        this.target = target;
    }
    public void write() {
        System.out.println("开启事务...");
        target.write();   // 目标对象的方法
        System.out.println("提交事务...");
    }
}
```


```java
UserDao target = new UserDao();
UserDaoProxy proxy = new UserDaoProxy(target);
proxy.write();
// 开启事务...
// write is OK
// 提交事务...
```

测试动态代理

```java
class ProxyFactory {

    // 维护一个目标对象
    private Object target;
    public ProxyFactory(Object target) {
        this.target=target;
    }

    // 给目标对象生成代理对象
    public Object getProxyInstance() {
        Object proxyInstance = Proxy.newProxyInstance(
                // 类加载器
                target.getClass().getClassLoader(),
                // 目标类的所有接口，目的是获取接口中的方法
                target.getClass().getInterfaces(),
                // 实现代理
                new InvocationHandler() {
                    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
                        // method为正在调用的方法
                        System.out.println("开启事务...");
                        Object result = method.invoke(target, args);
                        System.out.println("提交事务...");
                        return result;
                    }
                }
        );
        return proxyInstance;
    }
}
```

```java
InterfaceUserDao target = new UserDao();
System.out.println(target.getClass());
InterfaceUserDao proxy = (InterfaceUserDao) new ProxyFactory(target).getProxyInstance();
System.out.println(proxy.getClass());
proxy.write();
// class com.sxdt.spring.test.UserDao
// class com.sxdt.spring.test.$Proxy0
// 开启事务...
// write is OK
// 提交事务...
```