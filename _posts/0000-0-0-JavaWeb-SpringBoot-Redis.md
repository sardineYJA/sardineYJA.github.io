---
layout: post
title: "SpringBoot 使用 Redis"
date: 2019-12-29
description: "SpringBoot 使用 Redis"
tag: Java Web

---

## 使用场景

synchronize锁（只适合单点即单机模式）

redis分布式锁：多台机器上多个进程对一个数据进行操作的互斥


## 依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

```sh
spring:
  redis:
    host: 127.0.0.1
    port: 6379
```


```java
@Autowired
private RedisTemplate redisTemplate;

@Autowired
private StringRedisTemplate stringRedisTemplate;
// StringRedisTemplate 只针对键值是字符串的数据进行操作
```


## SpringBoot 使用 Redis 分布式锁

```java
@Component
public class RedisLock {

    @Autowired
    private StringRedisTemplate redisTemplate;

    /**
     * 加锁
     * @param key
     * @param value 当前时间+超时时间
     * @return
     */
    public boolean lock(String key, String value) {
        if(redisTemplate.opsForValue().setIfAbsent(key, value)) { 
        	// 即setnx函数，Set if Not exist, 键值对设置成功，加锁成功
            return true;
        }

        String currentValue = redisTemplate.opsForValue().get(key);  
        if (!StringUtils.isEmpty(currentValue)
                && Long.parseLong(currentValue) < System.currentTimeMillis()) {  // 锁已过期
            //获取上一个锁的时间
            String oldValue = redisTemplate.opsForValue().getAndSet(key, value); // getset函数，获取旧值，并设置新值
        	// 如果多个线程同时执行到此句，则需保证currentValue==oldValue，则才是加锁成功
            if (!StringUtils.isEmpty(oldValue) && oldValue.equals(currentValue)) {
                return true;
                // 上面有个问题：虽最终只有一个客户端可加锁，但这个客户端的锁的过期时间可能被其他客户端覆盖。且锁不具备拥有者标识，即任何客户端都可以解锁。
            }
        }

        return false;
    }

    /**
     * 解锁
     * @param key
     * @param value
     */
    public void unlock(String key, String value) {
        String currentValue = redisTemplate.opsForValue().get(key);
        if (!StringUtils.isEmpty(currentValue) && currentValue.equals(value)) {
            redisTemplate.opsForValue().getOperations().delete(key);  // 删除键值对
        }
    }

}
```


## Redis 分布式锁

```xml
<dependency>
    <groupId>redis.clients</groupId>
    <artifactId>jedis</artifactId>
    <version>2.9.0</version>
</dependency>
```

```java
/**
 * 尝试获取分布式锁
 * @param jedis      Redis客户端
 * @param lockKey    锁
 * @param requestId  请求标识
 * @param expireTime 超期时间
 * @return           是否获取成功
 */
public static boolean getDistributedLock(Jedis jedis, String lockKey, String requestId, int expireTime) {
    String result = jedis.set(lockKey, requestId, "NX", "PX", expireTime);
    // requestId可用UUID.randomUUID().toString()生成。加锁和解锁必须是同一个客户端，客户端自己不能把别人加的锁给解了。
    // "NX":SET IF NOT EXIST， "PX":给这个key加一个过期的设置
    if (result) { return true; }
    return false;
 
}
```

```java
/**
 * 释放分布式锁
 * @param jedis Redis客户端
 * @param lockKey 锁
 * @param requestId 请求标识
 * @return 是否释放成功
 */
public static boolean releaseDistributedLock(Jedis jedis, String lockKey, String requestId) {

    String script = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end";
    Object result = jedis.eval(script, Collections.singletonList(lockKey), Collections.singletonList(requestId));
    // eval()方法是将Lua代码交给Redis服务端执行。
    if (result) { return true; }
    return false;
 
}
```


## Redis 做缓存



# reference

https://blog.csdn.net/yb223731/article/details/90349502


