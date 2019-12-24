---
layout: post
title: "Spring：基于注解"
date: 2018-02-12
description: "简单介绍Spring"
tag: Java  Web

---


# 基于注解方式的装配

## 注解类型

加注解表示实例化对象，接口不可加注解

1. @Component：基本注解，标识一个受Spring管理的组件

2. @Respository：标识持久层组件

3. @Service：标识服务层组件

4. @Controller：标识表现层组件

5. @AutoWired：自动装配

6. @Qualifier：具体的指定要装配bean的id

## 依赖

```xml
<properties>
    <spring.version>4.0.0.RELEASE</spring.version>
</properties>

<dependencies>
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-context</artifactId>
        <version>${spring.version}</version>
    </dependency>

    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-core</artifactId>
        <version>${spring.version}</version>
    </dependency>

    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-beans</artifactId>
        <version>${spring.version}</version>
    </dependency>

    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-expression</artifactId>
        <version>${spring.version}</version>
    </dependency>

    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-aop</artifactId>
        <version>${spring.version}</version>
    </dependency>
</dependencies>
```

## 注解作用

```java
/**
 * 表现层组件
 * 相当于：<bean id="userController" class="com.sxdt.spring.controller.UserController"></bean>
 * id为首字母小写，也可以使用value属性指定
 * @Controller(value="yourID") 或 @Controller("yourID")
 */
@Controller
public class UserController {
	pass;
}
public class Main {
	public static void main(String[] args) {
		// 1、获取IOC容器
		ApplicationContext ctx = 
				new ClassPathXmlApplicationContext("testSpring.xml");
		// 2、从IOC容器中获取对象
		UserController uc = (UserController)ctx.getBean("userController");	
	}
}
```

## 开启注解扫描

创建一个Spring Config的xml文件

注意事项：IDEA与eclipse不同，没有namespace按钮，但是手动写会提示，回车自动导入命名空间

```xml
<!-- 开启注解扫描 只扫描com.sxdtspring包下-->
<context:component-scan base-package="com.sxdt.spring" use-default-filters="false">
    <!-- 限定扫描，需要配合use-default-filters为false 下面表示只扫描（实例化）@Service注解 -->
    <context:include-filter type="annotation" expression="org.springframework.stereotype.Service" />
    <!-- <context:exclude-filter type="annotation" expression=""/> 不扫描-->

    <!-- type的值annotation表示注解，assignable表示指定某个类  -->
</context:component-scan>
```


## @Autowired 自动装配

@AutoWired 优先采用类型的匹配的方式进行bean的装配，如果有多个类型兼容的bean匹配了，会使用属性名与bean的id进行匹配

例如：

```java
@Autowired
private UserDao userDao;     // 1. 自动装配，UserDao是接口的话，会装配它的实现类

@Autowired
private UserDao userImplDao; // 2. UserDao接口有多个实现类，则属性名与要装配的id相同即可

@Autowired
@Qualifier("userImplDao")
private UserDao userDao;     // 3. 使用@Qualifier指定装配id

@Autowired(required=false)   // 4. 表示有就装配，没有就算了（默认true）
```

# AOP 代理模式

## 启用AspectJ注解

```xml
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-aspects</artifactId>
    <version>4.3.18.RELEASE</version>
</dependency>
<dependency>
    <groupId>aopalliance</groupId>
    <artifactId>aopalliance</artifactId>
    <version>1.0</version>
</dependency>
<dependency>
    <groupId>org.aspectj</groupId>
    <artifactId>aspectjweaver</artifactId>
    <version>1.8.0</version>
</dependency>
```

## AspectJ的5种通知注解

1. @Before 前置通知，在方法执行之前执行

2. @After 后置通知，在方法执行之后执行，不管是否发生异常，访问不到返回值

3. @AfterRunning 返回通知，在方法正常执行返回结果之后执行，能访问到返回值

4. @AfterThrowing 异常通知，在方法抛出异常之后执行，在形参位置可指定抛出特定异常

5. @Around 环绕通知，围绕着方法执行，类似动态代理的整个过程


开启基于注解的aop自动代理

```xml
<aop:aspectj-autoproxy/>
```

## 实例

```java
@Component   // 标识为组件
@Aspect      // 标识为切面
@Order(3)    // 指定切面的优先级，值越小越优先，标注了@Order的切面比不标注的优先
public class LoggingAspectJ {

    @Pointcut("execution(* com.sxdt.spring.service.*.*(..))")
    public void pointcut(){}     // 重用切入点表达式

    // @Before("execution(public int com.sxdt.spring.service.UserService.write(int))")
    // 上面表示public修饰符返回值为Int，UserSerive类的write()函数，参数为Int
    // 下面表示任意修饰符任意返回值，service包下任意类，任意方法，任意参数
    @Before("execution(* com.sxdt.spring.service.*.*(..))")
    public void beforeMethod(JoinPoint joinPoint) {
        String name = joinPoint.getSignature().getName(); // 方法名
        Object[] args = joinPoint.getArgs();              // 方法参数
        System.out.println("@Before");
    }

    @After("execution(* com.sxdt.spring.service.*.*(..))")
    public void afterMethod(JoinPoint joinPoint) {
        String name = joinPoint.getSignature().getName(); // 方法名
        System.out.println("@Before");
    }

    @AfterReturning(value="execution(* com.sxdt.spring.service.*.*(..))", returning ="result")
    public void afterReturningMethod(JoinPoint joinPoint, Object result) {
        String name = joinPoint.getSignature().getName(); // 方法名
        System.out.println("@AfterReturning = " + result);
    }

    @AfterThrowing(value="execution(* com.sxdt.spring.service.*.*(..))", throwing ="ex")
    public void afterReturningMethod(JoinPoint joinPoint, Exception ex) {
        String name = joinPoint.getSignature().getName(); // 方法名
        System.out.println("@AfterThrowing = " + ex);
    }

    @Around("pointcut()")   // 重用表达式
    public Object aroundMethod(ProceedingJoinPoint pjp) {
        String name = pjp.getSignature().getName();
        Object[] args = pjp.getArgs();

        try {
            System.out.println("前置通知");
            Object result = pjp.proceed();
            System.out.println("返回通知");
            return result;
        } catch (Throwable throwable) {
            throwable.printStackTrace();
            System.out.println("异常通知");
        } finally {
            System.out.println("后置通知");
        }
        return null;
    }
}
```


# Spring jdbc

## 依赖

```xml
<dependency>
    <groupId>com.mchange</groupId>
    <artifactId>c3p0</artifactId>
    <version>0.9.5.2</version>
</dependency>
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-jdbc</artifactId>
    <version>${spring.version}</version>
</dependency>
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-orm</artifactId>
    <version>${spring.version}</version>
</dependency>
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-tx</artifactId>
    <version>${spring.version}</version>
</dependency>
<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <version>5.1.23</version>
</dependency>
```

## properties文件

```
jdbc.driver=com.mysql.jdbc.Driver
jdbc.url=jdbc:mysql://localhost:3306/test
jdbc.user=root
jdbc.password=root123456
```

## 装配

```xml
<!-- 配置数据源 -->
<!-- 引入外部化配置文件 -->
<context:property-placeholder location="classpath:db.properties"/>
<bean id="dataSource" class="com.mchange.v2.c3p0.ComboPooledDataSource">
    <property name="dataSourceName" value="${jdbc.driver}"></property>
    <property name="jdbcUrl" value="${jdbc.url}"></property>
    <property name="user" value="${jdbc.user}"></property>
    <property name="password" value="${jdbc.password}"></property>
</bean>

<!-- 配置jdbcTemplate -->
<bean id="jdbcTemplate" class="org.springframework.jdbc.core.JdbcTemplate">
    <property name="dataSource" ref="dataSource"></property>
</bean>
```

## 实例

```java
// 实例化IOC对象
ApplicationContext ctx = new ClassPathXmlApplicationContext("applicationContext.xml");

UserController uc = (UserController) ctx.getBean("userController");
System.out.println(uc);

UserService us = (UserService) ctx.getBean("userService");
System.out.println(us);

us.write(100, "SS");

// 获取JdbcTemplate
JdbcTemplate jt = (JdbcTemplate) ctx.getBean("jdbcTemplate");

// 单个值返回
Integer result = jt.queryForObject(
        "select count(name) from person", Integer.class);
System.out.println(result);

// 单行返回
RowMapper<Person> rm = new BeanPropertyRowMapper<Person>(Person.class);
Person p = jt.queryForObject("select name, age from person where name=?", rm, "liu");
System.out.println(p);

// 多行返回
List<Person> ps= jt.query("select name, age from person where name=?", rm, "wang");
for (Person person : ps) {
    System.out.println(person);
}

// 单个更新
jt.update("update person set name=? where age=?", "wang", 23);

// 批量插入
List<Object[]> batchArgs = new ArrayList<Object[]>();
batchArgs.add(new Object[]{"yang1", 21});
batchArgs.add(new Object[]{"yang2", 22});
jt.batchUpdate("insert into person (name, age) value (?,?)", batchArgs);
```


# 事务管理

开启事务管理，在方法前添加注解@Transactional，如果在类前添加注解，表示类中所有方法起作用。实质就是对注解的方法进行动态代理。打印：Xxx.getClass().getName(),可以发现变成代理类。

```xml
<!--  配置事务管理器  -->
<bean id="dataSourceTransactionManager" class=
        "org.springframework.jdbc.datasource.DataSourceTransactionManager">
    <property name="dataSource" ref="dataSource"></property>
</bean>

<!--  基于注解使用事务，需要开启事务注解  -->
<tx:annotation-driven transaction-manager="dataSourceTransactionManager" />
```

## 事务的属性

1. propagation：事务的传播行为。值REQUIRED表示使用调用者的事务；值REQUIRES_NEW表示将调用者的事务挂起，使用自己的新事务。

2. isolation：事务的隔离级别，最常用的就是READ_COMMITTED

3. readonly：指定事务是否为只读。如果是只读事务，代表这个事务只读取数据库的数据。而不进行修改操作。
若一个事务真的是只读取数据，就有必须要设置readOnly=true，可以帮助数据库引擎进行优化（无需加锁）。

4. timeout：（秒）超时指定强制回滚前事务。为了避免一个事务占用过长的时间。

5. 指定类或类名，进行回滚或不回滚

rollbackFor

rollbackForClassName

noRollbackFor

noRollbackForClassName

```java
@Transactional(propagation = Propagation.REQUIRES_NEW,
        isolation = Isolation.READ_COMMITTED,
        timeout = 3,                    // 超时3秒回滚
        noRollbackFor = {Xxxx.class},   // Xxx.class 异常不回滚
        readOnly = true)                
```



