---
layout: post
title: "Junit"
date: 2019-08-05
description: "简单介绍Junit"
tag: Java

---

# Junit


1. @Test: 测试方法

2. @Ignore: 被忽略的测试方法：加上之后，暂时不运行此段代码

3. @Before: 每一个测试方法之前运行

4. @After: 每一个测试方法之后运行

5. @BeforeClass: 方法要是静态方法（static 声明），所有测试开始之前运行

6. @AfterClass: 方法要是静态方法（static 声明），所有测试结束之后运行

 
## 依赖

```xml
<dependency>
	<groupId>junit</groupId>
	<artifactId>junit</artifactId>
	<version>RELEASE</version>
</dependency>
 ```

## 编写测试类的原则

1. 测试方法上必须使用@Test进行修饰

2. 测试方法必须使用public void 进行修饰，不能带任何的参数

3. 新建一个源代码目录来存放我们的测试代码，即将测试代码和项目业务代码分开

4. 测试类所在的包名应该和被测试类所在的包名保持一致

5. 测试单元中的每个方法必须可以独立测试，测试方法间不能有任何的依赖

6. 测试类使用Test作为类名的后缀（不是必须）

7. 测试方法使用test作为方法名的前缀（不是必须）


