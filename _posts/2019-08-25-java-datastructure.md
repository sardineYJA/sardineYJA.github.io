---
layout: post
title: "Java 数据结构"
date: 2019-08-25
description: "介绍Java 数据结构"
tag: Java

---


# 数据结构

## Collection

Collection
├List
│├LinkedList
│├ArrayList
│└Vector
│　└Stack
└Set
 ├HashSet
 └TreeSet


类均在java.util包

List 有序，可重复元素

LinkedList 非同步（多线程访问时需要自己实现），底层结构是链表，增删快，查询慢

ArrayList 非同步（多线程访问时需要自己实现），底层结构是数组，查询快，增删慢

Vector 同步，底层是数组，线程安全，增删慢，查询慢

Stack 继承 Vector

Set 无序，不含重复元素

## Map

Map
├Hashtable
├HashMap
└WeakHashMap

Map 提供 key-value 映射，键唯一，值不唯一

Hashtable 同步，任何非空（non-null）的对象都可作为 key 或 value

ConcurrentHashMap: 改进 Hashtable，线程安全，其关键在于使用了锁分离技术

HashMap 非同步，允许 null value 和 null key

WeakHashMap 改进的 HashMap，它对 key 实行“弱引用”，如果一个 key 不再被外部所引用，那么该 key 可以被GC回收


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




