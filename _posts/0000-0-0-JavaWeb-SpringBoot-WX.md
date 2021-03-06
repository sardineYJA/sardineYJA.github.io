---
layout: post
title: "SpringBoot 项目案例"
date: 2019-12-26
description: "SpringBoot 项目案例"
tag: Java Web

---


# MySql 数据库

```sql
-- 类目
create table `product_category` (
    `category_id` int not null auto_increment,
    `category_name` varchar(64) not null comment '类目名字',
    `category_type` int not null comment '类目编号',
    `create_time` timestamp not null default current_timestamp comment '创建时间',
    `update_time` timestamp not null default current_timestamp on update current_timestamp comment '修改时间',
    primary key (`category_id`)
);

-- 商品
create table `product_info` (
    `product_id` varchar(32) not null,
    `product_name` varchar(64) not null comment '商品名称',
    `product_price` decimal(8,2) not null comment '单价',
    `product_stock` int not null comment '库存',
    `product_description` varchar(64) comment '描述',
    `product_icon` varchar(512) comment '小图',
    `product_status` tinyint(3) DEFAULT '0' COMMENT '商品状态,0正常1下架',
    `category_type` int not null comment '类目编号',
    `create_time` timestamp not null default current_timestamp comment '创建时间',
    `update_time` timestamp not null default current_timestamp on update current_timestamp comment '修改时间',
    primary key (`product_id`)
);

-- 订单
create table `order_master` (
    `order_id` varchar(32) not null,
    `buyer_name` varchar(32) not null comment '买家名字',
    `buyer_phone` varchar(32) not null comment '买家电话',
    `buyer_address` varchar(128) not null comment '买家地址',
    `buyer_openid` varchar(64) not null comment '买家微信openid',
    `order_amount` decimal(8,2) not null comment '订单总金额',
    `order_status` tinyint(3) not null default '0' comment '订单状态, 默认为新下单',
    `pay_status` tinyint(3) not null default '0' comment '支付状态, 默认未支付',
    `create_time` timestamp not null default current_timestamp comment '创建时间',
    `update_time` timestamp not null default current_timestamp on update current_timestamp comment '修改时间',
    primary key (`order_id`),
    key `idx_buyer_openid` (`buyer_openid`)
);

-- 订单商品
create table `order_detail` (
    `detail_id` varchar(32) not null,
    `order_id` varchar(32) not null,
    `product_id` varchar(32) not null,
    `product_name` varchar(64) not null comment '商品名称',
    `product_price` decimal(8,2) not null comment '当前价格,单位分',
    `product_quantity` int not null comment '数量',
    `product_icon` varchar(512) comment '小图',
    `create_time` timestamp not null default current_timestamp comment '创建时间',
    `update_time` timestamp not null default current_timestamp on update current_timestamp comment '修改时间',
    primary key (`detail_id`),
    key `idx_order_id` (`order_id`)
);

-- 卖家(登录后台使用, 卖家登录之后可能直接采用微信扫码登录，不使用账号密码)
create table `seller_info` (
    `seller_id` varchar(32) not null,
    `username` varchar(32) not null,
    `password` varchar(32) not null,
    `openid` varchar(64) not null comment '微信openid',
    `create_time` timestamp not null default current_timestamp comment '创建时间',
    `update_time` timestamp not null default current_timestamp on update current_timestamp comment '修改时间',
    primary key (`seller_id`)
) comment '卖家信息表';
```

手动创建数据库和表



# 日志

## slf4j

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Test {
	public static Logger logger = LoggerFactory.getLogger(Test.class);  // 表示当前类
	logger.error("Error Message!");
	logger.warn("Warn Message!");
	logger.info("Info Message!");
	logger.debug("Debug Message!");
}
```

## 修改配置

此配置不仅在控制台输出，并保留在磁盘，info/debug/error/warn日志区分开，按照每天做归档。

在resources下新建logback-spring.xml，配置文件无需任何修改，它也可以被识别。

记得修改：`<property name="log.path" value="D:/log/" />` 目录位置

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- 日志级别从低到高分为TRACE < DEBUG < INFO < WARN < ERROR < FATAL，如果设置为WARN，则低于WARN的信息都不会输出 -->
<!-- scan:当此属性设置为true时，配置文件如果发生改变，将会被重新加载，默认值为true -->
<!-- scanPeriod:设置监测配置文件是否有修改的时间间隔，如果没有给出时间单位，默认单位是毫秒。当scan为true时，此属性生效。默认的时间间隔为1分钟。 -->
<!-- debug:当此属性设置为true时，将打印出logback内部日志信息，实时查看logback运行状态。默认值为false。 -->
<configuration  scan="true" scanPeriod="10 seconds">

    <contextName>logback</contextName>
    <!-- name的值是变量的名称，value的值时变量定义的值。通过定义的值会被插入到logger上下文中。定义变量后，可以使“${}”来使用变量。 -->
    <property name="log.path" value="D:/log/" />

    <!-- 彩色日志 -->
    <!-- 彩色日志依赖的渲染类 -->
    <conversionRule conversionWord="clr" converterClass="org.springframework.boot.logging.logback.ColorConverter" />
    <conversionRule conversionWord="wex" converterClass="org.springframework.boot.logging.logback.WhitespaceThrowableProxyConverter" />
    <conversionRule conversionWord="wEx" converterClass="org.springframework.boot.logging.logback.ExtendedWhitespaceThrowableProxyConverter" />
    <!-- 彩色日志格式 -->
    <property name="CONSOLE_LOG_PATTERN" value="${CONSOLE_LOG_PATTERN:-%clr(%d{yyyy-MM-dd HH:mm:ss.SSS}){faint} %clr(${LOG_LEVEL_PATTERN:-%5p}) %clr(${PID:- }){magenta} %clr(---){faint} %clr([%15.15t]){faint} %clr(%-40.40logger{39}){cyan} %clr(:){faint} %m%n${LOG_EXCEPTION_CONVERSION_WORD:-%wEx}}"/>


    <!--输出到控制台-->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <!--此日志appender是为开发使用，只配置最底级别，控制台输出的日志级别是大于或等于此级别的日志信息-->
        <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
            <level>info</level>
        </filter>
        <encoder>
            <Pattern>${CONSOLE_LOG_PATTERN}</Pattern>
            <!-- 设置字符集 -->
            <charset>UTF-8</charset>
        </encoder>
    </appender>


    <!--输出到文件-->

    <!-- 时间滚动输出 level为 DEBUG 日志 -->
    <appender name="DEBUG_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <!-- 正在记录的日志文件的路径及文件名 -->
        <file>${log.path}/log_debug.log</file>
        <!--日志文件输出格式-->
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>
            <charset>UTF-8</charset> <!-- 设置字符集 -->
        </encoder>
        <!-- 日志记录器的滚动策略，按日期，按大小记录 -->
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <!-- 日志归档 -->
            <fileNamePattern>${log.path}/debug/log-debug-%d{yyyy-MM-dd}.%i.log</fileNamePattern>
            <timeBasedFileNamingAndTriggeringPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
                <maxFileSize>100MB</maxFileSize>
            </timeBasedFileNamingAndTriggeringPolicy>
            <!--日志文件保留天数-->
            <maxHistory>15</maxHistory>
        </rollingPolicy>
        <!-- 此日志文件只记录debug级别的 -->
        <filter class="ch.qos.logback.classic.filter.LevelFilter">
            <level>debug</level>
            <onMatch>ACCEPT</onMatch>
            <onMismatch>DENY</onMismatch>
        </filter>
    </appender>

    <!-- 时间滚动输出 level为 INFO 日志 -->
    <appender name="INFO_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <!-- 正在记录的日志文件的路径及文件名 -->
        <file>${log.path}/log_info.log</file>
        <!--日志文件输出格式-->
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>
            <charset>UTF-8</charset>
        </encoder>
        <!-- 日志记录器的滚动策略，按日期，按大小记录 -->
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <!-- 每天日志归档路径以及格式 -->
            <fileNamePattern>${log.path}/info/log-info-%d{yyyy-MM-dd}.%i.log</fileNamePattern>
            <timeBasedFileNamingAndTriggeringPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
                <maxFileSize>100MB</maxFileSize>
            </timeBasedFileNamingAndTriggeringPolicy>
            <!--日志文件保留天数-->
            <maxHistory>15</maxHistory>
        </rollingPolicy>
        <!-- 此日志文件只记录info级别的 -->
        <filter class="ch.qos.logback.classic.filter.LevelFilter">
            <level>info</level>
            <onMatch>ACCEPT</onMatch>
            <onMismatch>DENY</onMismatch>
        </filter>
    </appender>

    <!-- 时间滚动输出 level为 WARN 日志 -->
    <appender name="WARN_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <!-- 正在记录的日志文件的路径及文件名 -->
        <file>${log.path}/log_warn.log</file>
        <!--日志文件输出格式-->
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>
            <charset>UTF-8</charset> <!-- 此处设置字符集 -->
        </encoder>
        <!-- 日志记录器的滚动策略，按日期，按大小记录 -->
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${log.path}/warn/log-warn-%d{yyyy-MM-dd}.%i.log</fileNamePattern>
            <timeBasedFileNamingAndTriggeringPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
                <maxFileSize>100MB</maxFileSize>
            </timeBasedFileNamingAndTriggeringPolicy>
            <!--日志文件保留天数-->
            <maxHistory>15</maxHistory>
        </rollingPolicy>
        <!-- 此日志文件只记录warn级别的 -->
        <filter class="ch.qos.logback.classic.filter.LevelFilter">
            <level>warn</level>
            <onMatch>ACCEPT</onMatch>
            <onMismatch>DENY</onMismatch>
        </filter>
    </appender>


    <!-- 时间滚动输出 level为 ERROR 日志 -->
    <appender name="ERROR_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <!-- 正在记录的日志文件的路径及文件名 -->
        <file>${log.path}/log_error.log</file>
        <!--日志文件输出格式-->
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>
            <charset>UTF-8</charset> <!-- 此处设置字符集 -->
        </encoder>
        <!-- 日志记录器的滚动策略，按日期，按大小记录 -->
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${log.path}/error/log-error-%d{yyyy-MM-dd}.%i.log</fileNamePattern>
            <timeBasedFileNamingAndTriggeringPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
                <maxFileSize>100MB</maxFileSize>
            </timeBasedFileNamingAndTriggeringPolicy>
            <!--日志文件保留天数-->
            <maxHistory>15</maxHistory>
        </rollingPolicy>
        <!-- 此日志文件只记录ERROR级别的 -->
        <filter class="ch.qos.logback.classic.filter.LevelFilter">
            <level>ERROR</level>
            <onMatch>ACCEPT</onMatch>
            <onMismatch>DENY</onMismatch>
        </filter>
    </appender>


    <root level="info">
        <appender-ref ref="CONSOLE" />
        <appender-ref ref="DEBUG_FILE" />
        <appender-ref ref="INFO_FILE" />
        <appender-ref ref="WARN_FILE" />
        <appender-ref ref="ERROR_FILE" />
    </root>

</configuration>
```

# 依赖

```xml
<!-- 数据连接 -->
<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
</dependency>

<!-- JPA方式操作数据库 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

<!-- 简化Getter/Setter等代码 -->
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
</dependency>
```


# yml 配置文件

## 数据库配合

```sh
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    username: root
    password: 123456
    url: jdbc:mysql://127.0.0.1:3306/sell?characterEncoding=utf-8&useSSL=false
  jpa:
    show-sql: true
```

## 将自定义配置项写成类

```java
@Data                                     // 省略Setter/Getter
@Component
@ConfigurationProperties(prefix = "app")  // 读取配置
public class AppAccountConfig {
    private String appId;
    private String appName;
    // ... 其他字段
}

@Autowired     // 使用时需要装载
private AppAccountConfig appAccountConfig;
```



# dao 层

dataobject 层创建数据库表对应的类

## product_category 表创建相应的类

```java
@Entity          // 运行自动会创建ProductCategory表
@DynamicUpdate   // 当字段相关update_time会随着改变
@Data            // 简化Setter/Getter,toString等
public class ProductCategory {   // 相应数据库表product_category
    @Id
    @GeneratedValue
    private Integer categoryId;
    // ... 其他字段略
}
```

## Repository 操作数据库接口

repository 层创建数据库表对应的类的JPA操作函数（继承接口即可），需要额外功能再接口下增加新的函数

```java
public interface ProductCategoryRepository extends JpaRepository<ProductCategory, Integer> {
    // 符合JPA命名规则的方法定义，创建相应的查询函数
}
```

## 测试类

```java
@RunWith(SpringRunner.class)
@SpringBootTest
public class ProductCategoryRepositoryTest {
    @Autowired
    private ProductCategoryRepository repository;

    @Test
    public void findOneTest() {
        ProductCategory productCategory = repository.findById(1).orElse(null);
        System.out.println(productCategory.toString());
    }
}
```

# Service 层

service 层

即对 Repository 数据库操作接口进行一步封装：

```java
public interface CategoryService {
    ProductCategory findOne(Integer categoryId);
    List<ProductCategory> findAll();
    // ...其他相应查询函数
}
```

```java
@Service
public class CategoryServiceImpl implements CategoryService {

    @Autowired
    private ProductCategoryRepository repository; // 实际使用的还是Repository接口

    @Override
    public ProductCategory findOne(Integer categoryId) {
        return repository.findById(categoryId).orElse(null);
    }

    @Override
    public List<ProductCategory> findAll() {
        return repository.findAll();
    }
    // ...其他相应函数
    // 注意事务的使用 @Transaction
}
```

# Controller 层

```java
@RestController
@RequestMapping("/buyer/product")
public class BuyerProductController {

    @Autowired
    private ProductService productService;

    // ... 其他相关Server类

    @GetMapping("/list")
    public ResultVO list(@RequestParam(value = "sellerId", required = false) String sellerId) {
        // ... 数据库查询逻辑
        // ... 整合数据，并返回
        return ResultVOUtil.success(productVOList);
        // 返回一个类即返回到url/buyer/product/list的json数据
    }

    // ... 其他相关链接响应函数
}
```

对于返回的数据进行封装成 VO 类：

```java
@Data       // Getter&Setting
public class ProductVO implements Serializable {  // 序列化
    @JsonProperty("name")  // 表示返回json时，字段名为name，并非categoryName
    private String categoryName;

    @JsonProperty("type")
    private Integer categoryType;

    @JsonProperty("foods")
    private List<ProductInfoVO> productInfoVOList; // 字段
}
```

ModelAndView 和 Map :

```java
@GetMapping("/list")
public ModelAndView list(Map<String, Object> map) {
    List<ProductCategory> categoryList = categoryService.findAll();
    map.put("categoryList", categoryList);
    return new ModelAndView("category/list", map);  // templates/category/list.html
}
```


# 登录登出

## 保存登录信息

- token(令牌)

- Cookie存储在浏览器，不是很安全。

- Session存储在服务器，当访问增多会比较占用服务器的性能。

- Redis(实现分布式系统下的Session共享)


## Cookie工具类

```java
public class CookieUtil {
    // 设置Session
    public static void set(HttpServletResponse response,
                           String name,
                           String value,
                           int maxAge) {
        Cookie cookie = new Cookie(name, value);
        cookie.setPath("/");
        cookie.setMaxAge(maxAge);
        response.addCookie(cookie);
    }

    // 获取cookie
    public static Cookie get(HttpServletRequest request,
                           String name) {
        Map<String, Cookie> cookieMap = readCookieMap(request);
        if (cookieMap.containsKey(name)) {
            return cookieMap.get(name);
        }else {
            return null;
        }
    }

    // 将cookie封装成Map
    private static Map<String, Cookie> readCookieMap(HttpServletRequest request) {
        Map<String, Cookie> cookieMap = new HashMap<>();
        Cookie[] cookies = request.getCookies();  // 里面可能有多个cookie
        if (cookies != null) {
            for (Cookie cookie: cookies) {
                cookieMap.put(cookie.getName(), cookie);
            }
        }
        return cookieMap;
    }
}
```

## 登录

```java
@GetMapping("/login")
public ModelAndView login(@RequestParam("openid") String openid,
                          HttpServletResponse response,
                          Map<String, Object> map) {

    //1. openid去和数据库里的数据匹配
    SellerInfo sellerInfo = sellerService.findSellerInfoByOpenid(openid);
    if (sellerInfo == null) {
        map.put("msg", "登录成功！");
        map.put("url", "/sell/seller/order/list");
        return new ModelAndView("common/error");    // templates/common/error.html
    }

    //2. 设置token至redis
    String token = UUID.randomUUID().toString();
    Integer expire = RedisConstant.EXPIRE;

    redisTemplate.opsForValue().set(String.format(RedisConstant.TOKEN_PREFIX, token), openid, expire, TimeUnit.SECONDS);

    //3. 设置token至cookie
    CookieUtil.set(response, CookieConstant.TOKEN, token, expire);
    return new ModelAndView("redirect:" + projectUrlConfig.getSell() + "/sell/seller/order/list");
}
```

## 登出

```java
@GetMapping("/logout")
public ModelAndView logout(HttpServletRequest request,
                   HttpServletResponse response,
                   Map<String, Object> map) {
    //1. 从cookie里查询
    Cookie cookie = CookieUtil.get(request, CookieConstant.TOKEN);
    if (cookie != null) {
        //2. 清除redis
        redisTemplate.opsForValue().getOperations().delete(String.format(RedisConstant.TOKEN_PREFIX, cookie.getValue()));

        //3. 清除cookie
        CookieUtil.set(response, CookieConstant.TOKEN, null, 0);
    }

    map.put("msg", ResultEnum.LOGOUT_SUCCESS.getMessage());
    map.put("url", "/sell/seller/order/list");
    return new ModelAndView("common/success", map);
}
```



# AOP 身份验证

## aspect 层

通过切片对访问url进行登录身份验证，非登录则抛出异常，并对异常进行捕获处理并调到登录界面。

```java
@Aspect
@Component
public class SellerAuthorizeAspect {

    @Autowired
    private StringRedisTemplate redisTemplate;

    // 验证范围表达式
    @Pointcut("execution(public * com.imooc.controller.Seller*.*(..))" +
    "&& !execution(public * com.imooc.controller.SellerUserController.*(..))")
    public void verify() {}

    @Before("verify()")         // 验证是否已登录
    public void doVerify() {
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        HttpServletRequest request = attributes.getRequest();

        //查询cookie
        Cookie cookie = CookieUtil.get(request, CookieConstant.TOKEN);
        if (cookie == null) {
            throw new SellerAuthorizeException();
        }

        //去redis里查询
        String tokenValue = redisTemplate.opsForValue().get(String.format(RedisConstant.TOKEN_PREFIX, cookie.getValue()));
        if (StringUtils.isEmpty(tokenValue)) {
            throw new SellerAuthorizeException();
        }
    }
}
```

## @ControllerAdvice 全局异常处理

```java
@ControllerAdvice         // 全局异常处理
public class SellExceptionHandler {
    //拦截登录异常 SellerAuthorizeException
    @ExceptionHandler(value = SellerAuthorizeException.class)
    @ResponseStatus(HttpStatus.FORBIDDEN)
    public ModelAndView handlerAuthorizeException() {
        return new ModelAndView("url");  // 进行登录界面跳转
    }
}
```

@ControllerAdvice 全局异常统一处理的类

@ExceptionHandler 处理具体异常类  

@ResponseStatus(HttpStatus.FORBIDDEN) 表示返回403 Forbidden 页面

@responseBody 该注解表示该方法的返回结果直接写到Http response Body中，不会解析成跳转地址，会解析成相应的json格式的对象 集合、字符串或xml等直接返回给前台。



# mybatis 的使用

## mapper 层

```xml
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>1.2.0</version>
</dependency>
```

```java
@SpringBootApplication
@MapperScan(basePackages = "com.sxdt.dataobject")    // mybatis 操作扫描的包（Mapper接口下）
@EnableCaching                                       // 使用缓存
public class SellApplication {
    public static void main(String[] args) {
        SpringApplication.run(SellApplication.class, args);
    }
}
```


## 注解方式

ProductCategoryMapper是接口，mybatis的dao接口不需要实现类。
jdk proxy 为接口生成了实现对应接口的类。

```java
public interface ProductCategoryMapper {

    @Insert("insert into product_category(category_name, category_type) values (#{categoryName, jdbcType=VARCHAR}, #{category_type, jdbcType=INTEGER})")
    int insertByMap(Map<String, Object> map);

    @Insert("insert into product_category(category_name, category_type) values (#{categoryName, jdbcType=VARCHAR}, #{categoryType, jdbcType=INTEGER})")
    int insertByObject(ProductCategory productCategory);

    @Select("select * from product_category where category_name = #{categoryName}")
    @Results({
        @Result(column = "category_id", property = "categoryId"),
        @Result(column = "category_name", property = "categoryName"),
        @Result(column = "category_type", property = "categoryType")
    })
    List<ProductCategory> findByCategoryName(String categoryName);

    // 两个参数及以上需要@Param指定
    @Update("update product_category set category_name = #{categoryName} where category_type = #{categoryType}")
    int updateByCategoryType(@Param("categoryName") String categoryName, @Param("categoryType") Integer categoryType);

    @Update("update product_category set category_name = #{categoryName} where category_type = #{categoryType}")
    int updateByObject(ProductCategory productCategory);

    @Delete("delete from product_category where category_type = #{categoryType}")
    int deleteByCategoryType(Integer categoryType);
}
```

## 注解的方式

application-dev.yml，
```sh
mybatis:
  mapper-locations: classpath:mapper/*.xml  # resources/mapper/路径下
```

resources/mapper/ProductCategoryMapper.xml
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd" >
<mapper namespace="com.imooc.dataobject.mapper.ProductCategoryMapper" > <!-- ProductCategoryMapper 自动装载类 -->

    <resultMap id="BaseResultMap" type="com.imooc.dataobject.ProductCategory">
        <id column="category_id" property="categoryId" jdbcType="INTEGER" />
        <id column="category_name" property="categoryName" jdbcType="VARCHAR" />
        <id column="category_type" property="categoryType" jdbcType="INTEGER" />
    </resultMap>

    <select id="selectByCategoryType" resultMap="BaseResultMap" parameterType="java.lang.Integer">
        select category_id, category_name, category_type
        from product_category
        where category_type = #{category_type, jdbcType=INTEGER}
    </select>
</mapper>
```


## 测试类

```java
@RunWith(SpringRunner.class)
@SpringBootTest
@Slf4j
public class ProductCategoryMapperTest {

    @Autowired     // 自动装载
    private ProductCategoryMapper mapper;

    @Test
    public void insertByMap() throws Exception {
        Map<String, Object> map = new HashMap<>();
        map.put("categoryName", "yang");
        map.put("category_type", 101);
        int result = mapper.insertByMap(map);
        Assert.assertEquals(1, result);
    }

    @Test
    public void insertByObject() {
        ProductCategory productCategory = new ProductCategory();
        productCategory.setCategoryName("yang");
        productCategory.setCategoryType(102);
        int result = mapper.insertByObject(productCategory);
        Assert.assertEquals(1, result);
    }

    @Test
    public void findByCategoryName() {
        List<ProductCategory> result = mapper.findByCategoryName("yang");
        Assert.assertNotEquals(0, result.size());
    }

    @Test
    public void updateByCategoryType() {
        int result = mapper.updateByCategoryType("yang", 101);
        Assert.assertEquals(1, result);
    }

    @Test
    public void updateByObject() {
        ProductCategory productCategory = new ProductCategory();
        productCategory.setCategoryName("yang");
        productCategory.setCategoryType(102);
        int result = mapper.updateByObject(productCategory);
        Assert.assertEquals(1, result);
    }

    @Test
    public void deleteByCategoryType() {
        int result = mapper.deleteByCategoryType(102);
        Assert.assertEquals(1, result);
    }

    @Test        // 这个测试xml方式
    public void selectByCategoryType() {
        ProductCategory productCategory = mapper.selectByCategoryType(101);
        Assert.assertNotNull(productCategory);
    }
}
```


# 优化

## 操作数据库

操作数据库，选择 JPA 或者 MyBatis 都行

但建表时，建议用sql，不用JPA的方法（后期不好维护）


## 高并发情况需要加锁

高并发请求：`ab -n 500 -c 100 http://127.0.0.1:8080/url`，其中 -n 表示请求数，-c 表示并发数。

synchronize锁（只适合单点即单机模式）

redis分布式锁：多台机器上多个进程对一个数据进行操作的互斥


## 使用 Redis 缓存

缓存：@EnableCaching

- @Cacheable 将函数返回的结果（可序列化），放到Cache中，下次再运行时不再运行函数，直接从Cache获取，用在查询函数中

- @CachePut 将函数返回的结果（可序列化），重新放到Cache，用在修改函数中

- @CacheEvict 将Cache清除掉，用在修改函数中

```java
@Cacheable(cacheNames = "product", key = "#sellerId")
public ResultVO list(@RequestParam(value = "sellerId", required = false) String sellerId) {
    pass;
}
```

## 部署

tomcat 方式：

java -jar 方式：


# reference

https://coding.imooc.com/class/117.html

https://www.cnblogs.com/zhangjianbing/p/8992897.html


