---
layout: post
title: "JVM 原理篇"
date: 2018-09-16
description: "JVM"
tag: Java

---

# JVM

JVM = ClassLoader + Execution Engine + Runtime Data Area

![png](/images/posts/all/JVM体系结构.jpg)

Main()方法是程序的起点，他被执行的线程初始化为程序的初始线程，程序中其他的线程都由他来启动。

Java中的线程分为两种：守护线程 （daemon）和普通线程（non-daemon）。守护线程是Java虚拟机自己使用的线程，比如负责垃圾收集的线程就是一个守护线程。

Java代码编译是由Java源码编译器来完成

Java字节码的执行是由JVM执行引擎来完成

每个Java程序使用内存的受限于JVM的启动参数决定的



# ClassLoader

ClassLoader负责class文件的加载，至于它是否可以运行，则由Execution Engine决定

## class 装载方式

ClassLoader 有两种装载class的方式 （时机）：
- 隐式：运行过程中，碰到new方式生成对象时，隐式调用 ClassLoader 到 JVM
- 显式：通过 Class.forName() 动态加载

## class 加载过程

类的加载过程采用双亲委托机制。除了顶层的Bootstrap class loader启动类加载器外，其余的类加载器都应当有自己的父类加载器。子类加载器和父类加载器不是以继承（Inheritance）的关系来实现，而是通过组合（Composition）关系来复用父加载器的代码。

双亲委派模型的工作过程为：

- 当前 ClassLoader 首先从自己已经加载的类中查询是否此类已经加载，如果已经加载则直接返回原来已经加载的类。每个类加载器都有自己的加载缓存，当一个类被加载了以后就会放入缓存，等下次加载的时候就可以直接返回了

- 当前 classLoader 的缓存中没有找到被加载的类的时候，委托父类加载器去加载，父类加载器采用同样的策略，首先查看自己的缓存，然后委托父类的父类去加载，一直到 Bootstrap ClassLoader。当所有的父类加载器都没有加载的时候，再由自身的类加载器加载，并将其放入它自己的缓存中，以便下次有加载请求的时候直接返回


## 自底向上检查

1. 启动类加载器（Bootstrap）C++

2. 扩展类加载器（Extension）Java

3. 应用程序类加载器（App）Java，也叫系统类加载器，加载当前应用的classpath的所有类

4. 用户自定义加载器 Java.lang.ClassLoader的子类，用户可以定制类的加载方式

![png](/images/posts/all/ClassLoader内部流程.jpg)



# Execution Engine

执行引擎：执行字节码，或者执行本地方法。



# Runtime Data Area

JVM Runtime Area 其实就是指 JVM 在运行期间，其对JVM内存空间的划分和分配。

所有程序都被加载到运行时数据区域中，不同类别存放在 Heap Area, Stack Area, Native Method Stack, PC Register, Method Area


## PC Register

- 线程私有，就是一个指针，指向方法区中的方法字节码（用来存储指向下一条指令的地址）
- 由执行引擎读取下一条指令，是一个非常小的内存空间，几乎可以忽略不记


## Native Method Stack

- 线程私有

- Native Method Stack 为虚拟机使用到的Native方法服务，而 Java Stack 为虚拟机执行Java方法服务

- 登记 native 方法，在 Execution Engine 执行时加载 native libraries。


## Java Stack

- 线程私有，生命期是跟随线程的生命期，线程结束栈内存也就释放，对于栈来说不存在垃圾回收问题

- 栈内存：基本类型的变量、实例方法、引用类型变量

- 栈分为3个部分：基本类型变量区、执行环境上下文、操作指令区(存放操作指令)。

每个方法在执行的同时都会创建一个栈帧（Stack Frame）:

![png](/images/posts/all/JVM虚拟机栈.png)

每个线程里面都是顺序执行的，里面的所有程序的执行都在栈帧里，若一段代码调用一个方法就会产生一个新的栈帧压到栈里去。

- StackOverflowError：如果线程请求的栈深度大于虚拟机所允许的深度，将抛出 StackOverflowError。

- OutOfMemoryError：如果虚拟机栈可以动态扩展，如果扩展时无法申请到足够的内存，将抛出 OutOfMemoryErro。



## Method Area

- 线程共享，通常用来保存装载的类的元结构信息，常量，静态变量。

- Method Area 别名叫 Non-Heap(非堆)。

- 运行时常量池（Runtime Constant Pool）是方法区的一部分（6版本及以前）。



## Heap Area

- 线程共享，一个JVM实例只存在一个堆内存

- 堆内存逻辑上分为三部分：新生+养老+永久

永久区是常驻内存区域，用于存放JDK自身携带的 Class, Interface 的元数据，即存储的是运行环境必须的类信息，被装载进此区域的数据时不会被垃圾回收器收掉的，关闭 JVM 才会释放此区域所占用的内存

![png](/images/posts/all/Heap堆内存逻辑划分.jpg)

new Test() --> Eden Space

当对象越来越多时，Eden Space即将满，然后启动 GC --> GC 后没被回收的到 Survivor 0 Space

Survivor 0 Space 即将满，然后启动 GC --> GC 后没被回收的到 Survivor 1 Space

Survivor 1 Space 即将满，然后启动 GC --> GC 后没被回收的到 Tenure Generation Space


Java7 Heap

![png](/images/posts/all/Heap-java7.jpg)

Java8 Heap

![png](/images/posts/all/Heap-java8.jpg)

Java8 中持久代的空间被彻底地删除，被元空间的区域所替代，元空间并不在虚拟机中，而是使用本地内存


测试：`-Xms8m -Xmx8m -XX:+PrintGCDetails`

```java
// java虚拟机可以使用的最大内存
long maxMemory = Runtime.getRuntime().maxMemory();
// 返回java虚拟机的内存总量
long totalMemory = Runtime.getRuntime().totalMemory();
System.out.println("maxMemory=" + maxMemory + "Byte," + (maxMemory/1024/1024) + "MB");
System.out.println("totalMemory=" + totalMemory + "Byte," + (totalMemory/1024/1024) + "MB");
```



# 总结 

## 存储

- Method Area : 所有的class和static变量，线程共享

- Heap Area: 对象实例，数组，线程共享

- Stack Area : 基本类型，方法，对象引用，线程私有


- java6 运行时常量池（包含字符串常量池）在方法区; 而Hotspot虚拟机对方法区的实现在永久代

- java7 字符串常量池在 Heap Area; 而运行时常量池还在方法区，即在hotspot永久代

- java8 去掉永久代，方法区的实现在 Metaspace；字符串常量还在堆，运行时常量还在方法区 



## 参数

* -Xms 初始的Heap的大小，默认为物理内存的1/64

* -Xmx 最大Heap的大小，默认为物理内存的1/4 (新生代+老年代)

* -Xss 规定每个线程堆栈的大小，一般情况下256K足够，影响进程中并发线程数大小

* -Xmn 设置年轻代内存大小

* -XX:PermSize 分配（非堆）初始内存，默认为物理内存的1/64

* -XX:MaxPermSize 分配（非堆）最大内存，默认为物理内存的1/4

* -XX:MaxMetaspaceSize 元空间大小

* -XX:+PrintGCDetails 输出详细的GC处理日志

* -XX:+PrintGCApplicationStoppedTime

* -XX:+PrintGCTimeStamps GC时间戳

* -XX:MaxTenuringThreshold 晋升老年代的年龄阀值




## 解释

java的垃圾回收器在内存使用达到 -Xms 值的时候才会开始回收

虚拟机栈使用的空间 = 内存 - Xmx（最大堆容量）- MaxPermSize（最大方法区容量）- 本地方法栈

Heap 越大可以供程序申请的内存空间越少，虚拟机栈越少（线程数量越少），堆内存存储了对象，称GC堆，我们增加-Xmx 只是增加了GC堆的大小，正真执行程序的内存空间反而小了

对于高并发，创建对象不多的项目，可以降低Xmx的配置，结合 Xms 设定堆范围 -Xms256m -Xmx512m 

对于低并发，创建对象多的项目，（数据处理型的）可以适当提高 Xmx（对象和数组是存放到Heap内的，栈帧中其实只存了对象地址，所以不存在爆的情况）




# 垃圾回收

## GC

引用标记无法解决双端引用

Minor GC : 清理年轻代内存（Eden和Survivor），Eden区清空，采用copying算法

Major GC : 清理老年代，采用标记清除(Mark-Sweep),清除标记未使用，标记整理(Mark-Compact)标记使用的并整理位置

Full GC ： 清理整个堆空间（年轻代和老年代）



## GC 处理日志

> java.lang.OutOfMemoryError: Java heap space

-Xmx12m -XX:+PrintGCDetails

```
[GC (Allocation Failure) [PSYoungGen: 3072K->495K(3584K)] 3072K->1392K(11776K), 0.0024608 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
[GC (Allocation Failure) [PSYoungGen: 2375K->511K(3584K)] 3272K->1771K(11776K), 0.0019005 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
[GC (Allocation Failure) [PSYoungGen: 511K->495K(3584K)] 1771K->1763K(11776K), 0.0013171 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
[Full GC (Allocation Failure) [PSYoungGen: 495K->0K(3584K)] [ParOldGen: 1268K->1365K(6144K)] 1763K->1365K(9728K), [Metaspace: 3301K->3301K(1056768K)], 0.0229571 secs] [Times: user=0.03 sys=0.02, real=0.02 secs] 
[GC (Allocation Failure) [PSYoungGen: 0K->0K(3584K)] 1365K->1365K(11776K), 0.0007629 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
[Full GC (Allocation Failure) [PSYoungGen: 0K->0K(3584K)] [ParOldGen: 1365K->1335K(8192K)] 1365K->1335K(11776K), [Metaspace: 3301K->3301K(1056768K)], 0.0124997 secs] [Times: user=0.03 sys=0.00, real=0.01 secs]

Heap
 PSYoungGen      total 3584K, used 148K [0x00000000ffc00000, 0x0000000100000000, 0x0000000100000000)
  eden space 3072K, 4% used [0x00000000ffc00000,0x00000000ffc253c8,0x00000000fff00000)
  from space 512K, 0% used [0x00000000fff80000,0x00000000fff80000,0x0000000100000000)
  to   space 512K, 0% used [0x00000000fff00000,0x00000000fff00000,0x00000000fff80000)
 ParOldGen       total 8192K, used 1335K [0x00000000ff400000, 0x00000000ffc00000, 0x00000000ffc00000)
  object space 8192K, 16% used [0x00000000ff400000,0x00000000ff54dd58,0x00000000ffc00000)
 Metaspace       used 3340K, capacity 4500K, committed 4864K, reserved 1056768K
  class space    used 360K, capacity 388K, committed 512K, reserved 1048576K
```

### 解析：[PSYoungGen: 511K->495K(3584K)] 1771K->1763K(11776K), 0.0013171 secs]

PSYoungGen : 新生代使用的是多线程垃圾收集器Parallel Scavenge

垃圾收集之前新生代占用空间 511K

垃圾收集之后新生代的空间 495K (新生代又细分为一个Eden区和两个Survivor区,Minor GC之后Eden区为空，495K就是Survivor占用的空间)

整个年轻代的大小 3584K

垃圾收集之前（1771K）与之后（1763K）Java堆的大小（总堆11776K，堆大小包括新生代和年老代）

垃圾收集过程所消耗的时间 0.0013171 secs



### 解析：[Times: user=0.03 sys=0.00, real=0.01 secs] 

- user : 用户模式 GC 占用的 CPU 时间 

- sys : 消耗系统态cpu时间

- real : 实际时间 (GC 是单线程，real time =user+system) (GC 是多线程，real < user)


### 解析：[Full GC (Allocation Failure) [PSYoungGen: 495K->0K(3584K)] [ParOldGen: 1268K->1365K(6144K)] 1763K->1365K(9728K), [Metaspace: 3301K->3301K(1056768K)]


Full GC 表示执行全局垃圾回收

[PSYoungGen: 495K->0K(3584K)] 新生代空间信息

[ParOldGen: 1268K->1365K(6144K)] 年老代空间信息

1763K->1365K(9728K) 整个堆空间信息

[Metaspace: 3301K->3301K(1056768K)] 元空间信息



# OutOfMemoryError

> java.lang.OutOfMemoryError: Java heap space

因为对象实例存储在heap中，设置：-Xmx12m

```java
public class OOM {
    static final int SIZE=2*1024*1024;
    public static void main(String[] args) {
        int[] i = new int[SIZE];
    }
}
```


> java.lang.OutOfMemoryError: StackOverflowError

因为变量和方法存储在stack中

Java Stack 和 Native Stack 溢出

```java
public void intAdd() {
	i++;
	intAdd();
}
```




> java.lang.OutOfMemoryError: GC overhead limit exceeded

耗尽了所有的可用内存, GC也清理不了


> java.lang.OutOfMemoryError: PermGen space

永久代(Permanent Generation) 内存区域已满



> java.lang.OutOfMemoryError: Metaspace 

元数据区(Metaspace) 已被用满



> java.lang.OutOfMemoryError: Unable to create new native thread

程序创建的线程数量已达到上限值



> java.lang.OutOfMemoryError: Out of swap space

交换空间(swap space,虚拟内存) 不足,是由于物理内存和交换空间都不足



> java.lang.OutOfMemoryError: Requested array size exceeds VM limit

创建的数组长度超过限制


# reference

《深入理解Java虚拟机》第2版

https://www.jianshu.com/p/6c875f0e7272?from=timeline&isappinstalled=0

https://blog.csdn.net/baidu_21179881/article/details/87979763

https://blog.csdn.net/lxlmycsdnfree/article/details/78356704

https://blog.csdn.net/renfufei/article/details/78178757



