---
layout: post
title: "Java SQL数据库"
date: 2018-01-23
description: "Java SQL"
tag: Java

---

# Java SQL 

```java
import java.sql.Driver;
import java.sql.Connection;
import java.sql.Statement;
import java.sql.PreparedStatement;
import java.sql.CallableStatement;
import java.sql.ResultSet;
import java.sql.DatabaseMetaData;
import java.sql.ResultSetMetaData;
```

```java
// Statement 用于执行不带参数的简单sql语句，executeQuery, executeUpdate, execute
// PreparedStatement(继承Statement) 执行带或不带参数的预编译sql语句
// CallableStatement(继承PreparedStatement) 调回数据库存储过程的方法
Class.forName("com.mysql.jdbc.Driver");
Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/name", "root", "123456");
Statement stmt = conn.createStatement();
ResultSet resultSet = stmt.executeQuery("yourSQL");
// prepareStatement对象防止sql注入的方式是把用户非法输入的单引号用\反斜杠做了转义
PreparedStatement preparedStatement = conn.prepareStatement("yourSQL");
ResultSet rs = preparedStatement.executeQuery();
while(rs.next()){
    System.out.println(rs.getString(1));  // name 根据类型取值
    System.out.println(rs.getInt(2));     // age
}
```

Properties 的使用

```java
Properties prop = new Properties();
prop.load(Xxx.class.getResourceAsStream("/db.properties"));
user = prop.getProperty("username");
password = prop.getProperty("password");
url = prop.getProperty("url");
driver = prop.getProperty("driverClassName");
```

db.propertie oracle数据库

```
driverClassName=oracle.jdbc.OracleDriver
url=jdbc:oracle:thin:@172.16.7.14:1521:ora10ha
username=root
password=123456
```

```
jdbc.driverClassName=com.mysql.jdbc.Driver
jdbc.url=jdbc:mysql://172.16.7.124:3306/test
jdbc.username=root
jdbc.password=root123456
```

