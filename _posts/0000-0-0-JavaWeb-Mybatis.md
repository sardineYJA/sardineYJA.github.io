---
layout: post
title: "Mybatis 基础使用"
date: 2018-03-03
description: "Mybatis"
tag: Java Web

---


# Maven 项目

## pom.xml

```xml
    <dependencies>
        <!-- mybatis核心包 -->
        <dependency>
            <groupId>org.mybatis</groupId>
            <artifactId>mybatis</artifactId>
            <version>3.3.0</version>
        </dependency>
        <!-- mysql驱动包 -->
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <version>5.1.29</version>
        </dependency>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.11</version>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <version>1.16.12</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <source>1.8</source>
                    <target>1.8</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
```

## 数据表创建相应类

com.example.bigdata.Entity层

```java
@Data
public class StudentEntity {
    private int id;
    private String name;
    private int age;
}
```

## 创建相应的数据库操作接口

com.example.bigdata.Dao层
```java
public interface StudentEntityDao {
    public List<StudentEntity> getListByName(String name);
    public boolean addStudent(StudentEntity student);          // 会自动返回影响条数
    ...
}
```



## 创建Mapper配置

resource/mapper/bigdata/mybatis-config.xml

在配置文件中设置数据库连接池（效率低，真实开发中不适用)以及配置映射关系

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration
        PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-config.dtd">

<configuration>
    <!-- 环境配置 -->
    <environments default="development">
        <environment id="development">
            <transactionManager type="JDBC"/>
            <!-- 数据库连接相关配置 ,这里动态获取config.properties文件中的内容-->
            <dataSource type="POOLED">
                <property name="driver" value="com.mysql.jdbc.Driver" />
                <property name="url" value="jdbc:mysql://192.168.243.124:3306/test" />
                <property name="username" value="root" />
                <property name="password" value="123456" />
            </dataSource>
        </environment>
    </environments>

    <!-- mapping文件路径配置 -->
    <mappers>
        <mapper resource="mapper/bigdata/student/StudentMapper.xml"/>
       	<!-- 或者下面写法 -->
        <!-- <package name="com.example.bigdata.Dao"/> -->
    </mappers>

</configuration>
```

## 创建表对应Mapper

resource/mapper/bigdata/student/StudentMapper.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<!--
mapper为映射的根节点，namespace指定Dao接口的完整类名，
依据这个接口动态创建一个实现类去实现这个接口，而这个实现类是一个Mapper对象
-->
<mapper namespace="com.example.bigdata.Entity.StudentEntity">

    <!--id ="接口中的方法名" parameterType="传入的参数类型" resultType = "返回实体类对象，使用包.类名"-->
    <select id="findById" parameterType="int" resultType="com.example.bigdata.Entity.StudentEntity">
    select * from student where id = #{id}
    </select>

    <select id="getListByName" parameterType="String" resultType="map">
    select * from student where name = #{name}
    </select>

</mapper>
```

## 测试

```java
@Test
public void test() throws IOException {

    String resources = "mapper/bigdata/mybatis-config.xml";
    // 读取mybatis-config.xml文件到reader对象中
    Reader reader = Resources.getResourceAsReader(resources);
    // 初始化mybatis,创建SqlSessionFactory类的实例
    SqlSessionFactory sqlMapper = new SqlSessionFactoryBuilder().build(reader);
    SqlSession session = sqlMapper.openSession();

    StudentEntity student = session.selectOne("findById",1);
    System.out.println(student.getName());


    // 第一种：根据xml文件定义接口的id查询
    StudentEntity student = session.selectOne("findById",1);
    System.out.println(student.getName());

    // 第二种：根据实现Dao接口查询（方法必须在接口定义），建议使用Mapper接口这种好
    StudentEntityDao studentEntityDao = session.getMapper(StudentEntityDao.class);
    List<StudentEntity> studnetList = studentEntityDao.getListByName("yang");
    System.out.println(studnetList);

    // 对于增删改操作，需要提交
    session.commit();
    session.close();
}
```



## 可以使用properties配置数据库

```xml
<properties resource="db.properties"></properties>   <!-- 增加路径 -->

<environments default="development">
    <environment id="development">
        <transactionManager type="JDBC"/>
        <dataSource type="POOLED">
            <property name="driver" value="${jdbc.driver}" /> <!-- 修改 -->
            <property name="url" value="${jdbc.url}" />
            <property name="username" value="${jdbc.username}" />
            <property name="password" value="${jdbc.password}" />
        </dataSource>
    </environment>
</environments>
```


## 多参数传递

第一种方式：接口方法中增加 @Param
```java
FindBy(@Param("name")String name, @Param("age")Integer age);
```
```xml
<select>
select * from student where name = #{name} and age = #{age}
</select>
```

第二种方式：
```xml
<select>
select * from student where name = #{0} and age = #{1}
</select>
```

# 分页


# SpringBoot 使用 Mybatis


