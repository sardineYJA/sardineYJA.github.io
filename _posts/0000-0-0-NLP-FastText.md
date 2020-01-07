---
layout: post
title: "Facebook文本分类工具fastText"
date: 2018-10-18
description: "简单介绍一下fastText工具，训练速度极快"
tag: Machine Learn

---

# 简介

fastText是Facebook在2016年开源的一个工具，主要功能有两个：

1. 训练词向量

2. 文本分类

fastText使用了自然语言处理和机器学习中最成功的理念，包括了`词袋（bow）`已经`n-gram` 表征语句，还有使用`subword`信息。

fastText的一个作者是Thomas Mikolov。也正是这个人在谷歌的时候，带领团队在2012年提出了`word2vec`代替了`one-hot`编码，将词表示为一个低维连续嵌入，极大促进了NLP的发展。14年她去了脸书，然后提出了word2vec的改进版:fasttext。所以fastText和word2vec在结构上很相似。

fastText是一个能用浅层网络取得和深度网络相媲美的精度（还是比深层网络差点），但是分类速度极快的算法（10万数据分几类，训练时间不到1秒）。按照作者的说法“在标准的多核CPU上，能够训练10亿词级别语料库的词向量在10分钟之内，能够分类有着30万多类别的50多万句子在1分钟之内”。但是它也有自己的使用条件，它适合类别特别多的分类问题，如果类别比较少，容易过拟合。

#  模型架构

词向量的训练，相比word2vec来说，增加了`subword`特征。word2vec仅使用词信息，但是这样使得词之间共享的信息很少，这个问题对低频词来说更严重，如果出现`OOV`(out of vocabulary)问题，新词不能利用词库中词的信息。所以fastText增加了`subword`信息，将词做进一步拆分。同一个语料对subword的覆盖率很定是高于词的覆盖率的
> 比如：中文里，字的数量是远远低于词的数量的，同一个中文语料对字的覆盖肯定超过对词的覆盖

这时候，即便出现OOV，也能共享高频词的subword信息。
在 fasttext 中，引入了两类特征：
- n-gram

示例：who am I? n-gram设置为2，n-gram特征有，`who, who am, am, am I, I`
- n-char

每个词被看做是 n-gram字母串包。为了区分前后缀情况，"<"， ">"符号被加到了词的前后端。除了词的子串外，词本身也被包含进了 n-gram字母串包。以 where 为例，n=3 的情况下，其子串分别为 `<wh, whe, her, ere, re>，where` 。

网络结构和word2vec类似，都是一个浅层网络，与word2vec不同点在于：

- word2vec的输入只有当前词的上下文2d个词，而fastText是当前句子或者当前文本的全部词的序列
- word2vec是预测当前词的概率，fastText是预测当前文本label的概率
- fastText在预测为标签的时候使用非线性激活函数，但是在中间层没有使用非线性机会函数

同样，fastText也使用了`Hierarchical Softmax`来加速最后一层softmax的计算。



# 调用fasttext库


Linux安装：pip install fasttext

Windows安装：pip install fasttext 会报错

> Microsoft Visual C++ 14.0 is required. Get it with "Microsoft Visual C++ Build Tools

解决方案：
1. 安装VS2017     
2. https://www.lfd.uci.edu/~gohlke/pythonlibs/下载xxx.whl包使用pip install xxx.whl

数据格式：
```
颜值 担当      __label__1
快递 速度      __label__2
```

```python
# Windows 版
import fastText.FastText as ff
classfier = ff.train_supervised("train.txt")
classfier.save_model('model')

classifier = ff.load_model('model')
result = classifier.test('test.txt')
print('准确率：', result)
# 准确率： (33417, 0.9593919262650746, 0.9593919262650746)
str_list = ['我 要 一款 内存 大 运行 快 的 苹果 电脑']
lab = classifier.predict(str_list, k=1)
print(lab)  # (['__label__2'], array([0.95485353]))
```

```python
import fasttext as ft
ft.supervised('train', 'model', label_prefix='__label__')  # 保存模型后缀自动加'.bin'

c = ft.load_model('model.bin',label_prefix='__label__')
result = c.test('test.txt')
print(result.precision)
print(result.recall)
print(result.nexamples)
lab = c.predict_proba(str_list, k=1)
print(lab)  # [[('2', 0.976563)]]
```



# 使用fasttext命令模式

训练数据格式:

1.如果是训练词向量，怎么文本分词以空格隔开就行

2.如果是预测文本，格式如上



下载：https://github.com/facebookresearch/fastText/

解压，进入目录

命令：make 进行安装


## 词向量

获取词向量：./fasttext skipgram -input data.txt -output model

参数：skipgram  或者  cbow 

data.txt 存储分词，词与词之间空格隔开（即一行），分行的话会有<\s>的词向量产生

生成model.bin和model.vec(model为自定义命名)

model.vec文件：第一句保存词向量个数（默认词出现次数大于等于5 才有词向量），与维度（默认100维）

常用参数：-minCount 5最小出现次数 -dim词向量维度

最后有无标签：__label__ 生成的词向量一样的


训练出来的模型model.bin可以用来计算词典之外的单词的向量表示，直接打印出来

命令：./fasttext print-word-vectors model.bin < queries.txt


## 文本分类

文本分类：./fasttext supervised -input train.txt -output model

每行最后加上__label__1或者label__sport之类的，生成model.bin和model.vec文件

预测最可能的标签：./fastttext predict model.bin my_test.txt

也可打印前k=2个最可能的标签：./fasttext predict-prob model.bin my_test.txt 2


## github地址

[文本分类方法汇总](https://github.com/brightmart/text_classification)

[fasttext的python接口地址](https://github.com/salestock/fastText.py)

[faxtText官方github地址](https://github.com/salestock/fastText.py)

# 参考

http://albertxiebnu.github.io/fasttext/

https://blog.csdn.net/qq_32023541/article/details/80839800