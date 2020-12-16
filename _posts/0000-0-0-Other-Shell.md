---
layout: post
title: "Shell 常用操作"
date: 2020-06-17
description: "Shell"
tag: Other

---


# shell

## sed 替换
```sh
# 替换后直接输出，需要直接替换到txt加：-i
sed 's/要被取代的字串/新的字串/g' your.txt

sed -i 's/要被取代的字串/直接修改文件内容/g' your.txt

# 把"单引号"变成"双引号"，变量不含斜杆
sed -i "s/要被取代的字串/${VALUE}/g" your.txt

# 如果变量字符串含有 / 斜杆，无法替换
# 先将 / 替换成 \/ 的字符串，再去替换文件
VALUE=`echo hh/hh | sed 's/\//\\\\\//g'`    # 这里 sed 使用的是单引号
sed -i "s/要被取代的字串/${VALUE}/g" your.txt

# 替换特定某一行
sed "10c ${new_string}" your.txt    # 替换第10行内容
```

## 删除字符
```sh
str="12345467"   
echo ${str:1}      # 去掉首字母
echo ${str%?}      # 去掉字符串最后1个字符，#是去掉左边， %是去掉右边

echo ${str::-4}    # 去掉最后4个字符
echo ${str:0:5}：  # 提取最左边的 5 个字节
```

## 切分字符串
```sh
str_array=(echo $str | tr "," "\n")   # 以逗号切分字符串
for s in ${str_array[@]} 
do
  echo $s
done
```

## 字符串是否为空
```sh
if [ ! -z $str ];then
    echo "$str is must be! exit ..."
    exit
fi
```

## 文件是否存在
```sh
if [ ! -f $your_file ];then
    echo "$your_file is not found! exit ..."
    exit
fi
```

## 目录是否存在
```sh
if [ ! -d $your_dir ];then
    mkdir -p $your_dir
    echo "create directory : $your_dir"
fi
```

## 读取文件
```sh
# 文件最后一行之后没有换行符\n，则read读取最后一行时遇到文件结束符EOF，循环即终止。
# 解决： [[ -n $line ]] ，-n 判断变量的值，是否为空
cat $file_name | while read line || [[ -n $line ]]  
do 
    if [ ! -z $line ]; then
        echo $line
    fi
done
```

## 用变量值做新变量名
```sh
LG_2020_NAME="yang"
YEAR="2020"
server_name=`eval echo '$'LG_"${YEAR}"_NAME`  # ==> yang
```

## 参数
```sh
echo "$@"          # 所有参数

echo "${@:-1}"     # 最后一个参数
 
echo "${@:2}"      # 除了第一个参数的其他所有参数
```

## 删除文件行
```sh
sed -i '1d' ./filename   # 删除文件第一行

sed -i '$d' ./filename   # 删除文件最后一行
```






# 其他

## vim 配置
用户目录下新建文件`.vimrc`保存：
```sh 
syntax on             # 语法高亮
set number            # 显示行号
set backupcopy=yes    # 设置备份时的行为为覆盖，可使vi修改文件后，inode不变
```

## vim 取消自动缩进

拷贝前输入:set paste


## top
- PID      进程id
- USER     进程所有者的用户名
- PR       优先级
- NI       nice值。负值表示高优先级，正值表示低优先级
- VIRT     进程使用的虚拟内存总量，单位kb。VIRT=SWAP+RES
- RES      进程使用的、未被换出的物理内存大小，单位kb。RES=CODE+DATA
- SHR      共享内存大小，单位kb
- S        进程状态。D=不可中断的睡眠状态R=运行S=睡眠T=跟踪/停止Z=僵尸进程
- %CPU     上次更新到现在的CPU时间占用百分比
- %MEM     进程使用的物理内存百分比
- TIME+    进程使用的CPU时间总计





# 防火墙

## 添加

编辑：/etc/sysconfig/iptables

重启：service iptables start

```sh
-A INPUT -s 10.17.65.164 -m tcp -p tcp --dport 9200:9309 -j ACCEPT
# 表示本机的 9200 到 9309 一系列端口对 10.17.65.164 开放

iptables -A INPUT -s 172.17.0.0/16 -p tcp --dport 9200 -j ACCEPT
# -A 添加策略
# -s 源地址，不指定则表示所有地址
# -p 协议
# -dport 目的端口
# -j 执行目标 ACCEPT, DROP, QUEUE, RETURN

# root 执行
iptables-save      # 查看防火墙

# 9200 只转发 10.0.0.0/8 的数据 ，否则直接丢掉
-A FORWARD ! -s 10.0.0.0/8 -p tcp -m tcp --dport 9200 -j DROP

```

## 清空防火墙
```sh
iptables -L     # 看到如下信息
Chain INPUT (policy DROP 0 packets, 0 bytes)  （注意 是DROP）
iptables -F     # 就肯定立马断开连接
# 清空防火墙
iptables -P INPUT ACCEPT  # 把默认策略改成 ACCEPT
iptables -F               # 再清空，如果不改掉，就清空防火墙，那么你服务器就打不开了，需要重新配置网络才行。
```

## 介绍

iptables 具有 Filter, NAT, Mangle, Raw四种内建表。

Filter 表：
- INPUT 链，处理来自外部的数据。
- OUTPUT 链，处理向外发送的数据。
- FORWARD 链，将数据转发到本机的其他网卡设备上。



## 重复防火墙

增加一条防火墙，自身并不会进行重复检测，可以在增加前进行检查：
```sh
#!/bin/bash
add_iptables(){
    check_rule=$(echo $@ | sed -e 's/-A/-C/g')
    `$check_rule` ;check=$?
    if [ "$check" -eq 0 ]; then
        :;
    else
        echo "$@"
        `$@`
    fi
}
add_iptables "iptables -A ..."
```





