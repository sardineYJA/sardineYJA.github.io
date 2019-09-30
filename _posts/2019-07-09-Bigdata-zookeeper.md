---
layout: post
title: "Zookeeper"
date: 2019-07-09
description: "介绍一下Zookeeper"
tag: Bigdata

---

# Zookeeper

为分布式应用提供协调服务：统一命名服务、统一配置管理、统一集群管理、服务器节点动态上下线、软负载均衡等

是一个基于观察者模式设计的分布式服务管理框架，负责存储和管理大家都关心的数据，然后接受观察者的注册，一旦这些数据的状态发生变化，Zookeeper负责通知已经注册的观察者做出相应的反应


## 特点

1. 一个Leader，多个Follower

2. 集群中只要半数以上节点存活就能正常服务

3. 全局数据一致：每个Server保存一份相同的数据副本，Client无论连接到哪个Server，数据都是一致的

4. 数据更新原子性


# 内部原理

## 选举机制

1. 半数机制：集群中半数以上机器存活，集群可用，适合安装奇数台服务器

2. 选举机制：Leader是通过内部的选举机制临时产生

## 节点类型

1. 持久（persistent）：客户端与服务器端断开连接后，创建的节点不删除

2. 短暂（ephemeral）：客户端与服务器端断开连接后，创建的节点自己删除

## Stat结构体


## 监听器原理

1. main()线程中创建zkClient客户端

2. zkClient创建俩个线程：connect负责网络连接通信，listener负责监听

3. 通过connect线程将注册的监听事件发送给Zookeeper

4. 在Zookeeper的注册监听器列表中将注册的监听事件添加到列表中

5. Zookeeper监听到有数据或路径变化，就会将消息发送给listener线程

6. listener线程内部调用process()方法


## 写数据流程

1. Client向Zookeeper的Server发送写请求

2. Server不是Learder，则Server将请求发送给Leader。Leader将写请求广播给各个Server

3. 各个Server完成写请求，通知Leader

4. Leader收到半数以上的通知，则说明数据写成功

5. Leader会通知先前的Server，由先前的Server通知Client完成写操作


# 安装部署

## 本地模式

1. 下载：https://zookeeper.apache.org

2. 解压：tar -zxvf zookeeper-3.4.10.tar.gz -C /../module/

3. 创建../zookeeper-3.4.10/zkData 目录

4. 配置文件conf目录：cp zoo_sample.cfg zoo.cfg

5. 修改zoo.cfg文件

```
dataDir=/.../zookeeper-3.4.10/zkData
```

6. 启动：bin/zkServer.sh start

7. 查看进程jps：QuorumPeerMain

8. 查看状态：bin/zkServer.sh status

9. 启动客户端：bin/zkCli.sh

10. 退出客户端：quit

11. 停止Zookeeper：bin/zkServer.sh stop


## 分布式安装

1. 创建zkData/myid文件，并写入

```
1
```

2. 编辑zoo.cfg，dataDir要绝对路径

```
dataDir=/.../zookeeper-3.4.10/zkData
#######################cluster##########################
server.1=hadoop101:2888:3888
server.2=hadoop102:2888:3888
server.3=hadoop103:2888:3888
```

3. 同步各个节点的配置文件，除了myid文件

4. 各个节点分别启动


# 客户端操作

启动客户端：bin/zkCli.sh

命令
```
help               显示所有操作
ls /               显示当前znode中包含的内容
ls /jiedian watch  监听路径变化
ls2 /              当前znode详细数据
create /jiedian "context"   创建节点（-s含序列，-e临时）
get /jiedian       获取节点的值
get /jiedian watch 监听值的变化
set /jiedian       修改节点的值
stat /jiedian      节点状态
delete /jiedian    删除节点
rmr    /jiedian    递归删除节点
```


# 项目

1. 创建Maven项目

2. 添加依赖

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
		<groupId>org.apache.zookeeper</groupId>
		<artifactId>zookeeper</artifactId>
		<version>3.4.10</version>
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

4. 测试zookeeper客户端操作命令

```java
import java.io.IOException;
import java.util.List;

import org.apache.zookeeper.CreateMode;
import org.apache.zookeeper.KeeperException;
import org.apache.zookeeper.WatchedEvent;
import org.apache.zookeeper.Watcher;
import org.apache.zookeeper.ZooDefs.Ids;
import org.apache.zookeeper.ZooKeeper;
import org.apache.zookeeper.data.Stat;
import org.junit.Before;
import org.junit.Test;

public class TestZnode {
	private static String connectString = "172.16.7.124:2181";
	// 多个节点逗号隔开"172.16.7.124:2181,172.16.7.125:2181"
	private static int sessionTimeout = 2000;
	private ZooKeeper zkClient = null;
	
	@Before
	public void init() throws IOException {
		System.out.println("--------init--------");
		zkClient = new ZooKeeper(connectString, sessionTimeout, new Watcher() {
			@Override
			public void process(WatchedEvent event) {
				System.out.println("--------process--------");
				// 收到事件通知后的回调函数（用户的业务逻辑）
				System.out.println(event.getType() + "--" + event.getPath());
				// 再次启动监听
				try {
					zkClient.getChildren("/", true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}
	
	// 创建子节点
	@Test
	public void create() throws KeeperException, InterruptedException {
		System.out.println("--------create--------");
		String nodeCreated = zkClient.create(
				"/jiedian",             // 创建的节点的路径
				"context".getBytes(),   // 节点数据
				Ids.OPEN_ACL_UNSAFE,    // 节点权限
				CreateMode.PERSISTENT); // 节点类型
	}
	
	// 获取子节点并监听节点变化
	@Test
	public void getChildren() throws KeeperException, InterruptedException {
		System.out.println("--------getChildren--------");
		List<String> children = zkClient.getChildren("/", true);
		for (String child: children) {
			System.out.println(child);
		}
	}
	
	// 判断Znode是否存在
	@Test
	public void exist() throws KeeperException, InterruptedException {
		System.out.println("--------exist--------");
		Stat stat = zkClient.exists("/jiedian", false);
		System.out.println(stat == null ? "not exist" : "exist");
	}
}
```

# 监听服务器节点动态上下线案例

## 需求

某分布式系统中，主节点可以有多台，可以动态上下线，任意一台客户端都能实时感知到主节点服务器的上下线

1. 先在集群上创建/servers节点：`create /servers "servers"`

2. 服务器端向Zookeeper注册

```java
import java.io.IOException;

import org.apache.zookeeper.CreateMode;
import org.apache.zookeeper.KeeperException;
import org.apache.zookeeper.WatchedEvent;
import org.apache.zookeeper.Watcher;
import org.apache.zookeeper.ZooDefs.Ids;
import org.apache.zookeeper.ZooKeeper;

public class DistributeServer {
	
	private static String connectString = "172.16.7.124:2181";
	private static int sessionTimeout = 2000;
	private ZooKeeper zk = null;
	private String parentNode = "/servers";
	
	// 创建到zk的客户端连接
	public void getConnect() throws IOException {
		zk = new ZooKeeper(connectString, sessionTimeout, new Watcher() {
			@Override
			public void process(WatchedEvent event) {
				
			}
		});
	}
	
	// 注册服务器
	public void registServer(String hostname) throws KeeperException, InterruptedException {
		String create = zk.create(
				parentNode+"/server",
				hostname.getBytes(),
				Ids.OPEN_ACL_UNSAFE,
				CreateMode.EPHEMERAL_SEQUENTIAL);
		System.out.println(hostname+" is online "+create);
	}
	
	// 业务功能
	public void business(String hostname) throws InterruptedException {
		System.out.println(hostname+" is working...");
		Thread.sleep(Long.MAX_VALUE);
	}

	public static void main(String[] args) throws KeeperException, InterruptedException, IOException {
		// 1、获取zk连接
		DistributeServer server = new DistributeServer();
		server.getConnect();
		
		// 2、利用zk连接注册服务器信息
		server.registServer(args[0]);
		
		// 3、启动业务功能
		server.business(args[0]);
	}
}
```

3. 客户端代码

```java
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.zookeeper.WatchedEvent;
import org.apache.zookeeper.Watcher;
import org.apache.zookeeper.ZooKeeper;

public class DistributeClient {
	
	private static String connectString = "172.16.7.124:2181";
	private static int sessionTimeout = 2000;
	private ZooKeeper zk = null;
	private String parentNode = "/servers";
	
	// 创建到zk的客户端连接
	public void getConnect() throws IOException {
		zk = new ZooKeeper(connectString, sessionTimeout, new Watcher() {
			@Override
			public void process(WatchedEvent event) {
				// 再次启动监听
				try {
					getServerList();
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}
	
	// 获取服务器列表信息
	public void getServerList() throws Exception {
		// 1、获取服务器子节点信息，并且对父节点进行监听
		List<String> children = zk.getChildren(parentNode, true);
        // 2、存储服务器信息列表
		ArrayList<String> servers = new ArrayList<>();
        // 3、遍历所有节点，获取节点中的主机名称信息
		for (String child : children) {
			byte[] data = zk.getData(parentNode + "/" + child, false, null);
			servers.add(new String(data));
		}
        // 4、打印服务器列表信息
		System.out.println(servers);
	}

	// 业务功能
	public void business() throws Exception{
		System.out.println("client is working ...");
		Thread.sleep(Long.MAX_VALUE);
	}

	public static void main(String[] args) throws Exception {

		// 1、获取zk连接
		DistributeClient client = new DistributeClient();
		client.getConnect();

		// 2、获取servers的子节点信息，从中获取服务器信息列表
		client.getServerList();

		// 3、业务进程启动
		client.business();
	}
}
```


