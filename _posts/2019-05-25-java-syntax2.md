---
layout: post
title: "java语法复习"
date: 2019-05-25
description: "简单介绍java语法复习"
tag: java

---

# IO

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

## Iterator

Iterator最高层 ———— hasNext() + next()

Iterator <-- Collection <-- Set <-- HashSet

Iterator <-- Collection <-- List <-- ArrayList

Map <-- HasMap


## 代码块

1. 在`类中`不加任何修饰符为构造块，构造块优先构造方法执行，每创建一个对象，构造块就执行一次

2. 在`方法中`不加任何修饰符为普通代码块，方法中代码过长，为避免变量重名，用普通代码块解决（限制变量作用域）

3. static{}为静态块，优先构造块执行，不管创建多少个对象都只在第一次创建该类对象时执行一次（加载驱动如数据库）

4. synchronized{}为同步代码块







