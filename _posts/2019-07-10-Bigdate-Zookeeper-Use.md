---
layout: post
title: "Zookeeper 场景实践"
date: 2019-07-10
description: "Zookeeper 场景实践"
tag: Bigdata

---

# 简介

Zookeeper作为一个集群提供一致的数据服务，自然，它要在所有机器间做数据复制。

数据复制的好处：容错，提高系统的扩展能力，把负载分布到多个节点上，或者增加节点来提高系统的负载能力；提高性能
，让客户端本地访问就近的节点，提高用户访问速度。


# 应用场景

## 统一命名服务

![png](/images/posts/all/Zookeeper应用-统一命名服务.PNG)

## 统一配置管理

![png](/images/posts/all/Zookeeper应用-统一配置管理.PNG)

## 统一集群管理

![png](/images/posts/all/Zookeeper应用-统一集群管理.PNG)

## 服务器动态上下线

![png](/images/posts/all/Zookeeper应用-服务器动态上下线.PNG)

## 软负载均衡

![png](/images/posts/all/Zookeeper应用-软负载均衡.PNG)


## 分布式锁

锁服务可以分为两类，一个是保持独占，另一个是控制时序。

第一类，将zookeeper上的一个znode看作是一把锁，通过createznode的方式来实现。
所有客户端都去创建 /distribute_lock 节点，最终成功创建的那个客户端也即拥有了这把锁。
用完删除掉自己创建的distribute_lock 节点就释放出锁。

对于第二类， /distribute_lock 已经预先存在，所有客户端在它下面创建临时顺序编号目录节点，
和选master一样，编号最小的获得锁，用完删除，依次方便。


# 实践

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

2. 服务器端向Zookeeper注册，查看:`ls /servers`

3. process(WatchedEvent event) 一直处于监听，当Server上/下线，运行process

```java
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
