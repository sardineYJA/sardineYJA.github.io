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


## ShuffleManager发展概述

Spark 0.8及以前 Hash Based Shuffle

Spark 0.8.1 为Hash Based Shuffle引入File Consolidation机制

Spark 0.9 引入ExternalAppendOnlyMap

Spark 1.1 引入Sort Based Shuffle，但默认仍为Hash Based Shuffle

Spark 1.2 默认的Shuffle方式改为Sort Based Shuffle

Spark 1.4 引入Tungsten-Sort Based Shuffle

Spark 1.6 Tungsten-sort并入Sort Based Shuffle

Spark 2.0 Hash Based Shuffle退出历史舞台

Spark 2.2.x Spark ShuffleManager 分为HashShuffleManager和SortShuffleManager。在普通模式下，shuffle过程中会发生排序行为；Spark可以根据业务场景需要进行ShuffleManager选择--Hash Shuffle Manager / Sort ShuffleManager（普通模式和bypass模式）。


## HashShuffle

HashShuffleManager有着一个非常严重的弊端，就是会产生大量的中间磁盘文件，进而由大量的磁盘IO操作影响了性能。

![png](/images/posts/all/Spark的HashShuffle.png)

参数：
```sh
spark.shuffle.manager	hash
spark.shuffle.consolidateFiles	false
```

Map任务会为每个Reduce创建对应的bucket，Map产生的结果会根据设置的partitioner得到对应的bucketId，然后填充到相应的bucket中去。bucket其实对应磁盘上的一个文件，Map的结果写到每个bucket中其实就是写到那个磁盘文件中，这个文件也被称为blockFile。

![png](/images/posts/all/Spark的HashShuffle改进.png)

参数：
```sh
spark.shuffle.manager	hash
spark.shuffle.consolidateFiles	true
```

开启consolidation，改进HashShuffle，减少中间文件

## SortShuffle

参数：
```sh
spark.shuffle.manager	sort
spark.shuffle.sort.bypassMergeThreshold	默认200
```

![png](/images/posts/all/Spark的SortShuffleManager.png)

![png](/images/posts/all/Spark的SortShuffleManager的bypass.png)

bypass模式与未经优化的 HashShuffleManager是一摸一样额，只是最后多了一了merge的操作，产生的文件包括一个盘文件和一个索引文件。

SortShuffleManager相较于HashShuffleManager来说，有了一定的改进。
主要就在于，每个Task在进行shuffle操作时，虽然也会产生较多的临时磁盘文件，但是最后会将所有的临时文件合并（merge）成一个磁盘文件，因此每个Task就只有一个磁盘文件。
在下一个stage的shuffle read task拉取自己的数据时，只要根据索引读取每个磁盘文件中的部分数据即可。

SortShuffle 类似下面：

假如有100亿条数据，但是内存只有1M，但是磁盘很大，现在要对100亿条数据进行排序，1M内存只能装进1亿条数据，每次都只能对这1亿条数据进行排序，排好序后输出到磁盘，总共输出100个文件，最后怎么把这100个文件进行merge成一个全局有序的大文件。
可以每个文件（有序的）都取一部分头部数据最为一个buffer，并且把这100个 buffer放在一个堆里面，进行堆排序，比较方式就是对所有堆元素（buffer）的head元素进行比较大小，然后不断的把每个堆顶的 buffer的head元素pop出来输出到最终文件中，然后继续堆排序，继续输出。
如果哪个buffer空了，就去对应的文件中继续补充一部分数据。最终就得到一个全局有序的大文件。


##  Hadoop的MapReduce Shuffle和Spark Shuffle差别总结如下：

- 一个落盘，一个不落盘，spark就是为了解决mr落盘导致效率低下的问题而产生的，原理还是mr的原理，只是shuffle放在内存中计算。

- Hadoop的有一个Map完成，Reduce便可以去fetch数据了，不必等到所有Map任务完成，而Spark的必须等到父stage完成，也就是父stage的map操作全部完成才能去fetch数据。

- Hadoop的Shuffle是sort-base的，那么不管是Map的输出，还是Reduce的输出，都是partion内有序的，而spark hash不要求这一点。

- Hadoop的Reduce要等到fetch完全部数据，才将数据传入reduce函数进行聚合，而spark是一边fetch一边聚合。




# shuffle相关参数调优

## spark.shuffle.file.buffer

- 默认值：32k

- 参数说明：该参数用于设置shuffle write task的BufferedOutputStream的buffer缓冲大小。将数据写到磁盘文件之前，会先写入buffer缓冲中，待缓冲写满之后，才会溢写到磁盘。

- 调优建议：如果作业可用的内存资源较为充足的话，可以适当增加这个参数的大小（比如64k），从而减少shuffle write过程中溢写磁盘文件的次数，也就可以减少磁盘IO次数，进而提升性能。在实践中发现，合理调节该参数，性能会有1%-5%的提升。

## spark.reducer.maxSizeInFlight

- 默认值：48m

- 参数说明：该参数用于设置shuffle read task的buffer缓冲大小，而这个buffer缓冲决定了每次能够拉取多少数据。

- 调优建议：如果作业可用的内存资源较为充足的话，可以适当增加这个参数的大小（比如96m），从而减少拉取数据的次数，也就可以减少网络传输的次数，进而提升性能。在实践中发现，合理调节该参数，性能会有1%-5%的提升。

## spark.shuffle.io.maxRetries

- 默认值：3

- 参数说明：shuffle read task从shuffle write task所在节点拉取属于自己的数据时，如果因为网络异常导致拉取失败，是会自动进行重试的。该参数就代表了可以重试的最大次数。如果在指定次数之内拉取还是没有成功，就可能会导致作业执行失败。

- 调优建议：对于那些包含了特别耗时的shuffle操作的作业，建议增加重试最大次数（比如60次），以避免由于JVM的full gc或者网络不稳定等因素导致的数据拉取失败。在实践中发现，对于针对超大数据量（数十亿-上百亿）的shuffle过程，调节该参数可以大幅度提升稳定性。

## spark.shuffle.io.retryWait

- 默认值：5s

- 参数说明：具体解释同上，该参数代表了每次重试拉取数据的等待间隔，默认是5s。

- 调优建议：建议加大间隔时长（比如60s），以增加shuffle操作的稳定性。

## spark.shuffle.memoryFraction

- 默认值：0.2

- 参数说明：该参数代表了Executor内存中，分配给shuffle read task进行聚合操作的内存比例，默认是20%。

- 调优建议：在资源参数调优中讲解过这个参数。如果内存充足，而且很少使用持久化操作，建议调高这个比例，给shuffle read的聚合操作更多内存，以避免由于内存不足导致聚合过程中频繁读写磁盘。在实践中发现，合理调节该参数可以将性能提升10%左右。

## spark.shuffle.manager

- 默认值：sort

- 参数说明：该参数用于设置ShuffleManager的类型。Spark 1.5以后，有三个可选项：hash、sort和tungsten-sort。HashShuffleManager是Spark 1.2以前的默认选项，但是Spark 1.2以及之后的版本默认都是SortShuffleManager了。tungsten-sort与sort类似，但是使用了tungsten计划中的堆外内存管理机制，内存使用效率更高。

- 调优建议：由于SortShuffleManager默认会对数据进行排序，因此如果你的业务逻辑中需要该排序机制的话，则使用默认的SortShuffleManager就可以；而如果你的业务逻辑不需要对数据进行排序，那么建议参考后面的几个参数调优，通过bypass机制或优化的HashShuffleManager来避免排序操作，同时提供较好的磁盘读写性能。这里要注意的是，tungsten-sort要慎用，因为之前发现了一些相应的bug。

## spark.shuffle.sort.bypassMergeThreshold

- 默认值：200

- 参数说明：当ShuffleManager为SortShuffleManager时，如果shuffle read task的数量小于这个阈值（默认是200），则shuffle write过程中不会进行排序操作，而是直接按照未经优化的HashShuffleManager的方式去写数据，但是最后会将每个task产生的所有临时磁盘文件都合并成一个文件，并会创建单独的索引文件。

- 调优建议：当你使用SortShuffleManager时，如果的确不需要排序操作，那么建议将这个参数调大一些，大于shuffle read task的数量。那么此时就会自动启用bypass机制，map-side就不会进行排序了，减少了排序的性能开销。但是这种方式下，依然会产生大量的磁盘文件，因此shuffle write性能有待提高。

## spark.shuffle.consolidateFiles

- 默认值：false

- 参数说明：如果使用HashShuffleManager，该参数有效。如果设置为true，那么就会开启consolidate机制，会大幅度合并shuffle write的输出文件，对于shuffle read task数量特别多的情况下，这种方法可以极大地减少磁盘IO开销，提升性能。

- 调优建议：如果的确不需要SortShuffleManager的排序机制，那么除了使用bypass机制，还可以尝试将spark.shffle.manager参数手动指定为hash，使用HashShuffleManager，同时开启consolidate机制。在实践中尝试过，发现其性能比开启了bypass机制的SortShuffleManager要高出10%-30%。


# reference

https://www.cnblogs.com/itboys/p/9201750.html

https://www.cnblogs.com/qiuhong10/p/7762532.html


