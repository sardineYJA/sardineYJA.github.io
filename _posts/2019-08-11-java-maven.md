---
layout: post
title: "Maven"
date: 2019-08-11
description: "简单介绍Maven"
tag: Java

---

# Maven知识

Maven会自动添加相应的jar包，而jar包会先在本地仓库中查找，如果找不到，则会去中央仓库(网络上)去进行下载

## Maven作用：
1. 添加第三方jar包
2. 添加jar包之间的依赖
3. 处理jar包之间的冲突
4. 项目分布式部署

## 项目构建：
1. 清理：将以前编译得到的旧class字节码删除
2. 编译：将java源文件编译成.class字节码
3. 测试：自动测试，自动调用junit程序
4. 报告：记录测试程序执行的结果
5. 打包：动态WEB工程打war包，java工程打jar包
6. 安装：将打包得到的文件复制到仓库中的指定位置
7. 部署：将动态WEB工程生成的war包复制到服务器的指定目录下

## Maven自动化构建：
1. POM（Project Object Model）
2. 约定的目录结构
3. 坐标(groupId<公司+项目名>, artifactId<项目模块>, version<版本>)
4. 依赖管理
5. 仓库管理
6. 生命周期
7. 插件和目标
8. 继承
9. 聚合

## 安装配置

1. 下载地址：https://maven.apache.org/download.cgi

2. 解压后配置系统变量

```
MAVEN_HOME=E:\apache-maven-3.6.1
PATH加上：%MAVEN_HOME%\bin
```

3. 测试`mvn -v`

4. 修改本地仓库位置，默认的本地仓库:`~/.m2/repository`，删除仓库

5. 修改settings.xml，复制到`~/.m2/`目录下

```xml
修改<localRepository>D\:maven-repository</localRepository>
```

6. 如觉得中央仓库下载jar很慢，可换阿里云，在settings.xml的mirrors添加子节点：

```xml
<mirror>  
    <id>nexus-aliyun</id>  
    <mirrorOf>central</mirrorOf>    
    <name>Nexus aliyun</name>  
    <url>http://maven.aliyun.com/nexus/content/groups/public</url>  
</mirror> 
```

7. 将jar包导入到仓库

```
mvn install:install-file \
	-Dfile=D:\ojdbc6-11.2.0.3.jar \
	-DgroupId=com.oracle \
	-DartifactId=ojdbc6 \
	-Dversion=11.2.0.3 -Dpackaging=jar
```


## 命令
mvn clean           清理
mvn compile         编译主程序
mvn test-compile    编译测试程序
mvn test            执行测试
mvn package         打包
mvn install         安装
mvn site            生成站点
mvn deploy          部署

## 依赖范围
坐标：`<scope>xxx</scope>`
### compile
1. main目录下的Java代码`可以`访问这个范围的依赖
2. test目录下的Java代码`可以`访问这个范围的依赖
3. 部署到Tomcat服务器上运行时`要`放在WEB-INF的lib目录下

### test
1. main目录下的Java代码`不能`访问这个范围的依赖
2. test目录下的Java代码`可以`访问这个范围的依赖
3. 部署到Tomcat服务器上运行时`不会`放在WEB-INF的lib目录下

### provided
1. main目录下的Java代码`可以`访问这个范围的依赖
2. test目录下的Java代码`可以`访问这个范围的依赖
3. 部署到Tomcat服务器上运行时`不会`放在WEB-INF的lib目录下


## 依赖的排除
```xml
<exclusions>
	<exclusion>
		<groupId>xxx</groupId>
		<artifactId>xxx</artifactId>
	</exclusion>
</exclusions>
```


## 统一配置方式
```xml
<properties>
	<xxx.version>4.0.0.RELEASE</xxx.version>
</properties>
......
	<version>${xxx.version}</version>
```


## Maven生命周期
1. Clean 生命周期
2. Site 生命周期
3. Default 生命周期


## 继承
```xml
<parent>
	......
	<!-- 指定从当前子工程的pom.xml文件出发，查找父工程的pom.xml的路径 -->
	<relativePath>../Parent/pom.xml</relativePath>
</parent>
```


