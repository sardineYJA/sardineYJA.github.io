---
layout: post
title: "matplotlib的使用"
date: 2018-04-11
description: "简单介绍一下matplotlib的使用"
tag: Python

---
# matplotlib基础

```python
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
import urllib
import matplotlib.dates as mdates

# 多点连线图
plt.plot([1,2,3], [5,7,4], label='First Line')
plt.plot([1,2,3], [10,14,12], label='Second Line')
# 图标
#plt.axis([0, 16, 0, 20])          # x轴y轴区
plt.xlabel('X axis')               # x轴标题
plt.ylabel('Y axis')               # y轴标题
plt.title(u'This is\n Title')      # 图标题
#plt.savefig('demo.jpg')           # 保存图片
plt.legend()                       # 显示label标签
plt.show()


# annotate()标记文本
t = np.arange(0.0, 5.0, 0.01)
s = np.cos(2*np.pi*t)
line = plt.plot(t, s, lw=2)   # lw 线段粗细
# 标注提示文本，xy箭头指向的点，xytext文本位置的点，arrowprops文本属性
plt.annotate('local max', xy=(2, 1), xytext=(3, 1.5),
            arrowprops=dict(facecolor='black', shrink=0.05),)
plt.ylim(-2,2)   # 限制y轴取值范围
plt.show()
```

<img src="/images/posts/2019-01-21/output_1_0.png">

<img src="/images/posts/2019-01-21/output_1_1.png">

# matplotlib基础：条形图，直方图


```python
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
import urllib
import matplotlib.dates as mdates


plt.rcParams['font.sans-serif'] = ['SimHei']   # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号
#plt.rcParams['font.size'] = 20                # 字体大小为20


'''
颜色：b --- blue     c --- cyan  g --- green    k ---- black
      m --- magenta  r --- red   w --- white    y ---- yellow
风格：‘-’实线；‘--’破折线； ‘-.’点划线； ‘：’虚线 
标记：‘.’点标记  ‘o’ 实心圈 ‘v’倒三角  ‘^’上三角
'''
t = np.arange(0., 5., 0.2)
plt.plot(t, t, 'r--', t, t**2, 'bs', t, t**3, 'g^')
plt.title('线的颜色，形状')
# 只希望在某地方绘制中文字符，不改变别的地方的字体属性： fontproperties
plt.xlabel('横轴：时间', fontproperties = 'FangSong', fontsize = 20)
plt.text(2, 100, '任意文本', fontsize=20)       # 在任意位置增加文本
plt.show()


# 条形图
plt.bar([1,3,5,7,9],[5,2,7,8,2], label="Example one")
plt.bar([2,4,6,8,10],[8,6,2,5,6], label="Example two", color='g')
plt.legend()
plt.show()

# 水平条形图  
plt.barh(bottom=(0,1,2),height=0.55,width=(40,30,50),align="center")
plt.show()


# 直方图，需要放入所有的值，然后指定放入哪个桶或容器
population_ages = [22,55,62,45,21,22,34,42,42,4,99,102,110,120,121,122,130,111,115,112,80,75,65,54,44,43,42,48]
bins = [0,10,20,30,40,50,60,70,80,90,100,110,120,130]
# alpha表示直方图的透明度[0, 1]; histtype = 'stepfilled' 表示去除条柱的黑色边框; rwidth直条之间的距离
# bins = 10 表示分成10份
plt.hist(population_ages, bins, histtype='bar', rwidth=0.8, alpha=0.35)
plt.show()
```

<img src="/images/posts/2019-01-21/output_3_0.png">

<img src="/images/posts/2019-01-21/output_3_1.png">   

<img src="/images/posts/2019-01-21/output_3_3.png">

<img src="/images/posts/2019-01-21/output_3_4.png">


# matplotlib基础：散点图，堆叠图，饼状图


```python
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
import urllib
import matplotlib.dates as mdates

# 散点图
x = [1,2,3,4,5,6,7,8]
y = [5,2,4,2,1,4,5,2]
plt.scatter(x,y, label='skitscat', color='k', s=25, marker="v")
plt.legend()
plt.show()


# 堆叠图
days = [1,2,3,4,5]            # 五天时间
sleeping = [7,8,6,11,7]       # 每天每个活动占据的时间
eating =   [2,3,4,3,2]
working =  [7,8,7,2,2]
playing =  [8,5,7,8,13]
plt.plot([],[],color='m', label='Sleeping', linewidth=5)
plt.plot([],[],color='c', label='Eating', linewidth=5)
plt.plot([],[],color='r', label='Working', linewidth=5)
plt.plot([],[],color='k', label='Playing', linewidth=5)
plt.stackplot(days, sleeping,eating,working,playing, colors=['m','c','r','k'])
plt.legend()
plt.show()


# 饼状图
slices = [7,2,2,13]
activities = ['sleeping','eating','working','playing']
cols = ['c','m','r','b']
plt.pie(slices,
        labels=activities,
        colors=cols,
        startangle=90,         # 起始角度
        shadow= True,         # 绘图阴影
        explode=(0,0.1,0,0),  # (逆时针)拉出第二个切片,距离0.1
        autopct='%0.2f%%')    # 将百分比放置到图表上
plt.axis('equal')             # 椭圆变成圆
plt.show()
```

<img src="/images/posts/2019-01-21/output_5_0.png">

<img src="/images/posts/2019-01-21/output_5_1.png">

<img src="/images/posts/2019-01-21/output_5_2.png">


# matplotlib基础：子图划分的几种方法


```python
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
import urllib
import matplotlib.dates as mdates


# 多图以及多个子图实例
plt.figure(1)                # 图一有两个子图
plt.subplot(211)             # 子图1在第一行第一列
plt.plot([1, 1, 1])

plt.subplot(212)             # 子图2在第一行第二列
plt.plot([2, 2, 2])

plt.figure(2)                # 图二有一个子图
plt.plot([3, 3, 3])          # creates a subplot(111) by default

# 回到图一，第一个子图
plt.figure(1)                # figure 1 current; subplot(212) still current
plt.subplot(211)             # make subplot(211) in figure1 current
plt.show()


# subplot2grid 绘制子图
# (3,3)分3行3列，（0,0）此子图在第1行第1列，colspan/rowspan占几列几行
plt.subplot2grid((3,3),(0,0), colspan=3)
plt.subplot2grid((3,3),(1,0), colspan=2)
plt.subplot2grid((3,3),(1,2), rowspan=2)
plt.subplot2grid((3,3), (2,1))
plt.show()


# GridSpec 类绘制子图
# gs[行，列]
import matplotlib.gridspec as gridspec
gs = gridspec.GridSpec(4,4)
ax1 = plt.subplot(gs[0, :])
ax2 = plt.subplot(gs[1, 0:3])
ax3 = plt.subplot(gs[1:4, 3])
ax4 = plt.subplot(gs[2:4, 1])
plt.show()
```  

<img src="/images/posts/2019-01-21/output_7_1.png">

<img src="/images/posts/2019-01-21/output_7_2.png">

<img src="/images/posts/2019-01-21/output_7_3.png">

<img src="/images/posts/2019-01-21/output_7_4.png">


# 面对对象的极坐标图绘制


```python
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
import urllib
import matplotlib.dates as mdates


# 面对对象的极坐标图绘制
N = 20
theta = np.linspace(0.0, 2*np.pi, N, endpoint=False) # 0到2pi创建20个元素的数组
radii = 10*np.random.rand(N)                         # 随机【0,1）的10倍数，个数20个
width = np.pi / 4*np.random.rand(N)
ax = plt.subplot(111, projection='polar')
bars = ax.bar(theta, radii, width=width, bottom=0.0)
for r, bar in zip(radii, bars):
        bar.set_facecolor(plt.cm.viridis(r/10.))
        bar.set_alpha(0.5)

plt.show()
```

<img src="/images/posts/2019-01-21/output_9_0.png">

# 条形图barh的绘制


```python
%matplotlib inline
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

data = {'Barton LLC': 109438.50,
        'Frami, Hills and Schmidt': 103569.59,
        'Fritsch, Russel and Anderson': 112214.71,
        'Jerde-Hilpert': 112591.43,
        'Keeling LLC': 100934.30,
        'Koepp Ltd': 103660.54,
        'Kulas Inc': 137351.96,
        'Trantow-Barrows': 123381.38,
        'White-Trantow': 135841.99,
        'Will LLC': 104437.60}
group_data = list(data.values())
group_names = list(data.keys())
group_mean = np.mean(group_data)  # 求取均值
print(group_mean)

plt.style.use('fivethirtyeight')          # 图形风格
fig, ax = plt.subplots(figsize=(8, 4))    # fig 背景，ax 水平条形图
ax.barh(group_names, group_data)
ax.axvline(group_mean, ls='--', color='r')# 均值线
```

<img src="/images/posts/2019-01-21/output_11_3.png">


