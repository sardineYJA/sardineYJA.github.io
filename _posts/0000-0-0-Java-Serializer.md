---
layout: post
title: "Java 常用序列化方式"
date: 2019-11-21
description: "常用序列化方式"
tag: Java

---


# 总结

序列化是经常需要处理的问题，比如在做分布式访问数据时，或是在做redis缓存存储数据时，需要序列化的类上implements Serializable接口去实现序列化，这种方式对并发很大的系统会受到严重影响，应此需要高效序列化的方式。

- 首推使用protostuff序列化，方便使用
 
- 如果需要可读性，或要求json格式，则推荐FastJson

- 空间需要极小（尽可能），则用Kryo

本人并没有进行测试，只是总结前人的经验。


# 序列化方式

## Serializable（Java原生）

- 无法跨语言
- 序列化后的码流太大
- 序列化性能低

## avro

- 速度快
- 序列化后体积小
- 提供rpc服务
- 需要自己写.avsc文件

## thrift（Facebook）

- 支持多种语言
- 适用大型系统中内部数据传输
- 提供rpc服务

## protobuf（Google）

- 高性能编解码
- 支持Java, C++, Python
- 结构化数据存储格式
- 序列化数据体积小
- 需要自己写.proto文件

## protostuff

- 基于protobuf实现的序列化方法
- 好处是不用写.proto文件来实现序列化

## Kryo

- 速度快
- 序列化后体积小
- 跨语言支持较复杂

## FastJson（Alibaba）

- 序列化成Json
- 无依赖，不需额外jar
- 高性能Json处理器


# 案例

## Serializable

```java
// 类直接implements Serializable即可序列化和反序列化
// 序列化
ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream("students.ser"));
out.writeObject(student);
// 反序列化
ObjectInputStream in = new ObjectInputStream(new FileInputStream("students.ser"));
Student s = (Student)in.readObject();
```

## avro

依赖：
```xml
<dependency>
	<groupId>org.apache.avro</groupId>
	<artifactId>avro</artifactId>
	<version>1.8.2</version>
</dependency>
```

定义schema，格式为avro文件：
```json
{"namespace": "com.sxdt.avro（包名）",
 "type": "record",
 "name": "Student（类名）",
 "fields": [
     {"name": "name", "type": "string"},
     {"name": "age",  "type": ["int", "null"]},
     {"name": "sex", "type": ["string", "null"]}
 ]
}
```

通过avro的工具生成Student.java：

工具下载：http://www.apache.org/dyn/closer.cgi/avro/

命令：`java -jar avro-tools-1.9.0.jar compile schema student.avsc`

还可以使用maven方式（推荐）生成Student.java，maven install即可：

```xml
<plugin>
    <groupId>org.apache.avro</groupId>
    <artifactId>avro-maven-plugin</artifactId>
    <version>1.8.2</version>
    <executions>
        <execution>
            <phase>generate-sources</phase>
            <goals>
                <goal>schema</goal>
                <goal>protocol</goal>
                <goal>idl-protocol</goal>
            </goals>
            <configuration>
                <!-- 源目录，用于存放avro的schema文件及protocol文件 ,如果没加如下配置
                那么默认从/src/main/avro下面找avsc文件，生成的java文件放到target/generated-sources/avro下面-->
                <sourceDirectory> ${project.basedir}/src/main/avro/</sourceDirectory>
                <outputDirectory> ${project.basedir}/src/main/java/</outputDirectory>
            </configuration>
        </execution>
    </executions>
</plugin>
```


```java
// 序列化
DatumWriter<Student> dw = new SpecificDatumWriter<Student>(Student.class);
DataFileWriter<Student> fw = new DataFileWriter<Student>(dw);
fw.create(s1.getSchema(), new File("student.avro"));  // 需要getSchema()
fw.append(s1);
fw.append(s2);
// 反序列化
DatumReader<Student> dr = new SpecificDatumReader<Student>(Student.class);
DataFileReader<Student> fr = new DataFileReader<Student>(new File("student.avro"), dr);
Student s = null;
while (fr.hasNext()) {
	s = fr.next(s);
}
```

## protobuf

IDEA安装protobuf：File --> Settings --> Plugins

依赖：
```xml
<properties>
    <os.detected.classifier>windows-x86_64</os.detected.classifier>
</properties>

<dependency>
    <groupId>com.google.protobuf</groupId>
    <artifactId>protobuf-java</artifactId>
    <version>3.1.0</version>
</dependency>

<!-- protobuf 编译组件 -->
<plugin>
    <groupId>org.xolstice.maven.plugins</groupId>
    <artifactId>protobuf-maven-plugin</artifactId>
    <version>0.5.1</version>
    <extensions>true</extensions>
    <configuration>
        <!-- proto文件所在目录 -->
        <protoSourceRoot>${project.basedir}/src/main/proto</protoSourceRoot>
        <!-- 产生java所在目录 -->
        <outputDirectory>${project.basedir}/src/main/proto</outputDirectory>
        <!--设置是否在生成java文件之前清空outputDirectory的文件，默认值为true，设置为false时也会覆盖同名文件-->
        <clearOutputDirectory>false</clearOutputDirectory>
        <protocArtifact>com.google.protobuf:protoc:3.1.0:exe:${os.detected.classifier}</protocArtifact>
    </configuration>
    <executions>
        <execution>
            <goals>
                <goal>compile</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

Maven:Plugins:protobuf:compile --> Student.proto文件：
```sh
syntax = "proto3";
option java_package = "Seri";           # 包名  
option java_outer_classname = "Person"; # 外部类名，默认文件名
message Student {             # 这个才是类名，序列化的类
     int32 id = 1;            # 变量序号1,2,3...
     string name = 2;
     string sex = 3;
}
```

```java
Person.Student.Builder builder = Person.Student.newBuilder();
builder.setName("yang");
builder.setSex("male");
Person.Student ps = builder.build();

byte[] array = ps.toByteArray();                      // 序列化
Person.Student ss = Person.Student.parseFrom(array);  // 反序列化
```

## protostuff

```xml
<dependency>
    <groupId>io.protostuff</groupId>
    <artifactId>protostuff-runtime</artifactId>
    <version>1.5.3</version>
</dependency>
<dependency>
    <groupId>io.protostuff</groupId>
    <artifactId>protostuff-core</artifactId>
    <version>1.5.3</version>
</dependency>
```

```java
public class MyProtoBufUtil {
    public MyProtoBufUtil() {}
    // 序列化 // 
    public static <T> byte[] serializer(T o) {    
        Schema schema = RuntimeSchema.getSchema(o.getClass());
        return ProtobufIOUtil.toByteArray(o, schema, LinkedBuffer.allocate(256));
    }
    // 反序列化 //
    public static <T> T deserializer(byte[] bytes, Class<T> clazz) throws IllegalAccessException, InstantiationException {
        T obj = null;
        obj = clazz.newInstance();
        Schema schema = RuntimeSchema.getSchema(obj.getClass());
        ProtostuffIOUtil.mergeFrom(bytes, obj, schema);
        return obj;
    }
}

byte[] array = MyProtoBufUtil.serializer(s);  // 序列化Studnet s 
Student ss = MyProtoBufUtil.deserializer(array, Student.class); // 反序列化
```

## FastJson

```xml
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>fastjson</artifactId>
    <version>1.2.47</version>
</dependency>
```

```java
String json = JSONObject.toJSONString(s);   // Student s 对象序列化成Json
Student sj = JSONObject.parseObject(json, Student.class); // json 反序列成对象
```


# reference

https://blog.csdn.net/qq_32523587/article/details/90551340

https://www.cnblogs.com/niutao/p/10548003.html

https://www.jianshu.com/p/b360c64bdbe4

