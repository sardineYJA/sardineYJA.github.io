---
layout: post
title: "python数据分析篇3"
date: 2019-01-11
description: "简单介绍一下python数据分析"
tag: 数据分析

---

# 贝叶斯拼写检查器
求解：argmaxc P(c|w) -> argmaxc P(w|c)P(c)/P(w)
P(c)   : 文章出现一个正确拼写词c的频率
P(w|c) : 在用户想键入c的情况下敲成w的概率
argmaxc: 用来枚举所有可能的c并且选取概率最大的
    
因为用户可以输错任何词, 因此对于任何 c 来讲, 出现 w 的概率 P(w) 都是一样的, 从而我们在上式中忽略它, 写成:
argmaxc P(w|c) P(c)

如果遇到一个完全正确却没有见过的的新词，先验概率P(c)会等于0，
所有用一个小概率来代表这种情况，lambda:1
    
编辑距离：
两个词之间的编辑距离定义为使用了几次插入，删除，交换，替换的操作，
从一个词变到另一个词

```python
import re,collections

# 把语料中的单词全部抽取出来，转成小写，并且取出单词中间的特殊符号
def words(text):
    return re.findall('[a-z]+',text.lower())

def train(features):
    # 输入语料库没有出现过的词，词频的默认出现数为1
    model = collections.defaultdict(lambda:1)
    for f in features:
        model[f] += 1
    return model

NWORDS = train(words(open('datas\\big.txt').read()))

apphabet = 'abcdefghijklmnopqrstuvwxyz'

# 返回所有与单词w编辑距离为1的集合
def edits1(word):
    n = len(word)
    return set([word[0:i]+word[i+1:] for i in range(n)] +                          # deletion
               [word[0:i]+word[i+1]+word[i]+word[i+2:] for i in range(n-1)] +      # transposition
               [word[0:i]+c+word[i+1:] for i in range(n) for c in apphabet] +      # alteration
               [word[0:i]+c+word[i:] for i in range(n+1) for c in apphabet])       # insertion


# 返回所有与单词w编辑距离为2的集合
# 在这些编辑距离小于2的词中间，只把那些正确的词作为候选词
def edits2(word):
    return set(e2 for e1 in editsl(word) for e2 in edits1(el) if e2 in NWORDS)

def known_edits2(words):
    return set(w for w in words if w in NWORDS)

def known(words):
    return set(w for w in words if w in NWORDS)

def correct(word):
    # 编辑距离为0的优先，>1,>2
    candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
    print(candidates)
    return max(candidates,key=lambda w:NWORDS[w])
```


```python
# 测试
print(correct('mor'))
print(correct('leare'))
print(correct('tess'))
```

# 用 Xgboost 做二分类问题
判断病人是否会在 5 年内患糖尿病，数据前 8 列是变量，最后一列是预测值为 0 或 1。

```python
dataset = loadtxt('data\\pima-indians-diabetes.csv', delimiter=",")
X = dataset[:,0:8]
Y = dataset[:,8]

seed = 7
test_size = 0.33   # 测试样本33%，模型样本67%
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)
```


```python
# 训练模型
model = XGBClassifier()
model.fit(X_train, y_train)

# xgboost 的结果是每个样本属于第一类的概率，需要用 round 将其转换为 0 1 值
y_pred = model.predict(X_test)
predictions = [round(value) for value in y_pred]

accuracy = accuracy_score(y_test, predictions)
print("Accuracy: %.2f%%" % (accuracy * 100.0))
```


```python
# 监控模型表现，每加入一颗树后打印出 logloss，并打印出 Early Stopping 的点
model = XGBClassifier()
eval_set = [(X_test, y_test)] # 每加入一个模型就进行测试
# early_stopping_rounds连续10次都没有下降则停止，verbose 是否打印每一次效果
model.fit(X_train, y_train, early_stopping_rounds=10, eval_metric="logloss", eval_set=eval_set, verbose=True)

y_pred = model.predict(X_test)
predictions = [round(value) for value in y_pred]

accuracy = accuracy_score(y_test, predictions)
print("Accuracy: %.2f%%" % (accuracy * 100.0))
```


```python
dataset = loadtxt('datas\\pima-indians-diabetes.csv', delimiter=",")
X = dataset[:,0:8]
Y = dataset[:,8]
model = XGBClassifier()
model.fit(X, Y)

# 画出特征的重要性
plot_importance(model)
pyplot.show()
```
调节参数
1.learning rate
2.tree
    max_depth
    min_child_weight
    subsample, colsample_bytree
    gamma
3.正则化参数
    lambda
    alpha

```python
dataset = loadtxt('datas\\pima-indians-diabetes.csv', delimiter=",")
X = dataset[:,0:8]
Y = dataset[:,8]

model = XGBClassifier()
learning_rate = [0.0001, 0.001, 0.01, 0.1, 0.2, 0.3]
param_grid = dict(learning_rate=learning_rate)
kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=7)
grid_search = GridSearchCV(model, param_grid, scoring="neg_log_loss", n_jobs=-1, cv=kfold)  # 寻找好的学习率
grid_result = grid_search.fit(X, Y)

print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))
```

# 时间序列ARIMA


```python
%matplotlib inline
from __future__ import print_function
import pandas as pd
import numpy as np
from scipy import  stats
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.graphics.api import qqplot
```


```python
dta=[10930,10318,10595,10972,7706,6756,9092,10551,9722,10913,
     11151,8186,6422,6337,11649,11652,10310,12043,7937,6476,
     9662,9570,9981,9331,9449,6773,6304,9355, 10477,10148,
     10395,11261,8713,7299,10424,10795,11069,11602,11427,9095,
     7707,10767,12136,12812,12006,12528,10329,7818,11719,11683,
     12603,11495,13670,11337,10232,13261,13230,15535,16837,19598,
     14823,11622,19391,18177,19994,14723,15694,13248,9543,12872,
     13101,15053,12619,13749,10228,9725,14729,12518,14564,15085,
     14722,11999,9390,13481,14795,15845,15271,14686,11054,10395]

dta=pd.Series(dta, dtype=float) #可能arima训练模型的数据必须为float
print(dta.shape)
print(type(dta))
dta.index = pd.Index(sm.tsa.datetools.dates_from_range('2001','2090'))  # 添加索引
dta.plot(figsize=(12,8))
```


```python
# 一次差分
fig = plt.figure(figsize=(12,8))
ax1= fig.add_subplot(111)
diff1 = dta.diff(1)
diff1.plot(ax=ax1)
```


```python
# 二次差分，可以看出二阶差分后的时间序列与一阶差分相差不大，因此可以将差分次数d设置为1。
fig = plt.figure(figsize=(12,8))
ax2= fig.add_subplot(111)
diff2 = dta.diff(2)
diff2.plot(ax=ax2)
```


```python
# 选择合适的ARIMA模型，即ARIMA模型中合适的p,qp,q。
diff1= dta.diff(1)
fig = plt.figure(figsize=(12,8))
ax1=fig.add_subplot(211)
fig = sm.graphics.tsa.plot_acf(dta,lags=40,ax=ax1)  # lags 表示滞后的阶数
ax2 = fig.add_subplot(212)
fig = sm.graphics.tsa.plot_pacf(dta,lags=40,ax=ax2)
```
通过两图观察得到： 
* 自相关图显示滞后有三个阶超出了置信边界； 
* 偏相关图显示在滞后1至7阶（lags 1,2,…，7）时的偏自相关系数超出了置信边界，从lag 7之后偏自相关系数值缩小至0 

根据上图，猜测有以下模型可以供选择： 
1.）ARMA(0,1)模型：即自相关图在滞后1阶之后缩小为0，且偏自相关缩小至0，则是一个阶数q=1的移动平均模型； 
2.）ARMA(7,0)模型：即偏自相关图在滞后7阶之后缩小为0，且自相关缩小至0，则是一个阶层p=7的自回归模型；
3.）ARMA(7,1)模型：即使得自相关和偏自相关都缩小至零。则是一个混合模型。 

```python
# aic，bic，hqic均最小，是最佳模型
arma_mod70 = sm.tsa.ARMA(dta,(7,0)).fit()
print(arma_mod70.aic,arma_mod70.bic,arma_mod70.hqic)
arma_mod30 = sm.tsa.ARMA(dta,(0,1)).fit()
print(arma_mod30.aic,arma_mod30.bic,arma_mod30.hqic)
arma_mod71 = sm.tsa.ARMA(dta,(7,1)).fit()
print(arma_mod71.aic,arma_mod71.bic,arma_mod71.hqic)
arma_mod80 = sm.tsa.ARMA(dta,(8,0)).fit()
print(arma_mod80.aic,arma_mod80.bic,arma_mod80.hqic)
```


```python
# 对ARMA(8,0)模型所产生的残差做自相关图
resid = arma_mod80.resid

fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(211)
fig = sm.graphics.tsa.plot_acf(resid.squeeze(), lags=40, ax=ax1)
ax2 = fig.add_subplot(212)
fig = sm.graphics.tsa.plot_pacf(resid, lags=40, ax=ax2)
plt.show()
```
德宾-沃森检验,简称D-W检验，是目前检验自相关性最常用的方法，但它只使用于检验一阶自相关性。
因为自相关系数ρ的值介于-1和1之间，所以 0≤DW≤４。
DW＝O＝＞ρ＝１　　   即存在正自相关性 
DW＝４＜＝＞ρ＝－１　即存在负自相关性 
DW＝２＜＝＞ρ＝０　　即不存在（一阶）自相关性 
因此，当DW值显著的接近于O或４时，则存在自相关性，
而接近于２时，则不存在（一阶）自相关性。
这样只要知道ＤＷ统计量的概率分布，在给定的显著水平下，
根据临界值的位置就可以对原假设Ｈ０进行检验。

```python
print(sm.stats.durbin_watson(arma_mod80.resid))
# 结果=2.023，所以残差序列不存在自相关性。
```


```python
# 使用QQ图，它用于直观验证一组数据是否来自某个分布，或者验证某两组数据是否来自同一（族）分布
print(stats.normaltest(resid))
fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)
fig = qqplot(resid, line='q', ax=ax, fit=True)  # 结果表明基本符合正态分布
```
Ljung-Box test是对randomness的检验,或者说是对时间序列是否存在滞后相关的一种统计检验。
对于滞后相关的检验，我们常常采用的方法还包括计算ACF和PCAF并观察其图像，但是无论是ACF还是PACF都仅仅考虑是否存在某一特定滞后阶数的相关。
LB检验则是基于一系列滞后阶数，判断序列总体的相关性或者说随机性是否存在。 
时间序列中一个最基本的模型就是高斯白噪声序列。而对于ARIMA模型，其残差被假定为高斯白噪声序列，
所以当我们用ARIMA模型去拟合数据时，拟合后我们要对残差的估计序列进行LB检验，判断其是否是高斯白噪声，
如果不是，那么就说明ARIMA模型也许并不是一个适合样本的模型。

```python
r,q,p = sm.tsa.acf(resid.squeeze(), qstat=True)
data = np.c_[range(1,41), r[1:], q, p]
table = pd.DataFrame(data, columns=['lag', "AC", "Q", "Prob(>Q)"])
print(table.set_index('lag'))
```
检验的结果就是看最后一列前十二行的检验概率（一般观察滞后1\~12阶），
如果检验概率小于给定的显著性水平，比如0.05、0.10等就拒绝原假设，其原假设是相关系数为零。
就结果来看，如果取显著性水平为0.05，那么相关系数与零没有显著差异，即为白噪声序列。
prob值均大于0.05，所以残差序列不存在自相关性。

```python
# 对未来十年的数据进行预测
predict_dta = arma_mod80.predict('2090', '2100', dynamic=True)
print(predict_dta)

# 绘制图形
fig, ax = plt.subplots(figsize=(12, 8))
ax = dta.ix['2000':].plot(ax=ax)
fig = arma_mod80.plot_predict('2090', '2100', dynamic=True, ax=ax, plot_insample=False)
plt.show()
```

# 时间序列ARIMA：美国消费者信心指数


```python
%load_ext autoreload
%autoreload 2
%matplotlib inline
%config InlineBackend.figure_format='retina'

from __future__ import absolute_import, division, print_function
import sys
import os
import pandas as pd
import numpy as np

import statsmodels.api as sm
import statsmodels.formula.api as smf
import statsmodels.tsa.api as smt

import matplotlib.pylab as plt
import seaborn as sns

pd.set_option('display.float_format', lambda x:'%.5f' % x)
np.set_printoptions(precision=5, suppress=True)

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 100)
print ("display.max_columns = ", pd.get_option("display.max_columns"))
print ("display.max_rows = ", pd.get_option("display.max_rows"))

sns.set(style='ticks', context='poster')
```


```python
# 美国消费者信心指数
Sentiment = 'datas\\sentiment.csv'
Sentiment = pd.read_csv(Sentiment, index_col=0, parse_dates=[0])
print(Sentiment.head())

# Select the series from 2005 - 2016
sentiment_short = Sentiment.loc['2005':'2016']
#print(sentiment_short)
print(type(sentiment_short))
```


```python
sentiment_short.plot(figsize=(12,8))
plt.legend(bbox_to_anchor=(1.25, 0.5))
plt.title("Consumer Sentiment")
sns.despine()
plt.show()
```


```python
# 画出一阶差分与二阶差分的图
sentiment_short['diff_1'] = sentiment_short['UMCSENT'].diff(1)
sentiment_short['diff_2'] = sentiment_short['diff_1'].diff(1)
sentiment_short.plot(subplots=True, figsize=(18, 12))
```


```python
# 画出ACF和PACF图像，要关闭重启Kernel，因为上一步求差分会影响ACF,PACF
fig = plt.figure(figsize=(12,8))

ax1 = fig.add_subplot(211)
fig = sm.graphics.tsa.plot_acf(sentiment_short, lags=20,ax=ax1)
ax1.xaxis.set_ticks_position('bottom')
fig.tight_layout()

ax2 = fig.add_subplot(212)
fig = sm.graphics.tsa.plot_pacf(sentiment_short, lags=20, ax=ax2)
ax2.xaxis.set_ticks_position('bottom')
fig.tight_layout()
```


```python
# 整合图形
def tsplot(y, lags=None, title='', figsize=(14, 8)):
    
    fig = plt.figure(figsize=figsize)
    layout = (2, 2)
    ts_ax   = plt.subplot2grid(layout, (0, 0))
    hist_ax = plt.subplot2grid(layout, (0, 1))
    acf_ax  = plt.subplot2grid(layout, (1, 0))
    pacf_ax = plt.subplot2grid(layout, (1, 1))
    
    # 原始数据分布图
    y.plot(ax=ts_ax)
    ts_ax.set_title(title)
    
    # 原始数据直方图
    y.plot(ax=hist_ax, kind='hist', bins=25)
    hist_ax.set_title('Histogram')
    
    # ACF，PACF图
    smt.graphics.plot_acf(y, lags=lags, ax=acf_ax)
    smt.graphics.plot_pacf(y, lags=lags, ax=pacf_ax)
    
    [ax.set_xlim(0) for ax in [acf_ax, pacf_ax]]
    sns.despine()
    plt.tight_layout()
    return ts_ax, acf_ax, pacf_ax

tsplot(sentiment_short, title='Consumer Sentiment', lags=36)
```


```python
# 散点图表示
lags = 9

ncols = 3
nrows = int(np.ceil(lags/ncols))

fig, axes = plt.subplots(ncols=ncols, nrows=nrows, figsize=(4*ncols, 4*nrows))

for ax, lag in zip(axes.flat, np.arange(1, lags+1, 1)):
    lag_str = 't-{} steps'.format(lag)
    X = (pd.concat([sentiment_short, sentiment_short.shift(-lag)], axis=1,
                  keys=['y'] + [lag_str]).dropna())
    
    X.plot(ax=ax, kind='scatter', y='y', x=lag_str)
    corr = X.corr().as_matrix()[0][1]
    ax.set_ylabel('Original datas')
    ax.set_title('Lag: {} (corr={:.2f})'.format(lag_str, corr))
    ax.set_aspect('equal')
    sns.despine()               # 去掉每个图的上右边框

fig.tight_layout()
```

# ARIMA模型训练


```python
filename_ts = 'datas\\sentiment.csv'
ts_df = pd.read_csv(filename_ts, index_col=0, parse_dates=[0])
print(ts_df.head())

# Select the series from 2005 - 2016
ts_df = ts_df.loc['2005':'2016']

n_sample = ts_df.shape[0]
print(ts_df.shape)
print(ts_df)
```


```python
# Create a training sample and testing sample
n_train = int(0.95*n_sample) + 1    # 训练的样本数量
n_forecast = n_sample - n_train     # 预测的样本数量
print('n_train = ', n_train)
print('n_forecast = ', n_forecast)

ts_train = ts_df.iloc[:n_train]['UMCSENT']
ts_test = ts_df.iloc[n_train:]['UMCSENT']
print(ts_train.shape)
print(ts_test.shape)
print('Training Series : ', "\n", ts_train.tail(), "\n")
print('Testing Series : ', '\n', ts_test)
```


```python
# 整合图形
def tsplot(y, lags=None, title='', figsize=(14, 8)):
    
    fig = plt.figure(figsize=figsize)
    layout = (2, 2)
    ts_ax   = plt.subplot2grid(layout, (0, 0))
    hist_ax = plt.subplot2grid(layout, (0, 1))
    acf_ax  = plt.subplot2grid(layout, (1, 0))
    pacf_ax = plt.subplot2grid(layout, (1, 1))
    
    # 原始数据分布图
    y.plot(ax=ts_ax)
    ts_ax.set_title(title)
    
    # 原始数据直方图
    y.plot(ax=hist_ax, kind='hist', bins=25)
    hist_ax.set_title('Histogram')
    
    # ACF，PACF图
    smt.graphics.plot_acf(y, lags=lags, ax=acf_ax)
    smt.graphics.plot_pacf(y, lags=lags, ax=pacf_ax)
    
    [ax.set_xlim(0) for ax in [acf_ax, pacf_ax]]
    sns.despine()
    plt.tight_layout()
    return ts_ax, acf_ax, pacf_ax

tsplot(ts_train, title='Consumer Sentiment', lags=20)
```


```python
# Fit the model
arima200 = sm.tsa.SARIMAX(ts_train, order=(0,1,2))  # (p,d,q)
model_results=arima200.fit()
```


```python
# 遍历p,d,q的取值范围，选取最好效果的一个

import itertools

p_min = 0
d_min = 0
q_min = 0
p_max = 4
d_max = 1
q_max = 4

# Initialize a DataFrame to store the results
results_bic = pd.DataFrame(index=['AR{}'.format(i) for i in range(p_min,p_max+1)],
                           columns=['MA{}'.format(i) for i in range(q_min,q_max+1)])

for p,d,q in itertools.product(range(p_min,p_max+1),
                               range(d_min,d_max+1),
                               range(q_min,q_max+1)):
    if p==0 and d==0 and q==0:
        results_bic.loc['AR{}'.format(p), 'MA{}'.format(q)] = np.nan
        continue

    try:
        model = sm.tsa.SARIMAX(ts_train, order=(p, d, q),
                               #enforce_stationarity=False,
                               #enforce_invertibility=False,
                              )
        results = model.fit()
        results_bic.loc['AR{}'.format(p), 'MA{}'.format(q)] = results.bic
    except:
        continue
results_bic = results_bic[results_bic.columns].astype(float)
```


```python
# 热度图，横坐标为 q 值，纵坐标为 p 值
fig, ax = plt.subplots(figsize=(10, 8))
ax = sns.heatmap(results_bic,
                 mask=results_bic.isnull(),
                 ax=ax,
                 annot=True,
                 fmt='.2f',
                 );
ax.set_title('BIC')
```


```python
# 输出AIC、BIC评价指标
train_results = sm.tsa.arma_order_select_ic(ts_train, ic=['aic', 'bic'], trend='nc', max_ar=4, max_ma=4)
print('AIC', train_results.aic_min_order)
print('BIC', train_results.bic_min_order)
```


```python
#残差分析 正态分布 QQ图线性
model_results.plot_diagnostics(figsize=(16, 12))
```

# k-mean图片压缩


```python
from skimage import io
from sklearn.cluster import KMeans
import numpy as np

image = io.imread('datas\\1.jpg')
io.imshow(image)
io.show()

rows = image.shape[0]
cols = image.shape[1]
print("像素：", rows, " X ", cols)

# 每个像素点当做一个样本（一共有像素行乘列的行数），每个为三原色
image = image.reshape(image.shape[0] * image.shape[1], 3)
# 128个簇，200次迭代
kmeans = KMeans(n_clusters=128, n_init=10, max_iter=200)
kmeans.fit(image)
print(image)
print(kmeans.cluster_centers_)
print(kmeans.labels_)

clusters = np.asarray(kmeans.cluster_centers_, dtype=np.uint8)
labels = np.asarray(kmeans.labels_, dtype=np.uint8)
labels = labels.reshape(rows, cols)
print(labels)

print(clusters, shape)
np.save('datas\\t1.npy', clusters)
io.imsave('datas\\t1.jpg', labels)
```


```python
# 查看压缩效果图
image = io.imread('datas\\t1.jpg')
io.imshow(image)
io.show()
```

# PCA主成分分析降维


```python
%matplotlib inline
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

iris = sns.load_dataset('iris')
print(iris.head(5))
```


```python
X = iris.iloc[:, 0:4].values
Y = iris.iloc[:, 4].values
#print('X = ',type(X), '\n', X)
#print('Y = \n', type(Y), '\n',Y)
```


```python
label_dict = {1: 'Iris-Setosa',
              2: 'Iris-Versicolor',
              3: 'Iris-Virginica'}
feature_dict = {0: 'sepal length [cm]',
                1: 'sepal width [cm]',
                2: 'petal length [cm]',
                3: 'petal length [cm]',}

plt.figure(figsize=(8, 6))
for cnt in range(4):
    plt.subplot(2, 2, cnt+1)
    for lab in ('setosa', 'versicolor', 'virginica'):
        plt.hist(X[Y==lab, cnt],
                label = lab,
                bins = 10,
                alpha = 0.3,)
        plt.xlabel(feature_dict[cnt])
        plt.legend(loc='upper right', fancybox=True, fontsize=8)

plt.tight_layout()
plt.show()
```


```python
from sklearn.preprocessing import StandardScaler
X_std = StandardScaler().fit_transform(X)   # 数据标准化
print(X_std)
```


```python
mean_vec = np.mean(X_std, axis=0)  # 求每一列的均值
print(mean_vec)
cov_mat = (X_std - mean_vec).T.dot((X_std - mean_vec)) / (X_std.shape[0]-1)
print('Covariance matrix \n %s' % cov_mat)
```


```python
# 也可以直接使用函数得到协方差矩阵
cov_mat = np.cov(X_std.T)
print(cov_mat)      # 转置？？
```


```python
# 求特征值，特征向量
eig_vals, eig_vecs = np.linalg.eig(cov_mat)
print('Eigenvectors : \n', eig_vecs)
print('\n Eigenvalues \n', eig_vals)
```


```python
# 归一化，每个特征向量占据的百分比
tot = sum(eig_vals)
var_exp = [(i/tot)*100 for i in sorted(eig_vals, reverse=True)]
print(var_exp)
# 累加
cum_var_exp = np.cumsum(var_exp)
print(cum_var_exp)
```


```python
plt.figure(figsize=(6,4))
plt.bar(range(4), var_exp, alpha=0.5, align='center',
       label = 'individual explained variance')
plt.step(range(4), cum_var_exp, where='mid',
        label = 'cumulative explained variance')

plt.ylabel('Explained variance ratio')
plt.xlabel('Principal components')
plt.legend()
plt.tight_layout()
plt.show()
```


```python
# 选取俩个特征向量
matrix_w = np.hstack((eig_vecs[:,0].reshape(4,1),
                      eig_vecs[:,1].reshape(4,1)))
print(matrix_w)
```


```python
Y_result = X_std.dot(matrix_w)
print(Y_result)
```


```python
# 四维选取两维绘图
plt.figure(figsize=(6, 4))
for lab, col in zip(('setosa', 'versicolor', 'virginica'),
                   ('blue', 'red', 'green')):
    plt.scatter(X[Y==lab, 0],
                X[Y==lab, 1],
                label = lab,
                c = col)
plt.xlabel('sepal_len')
plt.ylabel('sepal_wid')
plt.legend(loc='best')
plt.tight_layout()
plt.show()
```


```python
# 降维后，此时X轴与Y轴的实际意义已经不能确定了
plt.figure(figsize=(6, 4))
for lab, col in zip(('setosa', 'versicolor', 'virginica'),
                   ('blue', 'red', 'green')):
    plt.scatter(Y_result[Y==lab, 0],
                Y_result[Y==lab, 1],
                label = lab,
                c = col)
plt.xlabel('Principle Component 1')
plt.ylabel('Principle Component 2')
plt.legend(loc='lower center')
plt.tight_layout()
plt.show()
```

# 神经网络分类


```python
%matplotlib inline
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = (10.0,8.0)    # 创建一个10*8大小的绘图对象
plt.rcParams['image.interpolation'] = 'nearest'# 差值方式
plt.rcParams['image.cmap'] = 'gray'            # 灰度空间

np.random.seed(0) # 用于指定随机数生成时所用算法开始的整数值，如果使用相同的seed值，则每次生成的随机数相同
N = 100           # 每类有一百个点
D = 2             # 每个点是二维的，即x和y值为样本的特征向量
K = 3             # 总共有三类，因此总共三百个训练样本
X = np.zeros((N*K,D))           # 生成一个300*2的零矩阵
y = np.zeros(N*K,dtype='uint8') # 生成一个1*300的零矩阵，类型为uint8

for j in range(K):
    ix = range(N*j,N*(j+1))
    r = np.linspace(0.0,1,N)                                 # radius半径
    t = np.linspace(j*4,(j+1)*4,N) + np.random.randn(N)*0.2 # theta角度
    X[ix] = np.c_[r*np.sin(t),r*np.cos(t)] # np.c_是按行连接两个矩阵，就是把两矩阵左右相加，要求行数相等
    y[ix] = j # 给300个点分类，每一百一类，即[0，99]为0类，[100，199]为1类，以此类推
    
fig = plt.figure()
plt.scatter(X[:,0],X[:,1],c=y,s=40,cmap=plt.cm.Spectral) #scatter画散点图；
plt.xlim([-1,1])
plt.ylim([-1,1])
```


```python
# 使用单层神经网络，未使用激活函数，即线性分类
w = 0.01*np.random.randn(D,K) # 权值初始化，2*3，即输入两个特征向量，输出三个类别，[-0.01，0.01]
b = np.zeros((1,K))           # 阈值初始化，1*3的零矩阵
step_size = 1e-0              # 学习步长为1
reg = 1e-3                    # 正则化系数，10的负三次方
num_examples = X.shape[0]     # X是300*2，shape[0]求它第一维的长度即样本个数

for i in range(200):           # 迭代两百次
    scores = np.dot(X,w)+b     # 下面是softmax分类器解释,scores为300*3
    exp_score = np.exp(scores) # 为300*3
    probs = exp_score/np.sum(exp_score,axis = 1,keepdims = True) # 每个点分类的得分所占概率（包括正确分类和错误分类）,#300*3
    corect_logprobs = -np.log(probs[range(num_examples),y])       # probs[range(num_examples),y]是正确分类的概率
    data_loss = np.sum(corect_logprobs)/num_examples
    reg_loss = 0.5*reg*np.sum(w*w)                                # 正则化项
    loss = data_loss+reg_loss
    if i%10 == 0:  #每迭代10次输出一次Loss值
        print('iteration %d:loss %f'%(i,loss))

    dscores = probs
    dscores[range(num_examples),y] -= 1 # Loss关于scores的偏导，为probs-1
    dscores /= num_examples

    dW = np.dot(X.T,dscores) # data_loss传递下来的梯度
    db = np.sum(dscores,axis = 0,keepdims = True)

    dW += reg*w #再加上正则化项传递下来的梯度
    w += -step_size * dW
    b += -step_size * db

#求一下分类的准确率
scores = np.dot(X,w)+b
predicted_class = np.argmax(scores , axis=1)                     # predicted_class为[1,300],为每个点得分最大的所在的那个列数，即类
print('training accuracy:%.2f'%(np.mean(predicted_class == y)) ) # mean（）是求均值

#画出分类效果
h=0.02
x_min , x_max = X[:,0].min() - 1, X[:,0].max() + 1
y_min , y_max = X[:,1].min() - 1, X[:,1].max() +1
xx, yy = np.meshgrid(np.arange(x_min , x_max ,h),
                     np.arange(y_min , y_max ,h))
Z = np.dot(np.c_[xx.ravel(),yy.ravel()],w) + b
Z = np.argmax(Z,axis = 1)
Z = Z.reshape(xx.shape)
fig = plt.figure()
plt.contourf(xx,yy,Z,cmap=plt.cm.Spectral,alpha=0.8)
plt.scatter(X[:,0],X[:,1],c=y,s=40,cmap=plt.cm.Spectral)
plt.xlim(xx.min(),xx.max())
plt.ylim(yy.min(),yy.max())
plt.show()
```


```python
#使用双层神经网络，使用Relu激活函数,将之前的线性分类变为非线性分类
h = 100                        # 隐层神经元个数
w = 0.01*np.random.randn(D,h)  # D为输入层神经元个数
b = np.zeros((1,h))
w2 = 0.01*np.random.randn(h,K) # K为输出层神经元个数
b2 = np.zeros((1,K))
step_size = 1e-0               # 学习步长为1
reg = 1e-3                     # 正则化系数，10的负三次方
num_examples = X.shape[0]      # 由于X是300*3矩阵，这里的shape[0]读取它第一维长度及300为样本个数

for i in range(10000): # 迭代两百次
    hidden_layer = np.maximum(0,np.dot(X,w)+b) # ReLu激活函数，hidden_layer为300*100
    scores = np.dot(hidden_layer,w2) + b2

    exp_scores = np.exp(scores)
    probs = exp_scores / np.sum(exp_scores,axis=1,keepdims=True)

    corect_logprobs = -np.log(probs[range(num_examples),y])
    data_loss = np.sum(corect_logprobs) / num_examples
    reg_loss = 0.5*reg*np.sum(w*w) + 0.5*reg*np.sum(w2*w2)
    loss = data_loss + reg_loss
    if i%1000 == 0:  # 每迭代100次输出一次Loss值
        print('iteration %d:loss %f'%(i,loss))

    dscores = probs
    dscores[range(num_examples), y] -= 1  # Loss关于scores的偏导，为probs-1
    dscores /= num_examples

    dw2 = np.dot(hidden_layer.T,dscores)
    db2 = np.sum(dscores,axis=0,keepdims=True)

    dhidden = np.dot(dscores,w2.T) # 梯度的反向传播，dihidden是300*100
    dhidden[hidden_layer <= 0] = 0 # hidden_layer是隐层的输出值，若隐层输出为0，则对应位置的dhidden梯度为0不传播

    dw = np.dot(X.T,dhidden)
    db = np.sum(dhidden,axis=0,keepdims=True)

    dw2 += reg * w2
    dw += reg * w

    w += -step_size * dw
    w2+= -step_size * dw2
    b += -step_size * db
    b2 += -step_size * db2

# 求一下准确率
hidden_layer = np.maximum(0,np.dot(X,w)+b)
scores = np.dot(hidden_layer,w2) + b2
predicted_class = np.argmax(scores,axis = 1)
print('training accuracy: %.2f' %(np.mean(predicted_class == y)))

h=0.02
x_min , x_max = X[:,0].min() - 1, X[:,0].max() + 1
y_min , y_max = X[:,1].min() - 1, X[:,1].max() +1
xx, yy = np.meshgrid(np.arange(x_min , x_max ,h),
                     np.arange(y_min , y_max ,h))
Z = np.dot(np.maximum(0,np.dot(np.c_[xx.ravel(),yy.ravel()],w)+b),w2) + b2
Z = np.argmax(Z,axis = 1)
Z = Z.reshape(xx.shape)
fig = plt.figure()
plt.contourf(xx,yy,Z,cmap=plt.cm.Spectral,alpha=0.8)
plt.scatter(X[:,0],X[:,1],c=y,s=40,cmap=plt.cm.Spectral)
plt.xlim(xx.min(),xx.max())
plt.ylim(yy.min(),yy.max())
plt.show()
```
