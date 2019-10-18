---
layout: post
title: "shuffle 优化"
date: 2019-10-16
description: "shuffle 优化"
tag: Spark

---

# shuffle

![png](/images/posts/all/Spakr-Job样例图.png)

![png](/images/posts/all/Spark-Job样例shuffle结构图.png)


上图 shuffle 过程：前一个stage 的 ShuffleMapTask 进行 shuffle write，把数据存储在 blockManager 上面，并且把数据位置元信息上报到 driver 的 mapOutTrack 组件中，下一个 stage 根据数据位置元信息， 进行 shuffle read， 拉取上个stage 的输出数据。

shuffle的读写都是昂贵的，如果这两个值过大，应该重构应用代码或者调整Spark参数减少Shuffle。

# 优化

（待补充）





# reference

https://www.cnblogs.com/itboys/p/9201750.html




