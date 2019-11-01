---
layout: post
title: "adb 常用命令"
date: 2018-03-01
description: "adb 常用命令"
tag: Interest

---

## 前言

以前使用过安卓手机的挂机软件，不过基本上要root。简单控制手机发现adb命令也可以


## adb

adb即Android Debug Bridge，就是可以通过窗口命令，使在pc端可以调试安卓移动端的一个工具包。主要存放在sdk安装目录下的platform-tools文件夹中。

下载：https://developer.android.com/studio/releases/platform-tools.html

设置环境变量，手机开启开发者模式，打开`USB调试`

测试命令：

```sh
adb devices   # 查看设备

adb shell     # 进入shell

adb shell screencap -p /sdcard/1.png   # 屏幕截图，保存到内存卡

adb pull /sdcard/1.png D:/1.png        # 将图片上传到D盘

adb push D:/1.png /sdcard/1.png        # 将D盘图片上传到SD卡

adb shell input touchscreen swipe x1 y1 x2 y2 time  
# 从[x1,x2]点滑动到[x2,y2]点，然后滑动的时间（毫秒）
# 例：adb shell input touchscreen swipe 170 180 170 180 500

adb shell wm size  # 查看屏幕分辨率

```


## 手机设置

手机坐标以左上角为原点，向右表示x轴，向下表示y轴

可以在开发者选项中开启：指针位置。即可以获取某个点的具体坐标


## 跳一跳案例

参考网上adb命令对跳一跳小程序的测试：

主要思想：手机截图，将图片上传到PC端，在面板打开图片，点击起点与终点，计算触碰屏幕时间。


截图命令：`adb shell screencap -p [图片路径]`

模拟滑动事件：`adb shell input touchscreen swipe x1 y1 x2 y2 time`

滑动参数可以看到，从[x1,x2]点滑动到[x2,y2]点，然后滑动的时间。


> IOException: Cannot run program "adb": CreateProcess error=2, 系统找不到指定的文件。

设置adb环境变量后，依然报错。因为 IDEA 无法识别 adb 环境路径，重启 IDEA 即可。



```java

```

```java

```

```java

```

```java

```