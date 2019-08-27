---
layout: post
title: "Tomcat"
date: 2019-08-15
description: "简单介绍Tomcat"
tag: java

---

# tomcat

## IDEA新建tomcat项目

1. 下载tomcat：https://tomcat.apache.org/download-70.cgi

2. 解压：E:\apache-tomcat-7.0.96

3. File --> setting --> Plugins --> 安装tomcat插件(IDEA专业版已安装)

4. File --> setting --> Build,Exceution,Deployment --> Applicatin Server --> + --> E:\apache-tomcat-7.0.96

5. 项目右键 --> Add Framework Support --> Web Application

6. run --> edit configurations--> Deployment，可以看到`Application context`的目录：(如：/test)，打开浏览器http://localhost:8080/test

7. 输出日志乱码，修改conf/logging.properties：java.util.logging.ConsoleHandler.encoding = GBK

8. 如果要部署tomcat离线网页，添加tomcat的ROOT目录：run --> edit configurations--> Deployment --> + --> E:\apache-tomcat-7.0.96\webapps\ROOT




## Maven 生成 Web 模块

1. File --> project Structure --> Facets --> + --> Web

2. 自动生成web目录

3. Run --> edit Configurations --> + --> Tomcat Server --> local

4. 其中 Deployment 选择当前目录web ，生成Application context



```xml
<form action="" method="get">
    用户名称：<input type="text"name="username"/>
    <br/>
    用户密码：<input type="password"name="password"/>
    <br/>
    <input type="submit"value="Login"/>
</form>
```

```xml
<dependency>
    <groupId>javax.servlet</groupId>
    <artifactId>javax.servlet-api</artifactId>
    <version>4.0.1</version>
</dependency>
```


```xml
配置Servlet 请求与处理类的映射关系
请求到达后，先与url-pattern进行匹配，然后根据servlet-name定位到servlet-class，执行所配置类的相关方法

<servlet>
    <servlet-name>LoginServlet</servlet-name>
    <servlet-class>com.sxdt.web.LoginServlet</servlet-class>
</servlet>
<servlet-mapping>
    <servlet-name>LoginServlet</servlet-name>
    <url-pattern>/login</url-pattern>
</servlet-mapping>
```


```java
// doGet是处理get请求的
@Override
protected void doGet(HttpServletRequest req, HttpServletResponse resp)
		throws ServletException, IOException {
	//处理逻辑
	super.doGet(req, resp);
}
// doPost是处理post请求的
@Override
protected void doPost(HttpServletRequest req, HttpServletResponse resp)
		throws ServletException, IOException {
	//处理逻辑
	this.doGet(req, resp);
	// this.doPost(req, resp);
}
```

```java
public class LoginServlet  extends HttpServlet{
    /**
     *get请求与post请求在后台处理中没有太大的区别，因此可以只实现一个方法，然后让另一个方法去调用实现的方法.
     *
     *或者不用重写doGet 以及doPost方法，直接重写service方法即可
     *因为在HttpServlet的底层是有一个service方法中调用doGet以及doPost
     */
    public LoginServlet(){
        System.out.println("LoginServlet Constructor ....");
    }

    @Override
    public void service(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String user = request.getParameter("username");
        String password = request.getParameter("password");
        System.out.println(user + password);

    }
}
```