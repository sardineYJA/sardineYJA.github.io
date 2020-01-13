---
layout: post
title: "算法简介与伪代码"
date: 2019-06-01
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



# 最短路径

## Dijkstra

目标：解决单源点到其余顶点的最短路径问题。

思路：
- S集合存放已找到最短路径的顶点
- T集合存放还未找到最短路径的顶点
- S集合初始只有源点v0
- 从T中找到距离v0最近的点u，加入到S中，更新最短距离
- 重复上一步骤。

复杂度：`O(n*n)`


伪代码：
```C++
void Dijkstra(Graph G, int v0, int distance[], int path[])
{
    int n = G.Vertices.size;   // 点的数量
    int s[];                   // =0在S集合，=1在T集合

    // 初始化
    for (i = 0; i < n; i++) {
        distance[i] = G.edge[v0][i];   // distance[i]表示v0到i点的距离
        s[i] = 0;                      // 初始全部点在T集合
        if (i != 0 && distance[i] < 999) {
            path[i] = v0;
        } else {
            path[i] = -1;   // 表示i点到v0不可达
        }
    }
    s[v0] = 1;     // v0点加入到S集合

    // 其他n-1个点到v0的最短路径
    for ( i = 1; i < n; i++) { // 每次加入一个点到S集合的循环

        // 1.寻找到v0最短的点u，加入到S集合
        min = 999;
        for (j = 0; j < n; j++) {
            if( s[j] == 0 && distance[j] < min) {
                u = j;
                min = distance[j];
            }   
        }
        if (min == 999) return;   // 结束
        s[u] = 1;    // 表示从T集合放到S集合

        // 2. 更新v0到T集合中各个点的最短距离
        for (j = 0; j < n; j++) {
            if (s[j] == 0               // 表示j是T集合的点
                && G.edge[u][j] < 999   // u与j点可达 
                && distance[u] + G.edge[u][j] < distance[j]) {
                // 出现跟短的路径
                distance[j] = distance[u] + G.edge[u][j];
                path[j] = u;  // 表示j的前一个点是u
            }
        }
    }
}
```


## Floyd

目标：解决任意两点间的最短路径。

思路：

复杂度：`O(n*n*n)`

伪代码：
```C++
void Floyd(int cost[][N], int weight[][N], int path[][N]) 
{
    // 初始化
    for (i = 0; i < N; i++) {
        for (j = 0; j < N, j++) {
            weight[i][j] = cost[i][j];
            path[i][j] = -1;
        }
    }

    // i j 点之间加入k
    for (k = 0; k < N; k++) {
        for (i = 0; i < N; i++) {
            for (j = 0; j < N; j++) {
                if (weight[i][j] > weight[i][k] + weight[k][j]) {
                    weight[i][j] = weight[i][k] + weight[k][j];
                    path[i][j] = k; 
                }
            }
        }
    }
}
```


# 串的模式匹配

问题：从主串S中找到子串T，返回下标v


## Brute-Force

思路：逐个比较

复杂度：`O(n*m)`

伪代码：
```C++
int BF(char * S, char * T) 
{
    int i = 0;   // S 字符串的下标
    int j = 0;   // T 字符串的下标
    while (i < S.len && j < T.len) {
        if (S[i] == T[j]) {
            i++;
            j++;
        } else {
            i = i - j + 1;
            j = 0;
        }
    }
    if (j == T.len)
        v = i - T.len;    // 找到子串在主串开始的下标v
    else 
        v = -1;
    return v;
}
```



## KMP

思路：关键在于求 next[] 即前缀和后缀匹配数

伪代码：
```C++
int KMP(char * S, char * T) 
{
    int i = 0;   // S 字符串的下标
    int j = 0;   // T 字符串的下标
    while (i < S.len && j < T.len) {
        if (S[i] == T[j]) {
            i++;
            j++;
        } 
        else if (j==0) i++;   // 第一个字符都没对上，则下一个
        else j = next[j];
    }
    if (j == T.len)
        v = i - T.len;    // 找到子串在主串开始的下标v
    else 
        v = -1;
    return v;
}
```
关键在于求出子串T的next[]：
```C++
void getNext(char * T) 
{
    next[0] = -1; next[1] = 0;

    int j = 1; k = 0;  

    while (j < T.len-1) {
        if (T[j] = T[k]) {
            next[j+1] = k+1;
            j++;
            k++;
        } else if (k == 0) {
            next[j+1] = 0;
            j++;
        } else {
            k = next[k];
        }
    }
}
```

# 动态查找

## 二叉排序树

左节点数值 < 根节点数值 < 右节点数值，中序遍历则就是升序排序

循环方式查找：
```C++
int Search(BiTreeNode * root, DataType item) 
{
    BiTreeNode * p;
    if (root != NULL) {
        p = root;
        while (p != NULL) {
            if (p->data == item) return 1;           // 查找成功
            if (p->data < item) p = p->rightChild;   // 目标数较大，往右查
            if (p->data > item) p = p->leftChild;    // 目标数较小，往左查      
        }
    }
}
```

当二叉排序树是一颗完全二叉树，或实现平衡二叉树，它们平均查找长度`O(lbn)`。

B-树是一种平衡多叉排序树，主要用于动态查找。

B+树是B-树的变形，主要用于文件系统。



# 题目


## 两数之和

一个整数数组nums和一个目标值target，在该数组中找出和为目标值的那两个整数的下标。

1. 暴力破解，复杂度：`O(n*n)`。
2. 哈希表map：数字作为键，下标作为值。复杂度`O(n)`。

```C++
// 建立哈希表O(n)
for (i=0; i<nums.size(), i++)
    map[nums[i]] = i;

// 查找O(n)
for (i=0; i<nums.size(); i++)
{
    d = target-nums[i];
    // 在map中找是否存在差值d
    if (map.containsKey(d) && i!=map.get(d))
        // 找到两个下标：i和map.get(d)
}
```


## 链表翻转

```C++
ListNode * reverseList(ListNode * head) 
{
    ListNode * _next = NULL; // 保存原来的链表
        
    ListNode * cur = head;   // 每次处理的节点cur 

    ListNode * prev = NULL;  // prev 接到 cur 后

    while (cur) {
        _next = cur->next;   // 保存原来的链表

        cur->next = prev;    // 处理 cur
        prev = cur;
        cur = _next;
    }
    return prev;
}
```



