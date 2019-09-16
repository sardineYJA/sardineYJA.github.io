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








