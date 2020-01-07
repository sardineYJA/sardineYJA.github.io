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


# 基础操作

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

# 分布式锁

## 简单的zookeeper实现分布式锁的思路：

1. 用zookeeper中一个临时节点代表锁，比如在/exlusive_lock下创建临时子节点/exlusive_lock/lock。
2. 所有客户端争相创建此节点，但只有一个客户端创建成功。
3. 创建成功代表获取锁成功，此客户端执行业务逻辑
4. 未创建成功的客户端，监听/exlusive_lock变更
5. 获取锁的客户端执行完成后，删除/exlusive_lock/lock，表示锁被释放
6. 锁被释放后，其他监听/exlusive_lock变更的客户端得到通知，再次争相创建临时子节点/exlusive_lock/lock。

上述是较为简单的分布式锁实现方式。能够应付一般使用场景，但存在着如下两个问题：

1. 锁的获取顺序和最初客户端争抢顺序不一致，这不是一个公平锁。每次锁获取都是当次最先抢到锁的客户端。
2. 羊群效应，所有没有抢到锁的客户端都会监听/exlusive_lock变更。当并发客户端很多的情况下，所有的客户端都会接到通知去争抢锁，此时就出现了羊群效应。

## 改进

让每个客户端在/exlusive_lock下创建的临时节点为有序节点，这样每个客户端都在/exlusive_lock下有自己对应的锁节点，而序号排在最前面的节点，代表对应的客户端获取锁成功。排在后面的客户端监听自己前面一个节点，那么在他前序客户端执行完成后，他将得到通知，获得锁成功。逻辑修改如下：

1. 每个客户端往/exlusive_lock下创建有序临时节点/exlusive_lock/lock_。创建成功后/exlusive_lock下面会有每个客户端对应的节点，如/exlusive_lock/lock_000000001
2. 客户端取得/exlusive_lock下子节点，并进行排序，判断排在最前面的是否为自己
3. 如果自己的锁节点在第一位，代表获取锁成功，此客户端执行业务逻辑
4. 如果自己的锁节点不在第一位，则监听自己前一位的锁节点。例如，自己锁节点lock_000000002，那么则监听lock_000000001
5. 当前一位锁节点（lock_000000001）对应的客户端执行完成，释放了锁，将会触发监听客户端（lock_000000002）的逻辑。
6. 监听客户端重新执行第2步逻辑，判断自己是否获得了锁。


```java
public class DistributeLock {
    private ZooKeeper zkClient;
    private static final String LOCK_ROOT_PATH="/Locks";
    private static final String LOCK_NODE_NAME="Lock_";
    private String lockPath;

    // 监控lockPath的前一个节点的watcher
    private Watcher watcher = new Watcher() {
        @Override
        public void process(WatchedEvent watchedEvent) {
            System.out.println(watchedEvent.getPath() + " 前锁释放");
            synchronized (this) {
                notifyAll();
            }
        }
    };

    public DistributeLock() throws Exception{
        zkClient = new ZooKeeper("172.16.7.124:2181", 10000,
                new Watcher() {
                    @Override
                    public void process(WatchedEvent watchedEvent) {
                        if (watchedEvent.getState() == Event.KeeperState.Disconnected) {
                            System.out.println("失去连接");
                        }
                    }
            });
    }

    // 获取锁的原语
    public void acquireLock() throws Exception {
        createLock();    // 创建锁节点
        attemptLock();   // 尝试获取锁
    }

    // 创建节点
    private void createLock() throws Exception {
        // 如果根节点不存在，则创建
        Stat stat = zkClient.exists(LOCK_ROOT_PATH, false);
        if (stat == null) {
            zkClient.create(LOCK_ROOT_PATH, new byte[0],
                    ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.PERSISTENT);
        }
        // 创建节点
        String lockPath = zkClient.create(LOCK_ROOT_PATH+"/"+LOCK_NODE_NAME,   // 节点路径
                Thread.currentThread().getName().getBytes(),                         // 节点内容
                ZooDefs.Ids.OPEN_ACL_UNSAFE,
                CreateMode.EPHEMERAL_SEQUENTIAL);
        System.out.println(Thread.currentThread().getName() + " 锁创建：" + lockPath);
        this.lockPath=lockPath;
    }

    // 获取锁
    private void attemptLock() throws Exception {
        // 获取Lock所有子节点，按照节点号排序
        List<String> lockPaths = null;
        lockPaths = zkClient.getChildren(LOCK_ROOT_PATH, false);
        Collections.sort(lockPaths);
        int index = lockPaths.indexOf(lockPath.substring(LOCK_ROOT_PATH.length() + 1));

        // 如果lockPath是序号最小的节点，则获取锁
        if (index == 0) { // list序号最前即0就是最小
            System.out.println(Thread.currentThread().getName() + " 锁获得，lockPath：" + lockPath);
            return;
        } else {
            // lockPath不是序号最小，监控前一个节点
            String preLockPath = lockPaths.get(index-1);
            Stat stat = zkClient.exists(LOCK_ROOT_PATH + "/" + preLockPath, watcher);
            // 如果前一个节点不存在，比如执行完毕、掉线，重新获取锁
            if (stat == null) {
                attemptLock();
            } else {
                System.out.println("等待前锁释放，preLockPath：" + preLockPath);
                synchronized (watcher) {
                    watcher.wait();
                }
                attemptLock();
            }
        }
    }

    // 释放锁的原语
    public void releaseLock() throws Exception {
        zkClient.delete(lockPath, -1);
        zkClient.close();
        System.out.println("锁释放：" + lockPath);
    }
}
```

```java
public static void main(String[] args) throws Exception {
    // 开启多线程测试
    for (int i = 1; i <= 10; i++) {
        System.out.println("开启" + i + "线程");
        Thread th = new Thread(new Runnable() {
            @Override
            public void run() {
                DistributeLock distributeLock = null;
                try {
                    distributeLock = new DistributeLock();
                    distributeLock.acquireLock();
                } catch (Exception e) {
                    e.printStackTrace();
                }
                try {
                    //代表复杂逻辑执行了一段时间
                    Thread.sleep((int) (Math.random() * 20000));
                } catch (Exception e) {
                    e.printStackTrace();
                }
                System.out.println(Thread.currentThread().getName() + "工作结束");
                try {
                    distributeLock.releaseLock();
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
        th.setName("线程" + i + "号");
        th.start();
    }
}
```


# reference 

https://blog.csdn.net/liyiming2017/article/details/83786331
