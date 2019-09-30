---
layout: post
title: "阿里巴巴Druid连接池"
date: 2019-09-04
description: "介绍一下阿里巴巴的Druid"
tag: Database

---



# Druid 连接池


## 简介

DRUID是阿里巴巴开源平台上一个数据库连接池实现，加入日志监控，可以很好的监控DB池连接和SQL的执行情况，可以说是针对监控而生的DB连接池。

连接：https://github.com/alibaba/druid/


## 实例

```xml
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>druid</artifactId>
    <version>1.1.9</version>
</dependency>
```

```java
import java.sql.*;
import java.util.Properties;
import com.alibaba.druid.pool.DruidDataSource;
import com.alibaba.druid.pool.DruidDataSourceFactory;
import com.alibaba.druid.pool.DruidPooledConnection;

druidDataSource = new DruidDataSource();
druidDataSource.setDriverClassName("com.mysql.jdbc.Driver"); 
druidDataSource.setUsername("root");
druidDataSource.setPassword("123456");
druidDataSource.setUrl("jdbc:mysql://127.0.0.1:3306/demo"); 
druidDataSource.setInitialSize(5);
druidDataSource.setMinIdle(1);
druidDataSource.setMaxActive(10);
druidDataSource.setFilters("stat");
```

db.propertie oracle数据库

```
driverClassName=oracle.jdbc.OracleDriver
url=jdbc:oracle:thin:@172.16.7.14:1521:ora10ha
username=root
password=123456
filters=stat
initialSize=2
maxActive=300
maxWait=60000
timeBetweenEvictionRunsMillis=60000
minEvictableIdleTimeMillis=300000
validationQuery=select 1 from dual
testWhileIdle=true
testOnBorrow=false
testOnReturn=false
poolPreparedStatements=false
maxPoolPreparedStatementPerConnectionSize=200
```

## 连接池用法

```java
public class DBPoolConnection {
	private static DBPoolConnection dbPoolConnection = null;
	private static DruidDataSource druidDataSource = null;
	// 初始化
	static {
		Properties properties = new Properties();
		// 读取数据库全部参数
		properties.load(DBPoolConnection.class.getResourceAsStream("db.properties"));
		druidDataSource = (DruidDataSource)DruidDataSourceFactory.createDataSource(properties);
	}
	// 连接池单例
	public static synchronized DBPoolConnection getInstance() {
		if (null == dbPoolConnection) {
			dbPoolConnection = new DBPoolConnection();
		}
		return dbPoolConnection;
	}
	// 返回druid数据库连接
	public DruidPooledConnection getConnection() {
		return druidDataSource.getConnection();
	}
	// 释放资源
	public static void closeAll(DruidPooledConnection conn, PreparedStatement ps, ResultSet rs) {
		if (rs != null) {
			rs.close();
		}
		if (ps != null) {
			ps.close();
		}
		if (conn != null) {
			conn.close();
		}
	}
}
```

```java
DBPoolConnection dbp = DBPoolConnection.getInstance();
DruidPooledConnection conn = null;
PreparedStatement ps = null;
ResultSet rs = null;

conn = dbp.getConnection();
String sql = "UPDATE table_name SET name=? where age=?;"
ps = conn.prepareStatement(sql);
ps.setString(1, "yang");
ps.setString(2. "18");
ps.executeUpdate();
DBPoolConnection.closeAll(conn, ps, rs);
```

# 监控实例

maven 项目

```xml
<properties>
    <spring.version>4.0.0.RELEASE</spring.version>
</properties>

<dependencies>
	<!-- druid -->
	<dependency>
	    <groupId>com.alibaba</groupId>
	    <artifactId>druid</artifactId>
	    <version>1.1.9</version>
	</dependency>

	<!-- spring -->
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

    <!-- 数据库 -->
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

</dependencies>
```

src/main/resources下新建db.properties

```
jdbc.driverClassName=com.mysql.jdbc.Driver
jdbc.url=jdbc:mysql://172.16.7.124:3306/test
jdbc.username=root
jdbc.password=root123456
``` 

src/main/resources下新建Spring Config 文件 

```xml
<bean id="propertyConfigure"
      class="org.springframework.beans.factory.config.PropertyPlaceholderConfigurer">
    <property name="locations">
        <list>
            <value>./db.properties</value>
        </list>
    </property>
</bean>

<bean id="dataSource" class="com.alibaba.druid.pool.DruidDataSource"
      init-method="init" destroy-method="close">
    <property name="driverClassName" value="${jdbc.driverClassName}" />
    <property name="url" value="${jdbc.url}" />
    <property name="username" value="${jdbc.username}" />
    <property name="password" value="${jdbc.password}" />
    <!-- 配置初始化大小、最小、最大 -->
    <property name="initialSize" value="1" />
    <property name="minIdle" value="1" />
    <property name="maxActive" value="10" />

    <!-- 配置获取连接等待超时的时间 -->
    <property name="maxWait" value="10000" />

    <!-- 配置间隔多久才进行一次检测，检测需要关闭的空闲连接，单位是毫秒 -->
    <property name="timeBetweenEvictionRunsMillis" value="60000" />

    <!-- 配置一个连接在池中最小生存的时间，单位是毫秒 -->
    <property name="minEvictableIdleTimeMillis" value="300000" />

    <property name="testWhileIdle" value="true" />

    <!-- 这里建议配置为TRUE，防止取到的连接不可用 -->
    <property name="testOnBorrow" value="true" />
    <property name="testOnReturn" value="false" />

    <!-- 打开PSCache，并且指定每个连接上PSCache的大小 -->
    <property name="poolPreparedStatements" value="true" />
    <property name="maxPoolPreparedStatementPerConnectionSize"
              value="20" />

    <!-- 这里配置提交方式，默认就是TRUE，可以不用配置 -->

    <property name="defaultAutoCommit" value="true" />

    <!-- 验证连接有效与否的SQL，不同的数据配置不同 -->
    <property name="validationQuery" value="select 1 " />
    <property name="filters" value="stat" />
    <property name="proxyFilters">
        <list>
            <ref bean="logFilter" />
        </list>
    </property>
</bean>

<bean id="logFilter" class="com.alibaba.druid.filter.logging.Slf4jLogFilter">
    <property name="statementExecutableSqlLogEnable" value="false" />
</bean>
```

项目右键 --> add framework Support --> web

在生成的web.xml中

```xml
<!-- Druid连接池监控 -->
<servlet>
    <servlet-name>DruidStatView</servlet-name>
    <servlet-class>com.alibaba.druid.support.http.StatViewServlet</servlet-class>
</servlet>
<servlet-mapping>
    <servlet-name>DruidStatView</servlet-name>
    <url-pattern>/druid/*</url-pattern>
</servlet-mapping>
<filter>
    <filter-name>druidWebStatFilter</filter-name>
    <filter-class>com.alibaba.druid.support.http.WebStatFilter</filter-class>
    <init-param>
        <param-name>exclusions</param-name>
        <param-value>/public/*,*.js,*.css,/druid*,*.jsp,*.swf</param-value>
    </init-param>
    <init-param>
        <param-name>principalSessionName</param-name>
        <param-value>sessionInfo</param-value>
    </init-param>
    <init-param>
        <param-name>profileEnable</param-name>
        <param-value>true</param-value>
    </init-param>
</filter>
<filter-mapping>
    <filter-name>druidWebStatFilter</filter-name>
    <url-pattern>/*</url-pattern>
</filter-mapping>
```

测试spring，基于注解的实例是否可用

```java
// 1、获取IOC容器
ApplicationContext ctx =
    new ClassPathXmlApplicationContext("spring.xml");
// 2、从IOC容器中获取对象
DruidDataSource ds = (DruidDataSource)ctx.getBean("dataSource");

System.out.println("OK");
```

报错

> The last packet sent successfully to the server was 0 milliseconds ago. The driver has not received any packets from the server.

原因：数据库ip地址写错


配置run并运行run configurations --> tomcat server --> local

报错

> java.lang.ClassNotFoundException: com.alibaba.druid.support.http.WebStatFilter

检查pom.xml看maven是不是没有引入依赖，发现依赖并没有问题。检查tomcat本地安装路径下的lib文件夹有没有引入druid.jar的jar包，从maven的本地仓库中复制druid.jar到lib文件夹下

运行：http://localhost:8080/你的项目/druid

