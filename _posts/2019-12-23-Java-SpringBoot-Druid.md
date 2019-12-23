---
layout: post
title: "SpringBoot 整合 Druid"
date: 2019-12-23
description: "SpringBoot 整合 Druid"
tag: Java

---

## 依赖

```xml
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>druid-spring-boot-starter</artifactId>
    <version>1.1.10</version>
</dependency>
```

> 注意artifactId，另一种依赖是`<>druid</>`在这不适用。

## 配置文件

```sh
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver   # 注意是 cj
    url: jdbc:mysql://172.16.7.124:3306/test
    username: root
    password: root123456
    ## 数据源类别
    type: com.alibaba.druid.pool.DruidDataSource
    druid:
      initial-size: 5     # 初始化时建立物理连接的个数
      max-active: 20      # 最大连接池数量
      min-idle: 5         # 最小连接池数量
      max-wait: 30000     # 连接最大等待时间ms

      # 配置检测可以关闭的空闲连接间隔时间
      time-between-eviction-runs-millis: 60000
      # 配置连接在池中的最小生存时间
      min-evictable-idle-time-millis: 30000
      max-evictable-idle-time-millis: 400000

      # 是否缓存preparedStatement，也就是PSCache,PSCache对支持游标的数据库性能提升巨大，比如说oracle
      # 在mysql下建议关闭
      pool-prepared-statements: false
      # 要启用PSCache，必须配置大于0，当大于0时，poolPreparedStatements自动触发修改为true
      # 在Druid中，不会存在Oracle下PSCache占用内存过多的问题，可以把这个数值配置大一些，比如说100
      max-pool-prepared-statement-per-connection-size: -1

      # 配置 监控统计的stat和防sql注入的wall
      filters: stat,wall
      web-stat-filter:      # 监控配置
        enabled: true       # 开启StatFiler
        url-pattern: /*     # 过滤规则
        exclusions: /druid/*    # 忽视

      # Spring监控AOP切入点
      aop-patterns: com.sxdt.demo.*

      # 监控信息展示页面
      stat-view-servlet:
        enabled: true             # 开启
        url-pattern: /druid/*     # 访问路径
        reset-enable: false       # 是否能够重置数据
        login-password: 123456    # 登录密码
        login-username: root      # 登录用户
        allow: 127.0.0.1,172.16.8.214,172.16.7.124   # IP白名单
        # deny:    # IP黑名单（共同存在时，deny优先于allow）
```

此时可以直接启动，打开Web：url/druid，登录成功即可查看SQL监控。


## 注册Servlet和Filter开启监控

如果不使用上面配置文件开启监控，也可通过注册Servlet和Filter开启监控

```java
@Configuration
public class DruidConfiguration {
    @Bean
    public ServletRegistrationBean druidStatViewServlet() {
        ServletRegistrationBean servletRegistrationBean =
                new ServletRegistrationBean(new StatViewServlet(), "/druid/*");//urlMappings
        servletRegistrationBean.addInitParameter("allow", "127.0.0.1");//deny黑名单优先于allow
        servletRegistrationBean.addInitParameter("loginUsername", "admin");
        servletRegistrationBean.addInitParameter("loginPassword", "123456");
        servletRegistrationBean.addInitParameter("resetEnable", "false");
        return servletRegistrationBean;
    }

    @Bean
    public FilterRegistrationBean druidStatFilter() {
        FilterRegistrationBean filterRegistrationBean =
                new FilterRegistrationBean(new WebStatFilter());
        // 添加过滤规则
        filterRegistrationBean.addUrlPatterns("/*");
        filterRegistrationBean.addInitParameter("exclusions", "*.jpg,*.gif,/druid/*");
        return filterRegistrationBean;
    }
}
```

@Configuration: 可简单理解该类编程XML配置文件。

@Bean: 等同于XML配置文件中的<bean>，将返回值装载进Spring IoC容器。

```xml
<bean id="druidStatFilter" class=
	"org.springframework.boot.web.servlet.FilterRegistrationBean">
</bean>
```

再次运行SpringBoot，发现登录用户变成admin，可见配置文件的监控配置，会被自定义覆盖掉。




# reference

https://www.jianshu.com/p/ee00f7604c02?from=groupmessage



