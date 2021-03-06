---
layout: post
title: "Java 基础语法"
date: 2018-01-05
description: "Java语法复习"
tag: Java

---

## 基本数据类型字节数：
- char    2
- byte    1
- short   2
- int     4
- long    8
- float   4
- double  8


## 包装类，当成对象方便编程
Boolean, Character, Byte, Short, Integer, Long, Float, Double


## 访问控制修饰符：
- private    同一类内可见
- default    同一包内可见
- protected  同一包内和所有子类可见
- public     所有类可见


## 访问控制继承
- 父类中 public 的方法在子类中也必须为 public。
- 父类中 protected 的方法在子类中声明为 protected 或 public，不能声明为 private。
- 父类中 private 的方法，不能够被继承。


## 非访问修饰符：
- static
- final
- abstract
- synchronized
- transient（变量不会被序列化）
- volatile （每次被线程访问时，都强迫从共享内存中重读变量的值，当变量发生变化时强迫线程将变化值回写到共享内存。在任何时刻，两个不同的线程总看到变量的同一个值）


## 继承
- extends     类不可以多继承
- implements  接口可以多继承

- super 实现对父类成员的访问
- this  指向自己的引用

- final 声明类可以把类定义为不能继承的，即最终类
- final 用于修饰方法，该方法可继承但不能被子类重写

- 构造方法不能被重写。
- 声明为static的方法不能被重写，但是能够被再次声明


## 多态
- 必要条件：继承；重写；父类引用指向子类对象。
- 实现方法：重写；接口；抽象类和抽象方法。

- 如果一个类包含抽象方法，那么该类必须是抽象类。
- 任何子类必须重写父类的抽象方法，或者声明自身为抽象类。


## new 和 clone
- new 分配内存，调用构造函数填充对象的各个域。
- clone 分配内存，使用原对象中对应的各个域填充新对象。
- clone方法执行的是浅拷贝，深拷贝则要实现Cloneable接口。


## 接口与类的区别：
- 接口不能用于实例化对象。
- 接口没有构造方法。
- 接口中所有的方法必须是抽象方法。
- 接口不能包含成员变量，除了 static 和 final 变量。
- 接口不是被类继承了，而是要被类实现。
- 接口支持多继承。


## 数据结构
- 枚举    Enumeration
- 位集合  BitSet
- 向量    Vector
- 栈      Stack
- 字典    Dictionary
- 哈希表  Hashtable
- 属性    Properties


## 三种创建线程的方法：
- 通过实现 Runnable 接口。
- 通过继承 Thread 类本身。
- 通过 Callable 和 Future 创建线程。


## 值传递和引用传递

- 值传递（pass by value）：是指在调用函数时将实际参数复制一份传递到函数中，在函数中如果对参数进行修改，将不会影响到实际参数。

- 引用传递（pass by reference）：是指在调用函数时将实际参数的地址直接传递到函数中，在函数中如果对参数进行修改，将影响实际参数。

java 基本数据类型传递参数时是值传递 ；引用类型传递参数时是引用传递 。
对于对象来说传递的是引用的一个副本给参数。
引用数据类型分为：类，接口，数组。


## 类的实例化顺序
1. 父类静态变量   
2. 父类静态代码块
3. 子类静态变量   
4. 子类静态代码块 
5. 父类非静态变量 
6. 父类构造函数    
7. 子类非静态变量 
8. 子类构造函数  


## 代码块

1. 在`类中`不加任何修饰符{}为构造块，构造块优先构造方法执行，每创建一个对象，构造块就执行一次

2. 在`方法中`不加任何修饰符{}为普通代码块，方法中代码过长，为避免变量重名，用普通代码块解决（限制变量作用域）

3. static{}为静态块，优先构造块执行，不管创建多少个对象都只在第一次创建该类对象时执行一次（加载驱动如数据库）

4. synchronized{}为同步代码块


## 异常处理机制
Throwable-->Error和Exception：
- throws 在方法声明后面，如果抛出异常，由该方法的调用者来进行异常的处理
- throw  在方法体内，如果抛出异常，由方法体内的语句处理


## final，finalize, finally
final为关键字
finalize()为方法；在Object中进行了定义，用于在对象“消失”时，由JVM进行调用用于对对象进行垃圾回收
finally为区块标志，用于try语句中


## collection, collections
collection是结合类的上级接口,子接口有List和Set等。
collections是java.util下的一个工具类,提供一些列静态方法对集合搜索排序线程同步化等。



## 知识点

类进行序列化先实现Serializable接口，该接口没任何抽象方法只是起到一个标记作用。

boolean 类型不能转换成任何其它数据类型。

java中有指针，但是隐藏了，开发人员无法直接操作指针，由jvm来操作指针。

构造方法不能显式调用，不能当成普通方法调用，只有在创建对象的时候它才会被系统调用。

如果父类只有有参构造方法，那么子类必须要重写父类的构造方法。

当父类引用指向子类对象的时候，子类重写了父类方法和属性，访问的是父类的属性，调用的是子类的方法。

抽象类可以没有抽象方法。


重载overload实现的是编译时的多态性
重写override实现的是运行时的多态性

java使用的编码是Unicode

char 2字节可存储一个汉字

static静态方法不能被重写

static静态变量，一个类不管创建多少个对象，静态变量在内存中仅有一个拷贝

## == 和 equals()

== 基本数据类型比较的是值，引用类型（对象）比较的是地址值

equals 比较的是两个引用（对象）的字面值是不是相同



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


## 字节流

InputStream(抽象类)  <- FileInputStream : int read(byte[]b, int off, int len) 返回读取字节数

OutputStream(抽象类) <- FileOutputStream : void wirte(byte[] b, int off, int len)

```java
FileInputStream fis = new FileInputStream("D:/from.txt");
FileOutputStream fos = new FileOutputStream("D:/to.txt");
byte[] buffer = new byte[100];
while (true) {
	int byteLen = fis.read(buffer, 0, 100);
	if (byteLen == -1) {
		break;
	}
	fos.wirte(buffer, 0, byteLen);
}
fis.close();
fos.close();
```

```java
FileInputStream fis = new FileInputStream("D:/in/SxMt_Sts_02_0812110004");
DataInputStream inputStream = new DataInputStream(fis);
int read = 0;
byte[] strMsg = new byte[538];
int count = 0;
while (true) {
    read = inputStream.read(strMsg);
    if (read < 0) {
        System.out.println(read);
        break;
    }
    System.out.println(new String(strMsg));
    count++;
}
System.out.println("count = " + count);
```

## 字符流

Reader(抽象类) <- FileReader : int read(char[] b, int off, int len)

Writer(抽象类) <- FileWriter : void write(char[] b, int off, int len)

```java
FileReader fr = new FileReader("D:/from.txt");
FilWriter fw = new FIleWriter("D:/to.txt", true);  // 追加
char[] buffer = new char[100];
int temp = fr.read(buffer, 0, buffer.length);
fw.write(buffer, 0, temp);

// 字符输入处理流
BufferedReader br = new BufferedReader(new FileReader("D:/from.txt"));
line = br.readline();  // if line == null break
```



# reference

https://www.runoob.com/java/java-tutorial.html

https://www.cnblogs.com/eastday/p/8124580.html

https://www.cnblogs.com/zhoutongsheng/p/7910966.html

