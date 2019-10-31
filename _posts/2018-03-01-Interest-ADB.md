---
layout: post
title: "adb 常见使用"
date: 2018-03-01
description: "adb 常见使用"
tag: Interest

---

## 前言

以前使用过安卓手机的挂机软件，不过基本上要root。简单控制手机发现adb命令也可以

## adb

adb即Android Debug Bridge，就是可以通过窗口命令，使在pc端可以调试安卓移动端的一个工具包


下载：https://developer.android.com/studio/releases/platform-tools.html

设置环境变量



第一、截图命令：adb shell screencap -p [图片路径]

截取手机屏幕保存到设备目录下，一般都是SD卡，然后在借助adb pull命令弄到本地。


第二、模拟滑动事件：adb shell input touchscreen swipe x1 y1 x2 y2 time

滑动参数可以看到，从[x1,x2]点滑动到[x2,y2]点，然后滑动的时间。



