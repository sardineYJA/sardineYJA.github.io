---
layout: post
title: "Spring：基于xml"
date: 2019-05-29
description: "简单介绍Spring"
tag: Java

---

# Spring 简介：

IOC(Inversion of Control, 控制反转)

AOP(Aspect Oriented Programming, 面向切片)

不用new方式创建对象，而是使用配置的方式。

bean 配置形式：1、基于XML文件，2、基于注解方式。

# 安装配置

1. 下载对于eclipse相应版本的Spring：https://spring.io/tools3/sts/all

2. 打开eclipse的Help的install new software，选择下载好的压缩包。

3. 创建java项目（非Spring项目），创建lib将jar包放入，右键Bulid Path->Configura bulid path导入jar包到Referenced Libraries，后期可换成maven导入

4. 在src目录创建Spring Bean Configuration File即XML配置文件

```
commons-logging-1.1.1.jar
spring-beans-4.0.0.RELEASE.jar
spring-context-4.0.0.RELEASE.jar
spring-core-4.0.0.RELEASE.jar
spring-expression-4.0.0.RELEASE.jar
```



# 实例

```java
public class HelloWorld {
	private String name;
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public void sayHello() {
		System.out.println("HelloWorld Class say");
	}
}
```

```java
public class Main {
	public static void main(String[] args) {
		// HelloWorld hw = new HelloWorld();
		// hw.setName("Jon");
		// hw.sayHello();
		
		// 1、获取IOC容器
		ApplicationContext ctx = 
				new ClassPathXmlApplicationContext("testSpring.xml");
		// 2、从IOC容器中获取对象
		HelloWorld hello = (HelloWorld)ctx.getBean("helloWorld");	
		hello.sayHello();
	}
}
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
	<!--
		id:bean唯一标识
		class:指定全类名    反射的方式创建对象：
			Class cls = Class.forName("test.HelloWorld")
			Object obj = cls.newInstance(); // 需要提供默认的构造器
		property:通过set方法给指定的属性赋值
	 -->
	<bean id="helloWorld" class="test.HelloWorld">
		<property name="name" value="Jerry"></property>
	</bean>
</beans>
```

注意事项：

1. HelloWorld类需要提起默认的构造器；

2. setXXX()必须存在,property才可用；

## 获取对象函数

```java
ApplicationContext ctx = new ClassPathXmlApplicationContext("testSpring.xml");
// 1、从IOC容器中获取对象，需要强制转换
HelloWorld hello = (HelloWorld)ctx.getBean("helloWorld");	
// 2、无需强制转换，如果多个HelloWorld实例的bean，会报错
HelloWorld hello = ctx.getBean(HelloWorld.class);
// 3、结合以上两种
HelloWorld hello = ctx.getBean("helloWorld", HelloWorld.class);
```

注意事项：

1. xml文件中的bean都会实例化；


## 依赖注入的方式

1. 属性注入（setXXX方法）

2. 构造器注入

3. 工厂方法注入（不推荐）

```xml
<!-- set注入的前提是先调用无参数的构造函数创建对象-->
<bean id="car" class="test.Car">
	<property name="brand" value="Audi"></property>
	<property name="crop" value="yiqi"></property>
	<property name="price" value="400000"></property>
</bean>
```

```xml
<!-- 构造器注入
	value:注入值
	index:参数位置，如果不给定，则值需要与构造参数位置一致
	type:参数类型，如果不给定，则可能匹配到多个构造函数
-->
<bean id="car" class="test.Car">
	<constructor-arg value="BWM"></constructor-arg>
	<constructor-arg value="90000" index="2" type="double"></constructor-arg>
	<constructor-arg value="honguang", index="1"></constructor-arg>
</bean>
```

## 特殊字符注入

```xml
<!-- set注入的前提是先调用无参数的构造函数创建对象-->
<bean id="car" class="test.Car">
	<property name="num">
		<value>10001</value>
	</property>
	<property name="name">
		<!--
			<![CDATA[....]]> 来完成特殊字符的注入
		-->
		<value><![CDATA[《特殊字符》]]></value>
	</property>
	
</bean>
```

## 引用其他bean

```xml
<bean id="person" class="test.Person">
	<property name="name" value="yang"></property>
	<property name="age" value="24"></property>
	<!-- car属性为Car类，ref：指定要引用的bean的id-->
	<property name="car" ref="car"></property>
</bean>
```

## 使用内部bean

```xml
<bean id="person" class="test.Person">
	<property name="name" value="yang"></property>
	<property name="age" value="24"></property>
	<property name="car">
		<bean class="test.Car">
			<property name="price" value="400000"></property>
		</bean>
	</property>
</bean>s
```

## 注入list, set, array类型

```xml
<bean id="personList" class="test.Person">
	<property name="name" value="yang"></property>
	<property name="age" value="24"></property>
	<property name="car">
		<list>
			<ref bean="car1"/>
			<ref bean="car2"/>
			<ref bean="car3"/>
			<!-- <bean></bean> 还可以使用内部bean-->
		</list>
		<!--
			<set></set>
			<array></array>
		-->
		<map>
			<!-- <entry key="" key-ref="" value="" value-ref=""> -->
			<entry key="AA" value-ref="car1"></entry>
			<entry key="BB" value-ref="car2"></entry>
		</map>
	</property>
</bean>
```

## p命名空间

在xml配置文件下方点击Namespaces，勾选p导入命名空间

p:属性名 或 p:属性名-ref 的方式进行值的注入

```xml
<bean id="personP" class="test.Person"
	p:name="yang" p:age="24" p:car-ref="car">
	<!-- 不用使用以下两种方式赋值：
		<property></property>
		<constructor-arg></constructor-arg>
	-->
</bean>
```


## 自动装配

```java
public class Person {
	private String name;
	private Address address;
	private Car car;
}
```

自动装配car和address属性；
但是一般基于XML的注入不建议使用自动装配。

```xml
<bean id="address" class="autowireTest.Address">
	<property name="city" value="ShenZhen"></property>
	<property name="street" value="jiedao"></property>
</bean>
<bean id="car" class="autowireTest.Car" p:brand="Audi" p:price="600000">
</bean>
<!--
	autowire:
		byName:通过bean的id值与要进行注入的属性名进行匹配
				（id值必须与属性名如car相同）
		byType:通过bean的class值与要进行注入的属性的类型进行匹配
				（匹配到多个如Car的bean的话会报错）
-->
<bean id="person" class="autowireTest.Person" autowire="byName">
	<property name="name" value="yang"></property>
</bean>
```

## bean的继承

属性：autowire，abstract等不会被继承

```xml
<!-- bean之间的继承：
	parent:指定父类bean的id，实现继承
	abstract="true":指定为抽象bean,不能实例化对象
-->
<bean id="address1" class="autowireTest.Car" abstract="true">
	<property name="brand" value="audi"></property>
	<property name="price" value="30000"></property>
</bean>
<!-- 继承brand属性值，但price属性值覆盖 -->
<bean id="address2" parent="address1">
	<property name="price" value="40000"></property>
</bean>
```


## bean的作用域

1. singleton：单例（默认值），在IOC容器中，只有一个该bean的实例对象，并且该bean的对象会在IOC容器初始化的时候创建

2. prototype：原型，在IOC容器中，有多个该bean的实例对象，不会在IOC容器初始化的时候创建，而是在每次getBean的时候才会创建一个新的对象返回

3. request：一次请求期间

4. session：一次会话期间

## 引入外部化的配置文件

```
jdbc.driver=com.mysql.jdbc.Driver
jdbc.url=jdbc:mysql://localhost:3306/test
jdbc.user=root
jdbc.password=123456
```

```xml
<!-- 配置连接池 数据库 -->
<!-- 引入外部化的配置文件 -->
<context:property-placeholder location="classpath:db.properties" />
<bean id="dataSource" class="dao.ComboPooledDataSource">
	<property name="driver" value="${jdbc.driver}"></property>
	<property name="url" value="${jdbc.url}"></property>
	<property name="user" value="${jdbc.user}"></property>
	<property name="password" value="${jdbc.password}"></property>
</bean>
```

## bean的生命周期

1. 调用构造器创建对象

2. 给对象的属性设置值

3. 调用init方法进行初始化

4. 使用对象

5. 调用destroy方法进行对象的销毁


```xml
<bean id="car" class="Test.Car" init-method="yourInit" destroy-method="yourDestroy">
	<property name="price" value="300000"></property>
</bean>
```

## 基于xml的AOP代理模式

```xml
<!-- 配置切面 -->
<bean id="loggingAspectJ" class="test.LoggingAspectJ"></bean>
<!-- 配置目标bean -->
<bean id="userService" class="service.UserSErvice"></bean>

<!-- 配置aop -->
<aop:config>
	<!-- 配置切入点表达式 -->
	<aop:pointcut expression="execution(* com.sxdt.spring.*.*(..))" id="myPointCut"/>

	<!-- 配置切面通知 -->
	<aop:aspect ref="loggingAspectJ", order="3">
		<aop:before method="beforeMethod" pointcut-ref="myPointCut" />
		<aop:after method="afterMethod" pointcut-ref="myPointCut" />
		<aop:after-returning method="returnMethod" pointcut-ref="myPointCut" returning="result" />
		<aop:after-throwing method="throwingMethod" pointcut-ref="myPointCut" throwing="ex" />
	</aop:aspect>>
</aop:config>
```

## 基于xml的事务管理

```xml
<!-- 配置事物管理器 -->
<bean id="transactionManager" class="org.springframework.jdbc.datasource.DataSourceTransactionManager">
	<property name="dataSource"ref="dataSource"></property>
</bean>

<!-- 配置事务属性 -->

<tx:advice id="txAdvice" transaction-manager="transactionManager">
	<tx:attributes>
		<tx:method name="buyBook" propagation="REQUIRES_NEW" isolation="READ_COMMITTED" read-only="false" timeout="3"/>
		<tx:method name="checkOut"/>
		<tx:method name="update*" propagation="REQUIRES NEW"/>
		<tx:method name="insert*" propagation="REQUIRED"/>
		<tx:method name="delete*" propagation="REQUIRED"/>
		<tx:method name="get*" read-only="true"/>
		<!-- 代表除了上述指定的方法之外的方法-->
		<tx:method name="*"/>
	</tx:attributes>
</tx:advice>

<!-- 配置事务切入点，以及事务切入点和事务属性关联起来 -->
<aop:config>
	<aop:pointcut expression="execution（*com.atguigu.spring.tx.service.*.*（..））"id="txPointCut"/>
	<aop:advisor advice-ref="txAdvice" pointcut-ref="txPointCut"/>
</aop:config>
```


