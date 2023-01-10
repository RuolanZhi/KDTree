from typing import List
from collections import namedtuple
import time


class Point(namedtuple("Point", "x y")):
    def __repr__(self) -> str:
        #满足输出
        return f'Point{tuple(self)!r}'


class Rectangle(namedtuple("Rectangle", "lower upper")):
    def __repr__(self) -> str:
        return f'Rectangle{tuple(self)!r}'

    def is_contains(self, p: Point) -> bool:
        #是否满足在当前范围内
        return self.lower.x <= p.x <= self.upper.x and self.lower.y <= p.y <= self.upper.y


class Node(namedtuple("Node", "location left right")):
    """
    location: Point
    left: Node
    right: Node
    """
    def __repr__(self):
        return f'{tuple(self)!r}'


class KDTree:
    """k-d tree"""

    def __init__(self):
        #初始化树
        self._root = None
        self._n = 0


    def insert(self, p: List[Point]):
        """insert a list of points"""
        #将现有数据插入当前KD树
        #需要递归插入
        depth=0
        self._n=len(p[0])
        def insert_(p,depth):
            if len(p)>0:
                mid=len(p)//2#求出中位数的index
                #求出分割维度
                axis=depth%self._n
                #按当前维度进行排序
                p_copy=sorted(p,key=lambda x:x[axis])
                if depth==0:
                    #根节点
                    self._root=Node(p_copy[mid],insert_(p_copy[:mid],depth+1),insert_(p_copy[mid+1:],depth+1))
                node=Node(p_copy[mid],insert_(p_copy[:mid],depth+1),insert_(p_copy[mid+1:],depth+1))
                return node
        insert_(p,depth)

    def range(self, rectangle: Rectangle) -> List[Point]:
        """range query"""
        #进行范围查询
        lst=[]
        xl,yl,xu,yu=rectangle.lower.x,rectangle.lower.y,rectangle.upper.x,rectangle.upper.y
        depth=0
        node=self._root
        def find(node,depth):
            if node==None:
                return None
            axis=depth%self._n
            val=node.location[axis]
            if axis:
                #y轴
                if val>yu:
                    find(node.left,depth+1)
                elif val<yl:
                    find(node.right,depth+1)
                else:
                    find(node.left,depth+1)
                    find(node.right,depth+1)
                    #判断当前节点是不是
                    if rectangle.is_contains(node.location):
                        lst.append(node.location)
            else:
                if val>xu:
                    find(node.left,depth+1)
                elif val<xl:
                    find(node.right,depth+1)
                else:
                    find(node.left,depth+1)
                    find(node.right,depth+1)
                    #判断当前节点是不是
                    if rectangle.is_contains(node.location):
                        lst.append(node.location)
        find(node,0)
        return lst
    
    #实现最邻近查询
    def find_nearest(self,point,root=None,axis=0,dist_func=lambda x,y:((x[0]-y[0])**2+(x[1]-y[1])**2)) :
        #此处定义距离函数为欧式距离
        if root is None:
            root=self._root
            self._best=None
        #如果不是叶节点，则继续往下走
        if root.left or root.right:
            new_axis=(axis+1)%self._n
            if point[axis]<root.location[axis] and root.left:
                self.find_nearest(point,root.left,new_axis)
            elif root.right:
                self.find_nearest(point,root.right,new_axis)
        #回溯，尝试更新best
        dist=dist_func(root.location,point)
        if self._best is None or dist<self._best[0]:
            self._best=(dist,root.location)
        if abs(point[axis]-root.location[axis]) < self._best[0]:
            new_axis=(axis+1)%self._n
            if root.left and point[axis]>=root.location[axis]:
                self.find_nearest(point,root.left,new_axis)
            elif root.right and point[axis]<root.location[axis]:
                self.find_nearest(point,root.right,new_axis)
        return self._best
def range_test():
    points = [Point(7, 2), Point(5, 4), Point(9, 6), Point(4, 7), Point(8, 1), Point(2, 3)]
    kd = KDTree()
    kd.insert(points)
    result = kd.range(Rectangle(Point(0, 0), Point(6, 6)))
    assert sorted(result) == sorted([Point(2, 3), Point(5, 4)])


def performance_test():
    points = [Point(x, y) for x in range(1000) for y in range(1000)]

    lower = Point(500, 500)
    upper = Point(504, 504)
    rectangle = Rectangle(lower, upper)
    #  naive method
    start = int(round(time.time() * 1000))
    result1 = [p for p in points if rectangle.is_contains(p)]
    end = int(round(time.time() * 1000))
    print(f'Naive method: {end - start}ms')

    kd = KDTree()
    kd.insert(points)
    # k-d tree
    start = int(round(time.time() * 1000))
    result2 = kd.range(rectangle)
    end = int(round(time.time() * 1000))
    print(f'K-D tree: {end - start}ms')

    assert sorted(result1) == sorted(result2)
    #判断两者结果是否相同

    #实现最邻近算法
    point_test=Point(44.5,68.7)
    dis,point=kd.find_nearest(point_test)
    print('the nearest point:{},the distance is {}'.format(point,dis))
if __name__ == '__main__':
    range_test()
    performance_test()