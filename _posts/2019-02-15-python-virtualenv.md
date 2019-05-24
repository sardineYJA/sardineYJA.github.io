---
layout: post
title: "virtualenv的使用"
date: 2019-02-15
description: "介绍virtualenv的使用"
tag: python

---

# 安装配置
## 安装
```
pip install virtualenv
```

## 新建虚拟环境
```
C:\>virtualenv testenv                            // 默认版本
C:\>virtualenv -p D:\\Python27\\python testenv    // 指定2.7
// 默认情况下，虚拟环境会依赖系统环境中的site packages，
// 就是说系统中已经安装好的第三方package也会安装在虚拟环境中，
// 如果不想依赖这些package，那么可以加上参数 --no-site-packages建立虚拟环境
 
virtualenv --no-site-packages [虚拟环境名称]
C:\testenv\Scripts>activate    //激活
(testenv) C:\testenv\Scripts>  //注意终端发生了变化
(testenv) C:\testenv\Scripts>pip3 list
(testenv) C:\testenv\Scripts>deactivate   //关闭当前虚拟环境
C:\testenv\Scripts>
```

## 导出每个包版本/安装所需包
```
(venv) $ pip freeze > requirements.txt      # 导出
(venv) $ pip install -r requirements.txt    # 安装
```

## PyCharm使用virtualenv环境：
在新建项目中Base interpreter选择编译版本<br>
新建项目后，在File中Settings的Project Interpreter中添加即可


# 参考
1. https://www.jb51.net/article/129027.htm