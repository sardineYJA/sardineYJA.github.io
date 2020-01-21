---
layout: post
title: "Python 数据分析篇4"
date: 2019-01-12
description: "python数据分析"
tag: Python

---


```python
import pandas as pd
import numpy as np
import scipy.stats as ss
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.feature_selection import SelectKBest,RFE,SelectFromModel
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
```

## 异常值处理


```python
df = pd.DataFrame({"A": ["a0", "a1", "a1", "a2", "a3", "a4"],
                   "B": ["b0", "b1", "b2", "b2", "b3", None],
                   "C": [1, 2, None, 3, 4, 5], 
                   "D": [0.1, 10.2, 11.4, 8.9, 9.1, 12], 
                   "E": [10, 19, 32, 25, 8, None],
                   "F": ["f0", "f1", "g2", "f3", "f4", "f5"]})
print(df)  # 字符的空为 None，数值的空为 NaN

df.isnull()  # 打印空值位置

df.dropna()   # 将空值的行直接删除

df.dropna(subset=["B"])   # 删除属性 B 空值的行，而 C 的空值保留

print(df)
df.duplicated(["A"],keep="first")  # 属性 A 中找相同值，first首个，last最后一个

df.duplicated(["A","B"],keep="first")  # 属性 A B 的值都相同才算重复

 # 丢弃属性 A 重复值的行，保留first首个，last最后一个，False丢弃所有重复行；inplace=False,return a copy
df.drop_duplicates(["A"],keep="first",inplace=False)  

df["B"].fillna("b*")   # 替换空值

df["E"].fillna(df["E"].mean())  # 使用均值替换空值

df["C"].interpolate()    # 插入相邻两个数的平均值，如果是首个或尾个，则与邻近相同

df["E"].interpolate(method="spline",order=3)    # 三次样条插值

# 四分位数处理异常值
print(df)
upper_q = df['D'].quantile(0.75)   # 上四分位数
lower_q = df['D'].quantile(0.25)   # 下四分位数
q_int = upper_q - lower_q          # 四分位间距
print('上四分位数 = ',upper_q,'；下四分位数 = ',lower_q,'；四分位间距 = ',q_int)
# 第 0 行数据异常，去掉
print(df[df['D']>lower_q-1.5*q_int][df['D']<upper_q+1.5*q_int])

# 遍历属性 F 的每一个值，如果不是以 f 开头的行直接去掉
df[[True if item.startswith("f") else False for item in list(df["F"].values)]]
```

## 特征选择


```python
#特征选择
df=pd.DataFrame({"A":ss.norm.rvs(size=10),  # 10个正态分布的数
                 "B":ss.norm.rvs(size=10),
                 "C":ss.norm.rvs(size=10),
                 "D":np.random.randint(low=0,high=2,size=10)}) # D 属性为标注取值为0,1
X=df.loc[:,["A","B","C"]]
Y=df.loc[:,"D"]
print("X",X)
print("Y",Y)
```


```python
# 过滤思想进行特征选择
skb = SelectKBest(k=2)
skb.fit(X.values,Y.values)
print(skb.transform(X.values)) # 可以看出特征 B 去掉了
```


```python
# 包裹思想进行特征选择，特征集合构造简单模型，根据系数去掉弱特性
rfe = RFE(estimator=SVR(kernel="linear"),n_features_to_select=2,step=1) # step 每次去掉的特征数目
print(rfe.fit_transform(X,Y))  # 可以看出特征 B 去掉了
```


```python
# 嵌入思想进行特征选择，建立简单的回归模型，根据系数去掉弱特性
sfm=SelectFromModel(estimator=DecisionTreeRegressor(),threshold=0.1)  # threshold 特征因子数，如果特征低于此数则会被去掉
print(sfm.fit_transform(X,Y))
```

## 特征变换

```python
lst=[6,8,10,15,16,24,25,40,67]
# 离散化---等深
binings,bins=pd.qcut(lst,q=3,retbins=True,labels=["low","medium","high"])
print(binings)
print(list(bins))
```


```python
# 离散化---等距
print(pd.cut(lst,bins=3))
print(pd.cut(lst,bins=4,labels=["low","medium","high","very high"]))
```


```python
# 归一化：(X-Xmin) / (Xmax-Xmin) ；转化后总和为1
from sklearn.preprocessing import MinMaxScaler,StandardScaler
print(MinMaxScaler().fit_transform(np.array([1,4,10,15,21]).reshape(-1,1)))  # -1，表示不论几行
```


```python
# 标准化：(X-X均值) / 标准差；转化后均值为0，标准差为1
print(StandardScaler().fit_transform(np.array([1,1,1,1,0,0,0,0]).reshape(-1,1)))
print(StandardScaler().fit_transform(np.array([1, 0, 0, 0, 0, 0, 0, 0]).reshape(-1, 1)))
```


```python
# 数值化---标签化
from sklearn.preprocessing import LabelEncoder,OneHotEncoder
print(LabelEncoder().fit_transform(np.array(["Down","Down","Up","Down","Up"]).reshape(-1,1)))
print(LabelEncoder().fit_transform(np.array(["Low","Medium","Low","High","Medium"]).reshape(-1,1)))
```


```python
# 数值化---独热编码
lb_encoder = LabelEncoder()
lb_encoder = lb_encoder.fit(np.array(["Red","Yellow","Blue","Green"]))
lb_trans_f = lb_encoder.transform(np.array(["Red","Yellow","Blue","Green"]))
print(lb_trans_f)  

# 标签化可能会影响变量两两之间的关系，比如Red，与Yellow的距离为1，而与Blue的距离为2
# 独热编码可以保证两两之间关系还是一样
oht_enoder = OneHotEncoder().fit(lb_trans_f.reshape(-1,1))
print(oht_enoder.transform(lb_encoder.transform(np.array(["Red","Red","Yellow","Blue","Green"])).reshape(-1,1)).toarray())
```


```python
# 规范化
from sklearn.preprocessing import Normalizer
nor_a = [[1,1,3,-1,2],[2,1,3,-2,-1]]
print(nor_a)
print(Normalizer(norm="l1").fit_transform(nor_a))  # 对一行规范化
print(Normalizer(norm="l2").fit_transform(nor_a))  # 对一行规范化
```


```python
#LDA降维
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
X = np.array([[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]])
y = np.array([0, 0, 0, 1, 1, 1])
clf = LinearDiscriminantAnalysis(n_components=1)
print(clf.fit_transform(X, y))  # 降成一维后

lda = LinearDiscriminantAnalysis()
lda.fit(X, y)
print(lda.predict([[-0.8, -1]]))   # 将其分类到 0；可以当做分类器使用
```
