---
layout: post
title: "Jar 打包依赖"
date: 2018-09-24
description: "Jar 打包依赖"
tag: Java

---

以后打包同一用这个

hadoop jar 运行不含依赖

spark-submit jar 运行含依赖


```xml
<build>
    <finalName>test</finalName>  <!--打包jar文件名-->
    <plugins>

       <plugin>    <!--打包不含依赖-->
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.5.1</version>
            <configuration>
                <source>1.8</source>
                <target>1.8</target>
            </configuration>
        </plugin>

        <plugin>   <!--打包含依赖-->
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-assembly-plugin</artifactId>
            <version>3.0.0</version>
            <configuration>
                <descriptorRefs>
                    <descriptorRef>jar-with-dependencies</descriptorRef>
                </descriptorRefs>
                <archive>
                    <manifest>     <!--jar包入口Main-->
                        <mainClass>WeiboFollowerSpark.WordCount</mainClass>
                    </manifest>
                </archive>
            </configuration>
            <executions>
                <execution>
                    <id>make-assembly</id>
                    <phase>package</phase>
                    <goals>
                        <goal>single</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>

    </plugins>
</build>
```



