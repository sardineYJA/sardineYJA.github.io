---
layout: post
title: "SpringBoot 线程池"
date: 2019-11-23
description: "SpringBoot 线程池"
tag: Java Web

---

## 线程池

1. 自定义线程池

2. 配置spring默认的线程池

线程池ThreadPoolExecutor 执行：

![png](/images/posts/all/线程池ThreadPoolExecutor.png)




## 配置

properties参数配置
```sh
task.pool.corePoolSize=20
task.pool.maxPoolSize=40
task.pool.keepAliveSeconds=300
task.pool.queueCapacity=50
```

启动类添加注解
```java
@EnableConfigurationProperties({TaskThreadPoolConfig.class}) // 开启配置属性支持
@EnableAsync                                                 // 使用多线程
```

线程池配置属性类
```java
@ConfigurationProperties(prefix = "task.pool")  // 加载配置
public class TaskThreadPoolConfig {
    private int corePoolSize;       // 核心线程数
    private int maxPoolSize;        // 最大线程数
    private int keepAliveSeconds;   // 线程活跃时间(秒)
    private int queueCapacity;      // 队列容量
}
```

## 自定义线程池

```java
@Configuration   // 定义配置类，可替换xml配置文件，被注解的类内部包含有一个或多个被@Bean注解的方法
@EnableAsync     // 使用多线程
public class TaskExecutePool {
    @Autowired  
    private TaskThreadPoolConfig config;

    @Bean   // @Bean产生Bean对象，交给Spring管理
    public TaskExecutor mytaskExecutorPool() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(config.getCorePoolSize());
        executor.setMaxPoolSize(config.getMaxPoolSize());
        executor.setQueueCapacity(config.getQueueCapacity());
        executor.setKeepAliveSeconds(config.getKeepAliveSeconds());
        executor.setThreadNamePrefix("MyThread-");
        // 设置拒绝策略
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        // 等待所有任务结束后再关闭线程池
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.initialize();
        return executor;
    }
}
```

## 配置spring默认的线程池

```java
@Configuration
public class NativeAsyncTaskExecutePool implements AsyncConfigurer { 
// 不同点：实现AsyncConfigurer接口两个方法

    private final Logger logger = LoggerFactory.getLogger(this.getClass());
    @Autowired
    TaskThreadPoolConfig config;

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(config.getCorePoolSize());
        executor.setMaxPoolSize(config.getMaxPoolSize());
        executor.setQueueCapacity(config.getQueueCapacity());
        executor.setKeepAliveSeconds(config.getKeepAliveSeconds());
        executor.setThreadNamePrefix("AsyncThread-");
        // 设置拒绝策略
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        // 等待所有任务结束后再关闭线程池
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.initialize();
        return executor;
    }

    @Override    // 异步任务中异常处理
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return new AsyncUncaughtExceptionHandler() {
            @Override
            public void handleUncaughtException(Throwable throwable, Method method, Object... objects) {
                logger.error("=========="+throwable.getMessage()+"===========");
                logger.error("exception method:"+method.getName());
            }

        };
    }
}
```

## 测试


```java
@Component   // 实例化到spring容器中，@Autowired才可以装载AsyncTask类
public class AsyncTask {
    private final Logger logger = LoggerFactory.getLogger(this.getClass());

    // @Async加在线程任务的方法上（需要异步执行的任务）此处不写自定义线程池方法名，会用默认的线程池
    @Async//("mytaskExecutorPool")
    public void doTask(int i) {
        logger.info("Task-"+i+" start.");
        logger.info("do something ...");
    }
}
```

@Async 注解方法不带参数，使用的线程池是getAsyncExecutor()

@Async("mytaskExecutorPool")，使用的线程池是mytaskExecutorPool()

推荐使用默认的线程池，implements AsyncConfigurer这个方法。


```java
@RunWith(SpringRunner.class)
@SpringBootTest
public class MyTest {
    private final Logger logger = LoggerFactory.getLogger(this.getClass());
    @Autowired
    private AsyncTask asyncTask;

    @Test
    public void test() {
        for (int i=0; i < 10; i++) {
            asyncTask.doTask(i);
        }
        logger.info("All tasks finished.");
    }
}
```