---
layout: post
title: "IDE 常见问题及解决"
date: 2018-08-01
description: "关于常用IDE软件的使用"
tag: Other

---

# JAVA

## JDK目录
jdk1.8和1.7安装会有两个路径jdk和jre：

jdk的全称是：java development kit 

jre的全称是：java runtime environment

jdk安装目录下的jre可以看做是一个私有的jre环境，而外部独立的jre文件可以看做是一个共有的jre环境，这两者的本质实际上是相同的。

jdk11,12安装则只有jdk，jdk下也没有jre:

手动生成JRE：以管理员身份运行CMD，使用命令`bin\jlink.exe --module-path jmods --add-modules java.desktop --output jre`


# Sublime

## 在线安装 sftp

Ctrl + Shift + p 命令面板

输入 Install Package 回车

输入 sftp 回车 安装


## 离线安装 

安装 Package Control: https://github.com/wbond/package_control

1. 把下载好的zip包解压，重命名为 Package Control 文件夹

2. 打开Sublime3，菜单->Preferences->Browse Packages...然后Package Control文件夹放到该目录

3. 重启Sublime3,如果菜单->Preferences有Package Setting和Package Control就说明安装成功

4. Ctrl+Shift+p输入install选中Install Package回车就可以安装插件

安装 sftp:



## 打开远程目录

View --> Side bar 打开左侧栏

桌面 --> 新建文件夹 test

File --> Open Folder --> 选择 test

右键test --> SFTP/FTP --> Map to Remote

```json
"upload_on_save": true,

"host": "172.16.7.67",
"user": "sxit",
"password": "sxit",
"remote_path": "/home/sxit/Project_Folder/",
```

右键test --> SFTP/FTP --> Download Folder


# notepad++

## 将 tab 变成 2 个空格

设置- > 首选项- > 语言- > Tab Settings- > Replace by space


## CRLF 替换 LF

每一行的结尾符号，Windows 下默认为 CRLF，而 Unix 下默认为 LF：

1. Search -> Replace（或者 Ctrl+H）
2. Find what: \r\n
3. Replace with: \n
4. 将 Search mode 选为 Extended
5. Replace All



# eclipse

## eclipse的Maven项目更换jdk版本

先修改eclipse的jdk

window > preference > java > installed JRES > add > Standard VM > next > directory > jdk目录 > 勾选新的jdk > apply

修改项目的jdk

1. 项目右键 > Build Path > Configure Build Path > 
2. java Build Path > Libraries > Edit > Alternate JRE > 新的JDK
3. java Build Path > Order and Export > 勾选新的JDK
4. java Compiler > 勾选jdk版本
5. project Facets > java > 勾选jdk版本（我的eclipse没有此步骤）

修改pom.xml

将打包依赖的：maven-compiler—plugin修改相应的版本

右键 > Maven > Update Project

(当时我测试的是1.8换成1.7的)


## 下载TortoiseSVN：

地址：https://www.visualsvn.com/visualsvn/download/tortoisesvn/

语言包：http://tortoisesvn.net/downloads.html 


##  eclipse安装SVN

1. Eclipse --> Help --> Install New Software --> add
2. Name : SVN
3. Location：http://subclipse.tigris.org/update_1.10.x
4. 直接安装

打开SVN资源库

Window --> Show view --> other --> SVN资源库 --> 新建 --> 新建资源库位置

下载

project右键 --> 检出为 --> 做为工作空间中的项目检出

上传

project右键 --> Team --> Show Project --> 选择repository类型SVN --> ...

project右键 --> Team --> 提交

从服务器更新代码

project右键 --> Team --> 与资源库同步


## eclipse 添加本地 maven 仓库

window --> Preferences --> Installtions --> add (选择maven安装目录，不是仓库目录) --> 打钩

IDEA 好像自动识别加载 本地 maven 仓库


# IDEA

## IDEA 安装 SVM

1. 安装SVN是需要勾选command line client tools，否则没有svn.exe

2. file --> settings --> subversion --> 加上目录：E:\TortoiseSVN\bin\svn.exe

3. 关闭项目退到首页 --> check out from version control


## IDEA中SVN项目不同颜色含义

- 白色，加入，已提交，无改动

- 蓝色，加入，已提交，有改动

- 绿色，已经加入控制暂未提交

- 红色，未加入版本控制

- 灰色：版本控制已忽略文件


## 更换 jdk

File --> Settings --> Build,Execution,Deployment --> Compiler --> Java Compiler

Fiel --> Project Structure --> Project 以及 Modules 以及 SDKs


## IDEA 快捷键 

自动生成代码

1. Ctrl + Alt + v 变量提取

2. mylist.for + Tap 列表循环

3. Ctrl + Alt + o 优化布局已导入的包

4. Ctrl + Alt + T 生成try/catch或循环

5. Ctrl + o 重写方法

6. Ctrl + i 实现方法

7. Alt + Insert 生成Get/Set方法等


查询

1. Ctrl + p 方法参数提示

2. Ctrl + q 当前方法声明

3. Ctrl + 双击 或 Ctrl + Alt + b 跳转到类的实现

4. 全局搜索字符串：Edit --> Find in path


Debug

F8  单步

F7  步入函数

F9  执行到断点

Shift + F8 跳出函数


## src资源文件xml编译

在练习spring时，需要在src目录下创建xml文件。

如果使用的是Eclipse，Eclipse的src目录下的xml等资源文件在编译的时候会自动打包进输出到classes文件夹。Hibernate和Spring有时会将配置文件放置在src目录下，编译后要一块打包进classes文件夹，所以存在着需要将xml等资源文件放置在源代码目录下的需求。

IDEA的maven项目中，默认src目录下的xml等资源文件并不会在编译的时候一块打包进classes文件夹，而是直接舍弃掉。

如下：在IDEA是无法读取到src/applicationContext.xml的

```java
// 实例化IOC对象
ApplicationContext ctx = new ClassPathXmlApplicationContext("applicationContext.xml");
```

解决一：建立src/main/resources文件夹，将xml等资源文件放置到这个目录中。maven工具默认在编译的时候，会将resources文件夹中的资源文件一块打包进classes目录中。

解决二：pom文件增加下面内容，将xml文件放到src/main/java目录下

```xml
<build>
    <resources>
        <resource>
            <directory>src/main/java</directory>
            <includes>
                <include>**/*.xml</include>
            </includes>
        </resource>
    </resources>
</build>
```

`<directory>src/main/java</directory>`资源文件的路径

`<include>**/*.xml</include>`需要编译打包的文件类型是xml文件，如果有其它资源文件也需要打包，可以修改或添加通配符



## 依赖识别识别

依赖加入范围：`<scope>provided</scope>`，无法识别

原因是：IDEA默认下是不加载pom下的provided依赖的，而Eclipse是支持的。

Run/Debug Configuration --> 勾选 with "provided" scope


## jdk 自动变成1.5

maven的pom.xml文件中未配置jdk版本导致。当未配置jdk版本时，一旦pom文件发生变化，Java Compiler和Language level会自动变回到原来的默认1.5版本。

固定1.8
```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <configuration>
                <source>1.8</source>
                <target>1.8</target>
            </configuration>
        </plugin>
    </plugins>
</build>
```
