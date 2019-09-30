---
layout: post
title: "hdfs客户端操作"
date: 2019-06-09
description: "简单介绍一下hdfs客户端操作"
tag: Hadoop

---

# hdfs客户端

1. 创建Maven项目

2. xml依赖

```xml
<dependencies>
		<dependency>
			<groupId>junit</groupId>
			<artifactId>junit</artifactId>
			<version>RELEASE</version>
		</dependency>
		<dependency>
			<groupId>org.apache.logging.log4j</groupId>
			<artifactId>log4j-core</artifactId>
			<version>2.8.2</version>
		</dependency>
		<dependency>
			<groupId>org.apache.hadoop</groupId>
			<artifactId>hadoop-common</artifactId>
			<version>2.7.2</version>
		</dependency>
		<dependency>
			<groupId>org.apache.hadoop</groupId>
			<artifactId>hadoop-client</artifactId>
			<version>2.7.2</version>
		</dependency>
		<dependency>
			<groupId>org.apache.hadoop</groupId>
			<artifactId>hadoop-hdfs</artifactId>
			<version>2.7.2</version>
		</dependency>
</dependencies>
```

3. 创建src/main/resources/log4j.properties

```
log4j.rootLogger=INFO, stdout
log4j.appender.stdout=org.apache.log4j.ConsoleAppender
log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
log4j.appender.stdout.layout.ConversionPattern=%d %p [%c] - %m%n
log4j.appender.logfile=org.apache.log4j.FileAppender
log4j.appender.logfile.File=target/spring.log
log4j.appender.logfile.layout=org.apache.log4j.PatternLayout
log4j.appender.logfile.layout.ConversionPattern=%d %p [%c] - %m%n
```

注意：

5. 配置 Run configurations：
在VM arguments 增加用户：-DHADOOP_USER_NAME=yangja
未添加直接用junit测试并没报错

6. Windows环境没配置hadoop会报错，但是能够成功运行结果
> Failed to locate the winutils binary in the hadoop binary path

7. 测试代码

```java
package test;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.BlockLocation;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.LocatedFileStatus;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.RemoteIterator;
import org.apache.hadoop.io.IOUtils;
import org.junit.Test;

public class HdfsClient {
	
	@Test
	public void testHdfs() throws IOException, InterruptedException, URISyntaxException {
		
		// 获取文件系统
		Configuration conf = new Configuration();
		FileSystem fs = FileSystem.get(new URI("hdfs://172.16.7.124:9000"), conf, "yangja");
		
		// 1、创建目录
		fs.mkdirs(new Path("/hdfsClient2"));
		
		// 2、上传文件
		fs.copyFromLocalFile(new Path("e:/1.txt"), new Path("/hdfsClient/2.txt"));
		
		// 3、下载文件（是否删除原文件，下载的路径，下载到的路径，文件是否校验）
		fs.copyToLocalFile(true, new Path("/hdfsClient/2.txt"), new Path("e:/2.txt"), true);
		
		// 4、是删除目录、文件
		fs.delete(new Path("/hdfsClient2"));
		fs.delete(new Path("/hdfsClient/1.txt"));
		
		// 5、文件更名
		fs.rename(new Path("/1.txt"), new Path("/2.txt"));
		
		// 6、获取文件详情
		RemoteIterator<LocatedFileStatus> listFiles = fs.listFiles(new Path("/"), true);
		while(listFiles.hasNext()) {
			LocatedFileStatus status = listFiles.next();
			System.out.println(status.getPath().getName()); // 文件名
			System.out.println(status.getLen());            // 长度
			System.out.println(status.getPermission());     // 权限
			System.out.println(status.getGroup());          // 分组
			
			// 获取存储的块信息
			BlockLocation[] bls = status.getBlockLocations();
			for (BlockLocation bl : bls) {
				String[] hosts = bl.getHosts();
				for(String host: hosts) {
					System.out.println(host);
				}
			}
		}
		
		// 7、文件与文件夹判断（当前目录）
		FileStatus[] listStatus = fs.listStatus(new Path("/"));
		for (FileStatus fss : listStatus) {
			if (fss.isFile()) {
				System.out.println("f:"+fss.getPath().getName());
			} else {
				System.out.println("d:"+fss.getPath().getName());
			}
		}
		
		
		// 8、基于流的上传
		FileInputStream fis = new FileInputStream(new File("e:/1.txt"));
		FSDataOutputStream fos = fs.create(new Path("/3.txt"));
		IOUtils.copyBytes(fis, fos, conf);
		IOUtils.closeStream(fos);
		IOUtils.closeStream(fis);
		
		// 9、基于流的下载
		FSDataInputStream ffis = fs.open(new Path("/3.txt"));
		FileOutputStream ffos = new FileOutputStream(new File("e:/3.txt"));
		IOUtils.copyBytes(ffis, ffos, conf);
		IOUtils.closeStream(ffos);
		IOUtils.closeStream(ffis);
		
		System.out.println("test is OK");
		// 关闭资源
		fs.close();
	}
}
```

