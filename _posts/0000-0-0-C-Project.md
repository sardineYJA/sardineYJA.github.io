---
layout: post
title: "C++ 项目记录"
date: 2019-11-01
description: "Linux C++ 项目记录"
tag: C&C++

---

## 前言

最近需要维护C++老项目的代码，需要进行部分模块升级，oracle数据库更换成Mysql等。

记录一些笔记，方便以后复盘，代码都是Linux环境编写，运行测试，完整代码在仓库中。


## 编译的四个阶段

- 预处理：编译处理宏定义等宏命令（eg:#define），生成后缀为“.i”的文件 　　
- 编译：将预处理后的文件转换成汇编语言，生成后缀为“.s”的文件 　　
- 汇编：由汇编生成的文件翻译为二进制目标文件，生成后缀为“.o”的文件 　　
- 连接：多个目标文件（二进制）结合库函数等综合成的能直接独立执行的执行文件


## 区别

- gcc是GCC中的GUN C Compiler（C 编译器） 
- g++是GCC中的GUN C++ Compiler（C++编译器）
- gcc无法进行库文件的连接，即无法编译完成`连接`步骤
- g++则能完整编译出可执行文件（实质上g++从步骤1-3均是调用gcc完成，步骤4连接则由自己完成）


## make 使用

文件命名：makefile

```
all:
	g++ testServer.cpp  XLServer.cpp define.cpp ProcessMsg.cpp WriteLog.cpp ReadConfig.cpp Task.cpp ThreadPool.cpp -o server -std=c++11 -pthread

	g++ testClient.cpp XLClient.cpp define.cpp ProcessMsg.cpp WriteLog.cpp ReadConfig.cpp -o client -std=c++11

clean:
	rm server
	rm client
```


## string 转 char

```C++
// 如果直接打印string.c_str()，发现格式化后面部分（======）丢失
printf("------%s========\n", str.c_str());
// 果然c_str()转char*还是有些不同，下面方法转，注意将最后一个字符去掉即可
char ch[50] = {0}; 
int i;
for(i = 0; i < str.length()-1; i++)
{	// 这里-1必须去掉最后一个字符，否则格式化会出错（例：c_str()转换）
    ch[i] = str[i];
}
ch[i] = '\0';
```


## 避免同一个头文件被包含（include）多次 

```C++
// 方式一：
#ifndef  __MYSQLDB_H__
#define  __MYSQLDB_H__
... ... // 声明、定义语句
#endif

// 方式二：
#pragma once
... ... // 声明、定义语句
```

比较：

- ifndef：移植性好，编译时间较长

- pragma：编译速度提高，可以避免名字冲突，不支持跨平台，部分老版本的编译器不支持，兼容性较差



## 关于 using namespace std; 

尽量不用`using name std;`。因为命名空间std都会导出命名空间的所有名称，这与命名空间的初衷相矛盾。

可以换写：
```C++
using std::cin;
cin >> a;
// 或
std::cin >> a;
```


## detach函数和join函数

在声明一个std::thread对象之后，都可以使用detach和join函数来启动被调线程，区别在于两者是否阻塞主调线程。

- 当使用join()函数时，主调线程阻塞，等待被调线程终止，然后主调线程回收被调线程资源，并继续运行

- 当使用detach()函数时，主调线程继续运行，被调线程驻留后台运行，主调线程无法再取得该被调线程的控制权。当主调线程结束时，由运行时库负责清理与被调线程相关的资源


## list 遍历删除

list在遍历过程删除某个元素，测试时发现只有下面这种可以。

```C++
#include <list>
...
std::list< int> List;
std::list< int>::iterator itList;
for( itList = List.begin(); itList != List.end(); )
{
    if( WillDelete( *itList) )     // * 取值
    {
       List.erase( itList++);      // 这里地址必须++
    }
    else
       itList++;
}
```


## 子进程

```C++
pid_t fpid;     // fpid表示fork函数返回的值  
fpid=fork();   
if (fpid < 0)   // 创建子进程失败
    printf("error in fork!");   
else if (fpid == 0) {  
    printf("child process,id is %d/n",getpid()); // 子进程运行 
}  
else {  
    printf("parent process,id is %d/n",getpid());// 父进程运行
}  
```


## 用到.和::和：和->和?:符号的区别

1. A.B则A为对象或者结构体

2. A->B则A为指针，->是成员提取，A->B是提取A中的成员B，A只能是指向类、结构、联合的指针

3. ::是作用域运算符，A::B表示作用域A中的名称B，A可以是名字空间、类、结构

4. ：一般用来表示继承

5. ?:三目运算符如 表达式 ? 表达式 : 表达式


## 预定义宏
```C++
__LINE__ : 6（行号）

__FILE__ : test.cpp（文件名）

__DATE__ : Feb 28 2011

__TIME__ : 18:52:48
```


## 动态链接

链接库：`-I/home/ismg5-64/LIB/include -L/home/ismg5-64/LIB/lib`

> error while loading shared libraries: libXXX.so.X: cannot open shared object file: No such file

1. 在/etc/ld.so.conf.d/目录下加入的任何以.conf
2. 将目录写进文件：/.../lib
3. 命令：sudo ldconfig



## 字节序

- 主机字节顺序HBO（Host Byte Order）采用小头序（little-endian），从低到高的顺序存储。
低位字节排放在内存的低地址端，高位地址排放在高位地址端。（符合人类思维）

- 网络字节顺序NBO（Network Byte Order）采用大头序（big-endian），从高到低的顺序存储。
高位字节排放在内存的低地址端，低位地址排放在高位地址端。（最为直观）
TCP/IP协议定义网络字节为big-endian。

- htons 把 unsigned short 类型从主机序转换到网络序
- htonl 把 unsigned long 类型从主机序转换到网络序

- ntohs 把 unsigned short 类型从网络序转换到主机序
- ntohl 把 unsigned long 类型从网络序转换到祝继续



# 错误

> terminate called after throwing an instance of 'std::system_error'
  what():  Enable multithreading to use std::thread: Operation not permitted
 已放弃(吐核)

g++ 编译加：-pthread or -lpthread


> error This file requires compiler and library support for the ISO C++ 2011 standard. This support is currently experimental, and must be enabled with the -std=c++11 or -std=gnu++11 compiler options.

g++ 编译加：-std=c++11 or -std=gnu++11


# reference


list 遍历删除：
http://www.cppblog.com/Herbert/archive/2008/12/27/70479.html

类的成员函数作为线程函数：
https://blog.csdn.net/u013093948/article/details/53584461

写日志：
https://blog.csdn.net/oXiaoErBuYu123456/article/details/67632226


select函数详解：
https://www.cnblogs.com/alantu2018/p/8612722.html

