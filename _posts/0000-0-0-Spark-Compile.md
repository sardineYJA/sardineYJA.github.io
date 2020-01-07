---
layout: post
title: "Spark 源码编译"
date: 2019-09-26
description: "Spark 源码编译"
tag: Spark

---


# Windows 下 Spark 编译

1. 下载（Source Code）：https://spark.apache.org/downloads.html

2. IDEA 导入 -> Import Project -> Import project from external model -> Maven -> JDK1.8 -> (其他看情况)

3. 本人下载测试 spark-2.4.4，项目名为 spark-parent_2.11 (自动生成)

4. 对应版本Scala SDK：spark-parent_2.11 对应 scala 2.11

5. File -> Project Structure中 -> Global Libraries，点击+号，选择正确的scala版本

6. Maven 导入依赖，报错：找不到下面两项定义，加进即可

7. Maven -> Spark Project Parent POM -> Package -> Toggle 'Skip Tests' Model -> 执行

```xml
<session.executionRootDirectory>D:\IdeaProjects\spark-2.4.4\executionRootDirectory</session.executionRootDirectory>
<test_classpath>D:\IdeaProjects\spark-2.4.4\test_classpath</test_classpath>

<!--
  Overridable test home. So that you can call individual pom files directly without
  things breaking.
-->
<spark.test.home>${session.executionRootDirectory}</spark.test.home>
```

> An Ant BuildException has occured: Execute failed: java.io.IOException: Cannot run program "bash" (in directory "D:\IdeaProjects\spark-2.4.4\core"): CreateProcess error=2, 系统找不到指定的文件。

因为编译需要git，安装后添加Git/bin路径到Path，发现依然没有，只能换命令编译


解决办法：项目右键 Git Bash，执行下面命令
```sh
export MAVEN_OPTS="-Xmx2g -XX:MaxPermSize=512M -XX:ReservedCodeCacheSize=512m"
./build/mvn -Pyarn -Phadoop-2.7 -Dhadoop.version=2.7.3 -DskipTests clean package
```
官网已有介绍：http://spark.apache.org/docs/latest/building-spark.html


