---
layout: post
title: "漫画爬取"
date: 2019-09-20
description: "漫画爬取"
tag: 其他

---


## 前言

记得高中的时候，没有什么消遣娱乐，经常看同学买的《知音漫客》，里面有部漫画叫《神精榜》，虽然画风简单但故事比较有意思，自己也是从那时开始看，直到大学它连载完，如今重看了一遍，发现还是相当有意思的。

## 链接

神精榜漫画：https://www.mkzhan.com/208692

第一话：https://www.mkzhan.com/208692/486473.html

最后一话：https://www.mkzhan.com/208692/486683.html

集数表明部分单集的id并不是连续的，不能递增id爬取，只能先获取首页全集id

## 爬取全集

解析html：pip install beautifulsoup4


基础版，可自行增加多线程

```python
from urllib import request
from bs4 import BeautifulSoup
import re
import os
import time


def get_response(url):
    req = request.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36')
    response = request.urlopen(url).read()
    return response


def get_id_from_homepage(url):
    html = get_response(url).decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    id_html = soup.find(attrs={'class': 'chapter__list-box clearfix hide'})
    chapters = {}
    for elem in id_html:
        elem_str = str(elem).strip()
        if elem_str == "":
            continue
        chapter_name = elem.find('a').get_text().strip()       # 每集标题
        chapter_id = elem.find('a').attrs["data-chapterid"]    # 每集id
        chapters[chapter_id] = chapter_name
    return chapters


def get_chapter_images_url(url):
    html = get_response(url).decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    img_html = soup.find(attrs={'class': 'rd-article-wr clearfix'})
    temp_list = re.findall(r'data-src=".*?"', str(img_html))  # .*任意字符，?改为非贪婪
    img_list = []
    for e in temp_list:
        img_list.append(e[10:-1])
    return img_list


def save_images(url_list, chapter_dir):
    if not os.path.exists(chapter_dir):
        os.mkdir(chapter_dir)
    i = 0
    for url in url_list:
        i = i + 1
        response = get_response(url)
        with open(chapter_dir+"/" +str(i)+".jpg", 'wb') as f:
            f.write(response)


if __name__ == "__main__":
    begin_time = time.clock()

    url = "https://www.mkzhan.com/208692/"   # 神精榜首页
    save_root_dir = "E:/test/"
    if not os.path.exists(save_root_dir):
        os.mkdir(save_root_dir)
    chapters = get_id_from_homepage(url)     # 获取全集id和name

    for chapter_id in chapters:              # 保存每集图片
        try:
            chapter_url = url + chapter_id + ".html"
            images_url_list = get_chapter_images_url(chapter_url)
            chapter_dir = save_root_dir + chapters[chapter_id]
            save_images(images_url_list, chapter_dir)
            # time.sleep(0.5)
            print(chapter_id, ":", chapters[chapter_id], "--- 保存成功！")
        except Exception as e:
            print(chapter_id, ":", chapters[chapter_id], "--- 发生异常！")
            print("-------------------------------------------------")

    print("总耗时：" + str(time.clock() - begin_time))

```

## 其他

当然换个id，其他漫画也可以爬取，奇怪的是居然连VIP的漫画都可以。

盘龙漫画：https://www.mkzhan.com/211769/

偷星九月天：https://www.mkzhan.com/43/

