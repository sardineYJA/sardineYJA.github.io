---
layout: post
title: "SpringBoot 整合 Shiro 权限管理"
date: 2020-01-03
description: "SpringBoot 整合 Shiro"
tag: Java Web

---

## Shiro

与 Spring Security 相比，Shiro 则是一个轻量级的安全管理框架

## 三大功能模块

- Subject：主体，一般指用户。
- SecurityManager：安全管理器，管理所有Subject。
- Realms：用于进行权限信息的验证，一般需要自己实现。


# 测试案例

## 依赖

```xml
<dependency>
    <groupId>org.apache.shiro</groupId>
    <artifactId>shiro-spring</artifactId>
    <version>1.4.0</version>
</dependency>

<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <version>1.16.12</version>
</dependency>
```

## 实体类

一个User可能有多种角色Role，每种Role有相应的权限Permissions。

```java
@Data
public class User {
    private String id;
    private String userName;
    private String password;
    private Set<Role> rolse;  // 用户对应的角色集合
}
```

```java
@Data
public class Role {
    private String id;
    private String roleName;
    private Set<Permissions> permissions;
}
```

```java
@Data
public class Permissions {
    private String id;
    private String permissionName;
}
```

## Service

```java
@Service
public class LoginService {
    public User getUserByName(String name) {
        //模拟数据库查询，正常情况此处是从数据库或者缓存查询。
        return user;
    }
}
```
这里创建一个yang用户进行测试：
```java
Set<Permissions> permissionsSet = new HashSet<>();
permissionsSet.add(new Permissions("1","query"));  // query权限
permissionsSet.add(new Permissions("2","add"));    // add权限

Set<Role> roleSet = new HashSet<>();
roleSet.add(new Role("1","admin",permissionsSet)); // admin 角色

User user = new User("1","yang","123456",roleSet); // yang 用户 
```

## Realm 验证

```java
public class CustomRealm extends AuthorizingRealm {

    @Autowired
    private LoginService loginService;

    @Override   // 权限验证
    protected AuthorizationInfo doGetAuthorizationInfo(PrincipalCollection principalCollection) {
        // 获取登录用户名
        String name = (String) principalCollection.getPrimaryPrincipal();
        // 根据用户名去数据库查询用户信息
        User user = loginService.getUserByName(name);

        // 添加角色和权限
        SimpleAuthorizationInfo simpleAuthorizationInfo = new SimpleAuthorizationInfo();
        for (Role role: user.getRolse()) {
            // 添加角色
            simpleAuthorizationInfo.addRole(role.getRoleName());
            // 添加权限
            for (Permissions permissions: role.getPermissions()) {
                simpleAuthorizationInfo.addStringPermission(permissions.getPermissionName());
            }
        }
        return simpleAuthorizationInfo;
    }

    @Override   // 用户名密码验证
    protected AuthenticationInfo doGetAuthenticationInfo(AuthenticationToken authenticationToken) throws AuthenticationException {
        // 在Post请求的时候会先进认证，然后在到请求
        if (authenticationToken.getPrincipal() == null) {
            return null;
        }
        // 获取用户信息
        String name = authenticationToken.getPrincipal().toString();
        User user = loginService.getUserByName(name);
        if (user == null) {
            return null;
        } else {
            //验证authenticationToken和simpleAuthenticationInfo的信息
            SimpleAuthenticationInfo simpleAuthenticationInfo =
                    new SimpleAuthenticationInfo(name, user.getPassword().toString(), getName());
            return simpleAuthenticationInfo;
        }
    }
}
```

## ShiroConfig

```java
@Configuration
public class ShiroConfig {

    @Bean
    @ConditionalOnMissingBean
    public DefaultAdvisorAutoProxyCreator defaultAdvisorAutoProxyCreator() {
        DefaultAdvisorAutoProxyCreator defaultAAP = new DefaultAdvisorAutoProxyCreator();
        defaultAAP.setProxyTargetClass(true);
        return defaultAAP;
    }

    // 将自己的验证方式加入容器
    @Bean
    public CustomRealm getCustomRealm() {
        CustomRealm customRealm = new CustomRealm();
        return customRealm;
    }

    // 权限管理，配置主要是Realm的管理验证
    @Bean
    public SecurityManager securityManager() {
        DefaultWebSecurityManager securityManager = new DefaultWebSecurityManager();
        securityManager.setRealm(getCustomRealm());
        return securityManager;
    }

    // Filter 工厂，设置对应的过滤条件和跳转条件
    @Bean
    public ShiroFilterFactoryBean shiroFilterFactoryBean(SecurityManager securityManager) {
        ShiroFilterFactoryBean shiroFilterFactoryBean = new ShiroFilterFactoryBean();
        shiroFilterFactoryBean.setSecurityManager(securityManager);
        shiroFilterFactoryBean.setLoginUrl("/login");        // 登录
        shiroFilterFactoryBean.setSuccessUrl("/index");      // 首页
        shiroFilterFactoryBean.setUnauthorizedUrl("/error"); // 认证不通过跳转错误页面
        /**
         * anon：匿名用户可访问
         * authc：认证用户可访问
         * user：使用rememberMe可访问
         * perms：对应权限可访问
         * role：对应角色权限可访问
         **/
        Map<String, String> map = new HashMap<>();
        map.put("/logout", "logout");    // 登出
        map.put("/**", "authc");         // 对所有用户认证
        map.put("/student", "anon");     // 不用登录也可访问
        map.put("/user/index","authc");  // 认证用户可访问
        shiroFilterFactoryBean.setFilterChainDefinitionMap(map);
        return shiroFilterFactoryBean;
    }

    @Bean
    public AuthorizationAttributeSourceAdvisor authorizationAttributeSourceAdvisor(SecurityManager securityManager){
        AuthorizationAttributeSourceAdvisor authorizationAttributeSourceAdvisor = new AuthorizationAttributeSourceAdvisor();
        authorizationAttributeSourceAdvisor.setSecurityManager(securityManager);
        return authorizationAttributeSourceAdvisor;
    }
}
```

## 测试

```java
@RestController
public class LoginController {
    @RequestMapping("/login")
    public String login(User user) {
        //添加用户认证信息
        Subject subject = SecurityUtils.getSubject();
        UsernamePasswordToken usernamePasswordToken = new UsernamePasswordToken(
                user.getUserName(), user.getPassword());
        try {
            //进行验证，这里可以捕获异常，然后返回对应信息
            subject.login(usernamePasswordToken);
        } catch (AuthenticationException e) {
            return "账号或密码错误！";
        } catch (AuthorizationException e) {
            return "没有权限";
        }
        return "登录成功";
    }

    // 注解验角色和权限
    @RequiresRoles("admin")
    @RequiresPermissions("add")
    @RequestMapping("/index")
    public String index() {
        return "index";
    }
}
```

## 注解

- @RequiresGuest          代表无需认证即可访问，同理的就是 /path = anon
- @RequiresAuthentication 需要认证，只要登录成功后就允许你操作
- @RequiresPermissions    需要特定的权限，没有则抛出 AuthorizationException
- @RequiresRoles          需要特定的角色，没有则抛出 AuthorizationException



# reference

https://www.jianshu.com/p/7f724bec3dc3

