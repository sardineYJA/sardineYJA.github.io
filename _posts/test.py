# -*- coding: utf-8 -*-
"""
代码模板说明:
(1)测试数据将会以一个字典的形式传递进入main函数。字典的格式为{"MapData":((), (), (),...), "TestPoint":((), (), (),...)}
(2)地图信息(MapData)的内容是一个存储着地图中每个点的阻挡或者非阻挡的实际情况的二维元组,如((1, 0, 1, 0, 1...), (0, 1, 1, 0, 1...),...)。其中阻挡点为1，非阻挡点为0
(3)测试点数据(TestPoint)的内容是一个存储着坐标点信息的二维元组,二维元组中的每个小元组的内容代表着坐标点的x,y坐标,即(x, y).测试点数据(TestPoint)格式如:((2, 4), (7, 9), (11, 8),...)
(4)玩家需要在main函数里面进行编写自己的逻辑代码，即可以自己编写类、函数等模块在main函数内进行调用,辅助计算出满足赛题要求的结果
(5)在main函数逻辑结束前，必须要返回从TestPoint中筛选出全部处于最大闭合区域的坐标的一个元组,格式与测试点数据格式相同,是个二维元组,如：
TestPoint = ((15, 1), (2, 12), (5, 3), (18, 11), (13, 11), (16, 7), (3, 8), (5, 2), (18, 10), (19, 11), (1, 8)),
而通过计算获得符合要求的点有:(5, 3), (16, 7), (5, 2),最终从main函数将会返回一个((5, 3), (16, 7), (5, 2))二维元组,即return ((5, 3), (16, 7), (5, 2))
(6)python代码的运行环境是python 3, 不支持python的外部依赖包，只支持python标准库
(7)不要使用全局变量进行计算相关数据的存储和计算。可以使用局部变量、类的成员变量等方式替代全局变量的使用
(8)坐标原点(0, 0)是地图信息(MapData)二维元组中第一行,第一列的元素,即oMap.m_MapData[0][0],之后地图将会向下、向右依次进行坐标(x, y)的递增。第x行、第y列的坐标是oMap.m_MapData[x-1][y-1]
"""

def main(argv):

    oMap = CreateMap(argv)
    #####玩家代码开始编写#####


    print(oMap.Start())

    # 结束
    return oMap.Start()



def CreateMap(dInfo):
    return CMap.CreateMap(dInfo)

class CMap(object):
    def __init__(self):
        self.m_iWidth = 0
        self.m_iHeight = 0
        self.m_MapData = []
        self.m_TestPoint = []
        self.m_visited = []
        self.m_maxArea = []

    def SetData(self, mapData):
        """
        m_MapData[x][y]为坐标(x,y)的阻挡信息
        :param mapData:
        :return:
        """
        self.m_MapData = mapData
        self.m_iWidth = len(mapData)        # 地图宽  行
        self.m_iHeight = len(mapData[0])    # 地图高  列

    def IsBlock(self, x, y):
        """
        采用笛卡尔坐标系
        :param x:横坐标
        :param y:纵坐标
        :return:0:表示非阻挡，1表示阻挡
        """
        return self.m_MapData[x][y]

    def SetTestPoint(self, testPoint):
        """
        用于测试是否在最大闭合区域的点
        :param testPoint:
        :return:
        """
        self.m_TestPoint = map(tuple, testPoint)

    @classmethod
    def CreateMap(cls, dInfo):
        """
        地图数据的加载
        :param fpath:
        """
        mapData = dInfo.get("MapData", [])          #获得地图信息
        testPoint = dInfo.get("TestPoint", [])      #获得测试点数据
        oMap = CMap()
        oMap.SetData(mapData)
        oMap.SetTestPoint(testPoint)
        return oMap

    def RecursiveCheck(cls, i, j, f):
        black = []
        if 1 in f:
            if j > 0 and cls.m_MapData[i][j - 1] == 0 and [i, j - 1] not in cls.m_visited:
                black.append([i, j - 1])
                cls.m_visited.append([i, j - 1])
                black.extend(cls.RecursiveCheck(i, j - 1, [1, 2, 3, 4]))
        if 2 in f:
            if i > 0 and cls.m_MapData[i - 1][j] == 0 and [i - 1, j] not in cls.m_visited:
                black.append([i - 1, j])
                cls.m_visited.append([i - 1, j])
                black.extend(cls.RecursiveCheck(i - 1, j, [1, 2, 3, 4]))
        if 3 in f:
            if j < cls.m_iHeight - 1 and cls.m_MapData[i][j + 1] == 0 and [i, j + 1] not in cls.m_visited:
                black.append([i, j + 1])
                cls.m_visited.append([i, j + 1])
                black.extend(cls.RecursiveCheck(i, j + 1, [1, 2, 3, 4]))
        if 4 in f:
            if i < cls.m_iWidth - 1 and cls.m_MapData[i + 1][j] == 0 and [i + 1, j] not in cls.m_visited:
                black.append([i + 1, j])
                cls.m_visited.append([i + 1, j])
                black.extend(cls.RecursiveCheck(i + 1, j, [1, 2, 3, 4]))
        return black

    def Start(cls):
        res = 0
        for i in range(cls.m_iWidth):
            for j in range(cls.m_iHeight):
                if cls.m_MapData[i][j] == 0 and [i, j] not in cls.m_visited:
                    cls.m_visited.append([i, j])
                    s = cls.RecursiveCheck(i, j, [3, 4])
                    if len(s) > res:
                        res = len(s) + 1
                        cls.m_maxArea = s
                        cls.m_maxArea.append([i, j])
        result = []
        for point in cls.m_TestPoint:
            if list(point) in cls.m_maxArea:
                result.append(point)
        return tuple(result)




####  测试

argv = {
    "MapData": (
        (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),
        (1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1),
        (1,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1),
        (1,0,0,1,1,1,1,0,0,0,0,1,0,0,1,0,0,1,1,1),
        (1,0,0,1,1,1,1,0,0,0,0,1,0,0,1,0,0,1,1,1),
        (1,0,0,1,1,1,1,0,0,0,0,1,0,0,0,0,0,0,1,1),
        (1,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,1,0,1,1),
        (1,0,0,1,1,0,1,1,1,1,1,1,1,1,1,0,1,0,1,1),
        (1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1),
        (1,1,1,1,1,0,0,0,1,1,1,0,0,1,1,1,1,1,1,1),
        (1,1,1,1,1,1,1,0,1,1,1,0,0,1,1,1,1,1,1,1),
        (1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0,0,1,1),
        (1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0,0,1,1),
        (1,0,0,1,0,0,0,0,1,1,0,0,1,1,1,1,0,1,1,1),
        (1,0,0,1,1,1,1,0,1,1,0,0,1,1,1,0,0,1,1,1),
        (1,0,0,1,1,0,0,0,1,1,0,0,1,1,0,0,0,1,1,1),
        (1,1,1,1,1,0,1,0,1,1,1,1,1,1,0,0,0,1,1,1),
        (1,1,1,1,1,0,1,0,1,1,1,1,1,1,0,0,0,1,1,1),
        (1,1,1,1,0,0,0,0,1,1,1,1,1,1,0,0,0,1,1,1),
        (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),
        (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)
    ),
    "TestPoint": (
        (16, 15),
        (18, 4),
        (13, 2),
        (5, 2),
        (4, 12),
        (14, 2)
    )
}

# main(argv)


import random
def TestCreateMap():
    lstResult = []
    for _ in range(20):
        dData = CreateDemoData()
        setArea, iRepeat = Solve(dData["MapData"])
        if iRepeat != 1:     # 存在多个相同大小的最大连通区域
            continue

        lstArea = list(setArea)
        for _ in range(random.randint(1, 4)):
            tPoint = lstArea[random.randint(0, len(lstArea) - 1)]
            lstPoint = dData["TestPoint"]
            if not tPoint in lstPoint:
                lstPoint.append(tPoint)

        lstResult = []
        for tPoint in lstPoint:
            if not tPoint in setArea:
                continue
            lstResult.append(tPoint)

        break
    return dData, lstResult


def CreateDemoData():
    h = 200
    w = 200
    pointnum = 5
    dMapdata = {}
    lmap = []
    for i in range(0, h):
        lline = []
        for j in range(0, w):
            if i == 0 or i == h - 1 or j == 0 or j == w - 1:
                data = 1
            else:
                data = random.randint(0, 1)
            lline.append(data)
        lmap.append(lline)
    dMapdata["MapData"] = lmap
    lpoint = []
    for i in range(0, pointnum):
        lpoint.append((random.randint(0, h - 1), random.randint(0, w - 1)))
    dMapdata["TestPoint"] = lpoint
    return dMapdata


def Solve(dMap):
    iMRow = len(dMap)
    iMCol = len(dMap[0])
    iRepeat = 1
    lstMaxArea = set()

    setAll = set()
    for x in range(1, iMRow - 1):       # 去掉边界
        for y in range(1, iMCol - 1):   # 去掉边界
            if dMap[x][y] == 1:
                continue
            if (x, y) in setAll:
                continue

            lstArea = set([(x, y)])
            lstSearch = set([(x, y), ])
            while lstSearch:
                tSearch = lstSearch.pop()
                for tVector in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    tNewPos = (tSearch[0] + tVector[0], tSearch[1] + tVector[1])
                    if tNewPos in lstArea:
                        continue
                    if dMap[tNewPos[0]][tNewPos[1]] == 0:
                        lstSearch.add(tNewPos)
                        lstArea.add(tNewPos)
            if len(lstArea) > len(lstMaxArea):
                lstMaxArea = lstArea
                iRepeat = 1
            elif len(lstArea) == len(lstMaxArea):
                iRepeat += 1
            setAll.update(lstArea)
    return lstMaxArea, iRepeat


# dData, lstResult = TestCreateMap()
# print("输入:")
# print("测试点：", dData["TestPoint"])
# print("预期输出结果:")
# print(lstResult)

# main(dData)



