---
layout: post
title: "python爬虫基础"
date: 2019-05-20
description: "简单介绍python爬虫基础"
tag: Python

---

# 反爬虫机制
1. user-agent 用户代理信息（Headers头部修改）
2. cookie识别 用户登录信息（无需登录可禁用Cookie）
3. IP限制访问频率
4. 验证码策略（OCR验证码识别）
5. 无序网址（selenium自动化模拟）
6. 蜜罐技术（增加人类不会看到的链接）限制 IP+user-agent+Mac地址
7. Ajax数据请求（抓包分析）
8. 返回伪造数据
9. robots.txt 协议


# 基础爬虫

```python

from urllib import request

# 网络请求获取网页内容
req = request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0...')  # 用户代理
response = request.urlopen(url, timeout=30)     # 超时设置，抛出异常
html = response.read.decode('GBK')

# 响应的相关信息
print(response.info())
print(response.getcode())                # 状态码
print(response.geturl())                 # 访问链接
url_encode = request.quote(url)          # 对url编码
url_decode = request.unquote(url_encode) # 对url解码

# 自定义urlopen函数
# 代理IP要注意的是http、https,代理IP也需是http、https
# 代理IP不稳，可能失败
proxy = {'https': '59.48.148.226:61202'}   # 代理IP
proxy_support = request.ProxyHandler(proxy)
opener = request.build_opener(proxy_support)
opener.addheaders = [('User-Agent', 'Mozilla/5.0...')]  # 用户代理
request.install_opener(opener)
response = request.ulropen(url)
html = response.read().decode('utf-8')

# urlretrieve()打开链接并保存网页
request.urlretrieve('http://ww.csdn.net/', 'D:/save_name.html')
request.urlcleanup()   # 清除缓存


# HTTPError、URLError
import urllib.request
import urllib.error
try:
	urllib.request.ulropen('http://xxx.com')
# HTTPError放在URLError的前面，因为HTTPError是URLError的一个子类
except urllib.error.HTTPError as e:
	print(e.code)
	print(e.reason)
# URLError没有e.code属性
except urllib.error.URLError as e:
	print(e.reason)
# 合并两句：
except urllib.error.URLError as e:
	if hasattr(e, 'code'):
		print(e.code)
	if hasattr(e, 'reason'):
		print(e.reason)



# 登录访问
post_data = urllib.parse.urlencode({
	'username': 'xxx',
	'password': 'xxx'
	}).encode('utf-8')
req = request.Request(url, post_data)   # 只能访问单个页面
# 使用cookiejar保持登录状态
cjar = http.cookiejar.cookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cjar))
urllib.request.install_opener(opener)   # 将opener安装为全局
data = opener.open(req).read()
```

# BeautifulSoup


安装：pip install beautifulsoup4

解析器使用：html.parser
```python
html = get_response(url).decode("utf-8")
soup = BeautifulSoup(html, "html.parser")
```

获取某个class下的全部html
```python
id_html = soup.find(attrs={'class': 'chapter__list-box clearfix hide'})
```

解析每个Tag
```python
chapter_name = elem.find('a').get_text().strip()      # 获取标签内容
chapter_id = elem.find('a').attrs["data-chapterid"]   # 获取标签属性
```
```
<li class="j-chapter-item chapter__item id-486522">
<a class="j-chapter-link" data-chapterid="486522" data-hreflink="/208692/486522.html">
第50话 </a>
</li>
<li class="j-chapter-item chapter__item id-486521">
<a class="j-chapter-link" data-chapterid="486521" data-hreflink="/208692/486521.html">
第49话 </a>
</li>
```