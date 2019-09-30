---
layout: post
title: "词向量Word2Vec介绍"
date: 2018-10-03
description: "简单介绍一下word2vec"
tag: NLP

---

## gensim的word2vec参数使用


```python
1. sentences: 我们要分析的语料，可以是一个列表，或者从文件中遍历读出
    
2. size: 词向量的维度，默认值是100。这个维度的取值一般与我们的语料的大小相关，如果是不大的语料，
         比如小于100M的文本语料，则使用默认值一般就可以了。如果是超大的语料，建议增大维度。

3. window：即词向量上下文最大距离，这个参数在我们的算法原理篇中标记为，window越大，则和某一词较远的词也会产生上下文关系。
           默认值为5。在实际使用中，可以根据实际的需求来动态调整这个window的大小。如果是小语料则这个值可以设的更小。
           对于一般的语料这个值推荐在[5,10]之间。

4. sg: 即我们的word2vec两个模型的选择了。如果是0， 则是CBOW模型，是1则是Skip-Gram模型，默认是0即CBOW模型。

5. hs: 即我们的word2vec两个解法的选择了，如果是0， 则是Negative Sampling，
       是1的话并且负采样个数negative大于0， 则是Hierarchical Softmax。默认是0即Negative Sampling。

6. negative:即使用Negative Sampling时负采样的个数，默认是5。推荐在[3,10]之间。这个参数在我们的算法原理篇中标记为neg。

7. cbow_mean: 仅用于CBOW在做投影的时候，为0，则算法中的为上下文的词向量之和，为1则为上下文的词向量的平均值。
              在我们的原理篇中，是按照词向量的平均值来描述的。个人比较喜欢用平均值来表示,默认值也是1,不推荐修改默认值。

8. min_count: 需要计算词向量的最小词频。这个值可以去掉一些很生僻的低频词，默认是5。如果是小语料，可以调低这个值。

9. iter: 随机梯度下降法中迭代的最大次数，默认是5。对于大语料，可以增大这个值。

10. alpha: 在随机梯度下降法中迭代的初始步长。算法原理篇中标记为，默认是0.025。

11. min_alpha: 由于算法支持在迭代的过程中逐渐减小步长，min_alpha给出了最小的迭代步长值。
    随机梯度下降中每轮的迭代步长可以由iter，alpha， min_alpha一起得出。
    这部分由于不是word2vec算法的核心内容，因此在原理篇我们没有提到。
    对于大语料，需要对alpha, min_alpha,iter一起调参，来选择合适的三个值。
```


```python
from gensim.models import word2vec
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

raw_sentences = ['the quick 狗 猫 brown fox jumps over the lazy dogs', 'yoyoyo you go home now to sleep']
sentences = [s.split() for s in raw_sentences]
print(sentences)
```


```python
model = word2vec.Word2Vec(sentences, min_count=1)  
# 建模，min_count词的最小频率，太小则去掉；size 参数设置神经网络的层数，默认100

print(model.similarity('dogs', 'you'))  # 两个词必须都在模型有的
print(model.similarity('dogs', '狗'))
print(model.similarity('猫', '狗'))
print(model.most_similar('dogs'))
print(model.most_similar('dogs', topn=2))
```


```python
model.save("test.model")             #  保存模型
from gensim.models import Word2Vec   #  加载模型，此时导入Word2Vec，之前是word2vec
m = Word2Vec.load('test.model')
print(m)
print(model.most_similar('dogs'))
```

## 构造word2vec


```python
import tensorflow as tf
import numpy as np
import math
import collections     # 计算词频
import pickle as pkl   # 保存，读取模型
import re
import jieba
import os
import os.path as path

from pprint import pprint
```


```python
word_count = collections.Counter(raw_word_list)   # 统计每个词的数量
word_count = word_count.most_common(30000)        # 返回top30000
word_list = [x[0] for x in word_count]

print(len(word_count))
print(len(word_list))
print(word_count[0:20])        # 词汇数目最多的前20个词，返回的是元组列表
print(sentence_list[0:20])     # 前20行，每行的词列表
print(word_list[0:30])         # 所有词的列表
```


```python
class word2vec():
    def __init__(self,
                 vocab_list = None,    # 所有词的列表
                 embedding_size = 200, # 每个单词200维
                 win_len = 3,          # 上下文窗口大小，N-gram
                 learning_rate = 1,    # 学习率
                 logdir = '/tmp',     
                 model_path = None,
                 num_sampled = 100):   # 负采样个数，这个做的是negative simpling
        
        self.batch_size = None
        
        if model_path != None:
            self.load_model(model_path)
        else:
            assert type(vocab_list) == list  # 判断是否为列表，否则抛出异常
            self.vocab_list = vocab_list
            self.vocab_size = len(vocab_list)
            self.win_len = win_len
            self.num_sampled = num_sampled
            self.learning_rate = learning_rate
            self.embedding_size = embedding_size
            self.logdir = logdir
        
            self.word2id = {}
            for i in range(self.vocab_size):          # 用数字0,1,2...映射每一个词
                self.word2id[self.vocab_list[i]] = i  # 用字典进行id映射

            self.train_words_num = 0       # 训练的词数
            self.train_sents_num = 0       # 训练的句子
            self.train_times_num = 0       # 训练的次数
            
            # train loss records 保存最近10次误差
            self.train_loss_records = collections.deque(maxlen=10)
            self.train_loss_k10 = 0
        
        self.build_graph()
        self.init_op()
        if model_path != None:
            tf_model_path = os.path.join(model_path, 'tf_vars')
            self.saver.restore(self.sess, tf_model_path)
    
    def init_op(self):
        self.sess = tf.Session(graph= self.graph)
        self.sess.run(self.init)
        #self.summary_writer = tf.train.SummaryWriter(self.logdir, self.sess.graph)
        self.summary_writer = tf.summary.FileWriter(self.logdir, self.sess.graph)    # Tensorboard 保存
        
        
    def build_graph(self):             # 构建TensorFlow的图
        self.graph = tf.Graph()
        with self.graph.as_default():
            self.train_inputs = tf.placeholder(tf.int32, shape=[self.batch_size])    # 训练数据 id 的输入
            self.train_labels = tf.placeholder(tf.int32, shape=[self.batch_size, 1]) # 训练数据的标签，就是它上下文
            
            # 有 vocab_size 个单词，每个单词 embedding_size 维度  : n * 200 
            # tf.truncated_normal() 从截断的正态分布输出随机值
            #self.embedding_dict = tf.Variable(tf.truncated_normal(shape=[self.vocab_size, self.embedding_size]))
            #self.nec_weight = tf.Variable(tf.truncated_normal(shape=[self.vocab_size, self.embedding_size]))
            #self.bias = tf.Variable(tf.zeros([self.vocab_size]))   # 偏差
            # embedding_dict ，nec_weight 是 n*200 矩阵
            # bias 是 1*n 矩阵
            
            self.embedding_dict = tf.Variable(tf.random_uniform([self.vocab_size, self.embedding_size], -1.0,1.0))  # 最小-1，最大1
            self.nce_weight = tf.Variable(tf.truncated_normal([self.vocab_size, self.embedding_size],
                                                               stddev=1.0/math.sqrt(self.embedding_size))) # stddev 标准差
            self.nce_biases = tf.Variable(tf.zeros([self.vocab_size]))
            
            # 常用于NLP中将one-hot编码转换对应的向量编码
            # 就是根据input_ids中的id，寻找embeddings中的第id行
            embed = tf.nn.embedding_lookup(self.embedding_dict, self.train_inputs)
            # embed 即相当于[1.21, 1.43, ......] 1*200 的一个列表
            
            # 定义损失函数
            self.loss = tf.reduce_mean(   # 计算张量维度的元素平均值
                tf.nn.nce_loss(           # 计算并返回噪声对比估计训练损失
                               weights = self.nce_weight,     # n*200
                               biases = self.nce_biases,      # 1*n
                               inputs = embed,                # 1*200
                               labels = self.train_labels,
                               num_sampled = self.num_sampled,    # 负采样个数
                               num_classes = self.vocab_size      # 一共有几个词（即几个类）
                              ))
                                          
            # 训练操作
            self.train_op = tf.train.GradientDescentOptimizer(learning_rate=0.1).minimize(self.loss)
        
            # 测试相似度
            self.test_word_id = tf.placeholder(tf.int32, shape = [None])   
            vec_l2_model = tf.sqrt(tf.reduce_sum(tf.square(self.embedding_dict), 1, keep_dims=True))
            avg_l2_model = tf.reduce_mean(vec_l2_model)
            
            # 输出Summary包含单个标量值的协议缓冲区,用来显示标量信息
            tf.summary.scalar('avg_vec_model', avg_l2_model) # name, tensor
            
            self.normed_embedding = self.embedding_dict / vec_l2_model                  # 向量除于模，归一化
            test_embed = tf.nn.embedding_lookup(self.embedding_dict, self.test_word_id)
            
            # 两个相同行列不能相乘
            self.similarity = tf.matmul(test_embed, self.normed_embedding, transpose_b=True)              # 矩阵相乘
        
            self.init = tf.global_variables_initializer()         # 全局变量初始化
            
            tf.merge_all_summaries = tf.summary.merge_all
            self.merged_summary_op = tf.merge_all_summaries()
            
            self.saver = tf.train.Saver()                         # 模型的保存
            
                                          
                                          
    def train_by_sentence(self, input_sentence = []): 
        sent_num = len(input_sentence)  # 句子的数量
        batch_inputs = []               #
        batch_labels = []               # 
        for sent in input_sentence:
            for i in range(len(sent)):                 # i 代表每个句子
                start = max(0, i-self.win_len)         # 从句子往左
                end = min(len(sent), i+self.win_len+1)   # 从句子往右，以 i 为中心 
                
                for index in range(start, end):        # 上下文区间的索引
                    if index == i:
                        continue
                    else:
                        input_id = self.word2id.get(sent[i])     # 当前值
                        label_id = self.word2id.get(sent[index]) # 上下文
                        
                        if not (input_id and label_id):
                            continue
                        
                        batch_inputs.append(input_id)    # [1,1,2,2,2................]
                        batch_labels.append(label_id)    # [2,3,1,3,4................]
        
        if len(batch_inputs) == 0:
            return 
        
        
        if self.train_sents_num % 100 == 0:
            print('训练句子数：',self.train_sents_num)
            print('batch_inputs个数：',len(batch_inputs))
            print(batch_inputs[:20])
            print('batch_labels个数：',len(batch_labels))
            print(batch_labels[:20])
            print('这个训练中有',sent_num,'个句子')
        
        # reshape
        batch_inputs = np.array(batch_inputs, dtype=np.int32)
        batch_labels = np.array(batch_labels, dtype=np.int32)
        batch_labels = np.reshape(batch_labels, [len(batch_labels), 1])  # 变成n行，1列
        
        feed_dict = {
            self.train_inputs : batch_inputs,
            self.train_labels : batch_labels}
        _, loss_val, summary_str = self.sess.run([self.train_op, self.loss, self.merged_summary_op], feed_dict=feed_dict)
        
        
        self.train_loss_records.append(loss_val)
        self.train_loss_k10 = np.mean(self.train_loss_records)
        if self.train_sents_num % 100 == 0:
            self.summary_writer.add_summary(summary_str, self.train_sents_num)
            print('{a} sentences dealed, loss:{b}'.format(a=self.train_sents_num, b=self.train_loss_k10))
        
        self.train_words_num += len(batch_inputs)
        self.train_sents_num += len(input_sentence)
        self.train_times_num += 1
    
                                          
                                          
    def save_model(self, save_path):
        if os.path.isfile(save_path):
            raise RuntimeError('the save path should be a dir')
        if not os.path.exists(save_path):
            os.mkdir(save_path)
            
        # 记录模型各参数
        model = {}
        var_names = ['vocab_size',       # int
                     'vocab_list',       # list
                     'learning_rate',    # int
                     'word2id',          # dict
                     'embedding_size',   # int
                     'logdir',           # str
                     'win_len',          # int
                     'num_sampled',      # int
                     'train_words_num',  # int
                     'train_sents_num',  # int
                     'train_times_num',  # int
                     'train_loss_records',# int
                     'train_loss_k10',    # int 
                    ]
        for var in var_names:
            model[var] = eval('self.'+var)
        
        param_path = os.path.join(save_path, 'params.pkl')
        if os.path.exists(param_path):
            os.remove(param_path)
        with open(param_path, 'wb') as f:
            pkl.dump(model, f)
        
        # 记录tf模型
        tf_path = os.path.join(save_path, 'tf_vars')
        if os.path.exists(tf_path):
            os.remove(tf_path)
        self.saver.save(self.sess, tf_path)
        
    def load_model(self, model_path):
        if not os.path.exists(model_path):
            raise RuntimeError('file not exists')
            
        param_path = os.path.join(model_path, 'params.pkl')
        with open(param_path, 'rb') as f:
            model = pkl.load(f)
            self.vocab_list = model['vocab_list']
            self.vocab_size = model['vocab_size']
            self.logdir = model['logdir']
            self.word2id = model['word2id']
            self.embedding_size = model['embedding_size']
            self.learning_rate = model['learning_rate']
            self.win_len = model['win_len']
            self.num_sampled = model['num_sampled']
            self.train_words_num = model['train_words_num']
            self.train_sents_num = model['train_sents_num']
            self.train_times_num = model['train_times_num']
            self.train_loss_records = model['train_loss_records']
            self.train_loss_k10 = model['train_loss_k10']
                                          
    def cal_similarity(self, test_word_id_list, top_k=10):                                  
        sim_matrix = self.sess.run(self.similarity, feed_dict={self.test_word_id:test_word_id_list})
        sim_mean = np.mean(sim_matrix)
        sim_var = np.mean(np.square(sim_matrix-sim_mean))
        
        test_words = []
        near_words = []
        for i in range(len(test_word_id_list)):
            test_words.append(self.vocab_list[test_word_id_list[i]])
            nearest_id = (-sim_matrix[i,:]).argsort()[1:10]
            nearest_word = [self.vocab_list[x] for x in nearest_id]
            near_words.append(nearest_word)
        return test_words, near_words, sim_mean, sim_var
                     
```


```python
w2v = word2vec(vocab_list = word_list,
               embedding_size = 200,
               learning_rate = 1,
               num_sampled = 100)
num_steps = 1000
for i in range(num_steps):
    sent = sentence_list[i]
    w2v.train_by_sentence([sent])
w2v.save_model('model')
print('模型保存成功')
```


```python
w2v.load_model('model')
test_word = ['女人', '星空']
test_id = [word_list.index(x) for x in test_word]
test_words, near_words, sim_mean, sim_var = w2v.cal_similarity(test_id)
print(test_words, near_words, sim_mean, sim_var)
```
