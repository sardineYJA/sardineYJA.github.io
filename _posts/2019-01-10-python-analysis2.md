---
layout: post
title: "python数据分析篇2"
date: 2019-01-10
description: "简单介绍一下python数据分析"
tag: python

---

```python
%matplotlib inline
import numpy as np
import scipy.stats as ss
import numpy as np
import pandas as pd
import seaborn as sns
from statsmodels.graphics.api import qqplot
from matplotlib import pyplot as plt
```


```python
norm_dist = ss.norm.rvs(size=20)   # 标准正态分布
print(norm_dist)

# 检查是否符合正太分布
# returns a 2-tuple of the chi-squared statistic(卡方统计量), and the associated p-value(相关P值).
# If the p-val is very small, it means it is unlikely that the data came from a normal distribution.
# For example:  # pval < 0.05
print(ss.normaltest(ss.uniform.rvs(size = 100)))

print(ss.normaltest(norm_dist))
```

>NormaltestResult(statistic=26.324735009186401, pvalue=1.92157094760205e-06)
>NormaltestResult(statistic=3.1799326649700697, pvalue=0.20393247751837457)
    


# 卡方检验
```python
# 想对两个或两个以上因子彼此之间是否相互独立做检验时，用卡方检验
ss.chi2_contingency([[15,95],[85,5]])
# 卡方值，P值，自由度，与原数据数组同维度的对应理论值
```
>(126.08080808080808, 2.9521414005078985e-29, 1, array([[ 55.,  55.],[ 45.,  45.]]))


# t 检验
```python
# t 检验：正态均值的比较，X,Y
ss.ttest_ind(ss.norm.rvs(size=10), ss.norm.rvs(size=20))
```
>Ttest_indResult(statistic=0.95450529436678189, pvalue=0.34799646860843469)


```python
ss.ttest_ind([65,68,72,75,82,85,91,95], [50,59,71,80])
```
>Ttest_indResult(statistic=1.9860353294081732, pvalue=0.07511465244258364)


# F 检验（方差检验）
```python
# F 检验（方差检验）：多个正态总体方差的比较
ss.f_oneway([49,50,39,40,43], [28,32,30,26,34], [38,40,45,42,48])
```
>F_onewayResult(statistic=17.619417475728156, pvalue=0.00026871530798216412)

```python
ss.f_oneway([1071,1076,1070,1083,1082,1067,1078,1080,1084,1075,1080,1075],
           [1074,1069,1067,1068,1079,1075,1082,1064,1073,1070,1072,1075])
```
>F_onewayResult(statistic=4.2148410858000274, pvalue=0.052152007956100782)

```python
ss.f_oneway([5.5,4.6,4.4,3.4,1.9,1.6,1.1,0.8,0.1,-0.1],
            [3.7,3.4,2.0,2.0,0.8,0.7,0,-0.1,-0.2,-1.6])
```
>F_onewayResult(statistic=2.3187173412093087, pvalue=0.14520038876939032)



# QQ图
```python
# qq图默认检查是否符合正态分布
plt.show(qqplot(ss.norm.rvs(size=100)))
```
![png](/images/posts/2019-01-10/output_13_0.png)


# 相关系数
```python
s1 = pd.Series([1,2,3,4,5])
s2 = pd.Series([2,3,7,9,12])
print(s1.corr(s2))
print(s1.corr(s2, method='spearman'))
```
>0.988371697651
>1.0
    

# 线性回归
```python
x = np.arange(10).astype(np.float).reshape((10,1))
y = x*3 + 4 + np.random.random((10,1))  # 加上0-1的噪声
print(x.T)
print(y.T)
```
>[[ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9.]]
>[[  4.6851856    7.89541776  10.86978756  13.63687922  16.12832461
>   19.41637768  22.21882588  25.26868984  28.41653041  31.94667092]]
    


```python
from sklearn.linear_model import LinearRegression
reg = LinearRegression()
res = reg.fit(x, y)
print(reg.predict(x))  # 估计值
print(reg.coef_)       # 参数
print(reg.intercept_)  # 截距
```
```
    [[  4.68382638]
     [  7.65370251]
     [ 10.62357863]
     [ 13.59345476]
     [ 16.56333088]
     [ 19.53320701]
     [ 22.50308314]
     [ 25.47295926]
     [ 28.44283539]
     [ 31.41271151]]
    [[ 2.96987613]]
    [ 4.68382638]
 ```   


# PCA降维
默认使用奇异分解降维
Linear dimensionality reduction using Singular Value Decomposition of the data to project it to a lower dimensional space.
explained_variance_，它代表降维后的各主成分的方差值。方差值越大，则说明越是重要的主成分。
explained_variance_ratio_，它代表降维后的各主成分的方差值占总方差值的比例，这个比例越大，则越是重要的主成分。
components_ ：返回具有最大方差的成分。

n_components='mle'，将自动选取特征个数n

```python
from sklearn.decomposition import PCA
data = np.array([np.array([2.5,0.5,2.2,1.9,3.1,2.3,2,1,1.5,1.1]),
                np.array([2.4,0.7,2.9,2.2,3,2.7,1.6,1.1,1.6,0.9]),
                np.array([2.2,0.3,2.3,2.8,3,1.7,1.3,1.6,1.1,1.9]),
                np.array([1.2,1.3,2.2,1.8,2,1.2,2.3,2.1,2.2,2.9])]).T
print(data)

lower_dim = PCA(n_components=2)             # 降成2维
lower_dim.fit(data)
print('信息量：',          lower_dim.explained_variance_ratio_) # 降维后信息量
print('主成分方差值：',    lower_dim.explained_variance_)       # 主成分方差值
print('最大方差的成分：\n',lower_dim.components_)               # 最大方差的成分
print('降维后：\n',        lower_dim.fit_transform(data))       # 降维后数据
```
```
    [[ 2.5  2.4  2.2  1.2]
     [ 0.5  0.7  0.3  1.3]
     [ 2.2  2.9  2.3  2.2]
     [ 1.9  2.2  2.8  1.8]
     [ 3.1  3.   3.   2. ]
     [ 2.3  2.7  1.7  1.2]
     [ 2.   1.6  1.3  2.3]
     [ 1.   1.1  1.6  2.1]
     [ 1.5  1.6  1.1  2.2]
     [ 1.1  0.9  1.9  2.9]]
    信息量： [ 0.7539339   0.17181876]
    主成分方差值： [ 1.72818404  0.39384678]
    最大方差的成分：
     [[-0.57304158 -0.6185144  -0.53346569  0.06691513]
     [-0.11412554 -0.25886415  0.52353361  0.8036649 ]]
    降维后：
     [[-0.94936661 -0.58528601]
     [ 2.26846737 -0.83131326]
     [-1.07314277  0.17553784]
     [-0.76176911  0.33128125]
     [-2.03754065  0.25267899]
     [-0.75357976 -0.90188695]
     [ 0.38569147  0.09171922]
     [ 1.09456752  0.33160393]
     [ 0.77221389 -0.03629123]
     [ 1.05445864  1.17195621]]
```  


# 交叉分析
```python
df=pd.read_csv("data\\HR.csv")
dp_indices=df.groupby(by="department").indices              # 获取到所有部门的分类索引，如 marketing,sales等部门
# print(dp_indices['marketing'])
sales_values=df["left"].iloc[dp_indices["sales"]].values    # sales 部门的离职登记
print(sales_values)
technical_values=df["left"].iloc[dp_indices["technical"]].values # technical 部门的离职登记
print(technical_values)
print(ss.ttest_ind(sales_values,technical_values))          # t 检验，比较均值
```

```python
# 计算每个部门，两两之间的 t 检验，部门与部门之间的离职率是否有显著差异；原假设u=u0
dp_keys=list(dp_indices.keys())
print(dp_keys)

dp_t_mat=np.zeros((len(dp_keys),len(dp_keys)))
print(dp_t_mat)

# 计算每个部门两两之间的 p 值
for i in range(len(dp_keys)):
    for j in range(len(dp_keys)):
        p_value=ss.ttest_ind(df["left"].iloc[dp_indices[dp_keys[i]]].values,\
                                    df["left"].iloc[dp_indices[dp_keys[j]]].values)[1]
        if p_value<0.05:       
            dp_t_mat[i][j]=-1       # p 值过小，赋予同一颜色值（离职率有显著差异）
        else:
            dp_t_mat[i][j]=p_value  # （离职率没有显著差异）
plt.figure(figsize=(18, 6))
sns.heatmap(dp_t_mat,xticklabels=dp_keys,yticklabels=dp_keys)
plt.show()
```
```
    ['marketing', 'support', 'RandD', 'technical', 'management', 'hr', 'accounting', 'IT', 'product_mng', 'sale', 'sales']
    [[ 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.]
     [ 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.]
     [ 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.]
     [ 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.]
     [ 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.]
     [ 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.]
     [ 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.]
     [ 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.]
     [ 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.]
     [ 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.]
     [ 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.]]
    

    E:\Anaconda3\lib\site-packages\scipy\stats\_distn_infrastructure.py:879: RuntimeWarning: invalid value encountered in greater
      return (self.a < x) & (x < self.b)
    E:\Anaconda3\lib\site-packages\scipy\stats\_distn_infrastructure.py:879: RuntimeWarning: invalid value encountered in less
      return (self.a < x) & (x < self.b)
    E:\Anaconda3\lib\site-packages\scipy\stats\_distn_infrastructure.py:1818: RuntimeWarning: invalid value encountered in less_equal
      cond2 = cond0 & (x <= self.a)
```  


![png](/images/posts/2019-02-03/output_24_2.png)



```python
# 透视表交叉分析 ,aggfunc聚合函数
# piv_tb = pd.pivot_table(df, values="left",
#                       index=["department", "salary"],
#                       columns=["time_spend_company"],aggfunc=np.mean)
# print(piv_tb)
# piv_tb = pd.pivot_table(df, values="left",
#                       index=["department"],
#                       columns=["number_project"],aggfunc=np.mean)
# print(piv_tb)
piv_tb = pd.pivot_table(df, values="left", 
                        index=["promotion_last_5years", "salary"],
                        columns=["Work_accident"],aggfunc=np.mean)
print(piv_tb) #可以看出5年没有升职，没有工作事故，工资较低的人离职率高（0.3319）
              # nme 应该是异常值
```
```
    Work_accident                        0         1
    promotion_last_5years salary                    
    0                     high    0.082996  0.000000
                          low     0.331942  0.090020
                          medium  0.230683  0.081655
                          nme     1.000000       NaN
    1                     high    0.000000  0.000000
                          low     0.229167  0.166667
                          medium  0.028986  0.023256
```


```python
# 去掉异常值，本应该在数据预处理做的
piv_tb.drop(piv_tb.index[[3]],inplace=True)  # inplace=True表示直接在原数据上修改
print(piv_tb)
```
```
    Work_accident                        0         1
    promotion_last_5years salary                    
    0                     high    0.082996  0.000000
                          low     0.331942  0.090020
                          medium  0.230683  0.081655
    1                     high    0.000000  0.000000
                          low     0.229167  0.166667
                          medium  0.028986  0.023256
 ```   


```python
sns.heatmap(piv_tb, vmax = 1, vmin = 0,                  # 最大值1，最小值0
           cmap=sns.color_palette('Reds',n_colors=256))  # 颜色随值大而变深
plt.show()
```


![png](/images/posts/2019-02-03/output_27_0.png)



```python
# 分组分析
sns.barplot(x="salary",y="left",hue="department",data=df)
plt.show()
```
![png](/images/posts/2019-02-03/output_28_1.png)



```python
# 去掉两个空值，本应该在数据预处理做的
sl_s = df["satisfaction_level"]
#print(sl_s)
sl_s = sl_s[sl_s > 0]
#print(sl_s)

# 值过多，绘制图片不成功
# sns.barplot(list(range(len(sl_s))),sl_s.sort_values())
# plt.show()
# 目的是查看值的转折点（跳跃点）


d = pd.Series([11,22,22,33,55,77,88,55,44,33])
sns.barplot([0,1,2,3,4,5,6,7,8,9],d.sort_values())
plt.show()

```
![png](/images/posts/2019-02-03/output_29_1.png)

