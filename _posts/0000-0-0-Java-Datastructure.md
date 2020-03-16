---
layout: post
title: "Java 常用数据结构"
date: 2018-01-11
description: "介绍Java 数据结构"
tag: Java

---


# 数据结构

## Collection

```
Collection
├List
│├LinkedList
│├ArrayList
│└Vector
│　└Stack
└Set
 ├HashSet
 └TreeSet
```

List 有序，可重复元素, Set 无序，不含重复元素

## Vector、ArrayList、LinkedList

Vector `同步`(线程安全，所以性能比Vector较差)，底层是`数组`，线程安全，增删慢，查询慢

ArrayList `非同步`（多线程访问时需要自己实现），底层结构是`数组`，查询快，增删慢

LinkedList 非同步（多线程访问时需要自己实现），底层结构是链表，增删快，查询慢




## Map

```
Map
├Hashtable
├HashMap
└WeakHashMap
```

Map 提供 key-value 映射，键唯一，值不唯一

HashMap 非线程安全，允许 null value 和 null key

Hashtable 线程安全，任何非空（non-null）的对象都可作为 key 或 value

ConcurrentHashMap: 改进 Hashtable，线程安全，其关键在于使用了锁分离技术

WeakHashMap 改进的 HashMap，它对 key 实行“弱引用”，如果一个 key 不再被外部所引用，那么该 key 可以被GC回收

HashTable:
底层数组+链表实现，无论key还是value都不能为null，线程安全。
实现线程安全的方式是在修改数据时Synchronize锁住整个HashTable，效率低，ConcurrentHashMap做了相关优化。
Hashtable继承自Dictionary类


HashMap:
底层数组+链表实现，可以存储null键和null值，线程不安全。
在多线程环境中，需要手动实现同步机制。
HashMap继承自AbstractMap类。

```java
// HashMap 实现线程安全
Map<Long, User> users = Collections.synchronizedMap(new HashMap<Long, User>());
```

ConcurrentHashMap:
底层采用分段的数组+链表实现，线程安全。
ConcurrentHashMap允许多个修改操作并发进行，其关键在于使用了锁分离技术。




## String、StringBuffer、StringBuilder

String 是引用类型，底层用char数组实现。

String s ="123"; s = s+"456";对象没有改变，只是s指向新的String对象了。以往如此，会引起内存开销。

String不能被继承，String类有final修饰符，而final修饰的类是不能被继承的。
平常定义的String str=”a”;（引用）其实和String str=new String(“a”)（构建新对象）还是有差异的。

String str=”aaa”,与String str=new String(“aaa”)不一样的。因为内存分配的方式不一样。
第一种，创建的”aaa”是常量，jvm都将其分配在常量池中。
第二种，创建的是一个对象，jvm将其值分配在堆内存中。

- String 字符串常量(final修饰，不可被继承)，String是常量，当创建之后即不能更改。
- StringBuffer 字符串变量（线程安全）,其也是final类别的，不允许被继承，其中的绝大多数方法都进行了同步处理。
- StringBuilder 字符串变量（非线程安全），方法除了没使用synch修饰以外基本与StringBuffer一致，速度更快。




# 实例

## 基础

```java
List<Integer> linkedList = new LinkedList<>();
linkedList.add(1);
linkedList.add(4);
linkedList.add(2);
linkedList.sort(new Comparator<Integer>() {
    @Override
    public int compare(Integer o1, Integer o2) {
        return o1.compareTo(o2);
    }
});

Set hashSet = new HashSet<>();
hashSet.add("hs1");
hashSet.add("hs2");
hashSet.add(100);
```


## Map 键值对排序：key(String), value(Integer)

```java
Map<String, Integer> phone = new HashMap();
phone.put("Hawei", 9000);
phone.put("Xiaomi", 8880);
phone.put("Redmi", 5000);
phone.put("Chuizi", 7800);
System.out.println(phone);

// key(String)-sort
Set set = phone.keySet();    // 获取 key 集合
Object[] arr = set.toArray();
Arrays.sort(arr);            // key(String) 排序
for (Object key : arr) {
    System.out.println(key + ": " + phone.get(key));
}

//value(Integer)-sort
List<Map.Entry<String, Integer>> list = new ArrayList<Map.Entry<String, Integer>>(phone.entrySet());

// 第一种：list.sort()
list.sort(new Comparator<Map.Entry<String, Integer>>() {
    @Override
    public int compare(Map.Entry<String, Integer> o1, Map.Entry<String, Integer> o2) {
        return o2.getValue().compareTo(o1.getValue());  // 降序
    }
});

//第二种：collections.sort()
Collections.sort(list, new Comparator<Map.Entry<String, Integer>>() {
    @Override
    public int compare(Map.Entry<String, Integer> o1, Map.Entry<String, Integer> o2) {
        return o2.getValue().compareTo(o1.getValue());
    }
});

for (int i = 0; i < list.size(); i++) {
    System.out.println(list.get(i).getKey() + ": " + list.get(i).getValue());
}
```

# 参考

https://www.cnblogs.com/diegodu/p/6119701.html

https://blog.csdn.net/xHibiki/article/details/82938480




