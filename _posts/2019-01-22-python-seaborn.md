---
layout: post
title: "seaborn的使用"
date: 2019-01-22
description: "简单介绍一下seaborn的使用"
tag: python

---

```python
%matplotlib inline
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy import stats, integrate   # 该包包含是常用的数学函数
```


```python
# 忽略警告
import warnings
warnings.filterwarnings('ignore')
```


```python
# 加载测试数据
titanic = sns.load_dataset('titanic')
tips = sns.load_dataset('tips')
iris = sns.load_dataset('iris')
anscombe = sns.load_dataset("anscombe")
#print(titanic.head(5))
#print(titanic.info())
```

# seaborn属性简单使用


```python
def sinplot(flip=1):
    x = np.linspace(0, 14, 100)  # 0-14创建100个样本
    for i in range(1, 7):
        plt.plot(x, np.sin(x + i * .5) * (7 - i) * flip)
sinplot()
plt.show()
```

<img src="/images/posts/2019-01-22/output_4_0.png">


```python
# 暗网格(darkgrid)，白网格(whitegrid)，全黑(dark)，全白(white)，全刻度(ticks)
sns.set_style("dark")  # 改变主题
sinplot()
plt.show()
```

<img src="/images/posts/2019-01-22/output_5_0.png">



```python
# 在with语句中使用axes_style()函数临时设置绘图参数
with sns.axes_style("darkgrid"):
    sinplot()
    plt.show()
```

<img src="/images/posts/2019-01-22/output_6_0.png">



```python
sns.set_style("white")
sinplot()        # 默认无参数状态，就是删除上方和右方的边框
#sns.despine()   # 用despine()进行边框控制
sns.despine(left=True) # 删除左边边框
```

<img src="/images/posts/2019-01-22/output_7_0.png">



```python
sns.set()      #重置参数
sns.set_context("notebook", font_scale=2.5, rc={"lines.linewidth": 2.5})
plt.figure(figsize=(8,6))
sinplot()
```

<img src="/images/posts/2019-01-22/output_8_0.png">



```python
# 创建调色面板
current_palette = sns.color_palette()
sns.palplot(current_palette)
# deep, muted, pastel, bright, dark, 和 colorblind
current_palette = sns.color_palette("bright") # 直接传入对应的参数即可变化
sns.palplot(current_palette)
```

<img src="/images/posts/2019-01-22/output_9_0.png">


<img src="/images/posts/2019-01-22/output_9_1.png">


# 绘制单变量分布


```python
x = np.random.normal(size=100)  # 正态分布
# hist=False直方图抹掉
sns.distplot(x)
plt.show()
```

<img src="/images/posts/2019-01-22/output_11_0.png">



```python
x = np.random.normal(size=100)  # 正态分布
# 控制密度曲线的有无通过参数kde来控制，控制数据量刻度的有无使用参数rug
sns.distplot(x,kde=False,rug=True)
plt.show()
```

<img src="/images/posts/2019-01-22/output_12_0.png">



```python
# 指定数据段的多少可以通过参数bins来控制
x = np.random.normal(size=100)
sns.distplot(x,bins=20,kde=False,rug=True)
plt.show()
```

<img src="/images/posts/2019-01-22/output_13_0.png">



```python
x = np.random.normal(size=100)  # 正态分布
# 概率密度函数，shade阴影部分
sns.kdeplot(x,shade=True)
plt.show()
```

<img src="/images/posts/2019-01-22/output_14_0.png">



```python
# KDE的带宽（bw）参数控制估计与数据的拟合程度，非常类似于直方图中的bin大小。
# 它对应于我们在上面绘制的内核的宽度
x = np.random.normal(0,1,size=30)
sns.kdeplot(x)
sns.kdeplot(x,bw=.2,label='bw:0.2')
sns.kdeplot(x,bw=2,label='bw:2')
plt.show()
```

<img src="/images/posts/2019-01-22/output_15_0.png">



```python
# 使用distplot()将参数分布拟合到数据集，并直观地评估它与观察数据的对应程度
x = np.random.gamma(6,size=200)
sns.distplot(x,kde=False,fit=stats.gamma)
plt.show()
```

<img src="/images/posts/2019-01-22/output_16_0.png">


# jointplot绘制二元分布


```python
mean, cov = [0,1], [(1,.5), (.5,1)]  # 均值，协方差
data = np.random.multivariate_normal(mean, cov, 200)
df = pd.DataFrame(data, columns=['x', 'y'])
```


```python
# 散点图
sns.jointplot(x= 'x', y = 'y', data=df)
```

<img src="/images/posts/2019-01-22/output_19_1.png">



```python
# 核密度估计
sns.jointplot(x='x', y='y', data=df, kind='kde')
```

<img src="/images/posts/2019-01-22/output_20_1.png">



```python
# 核密度估计
f, ax = plt.subplots(figsize=(6, 6)) # 相当于下面两句
#fig = plt.figure()
#ax = fig.add_subplot(111)
sns.kdeplot(df.x, df.y, ax=ax)
sns.rugplot(df.x, color="g", ax=ax)
sns.rugplot(df.y, vertical=True, ax=ax) # vertical控制y列数据是否垂直放置
```

<img src="/images/posts/2019-01-22/output_21_1.png">



```python
# Hexbin图
x, y = np.random.multivariate_normal(mean, cov, 1000).T
sns.jointplot(x=x, y=y, kind='hex')
```

<img src="/images/posts/2019-01-22/output_22_1.png">



```python
# 如果希望更连续地显示双变量密度，可以简单地增加轮廓线的数量
f,ax = plt.subplots(figsize=(6,6))
cmap =sns.cubehelix_palette(as_cmap=True,dark=0,light=1,reverse=True)
sns.kdeplot(df.x,df.y,cmap=cmap,n_levels=60,shade=True)
```

<img src="/images/posts/2019-01-22/output_23_1.png">



```python
# jointplot()在绘制后返回JointGrid对象，使用jointGrid来管理图形
mean, cov = [0,1], [(1,.5), (.5,1)]  # 均值，协方差
data = np.random.multivariate_normal(mean, cov, 200)
df = pd.DataFrame(data, columns=['x', 'y'])

g = sns.jointplot(x="x", y="y", data=df, kind="kde", color="m")
g.plot_joint(plt.scatter, c="w", s=30, linewidth=1, marker="+")
g.ax_joint.collections[0].set_alpha(0)
g.set_axis_labels("$X$", "$Y$")        # 设置轴标签，使用markdown语法
plt.show()
```

<img src="/images/posts/2019-01-22/output_24_0.png">


# FacetGrid，PairGrid进行绘制


```python
# 并没有绘制任何东西
g = sns.FacetGrid(tips, col="time")
```

<img src="/images/posts/2019-01-22/output_26_0.png">



```python
# 使用FacetGrid.map()方法，提供一个绘图功能和数据框中变量的名称来绘制
g = sns.FacetGrid(tips, col="sex", hue="smoker")
g.map(plt.scatter, "total_bill", "tip", alpha=.7)
g.add_legend();
```

<img src="/images/posts/2019-01-22/output_27_0.png">


```python
g = sns.FacetGrid(tips, hue="sex", palette="Set1", size=5, hue_kws={"marker": ["^", "v"]})
g.map(plt.scatter, "total_bill", "tip", s=100, linewidth=.5, edgecolor="white")
g.add_legend()
```

<img src="/images/posts/2019-01-22/output_28_1.png">



```python
# 当没有行或列面的图形时，还可以使用ax属性直接访问单个轴
g = sns.FacetGrid(tips, col="smoker", margin_titles=True, size=4)
g.map(plt.scatter, "total_bill", "tip", color="#338844", edgecolor="white", s=50, lw=1)
for ax in g.axes.flat:
    ax.plot((0, 50), (0, .2 * 50), c=".2", ls="--")
g.set(xlim=(0, 60), ylim=(0, 14))
```

<img src="/images/posts/2019-01-22/output_29_1.png">



```python
sns.factorplot(x='time', y='total_bill', hue='smoker',
              col='day',   # col值决定分几个图
              data=tips, kind='box',size=4, aspect=.5)
```

<img src="/images/posts/2019-01-22/output_30_1.png">



```python
sns.factorplot(x='day', y='total_bill', hue='smoker',
              col='time', data=tips, kind='swarm')
```

<img src="/images/posts/2019-01-22/output_31_1.png">



```python
# 用PairGrid and pairplot()绘制成对的关系
g = sns.PairGrid(iris, vars=["sepal_length", "sepal_width"], hue="species")
g.map(plt.scatter)
```

<img src="/images/posts/2019-01-22/output_32_0.png">



```python
g = sns.PairGrid(iris, hue="species")
g.map_diag(plt.hist)
g.map_offdiag(plt.scatter)
g.add_legend()
```

<img src="/images/posts/2019-01-22/output_33_1.png">



```python
# 可以在上下三角形中使用不同的功能来强调关系的不同方面
g = sns.PairGrid(iris)
g.map_upper(plt.scatter)
g.map_lower(sns.kdeplot, cmap="Blues_d")
g.map_diag(sns.kdeplot, lw=3, legend=False)
```

<img src="/images/posts/2019-01-22/output_34_1.png">



```python
g = sns.pairplot(iris, hue="species", palette="Set2", diag_kind="kde", size=2.5)
```

<img src="/images/posts/2019-01-22/output_25_0.png">


# 分类散点图


```python
# 使用stripplot()可以非常简单的将某种分类别的数据展现在散点图上
sns.stripplot(x = 'day', y = 'total_bill', data = tips)
plt.show()
```

<img src="/images/posts/2019-01-22/output_37_0.png">



```python
# 使用随机抖动，让散点图不重叠
sns.stripplot(x = 'day', y = 'total_bill', data = tips, jitter = True)
plt.show()
```


<img src="/images/posts/2019-01-22/output_38_0.png">



```python
# 使用函数swarmplot()，它使用避免重叠点的算法定位分类轴上的每个散点图点
sns.swarmplot(x = 'day', y = 'total_bill', data = tips)
plt.show()
```

<img src="/images/posts/2019-01-22/output_39_0.png">



```python
# 可以使用hue参数添加嵌套的分类变量
sns.swarmplot(x = 'day', y = 'total_bill', data = tips, hue = 'sex')
plt.show()
```

<img src="/images/posts/2019-01-22/output_40_0.png">



```python
# 数据是pandas类型那么会默认按着pandas的既定顺序给出，
# 如果是其他数据类型，比如string类型，那么将会按着在DataFram的出现顺序给出，
# 但是如果类别是数字类型的将会自动排序
sns.swarmplot(x="size", y="total_bill", data=tips)
plt.show()
```

<img src="/images/posts/2019-01-22/output_41_0.png">



```python
# 将垂直的散点图横向过来放置在y轴上可以使用orient关键字强制定向，
# 但通常可以颠倒x和y的顺序来改变绘图方向：
sns.swarmplot(x="total_bill", y="day", hue="time", data=tips)
plt.show()
```

<img src="/images/posts/2019-01-22/output_42_0.png">


# 绘制线性回归模型的函数


```python
# 两个函数绘制了两个变量x和y的散点图，然后拟合回归模型y〜x
# 并绘制了该回归线的结果回归线和95％置信区间：
sns.regplot(x="total_bill", y="tip", data=tips)
plt.show()
```

<img src="/images/posts/2019-01-22/output_44_0.png">



```python
sns.lmplot(x="total_bill", y="tip", data=tips)
plt.show()
```

<img src="/images/posts/2019-01-22/output_45_0.png">



```python
# 添加一些随机噪声的“抖动”(jitter)
sns.lmplot(x="size", y="tip", data=tips, x_jitter=.05)
plt.show()
```

<img src="/images/posts/2019-01-22/output_46_0.png">



```python
# 在每个独立的数据分组中对观察结果进行折叠，以绘制中心趋势的估计以及置信区间：
sns.lmplot(x="size", y="tip", data=tips, x_estimator=np.mean)
plt.show()
```

<img src="/images/posts/2019-01-22/output_47_0.png">


```python
sns.lmplot(x="x", y="y", data=anscombe.query("dataset == 'I'"),
           ci=None, scatter_kws={"s": 80})
```

<img src="/images/posts/2019-01-22/output_48_1.png">



```python
sns.lmplot(x="x", y="y", data=anscombe.query("dataset == 'II'"),
           ci=None, scatter_kws={"s": 80})
```

<img src="/images/posts/2019-01-22/output_49_1.png">



```python
# 在存在这些高阶关系的情况下，lmplot()和regplot()可以拟合多项式回归模型来拟合数据集中的简单类型的非线性趋势：
sns.lmplot(x="x", y="y", data=anscombe.query("dataset == 'II'"), order=2, ci=None, scatter_kws={"s": 80})
```

<img src="/images/posts/2019-01-22/output_50_1.png">



```python
# 由于异常值而偏离了主要关系：
sns.lmplot(x="x", y="y", data=anscombe.query("dataset == 'III'"), ci=None, scatter_kws={"s": 80})
```

<img src="/images/posts/2019-01-22/output_51_1.png">



```python
# 拟合一个健壮的回归模型，传入robust=True：
sns.lmplot(x="x", y="y", data=anscombe.query("dataset == 'III'"), robust=True, ci=None, scatter_kws={"s": 80})
```

<img src="/images/posts/2019-01-22/output_52_1.png">



```python
# 当y变量是二进制时，简单的线性回归也“工作”了，但提供了不可信的预测结果：
tips["big_tip"] = (tips.tip / tips.total_bill) > .15
sns.lmplot(x="total_bill", y="big_tip", data=tips, y_jitter=.03)
```

<img src="/images/posts/2019-01-22/output_53_1.png">



```python
# 在这种情况下，解决方案是拟合逻辑(Logistic)回归，使得回归线显示给定值x的y=1的估计概率：
sns.lmplot(x="total_bill", y="big_tip", data=tips, logistic=True, y_jitter=.03)
```

<img src="/images/posts/2019-01-22/output_54_1.png">



```python
# 使用一个lowess smoother拟合非参数回归。
# 这种方法具有最少的假设，尽管它是计算密集型的，因此目前根本不计算置信区间：
sns.lmplot(x="total_bill", y="tip", data=tips, lowess=True)
```

<img src="/images/posts/2019-01-22/output_55_1.png">



```python
# residplot()是一个有用的工具，用于检查简单的回归模型是否拟合数据集。它拟合并移除一个简单的线性回归，
# 然后绘制每个观察值的残差值。 理想情况下，这些值应随机散布在y = 0附近：
sns.residplot(x="x", y="y", data=anscombe.query("dataset == 'I'"), scatter_kws={"s": 80});
```

<img src="/images/posts/2019-01-22/output_56_0.png">



```python
# 如果残差中有结构，则表明简单的线性回归是不合适的：
sns.residplot(x="x", y="y", data=anscombe.query("dataset == 'II'"), scatter_kws={"s": 80});
```

<img src="/images/posts/2019-01-22/output_57_0.png">



```python
sns.lmplot(x="total_bill", y="tip", hue="smoker", data=tips,
           markers=["o", "x"], palette="Set1")
```

<img src="/images/posts/2019-01-22/output_58_1.png">



```python
sns.lmplot(x="total_bill", y="tip", hue="smoker", col="time", row="sex", data=tips)
```

<img src="/images/posts/2019-01-22/output_59_1.png">



```python
# lmplot()图的大小和形状通过FacetGrid界面使用size和aspect参数进行控制
sns.lmplot(x="total_bill", y="tip", col="day", data=tips, col_wrap=2, size=3, aspect=.5);
```

<img src="/images/posts/2019-01-22/output_60_0.png">


# 分类：观测值分布


```python
# 箱型图
sns.boxplot(x="day", y="total_bill", hue="time", data=tips)
plt.show()
```

<img src="/images/posts/2019-01-22/output_62_0.png">



```python
sns.boxplot(data=iris,orient="h")
```

<img src="/images/posts/2019-01-22/output_63_1.png">



```python
# 琴型图
sns.violinplot(x='total_bill', y='day', hue='time', data=tips)
plt.show()
```

<img src="/images/posts/2019-01-22/output_64_0.png">



```python
# 琴型图
sns.violinplot(x='day', y='total_bill', hue='time', data=tips)
plt.show()
```

<img src="/images/posts/2019-01-22/output_65_0.png">



```python
sns.violinplot(x="day", y="total_bill", hue="sex", data=tips, split=True, inner="stick", palette="Set3")
```

<img src="/images/posts/2019-01-22/output_66_1.png">



```python
sns.violinplot(x="day", y="total_bill", data=tips, inner=None)
sns.swarmplot(x="day", y="total_bill", data=tips, color="w", alpha=.5)
```

<img src="/images/posts/2019-01-22/output_67_1.png">


# 分类：统计估计


```python
# 条形图
sns.barplot(x='sex', y='survived', hue='class', data=titanic)
plt.show()
```

<img src="/images/posts/2019-01-22/output_69_0.png">



```python
# 想要显示每个类别中的观察值数量，而不是根据第二个维度变量的统计量
sns.countplot(x='deck', data=titanic, palette='Greens_d')
plt.show()
```

<img src="/images/posts/2019-01-22/output_70_0.png">



```python
sns.countplot(x="deck", hue="class", data=titanic, palette="Greens_d")
plt.show()
```

<img src="/images/posts/2019-01-22/output_71_0.png">



```python
# 只绘制点估计和置信区间
sns.pointplot(x="sex", y="survived", hue="class", data=titanic)
```

<img src="/images/posts/2019-01-22/output_72_1.png">



```python
sns.pointplot(x="class", y="survived", hue="sex", data=titanic,
              palette={"male": "g", "female": "m"},
              markers=["^", "o"], linestyles=["-", "--"])
```

<img src="/images/posts/2019-01-22/output_73_1.png">

