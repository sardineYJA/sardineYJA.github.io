---
layout: post
title: "Python 数据分析篇1"
date: 2019-01-09
description: "python数据分析"
tag: Python

---

## 前言


以前学习过一些python分析的知识和书籍，记录一些python对数据的常用分析以及处理。


## 处理方式

- Correcting  对错误值修正
- Completing  对缺失值补充
- Creating    创造新的属性值
- Converting  转换成label，onehot


```python
import warnings   # 忽视警告
warnings.filterwarnings('ignore')
```


```python
# 读写文件，基础操作

data = pd.read_excel('1.xls', index_col = u'日期') # 读取数据，指定“日期”列为索引列
train = pd.read_csv('train.csv')                   # 读取
data.to_csv("Submission.csv", index=False)        # 写进

train.info()                   # 数据信息
train.head(5)                  # 前5个样本
train.sample(10)               # 随机10个样本
print(train.columns.values)    # 查看所有列值的名称
print(train.Sex.unique())      # 查看属性Sex(Sex列)的取值种类
print(train.Sex.value_counts())# 查看属性Sex(Sex列)每类的数量
train.isnull().sum()           # 每列空值的数量
train['Sex'].fillna('male')    # 补充空值
train.drop(['Sex', 'Age'], axis = 1) # 去掉Sex列，Age列


data.describe(include = 'all')   # 数据基本情况
data['Sex'].mode()# 返回Sex列的众数
data.sum()        # 每列的总和
data.mean()       # 每列的均值
data.var()        # 每列的方差
data.std()        # 每列的标准差
data.corr()       # 相关系数矩阵，参数method='pearson','spearman','kendall'
data.cov()        # 协方差矩阵
data.skew()       # 偏度（三阶矩）分布的对称性状况的描述，正值，则 x 均值左侧的离散度比右侧弱
data.kurt()       # 峰度（四阶矩）分布的峰值是否突兀或是平坦的描述，
                  # 峰值比正态分布的高时，峰度大于3；当比正态分布的低时，峰度小于3

data.max()
data.min()
data.abs()
d1 = pd.cut(data, 4, labels = range(k)) # 等宽离散化
d2 = pd.qcut(data, 4, labels=range(k))  # 等频率离散化
print(pd.value_counts(d1))  # 每个面元有多少个元素

pd.cumsum()   # 累加和，依次给出前1,2,3....的和
pd.cumprod()  # 累乘积，依次给出前1,2,3....的积
pd.cummax()   # 依次给出前1,2,3....最大值
pd.cummin()   # 依次给出前1,2,3....最小值

pd.rolling_sum()
pd.rolling_mean()  
pd.rolling_var()
pd.rolling_std() 
pd.rolling_corr()  
pd.rolling_cov()   
pd.rolling_skew() 
pd.rolling_kurt() 

pd.get_dummies(df)                         # one-hot编码
pd.crosstab(data['Sex'],data['Survived'])  # 以Sex属性为行，Survived属性为列的交叉表
df.pivot_table(index=['产地','类别'])      # 透视表，以产地分类，再以类别分类，其他属性输出均值
df['target'].groupby(df['Sex']).mean()     # 以Sex属性分类，分成male,female，计算属性target的均值（即male的target均值，femal的target均值）

```


```python
# 交叉验证 
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(data, data[target], test_size=0.4, random_state=0)
```


```python
from sklearn import preprocessing
df = preprocessing.scale(X_train) # 每列标准化,0均值,1标准差

# 对新的数据集进行同样的转换
scaler = preprocessing.StandardScaler().fit(X_train)    # 标椎化
data = scaler.transform(new_data)

data = preprocessing.normalize(X_train, norm='l2')      # 正则化
normalizer = preprocessing.Normalizer().fit(X_train)    # 计算：每行的根号范数除以范数
normalizer.transform(x)

min_max_scaler = preprocessing.MinMaxScaler()
X_train_minmax = min_max_scaler.fit_transform(X_train)  # 归一化[0,1]
X_test_minmax = min_max_scaler.transform(X_test)        # 用前面计算出的(X-min)/(max-min)，将新的X值带入

max_abs_scaler = preprocessing.MaxAbsScaler()
X_train_maxabs = max_abs_scaler.fit_transform(X_train) # 归一化[-1,1]，负数使用绝对值
X_test_maxabs = max_abs_scaler.transform(X_test)       # 用前面计算出的(X-min)/(max-min)，将新的X值带入

# 规模化稀疏数据
如果对稀疏数据进行去均值的中心化就会破坏稀疏的数据结构
MaxAbsScaler 和 maxabs_scale这两个方法是专门为稀疏数据的规模化所设计的

# 规模化有异常值的数据
数据有许多异常值，使用数据的均值与方差去做标准化就不行。
使用 robust_scale 和 RobustScaler 它会根据中位数或者四分位数去中心化数据

# 二值化
binarizer = preprocessing.Binarizer(threshold=1.5)  # 大于1.5的都标记为1，小于等于1.5的都标记为0
data = binarizer.transform(x)

# 独热编码
enc = preprocessing.OneHotEncoder(n_values=[2,3,4]) # 指定每个特征取值种类数量
enc.fit([[1, 2, 3], [0, 2, 0]])
enc.transform([[1,0,0]]).toarray()

# 标签化
label = preprocessing.LabelEncoder()
label.fit_transform(dataset['Sex']) # 标签化
inverse_transform([0,0,1,0,1,1])    # 反标签
```


```python
#Common Model Algorithms
from sklearn import svm, tree, linear_model, neighbors, naive_bayes, ensemble, discriminant_analysis, gaussian_process
from xgboost import XGBClassifier
MLA = [
    #Ensemble Methods
    ensemble.AdaBoostClassifier(),
    ensemble.BaggingClassifier(),
    ensemble.ExtraTreesClassifier(),
    ensemble.GradientBoostingClassifier(),
    ensemble.RandomForestClassifier(),

    #Gaussian Processes
    gaussian_process.GaussianProcessClassifier(),
    
    #GLM
    linear_model.LogisticRegressionCV(),
    linear_model.PassiveAggressiveClassifier(),
    linear_model.RidgeClassifierCV(),
    linear_model.SGDClassifier(),
    linear_model.Perceptron(),
    
    #Navies Bayes
    naive_bayes.BernoulliNB(),
    naive_bayes.GaussianNB(),
    
    #Nearest Neighbor
    neighbors.KNeighborsClassifier(),
    
    #SVM
    svm.SVC(probability=True),
    svm.NuSVC(probability=True),
    svm.LinearSVC(),
    
    #Trees    
    tree.DecisionTreeClassifier(),
    tree.ExtraTreeClassifier(),
    
    #Discriminant Analysis
    discriminant_analysis.LinearDiscriminantAnalysis(),
    discriminant_analysis.QuadraticDiscriminantAnalysis(),
    
    #xgboost: http://xgboost.readthedocs.io/en/latest/model.html
    XGBClassifier()    
    ]

#split dataset in cross-validation with this splitter class: http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.ShuffleSplit.html#sklearn.model_selection.ShuffleSplit
#note: this is an alternative to train_test_split
cv_split = model_selection.ShuffleSplit(n_splits = 10, test_size = .3, train_size = .6, random_state = 0 )# run model 10x with 60/30 split intentionally leaving out 10%

#create table to compare MLA metrics
MLA_columns = ['MLA Name', 'MLA Parameters','MLA Train Accuracy Mean', 'MLA Test Accuracy Mean', 'MLA Test Accuracy 3*STD' ,'MLA Time']
MLA_compare = pd.DataFrame(columns = MLA_columns)

#create table to compare MLA predictions
MLA_predict = train[Target]

#index through MLA and save performance to table
row_index = 0
for alg in MLA:
    #set name and parameters
    MLA_name = alg.__class__.__name__
    MLA_compare.loc[row_index, 'MLA Name'] = MLA_name
    MLA_compare.loc[row_index, 'MLA Parameters'] = str(alg.get_params())
    
    #score model with cross validation: http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.cross_validate.html#sklearn.model_selection.cross_validate
    cv_results = model_selection.cross_validate(alg, train, train[Target], cv  = cv_split)

    MLA_compare.loc[row_index, 'MLA Time'] = cv_results['fit_time'].mean()
    MLA_compare.loc[row_index, 'MLA Train Accuracy Mean'] = cv_results['train_score'].mean()
    MLA_compare.loc[row_index, 'MLA Test Accuracy Mean'] = cv_results['test_score'].mean()   
    #if this is a non-bias random sample, then +/-3 standard deviations (std) from the mean, should statistically capture 99.7% of the subsets
    MLA_compare.loc[row_index, 'MLA Test Accuracy 3*STD'] = cv_results['test_score'].std()*3   #let's know the worst that can happen!
    

    #save MLA predictions - see section 6 for usage
    alg.fit(train, train[Target])
    MLA_predict[MLA_name] = alg.predict(train)
    
    row_index+=1

    
#print and sort table: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.sort_values.html
MLA_compare.sort_values(by = ['MLA Test Accuracy Mean'], ascending = False, inplace = True)
print(MLA_compare)
#MLA_predict
```


# reference

《python数据分析与挖掘实战》

