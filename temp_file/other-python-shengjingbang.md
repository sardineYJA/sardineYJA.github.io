


## 前言

记得高中的时候，没有什么消遣娱乐，经常看同学买的《知音漫客》，里面有部漫画叫《神精榜》，虽然画风简单但故事比较有意思，自己也是从那时开始看，直到大学它连载完，如今重看了一遍，发现还是相当有意思的。

## 链接

神精榜漫画：https://www.mkzhan.com/208692

第一话：https://www.mkzhan.com/208692/486473.html

最后一话：https://www.mkzhan.com/208692/486683.html

集数表明部分单集的id并不是连续的，不能递增id爬取，只能先获取首页全集id

## 爬取首页全集id

```python
from urllib import request

# 网络请求获取网页内容
req = request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0...')  # 用户代理
response = request.ulropen(url, timeout=30)     # 超时设置，抛出异常
html = response.read.decode('GBK')
```


## 每集爬取


## 多线程爬取






