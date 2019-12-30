---
layout: post
title: "算法简介与伪代码"
date: 2020-01-01
description: "算法简介与伪代码"
tag: Other

---


# 排序


## 冒泡排序

思路：

复杂度：`O(n*n)`

伪代码：
```python
def bubble_sort(data):
	for(int i=0; i<data.len; i++)
		for (int j=0; j<data.len-i-1; j++) 
		    # 较大的数慢慢往后排
			if (data[j] > data[j+1])
				temp = data[j]
				data[j] = data[j+1]
				data[j+1] = temp
```


## 快速排序

复杂度：`O(nlogn)`

伪代码：
```python
def quick_sort(data, low, high):
	i, j = low, high
	temp = data[i]
	while i < j: # 每轮在最左找比temp大的，在最右找比temp小的

		while(i<j && temp <= data[j]):
			j--
		if i < j:
			data[i] = data[j]    # 将小的数据放左边
			i++

		while (i<j && temp >= data[i]):
			i++;
		if i < j:
			data[j] = data[i]    # 将大的数据放右边
			j--;

	# 递归
	data[i] = temp
	if low < i:
		quick_sort(data, low, i-1)
	if i < high:
		quick_sort(data, j+1, high)

```



## 归并排序

思路：
- 两个小组进行排序并合并，如1与2组，3与4组....
- l1表示组1的起始位置，u1表示组1的结束位置
- l2表示组2的起始位置，u2表示组2的结束位置
- swap表示排序成功后的数组结果

复杂度：`O(nlogn)`

伪代码：
```python
# 归并排序
def merge(data, swap, k):
    m = 0   # swap 的索引
    n = len(data)
    l1 = 0
    while (l1+k <= n-1):
        l2 = l1 + k
        u1 = l2 - 1
        u2 = (l2+k-1 <= n-1) ? l2+k-1 : n-1   # 防越界

        # 两个有序合并,小数先进swap
        for (i=l1, j=l2; i<=u1, j<=u2; m++)
            if data[i] <= data[j]:
                swap[m] = data[i]
                i += 1
            else:
                swap[m] = data[j]
                j += 1

        # 组2先归并完
        while i <= u1:
            swap[m] = data[i]
            m++
            i++
        # 组1先归并完
        while j <=u2:
            swap[m] = data[j]
            m++
            j++

        l1 = u2+1   # 接下两组进行归并

    for (i=l1; i<n; i++, m++) # 奇数，剩余最后一组
        swap[m] = data[i]


def merge_sort(data):
    n = len(data)
    k = 1         # 每组数据的个数
    while k < n:
        merge(data, swap, k)
        k = 2*k   # 每组数据个数2倍增长
```



## 堆排序

思路：

复杂度：

伪代码：





