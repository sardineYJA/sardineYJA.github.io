---
layout: post
title: "SpringBoot 使用 Filter、Listener"
date: 2019-12-23
description: "SpringBoot 使用 Filter、Listener"
tag: Java

---

# 过滤器 Filter

## 简介

处于客户端与服务器资源文件之间的一道过滤网，对JSP、Servlet、静态图片文件或静态HTML文件等进行拦截，可实现URL级别的权限访问控制、过滤敏感词、压缩响应等功能。

Filter的创建和销毁由Web服务器负责。创建时调用init()，读取web.xml。访问URL时，执行doFilter方法。卸载时，调用destroy()。多个Filter组成FilterChain。


## 案例

```java
@WebFilter(filterName = "studentFilter", urlPatterns = "/*")
public class StudentFilter implements Filter {
    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
        System.out.println("Filter_init()");
    }

    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
        System.out.println("Filter_doFilter()");
        // 直接传给下一个过滤器
        filterChain.doFilter(servletRequest, servletResponse);
    }

    @Override
    public void destroy() {
        System.out.println("Filter_destroy()");
    }
}
```

入口类添加@ServletComponentScan，Servlet、Filter、Listener可直接通过@WebServlet、@WebFilter、@WebListener注解自动注册。

```java
@SpringBootApplication
@ServletComponentScan
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }

}
```


# 监听器 Listener

用于监听Web应用中某些对象、信息的创建、销毁、增加、修改等动作的发生，并作出相应处理。

根据`监听对象`分类：
- ServletContext(对应application)
- HttpSession(对应session)
- ServletRequest(对应request)

根据`监听事件`分类：
- 监听对象创建与销毁，如 ServletContextListener
- 监听对象域中属性的增加和删除，如 HttpSessionListener, ServletRequestListener
- 监听绑定到Session上的某个对象的状态，如 ServletContextAttributeListener, HttpSessionAttributeListener

```java
@WebListener
public class StudentListener implements ServletContextListener {
    @Override
    public void contextInitialized(ServletContextEvent sce) {
        System.out.println("ServletContext上下文初始化");
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
        System.out.println("ServletContext上下文销毁");
    }
}
```



