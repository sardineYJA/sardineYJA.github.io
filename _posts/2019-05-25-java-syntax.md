---
layout: post
title: "java语法复习"
date: 2019-05-25
description: "简单介绍java语法复习"
tag: Java

---

## 基本数据类型：
char    2
byte    1
short   2
int     4
long    8
float   4
double  8

String 是引用类型，底层用char数组实现。


## 包装类，当成对象方便编程
Boolean, Character, Byte, Short, Integer, Long, Float, Double


## 访问控制修饰符：
private    同一类内可见
default    同一包内可见
protected  同一包内和所有子类可见
public     所有类可见


类进行序列化先实现Serializable接口，该接口没任何抽象方法只是起到一个标记作用。


## 访问控制继承
1. 父类中 public 的方法在子类中也必须为 public。
2. 父类中 protected 的方法在子类中声明为 protected 或 public，不能声明为 private。
3. 父类中 private 的方法，不能够被继承。

## 非访问修饰符：
static
final
abstract
synchronized
transient（变量不会被序列化）
volatile （每次被线程访问时，都强迫从共享内存中重读变量的值，当变量发生变 化时强迫线程将变化值回写到共享内存。在任何时刻，两个不同的线程总看到变量的同一个值）

## 继承
extends     类不可以多继承
implements  接口可以多继承

super 实现对父类成员的访问
this  指向自己的引用

final 声明类可以把类定义为不能继承的，即最终类
final 用于修饰方法，该方法可继承但不能被子类重写

构造方法不能被重写。
声明为static的方法不能被重写，但是能够被再次声明


## 多态
必要条件：继承；重写；父类引用指向子类对象。
实现方法：重写；接口；抽象类和抽象方法。

如果一个类包含抽象方法，那么该类必须是抽象类。
任何子类必须重写父类的抽象方法，或者声明自身为抽象类。


## new 和 clone
new 分配内存，调用构造函数填充对象的各个域
clone 分配内存，使用原对象中对应的各个域填充新对象
clone方法执行的是浅拷贝，深拷贝则要实现Cloneable接口

## 接口与类的区别：
接口不能用于实例化对象。
接口没有构造方法。
接口中所有的方法必须是抽象方法。
接口不能包含成员变量，除了 static 和 final 变量。
接口不是被类继承了，而是要被类实现。
接口支持多继承。


## 数据结构
枚举    Enumeration
位集合  BitSet
向量    Vector
栈      Stack
字典    Dictionary
哈希表  Hashtable
属性    Properties


## 三种创建线程的方法：
通过实现 Runnable 接口；
通过继承 Thread 类本身；
通过 Callable 和 Future 创建线程。

## List三个子类
ArrayList 底层结构是数组，查询快，增删慢
LinkedList 底层结构是链表，增删快，查询慢
voctor 底层是数组，线程安全，增删慢，查询慢


## 知识点
boolean 类型不能转换成任何其它数据类型。

值传递（pass by value）：是指在调用函数时将实际参数复制一份传递到函数中，在函数中如果对参数进行修改，将不会影响到实际参数。

引用传递（pass by reference）：是指在调用函数时将实际参数的地址直接传递到函数中，在函数中如果对参数进行修改，将影响实际参数。

java 基本数据类型传递参数时是值传递 ；引用类型传递参数时是引用传递 。
对于对象来说传递的是引用的一个副本给参数。
引用数据类型分为：类，接口，数组。

String不能被继承，String类有final修饰符，而final修饰的类是不能被继承的。
平常定义的String str=”a”;（引用）其实和String str=new String(“a”)（构建新对象）还是有差异的。


String str=”aaa”,与String str=new String(“aaa”)不一样的。因为内存分配的方式不一样。
第一种，创建的”aaa”是常量，jvm都将其分配在常量池中。
第二种，创建的是一个对象，jvm将其值分配在堆内存中。


1. String 字符串常量(final修饰，不可被继承)，String是常量，当创建之后即不能更改。
2. StringBuffer 字符串变量（线程安全）,其也是final类别的，不允许被继承，其中的绝大多数方法都进行了同步处理。
3. StringBuilder 字符串变量（非线程安全），方法除了没使用synch修饰以外基本与StringBuffer一致，速度更快。


final为关键字；
finalize()为方法；在Object中进行了定义，用于在对象“消失”时，由JVM进行调用用于对对象进行垃圾回收。
finally为区块标志，用于try语句中；

collection是结合类的上级接口,子接口有List和Set等。
Collections是java.util下的一个工具类,提供一些列静态方法对集合搜索排序线程同步化等。


ArrayList和LinkedList都实现了List接口：
ArrayList是基于索引的数据接口，以O(1)时间复杂度对元素进行随机访问。
LinkedList是以元素列表的形式存储它的数据，链接在一起，在这种情况下，查找某个元素的时间复杂度是O(n)，插入，添加，删除操作速度更快。


类的实例化顺序：
父类静态变量
父类静态代码块
子类静态变量
子类静态代码块
父类非静态变量
父类构造函数
子类非静态变量
子类构造函数

## 代码块

1. 在`类中`不加任何修饰符为构造块，构造块优先构造方法执行，每创建一个对象，构造块就执行一次

2. 在`方法中`不加任何修饰符为普通代码块，方法中代码过长，为避免变量重名，用普通代码块解决（限制变量作用域）

3. static{}为静态块，优先构造块执行，不管创建多少个对象都只在第一次创建该类对象时执行一次（加载驱动如数据库）

4. synchronized{}为同步代码块


java中有指针，但是隐藏了，开发人员无法直接操作指针，由jvm来操作指针。

构造方法不能显式调用，不能当成普通方法调用，只有在创建对象的时候它才会被系统调用。

如果父类只有有参构造方法，那么子类必须要重写父类的构造方法。

当父类引用指向子类对象的时候，子类重写了父类方法和属性，访问的是父类的属性，调用的是子类的方法。

抽象类可以没有抽象方法。

进程间通信：管道，FIFO(命名管道)，消息队列，信号量，共享内存

重载overload实现的是编译时的多态性
重写override实现的是运行时的多态性

java使用的编码是Unicode

char 2字节可存储一个汉字

static静态方法不能被重写

static静态变量，一个类不管创建多少个对象，静态变量在内存中仅有一个拷贝

== 是数值是否相同，equals是对象包括hash是否相同

String s ="123"; s = s+"456";对象没有改变，只是s指向新的String对象了。以往如此，会引起内存开销。


## 异常处理机制
Throwable-->Error和Exception
Error 表示程序本身无法克服和恢复的问题
Exception 表示程序能够克服和恢复的问题


throws 在方法声明后面，如果抛出异常，由该方法的调用者来进行异常的处理
throw  在方法体内，如果抛出异常，由方法体内的语句处理


## 接口特点：
1. 接口中声明全是public static final修饰的常量
2. 接口中所有方法都是抽象方法
3. 接口是没有构造方法的
4. 接口也不能直接实例化
5. 接口可以多继承

Java中异常：编译时异常和运行时异常

线程同步的方法：
1. wait():让线程等待。将线程存储到一个线程池中。
2. notify()：唤醒被等待的线程。通常都唤醒线程池中的第一个。让被唤醒的线程处于临时阻塞状态。
3. notifyAll(): 唤醒所有的等待线程。将线程池中的所有线程都唤醒。


## nio 和 bio:
BIO（Blocking I/O）同步阻塞I/O处理：一个客户端请求，服务器端分配一个线程（以及内存空间）处理。
NIO（Non-blocking I/O) 同步非阻塞的I/O模型：一个有效请求对于一个线程，当连接没有数据时，是没有工作线程来处理的。
NIO2.0，也就是AIO（Asynchronous 异步非阻塞IO）

BIO是面向流的，NIO是面向缓冲区的。
BIO方式适用于连接数目比较小且固定的架构，对服务器资源要求比较高，并发局限于应用中，但程序直观简单易理解。
NIO方式适用于连接数目多且连接比较短（轻操作）的架构，比如聊天服务器，并发局限于应用中，编程比较复杂。

BIO：InputStream、OutputStream、Writer、Reader
NIO：Channels, Buffers, Selectors

同步和异步是针对程序和内核的交互而言，同步指用户进程触发IO操作并等待或者轮询的去查看IO操作是否就绪，而异步指用户进程触发IO操作以后便开始做自己的事情，当IO操作已经完成的时候会得到IO完成的通知。
阻塞和非阻塞是针对于进程在访问数据的时候，阻塞方式下读取或者写入函数将一直等待，而非阻塞方式下，读取或者写入函数会立即返回一个状态值。


## Map（key-value对）
HashTable:
底层数组+链表实现，无论key还是value都不能为null，线程安全。
实现线程安全的方式是在修改数据时Synchronize锁住整个HashTable，效率低，ConcurrentHashMap做了相关优化。
Hashtable继承自Dictionary类

HashMap:
底层数组+链表实现，可以存储null键和null值，线程不安全。
在多线程环境中，需要手动实现同步机制。
HashMap继承自AbstractMap类。

ConcurrentHashMap:
底层采用分段的数组+链表实现，线程安全。
ConcurrentHashMap允许多个修改操作并发进行，其关键在于使用了锁分离技术。

## 反射
JAVA反射机制是在运行状态中，对于任意一个类，都能够知道这个类的所有属性和方法；对于任意一个对象，都能够调用它的任意一个方法和属性；这种动态获取的信息以及动态调用对象的方法的功能称为java语言的反射机制。
获取Class对象的三种方式
1. Object ——> new 类名().getClass();
2. 任何数据类型（包括基本数据类型）都有一个“静态”的class属性，类名.class;
3. 通过Class类的静态方法：Class.forName（String  className）(常用)


## 请求连接：
C   ------SYN----->  S
C   <---SYN,ACK----  S
C   ------ACK----->  S

## 断开连接：
C   -----FIN----->  S
C   <-----ACK-----  S
C   <-----FIN-----  S
C   -----ACK----->  S



## 图形界面
AWT和Swing之间的区别：
1. AWT 是基于本地方法的C/C++程序，运行速度较快；Swing是基于AWT的Java程序，运行速度较慢。
2. AWT的控件在不同的平台可能表现不同，而Swing在所有平台表现一致。



# 框架
SSH:Spring, Struts, Hibernate
SSM:Spring, SpringMVC, MyBatis



# 参考
1. https://www.runoob.com/java/java-tutorial.html

2. https://www.cnblogs.com/eastday/p/8124580.html

3. https://www.cnblogs.com/zhoutongsheng/p/7910966.html

