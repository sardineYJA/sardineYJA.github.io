---
layout: post
title: "python数据分析篇5"
date: 2019-01-13
description: "简单介绍一下python数据分析"
tag: python

---

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from sklearn.preprocessing import LabelEncoder,OneHotEncoder
from sklearn.preprocessing import Normalizer
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
```

# 数据预处理


```python
# sl:  satisfaction_level-----False:MinMaxScaler;True:StandardScaler
# le:  last_evaluation--------False:MinMaxScaler;True:StandardScaler
# npr: number_project---------False:MinMaxScaler;True:StandardScaler
# amh: average_monthly_hours--False:MinMaxScaler;True:StandardScaler
# tsc: time_spend_company-----False:MinMaxScaler;True:StandardScaler
# wa:  Work_accident----------False:MinMaxScaler;True:StandardScaler
# pl5: promotion_last_5years--False:MinMaxScaler;True:StandardScaler
# dp:  department-------------False:LabelEncoding;True:OneHotEncoding
# slr:  salary----------------False:LabelEncoding;True:OneHotEncoding
def hr_preprocessing(sl=False,le=False,npr=False,amh=False,tsc=False,wa=False,pl5=False,dp=False,slr=False,lower_d=False,ld_n=1):
    df=pd.read_csv("data\\HR.csv")
    #1、清洗数据
    df=df.dropna(subset=["satisfaction_level","last_evaluation"])
    df=df[df["satisfaction_level"]<=1][df["salary"]!="nme"]
    #2、得到标注
    label = df["left"]
    df = df.drop("left", axis=1)
    #3、特征选择（暂时保留所有特征）
    #4、特征处理
    scaler_lst=[sl,le,npr,amh,tsc,wa,pl5]
    column_lst=["satisfaction_level","last_evaluation","number_project",\
                "average_monthly_hours","time_spend_company","Work_accident",\
                "promotion_last_5years"]
    
    # 对数值属性进行 LabelEncoding 或者 OneHotEncoding处理
    for i in range(len(scaler_lst)):
        if not scaler_lst[i]:
            df[column_lst[i]]=\
                MinMaxScaler().fit_transform(df[column_lst[i]].values.reshape(-1,1)).reshape(1,-1)[0]
        else:
            df[column_lst[i]]=\
                StandardScaler().fit_transform(df[column_lst[i]].values.reshape(-1,1)).reshape(1,-1)[0]
                
    # 对属性salary和department进行 inMaxScaler 或者 StandardScaler 处理
    scaler_lst=[slr,dp]
    column_lst=["salary","department"]
    for i in range(len(scaler_lst)):
        if not scaler_lst[i]:
            if column_lst[i]=="salary":
                df[column_lst[i]]=[map_salary(s) for s in df["salary"].values]
            else:
                df[column_lst[i]]=LabelEncoder().fit_transform(df[column_lst[i]])
            df[column_lst[i]]=MinMaxScaler().fit_transform(df[column_lst[i]].values.reshape(-1,1)).reshape(1,-1)[0]
        else:
            df=pd.get_dummies(df,columns=[column_lst[i]])
    if lower_d:
        return PCA(n_components=ld_n).fit_transform(df.values),label
    return df,label

# salary的low,medium,high 映射成0,1,2
d=dict([("low",0),("medium",1),("high",2)])
def map_salary(s):
    return d.get(s,0)

features,label=hr_preprocessing()
print(features)
```

# 划分训练集和测试集


```python
from sklearn.model_selection import train_test_split
f_v = features.values
l_v = label.values
f_names = features.columns.values
print(f_names)

X_tt,X_validation,Y_tt,Y_validation = train_test_split(f_v,l_v,test_size=0.2)
print('验证集数据量：',len(X_validation))

X_train,X_test,Y_train,Y_test = train_test_split(X_tt,Y_tt,test_size=0.25)
print('训练集数据量：',len(X_train))
print('测试集数据量：',len(X_test))
```

# KNN分类预测


```python
from sklearn.neighbors import KNeighborsClassifier
knn_clf = KNeighborsClassifier(n_neighbors=3)
knn_clf.fit(X_train, Y_train)
Y_pred = knn_clf.predict(X_validation)  # 模型预测验证集

# 预测的验证集与真实验证集相比较
from sklearn.metrics import accuracy_score, recall_score, f1_score
print('ACC : ',accuracy_score(Y_validation, Y_pred)) 
print('REC : ',recall_score(Y_validation, Y_pred))    # recall is the ratio tp / (tp + fn)
print('F1 Score : ',f1_score(Y_validation, Y_pred))   # F1 = 2 * (precision * recall) / (precision + recall)

# 保存模型，加载模型
from sklearn.externals import joblib 
# joblib.dump(knn_clf, 'knn_clf')   # 保存模型
# knn_clf = joblib.load('knn_clf')  # 加载模型
```

# 其他分类


```python
from sklearn.metrics import accuracy_score, recall_score, f1_score      # 测试预测分类效果
from sklearn.neighbors import NearestNeighbors,KNeighborsClassifier     # KNN分类
from sklearn.naive_bayes import GaussianNB,BernoulliNB                  # 高斯贝叶斯，伯努利贝叶斯
from sklearn.tree import DecisionTreeClassifier,export_graphviz         # 决策树
from sklearn.externals.six import StringIO 
from sklearn.svm import SVC                                             # 支持向量机
from sklearn.ensemble import RandomForestClassifier                     # 随机森林
from sklearn.ensemble import AdaBoostClassifier                         # boost提升
from sklearn.linear_model import LogisticRegression                     # 逻辑回归
from sklearn.ensemble import GradientBoostingClassifier                 # 梯度提升决策树

import os
import pydotplus
os.environ["PATH"]+=os.pathsep+"F:/Graphviz/bin/"                # 添加路径

models=[]
models.append(("KNN",KNeighborsClassifier(n_neighbors=3)))
models.append(("GaussianNB",GaussianNB()))
models.append(("BernoulliNB",BernoulliNB()))
models.append(("DecisionTreeGini",DecisionTreeClassifier()))
models.append(("DecisionTreeEntropy",DecisionTreeClassifier(criterion="entropy")))
models.append(("SVM Classifier",SVC(C=1000)))
models.append(("OriginalRandomForest",RandomForestClassifier()))
models.append(("RandomForest",RandomForestClassifier(n_estimators=11,max_features=None)))
models.append(("Adaboost",AdaBoostClassifier(n_estimators=100)))
models.append(("LogisticRegression",LogisticRegression(C=1000,tol=1e-10,solver="sag",max_iter=10000)))
models.append(("GBDT",GradientBoostingClassifier(max_depth=6,n_estimators=100)))
for clf_name,clf in models:
    clf.fit(X_train,Y_train)
    xy_lst=[(X_train,Y_train),(X_validation,Y_validation),(X_test,Y_test)]
    for i in range(len(xy_lst)):
        X_part=xy_lst[i][0]
        Y_part=xy_lst[i][1]
        Y_pred=clf.predict(X_part)
        print(i)
        print(clf_name,"-ACC:",accuracy_score(Y_part,Y_pred))
        print(clf_name,"-REC:",recall_score(Y_part,Y_pred))
        print(clf_name,"-F1:",f1_score(Y_part,Y_pred))
        
#         # 决策树生成PDF可视化
#         dot_data=StringIO()
#         export_graphviz(clf,out_file=dot_data,
#                                  feature_names=f_names,
#                                  class_names=["NL","L"],
#                                  filled=True,
#                                  rounded=True,
#                                  special_characters=True)
#         graph=pydotplus.graph_from_dot_data(dot_data.getvalue())
#         graph.write_pdf("dt_tree.pdf")
```

# 回归


```python
def regr_test(features,label):
    print("X",features)
    print("Y",label)
    from sklearn.linear_model import LinearRegression,Ridge,Lasso
    regr = LinearRegression()     # 线性回归
    #regr = Ridge(alpha=1)        # 岭回归
    #regr = Lasso(alpha=0.1)      # lasso回归
    regr.fit(features.values,label.values )
    Y_pred=regr.predict(features.values)
    print("Coef:",regr.coef_)     # 拟合函数的参数
    from sklearn.metrics import mean_squared_error,mean_absolute_error,r2_score
    print("MSE:",mean_squared_error(label.values,Y_pred))   # 均方误差
    print("MAE:",mean_absolute_error(label.values,Y_pred))  
    print("R2:",r2_score(label.values,Y_pred))

regr_test(features[["number_project","average_monthly_hours"]],features["last_evaluation"])
```

# 神经网络


```python
%matplotlib inline
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.optimizers import SGD  # 随机梯度下降算法

mdl = Sequential()
mdl.add(Dense(50, input_dim=len(f_v[0])))
mdl.add(Activation("sigmoid"))   # 激活函数

mdl.add(Dense(2))
mdl.add(Activation("softmax"))

sgd = SGD(lr=0.1)    # 学习率0.1
mdl.compile(loss="mean_squared_error", optimizer="adam")
# Y_train 必须为one-hot形式
mdl.fit(X_train, np.array([[0, 1] if i == 1 else [1, 0] for i in Y_train]), nb_epoch=5, batch_size=8999)
xy_lst = [(X_train, Y_train), (X_validation, Y_validation), (X_test, Y_test)]
```


```python
from sklearn.metrics import accuracy_score, recall_score, f1_score      # 测试预测分类效果
for i in range(len(xy_lst)):
    X_part = xy_lst[i][0]
    Y_part = xy_lst[i][1]
    Y_pred = mdl.predict_classes(X_part)
    print(i)
    print("NN", "-ACC:", accuracy_score(Y_part, Y_pred))
    print("NN", "-REC:", recall_score(Y_part, Y_pred))
    print("NN", "-F1:", f1_score(Y_part, Y_pred))
```


```python
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, roc_auc_score
f = plt.figure()
for i in range(len(xy_lst)):
    X_part = xy_lst[i][0]
    Y_part = xy_lst[i][1]
    Y_pred = mdl.predict(X_part)
    print(Y_pred)
    Y_pred = np.array(Y_pred[:, 1]).reshape((1, -1))[0]
    f.add_subplot(1, 3, i + 1)
    fpr, tpr, threshold = roc_curve(Y_part, Y_pred)
    plt.plot(fpr, tpr)
    print("NN", "AUC", auc(fpr, tpr))
    print("NN", "AUC_Score", roc_auc_score(Y_part, Y_pred))
plt.show()
```

# 聚类


```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_circles,make_blobs,make_moons
from sklearn.cluster import KMeans,DBSCAN,AgglomerativeClustering
n_samples=1000
circles=make_circles(n_samples=n_samples,factor=0.5,noise=0.05)
moons=make_moons(n_samples=n_samples,noise=0.05)
blobs=make_blobs(n_samples=n_samples,random_state=8,center_box=(-1,1),cluster_std=0.1)
random_data=np.random.rand(n_samples,2),None

colors="bgrcmyk"
data=[circles,moons,blobs,random_data]
models=[("None",None),("Kmeans",KMeans(n_clusters=3)),
        ("DBSCAN",DBSCAN(min_samples=3,eps=0.2)),
        ("Agglomerative",AgglomerativeClustering(n_clusters=3,linkage="ward"))] # 层次聚类

from sklearn.metrics import silhouette_score
f=plt.figure(figsize=(18,16))
for inx,clt in enumerate(models):
    clt_name,clt_entity=clt
    for i,dataset in enumerate(data):
        X,Y=dataset
        if not clt_entity:
            clt_res=[0 for item in range(len(X))]
        else:
            clt_entity.fit(X)
            clt_res=clt_entity.labels_.astype(np.int)
        f.add_subplot(len(models),len(data),inx*len(data)+i+1)
        plt.title(clt_name)
        try:
            print(clt_name,i,silhouette_score(X,clt_res))   # 轮廓系数
        except:
            pass
        [plt.scatter(X[p,0],X[p,1],color=colors[clt_res[p]]) for p in range(len(X))]
plt.show()
```

# 关联


```python
from itertools import combinations

# 获取所有的项集组合
def comb(lst):
    ret=[]
    for i in range(1,len(lst)+1):
        ret+=list(combinations(lst,i))
    return ret
class AprLayer(object):
    d=dict()
    def __init__(self):
        self.d=dict()
class AprNode(object):
    def __init__(self,node):
        self.s=set(node)
        self.size=len(self.s)
        self.lnk_nodes=dict()
        self.num=0
    def __hash__(self):
        return hash("__".join(sorted([str(itm) for itm in list(self.s)])))
    def __eq__(self, other):
        if "__".join(sorted([str(itm) for itm in list(self.s)]))=="__".join(sorted([str(itm) for itm in list(other.s)])):
            return True
        return False
    def isSubnode(self,node):
        return self.s.issubset(node.s)
    def incNum(self,num=1):
        self.num+=num
    def addLnk(self,node):
        self.lnk_nodes[node]=node.s

class AprBlk():
    def __init__(self,data):
        cnt=0
        self.apr_layers = dict()
        self.data_num=len(data)
        for datum in data:
            cnt+=1
            datum=comb(datum)
            nodes=[AprNode(da) for da in datum]
            for node in nodes:
                if not node.size in self.apr_layers:
                    self.apr_layers[node.size]=AprLayer()
                if not node in self.apr_layers[node.size].d:
                    self.apr_layers[node.size].d[node]=node
                self.apr_layers[node.size].d[node].incNum()
            for node in nodes:
                if node.size==1:
                    continue
                for sn in node.s:
                    sub_n=AprNode(node.s-set([sn]))
                    self.apr_layers[node.size-1].d[sub_n].addLnk(node)

    def getFreqItems(self,thd=1,hd=1):
        freq_items=[]
        for layer in self.apr_layers:
            for node in self.apr_layers[layer].d:
                if self.apr_layers[layer].d[node].num<thd:
                    continue
                freq_items.append((self.apr_layers[layer].d[node].s,self.apr_layers[layer].d[node].num))
        freq_items.sort(key=lambda x:x[1],reverse = True)
        return freq_items[:hd]

    def getConf(self,low=True, h_thd=10, l_thd=1, hd=1):
        confidence = []
        for layer in self.apr_layers:
            for node in self.apr_layers[layer].d:
                if self.apr_layers[layer].d[node].num < h_thd:
                    continue
                for lnk_node in node.lnk_nodes:
                    if lnk_node.num < l_thd:
                        continue
                    conf = float(lnk_node.num) / float(node.num)
                    confidence.append([node.s, node.num, lnk_node.s, lnk_node.num, conf])

        confidence.sort(key=lambda x: x[4])
        if low:
            return confidence[:hd]
        else:
            return confidence[-hd::-1]

class AssctAnaClass():
    def fit(self,data):
        self.apr_blk=AprBlk(data)
        return self
    
    # 获取频繁项集
    def get_freq(self,thd=1,hd=1):
        return self.apr_blk.getFreqItems(thd=thd,hd=hd)
    
    # 获取高置信度的组合
    def get_conf_high(self,thd,h_thd=10):
        return self.apr_blk.getConf(low=False, h_thd=h_thd, l_thd=thd)
    
    # 获取低置信度的组合
    def get_conf_low(self,thd,hd,l_thd=1):
        return self.apr_blk.getConf(h_thd=thd,l_thd=l_thd,hd=hd)


def main():
    data=[
        ["牛奶","啤酒","尿布"],
        ["牛奶","啤酒","咖啡","尿布"],
        ["香肠","牛奶","饼干"],
        ["尿布","果汁","啤酒"],
        ["钉子","啤酒"],
        ["尿布","毛巾","香肠"],
        ["啤酒","毛巾","尿布","饼干"]
    ]
    print("Freq",AssctAnaClass().fit(data).get_freq(thd=3,hd=10))
    print("Conf",AssctAnaClass().fit(data).get_conf_high(thd=3,h_thd=3))
if __name__=="__main__":
    main()
```

# 半监督


```python
import numpy as np
from sklearn import datasets

iris = datasets.load_iris()
labels = np.copy(iris.target)
print(labels)
random_unlabeled_points = np.random.rand(len(iris.target))
print(random_unlabeled_points)
random_unlabeled_points = random_unlabeled_points < 0.7 # 将其转化为 0，1 的数
print(random_unlabeled_points)

Y = labels[random_unlabeled_points]
labels[random_unlabeled_points]=-1   # 未分类的标注为 -1
print("Unlabeled Number:",list(labels).count(-1))
print(labels)

from sklearn.semi_supervised import LabelPropagation
label_prop_model = LabelPropagation()
label_prop_model.fit(iris.data,labels)
Y_pred = label_prop_model.predict(iris.data)
Y_pred = Y_pred[random_unlabeled_points]
from sklearn.metrics import accuracy_score,recall_score,f1_score
print("ACC:",accuracy_score(Y,Y_pred))
print("REC:",recall_score(Y,Y_pred,average="micro"))
print("F-Score",f1_score(Y,Y_pred,average="micro"))
```
