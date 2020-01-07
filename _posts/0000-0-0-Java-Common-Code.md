---
layout: post
title: "Common Code"
date: 2018-09-27
description: "Common Code"
tag: Java

---

## 日志信息

slf4j(Simple Logging Facade for Java)，是一系列的日志接口，是Java中所有日志框架的抽象

创建src/main/resources/log4j.properties

```
log4j.rootCategory=INFO, console
log4j.appender.console=org.apache.log4j.ConsoleAppender
log4j.appender.console.target=System.err
log4j.appender.console.layout=org.apache.log4j.PatternLayout
log4j.appender.console.layout.ConversionPattern=%d{yy/MM/dd HH:mm:ss} %p %c{1}: %m%n
```


```xml
<dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-api</artifactId>
    <version>1.7.24</version>
</dependency>
```


```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Test {
	public static Logger logger = LoggerFactory.getLogger(Xxx.class);
	logger.error("Error Message!");
	logger.warn("Warn Message!");
	logger.info("Info Message!");
	logger.debug("Debug Message!");
}

```

> ERROR StatusLogger No log4j2 configuration file found. Using default configuration: logging only errors to the console. Set system property 'org.apache.logging.log4j.simplelog.StatusLogger.level' to TRACE to show Log4j2 internal initialization logging.

解决：log4j.properties的文件改为log4j2.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Configuration status="WARN">
    <Appenders>
        <Console name="Console" target="SYSTEM_OUT">
            <PatternLayout pattern="%d{YYYY-MM-dd HH:mm:ss} [%t] %-5p %c{1}:%L - %msg%n" />
        </Console>
 
        <RollingFile name="RollingFile" filename="log/test.log"
            filepattern="${logPath}/%d{YYYYMMddHHmmss}-fargo.log">
            <PatternLayout pattern="%d{YYYY-MM-dd HH:mm:ss} [%t] %-5p %c{1}:%L - %msg%n" />
            <Policies>
                <SizeBasedTriggeringPolicy size="10 MB" />
            </Policies>
            <DefaultRolloverStrategy max="20" />
        </RollingFile>
 
    </Appenders>
    <Loggers>
        <Root level="info">
            <AppenderRef ref="Console" />
            <AppenderRef ref="RollingFile" />
        </Root>
    </Loggers>
</Configuration>
```



## 时间格式化

```java
import java.text.SimpleDateFormat;
import java.util.Date;
SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
System.out.println(df.format(new Date()));
// 2019-08-19 17:50:46
System.out.println(df.format(System.currentTimeMillis()));
```
```java
// Date 源码就是System.currentTimeMillis() 单位ms
// 可以将 new Date() 换成 System.currentTimeMillis() 更好
public Date()
{
this(System.currentTimeMillis());
}
```

## 批量转码

```java
import java.io.*;
import java.util.ArrayList;
// 批量文件转码
public class ToEncode {
	
	public static void main(String[] args) throws IOException {
		String inPathStr = "D:/in";
		String outPathStr = "D:/out";    // 不需要事先创建
		convertEncode(new File(inPathStr), outPathStr, "GBK", "utf-8");
		System.out.println("Main is complete");
	}
	 
	public static void convertEncode(File file, String outPathStr, String inEncode, String outEncode)  {
		
	    if (file.isFile() && file.getName().endsWith(".md")) {
	        BufferedReader br = null;
	        PrintStream out = null;
			try {
				// 以InputEncode编码读取
				br = new BufferedReader(new InputStreamReader(new FileInputStream(file), inEncode));
				ArrayList<String> lines = new ArrayList<String>();
		        String line;
		        while ((line = br.readLine()) != null)
		            lines.add(line);
		        br.close();
		       
		        // 创建子文件夹
		        File outPath = new File(outPathStr);
		        if (!outPath.exists()) {
		        	outPath.mkdirs();
		        }
		        
		        File savefile = new File(outPathStr+file.getName());
		        // 以outputEncode编码写出
		        out = new PrintStream(savefile, outEncode);
		        for (String s : lines)
		            out.println(s);
			} catch (Exception e) {
				System.out.println(file.toString() + "======= error");
			} finally {
		        out.flush();
		        out.close();
			}
	        System.out.println(file.toString() + " ---- OK");
	        
	    } else if (file.isDirectory()) {
	    	String dir = file.getName();
	        File[] files = file.listFiles();
	        if (files != null) {
	            for (File f : files) {
	            	convertEncode(f, outPathStr+"/"+dir+"/", inEncode, outEncode);
	            } 
	        }
	    }
	}
}
```


## Jar 打包依赖

- hadoop jar 运行不含依赖

- spark-submit jar 运行含依赖


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


## SQL 

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

