---
layout: post
title: "Java 线程池篇"
date: 2018-01-28
description: "线程池篇"
tag: Java

---

# 基础线程

![png](/images/posts/all/Java线程生命周期.png)

## 三种创建线程的方法

通过实现 Runnable 接口

通过继承 Thread 类本身

通过 Callable 和 Future 创建线程，有返回值

## 方法

- synchronized 同步代码块里使用 wait()、notify/notifyAll() 方法

- wait()使当前线程阻塞，前提是 必须先获得锁

- notify/notifyAll() 的执行只是唤醒沉睡的线程，而不会立即释放锁


```java
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
            // 获取当前线程的名字
            System.out.println(Thread.currentThread().getName() + "工作结束");
            try {
                distributeLock.releaseLock();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    });
    th.setName("线程" + i + "号");  // 设置线程名字
    th.start();
}
```

1. 创建 Callable 接口的实现类，并实现 call() 方法，该 call() 方法将作为线程执行体，并且有返回值。
2. 创建 Callable 实现类的实例，使用 FutureTask 类来包装 Callable 对象，该 FutureTask 对象封装了该 Callable 对象的 call() 方法的返回值。
3. 使用 FutureTask 对象作为 Thread 对象的 target 创建并启动新线程。
4. 调用 FutureTask 对象的 get() 方法来获得子线程执行结束后的返回值。

```java
public class CallableThreadTest implements Callable {
    @Override
    public Integer call() throws Exception {
        int i = 0;
        for(; i<10; i++)
        {
            System.out.println(Thread.currentThread().getName()+" "+i);
        }
        return i;
    }

    public static void main(String[] args) throws Exception {
        CallableThreadTest ctt = new CallableThreadTest();
        FutureTask<Integer> ft = new FutureTask<>(ctt);
        // FutureTask 对象封装了该 Callable 对象的 call() 方法的返回值

        // 使用 FutureTask 对象作为 Thread 对象的 target 创建并启动新线程
        new Thread(ft, "子线程").start();
        System.out.println("子线程的返回值："+ft.get());
    }
}
```


# 线程池

![png](/images/posts/all/Java线程池相关接口与类.png)

- Executor：是一个接口，其只定义了一个execute()方法

- ExecutorService：在Executor的基础上加入了线程池的生命周期管理

- ThreadPoolExecutor：是线程池中最核心的类

- ScheduledThreadPoolExecutor：在ThreadPoolExecutor基础上加入了任务定时执行的功能

- ForkJoinPool一般配合stream API来使用，它适合做一些CPU密集型任务而不是I/O密集型任务。

## 提交任务

1. 判断核心线程池是否已满，如果不是，则创建线程执行任务

2. 如果核心线程池满了，判断队列是否满了，如果队列没满，将任务放在队列中

3. 如果队列满了，则判断线程池是否已满，如果没满，创建线程执行任务

4. 如果线程池也满了，则按照拒绝策略对任务进行处理

![png](/images/posts/all/Java线程池ThreadPoolExecutor的处理流程.png)

- corePool -> 核心线程池
- maximumPool -> 线程池
- BlockQueue -> 队列
- RejectedExecutionHandler -> 拒绝策略

## ThreadPoolExecutor

```java
public ThreadPoolExecutor(int corePoolSize,
                          int maximumPoolSize,
                          long keepAliveTime,
                          TimeUnit unit,
                          BlockingQueue<Runnable> workQueue,
                          ThreadFactory threadFactory,
                          RejectedExecutionHandler handler);
```

- corePoolSize，线程池中的核心线程数
- maximumPoolSize，线程池中的最大线程数
- keepAliveTime，空闲时间，当线程池数量超过核心线程数时，多余的空闲线程存活的时间，即：这些线程多久被销毁。
- unit，空闲时间的单位，可以是毫秒、秒、分钟、小时和天，等等
- workQueue，等待队列，线程池中的线程数超过核心线程数时，任务将放在等待队列，它是一个BlockingQueue类型的对象
- threadFactory，线程工厂，可以使用它来创建一个线程
- handler，拒绝策略，当线程池和等待队列都满了之后，需要通过该对象的回调函数进行回调处理

## 等待队列 workQueue

等待队列是BlockingQueue类型的，理论上只要是它的子类，都可以用来作为等待队列。

jdk内部自带阻塞队列：

- ArrayBlockingQueue，队列是有界的，基于数组实现的阻塞队列
- LinkedBlockingQueue，队列可以有界，也可以无界。基于链表实现的阻塞队列
- SynchronousQueue，不存储元素的阻塞队列，每个插入操作必须等到另一个线程调用移除操作，否则插入操作将一直处于阻塞状态
- PriorityBlockingQueue，带优先级的无界阻塞队列

## 拒绝策略 handler

jdk自带4种拒绝策略：

- CallerRunsPolicy    // 在调用者线程执行
- AbortPolicy         // 直接抛出RejectedExecutionException异常
- DiscardPolicy       // 任务直接丢弃，不做任何处理
- DiscardOldestPolicy // 丢弃队列里最旧的那个任务，再尝试执行当前任务

## 提交任务

- execute()用于提交不需要返回结果的任务

```java
ExecutorService executor = Executors.newFixedThreadPool(2);
executor.execute(() -> System.out.println("hello"));
```

- submit()用于提交一个需要返回果的任务，返回一个Future对象

```java
ExecutorService executor = Executors.newFixedThreadPool(2);
Future<Long> future = executor.submit(() -> {
    System.out.println("task is executed");
    return System.currentTimeMillis();
});
System.out.println("task execute time is: " + future.get());
```

## 总结

- Java中线程是一个比较昂贵的对象，线程的频繁创建和销毁会影响性能，因此借助"对象复用"思想产生线程池。由线程池来管理我们的线程。

- 使用Executors创建线程池时要明确创建的阻塞队列是否有界，如果是无界队列则饱和策略将失效，所有请求将一直排队等待被执行，可能会产生内存溢出的风险。最好自己创建ThreadPoolExecutor。

- 线程池不要申明为本地变量，如果每次请求都要创建和销毁线程池，那么线程池也就失去了它的意义，应该将线程池申明为全局的。



# reference

https://www.jianshu.com/p/0d9ef81aaa26

https://www.jianshu.com/p/7ab4ae9443b9

