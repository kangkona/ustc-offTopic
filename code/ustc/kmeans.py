#!/usr/bin/env python
#coding:utf-8
import os
import random
import math
class Center(object):
    def __init__(self, vector):
        self.vector = vector
        self.objects = []
class Vector(object):
    """单个数据记录的向量表示"""
    def __init__(self, label):
        # 由于当前向量比较稀疏，所以使用字典而非数组来表示
        self.words = {}
        self.label = label
    def loadFromFile(self, file_name, word_dict):
        with open(file_name,'r') as f:
            words = f.read().split()
            for word in words:
                if word not in word_dict:
                    word_dict[word] = len(word_dict)
                word_id = word_dict[word]
                self.words[word_id] = 1
    def addToNearestCenter(self, centers):
        nearest = centers[0]
        d = self.distance(centers[0].vector)
        for center in centers[1:]:
            new_d = self.distance(center.vector)
            if new_d < d:
                d = new_d
                nearest = center
        nearest.objects.append(self)
    """
        计算两个向量之间的欧几里得距离,注意数据维度上的值非常稀疏.
    """
    def distance(self, vector):
        square_sum = 0.0
        for word in vector.words:
            if word not in self.words:
                a = vector.words[word]
                square_sum += math.pow(a, 2)
            if word in self.words:
                a,b = vector.words[word],self.words[word]
                square_sum += math.pow((a-b), 2)
        for word in self.words:
            if word not in vector.words:
                a = self.words[word]
                square_sum += math.pow(a, 2)
        result = math.sqrt(square_sum)
        return result
class KMeans(object):
    """ 准备数据，把新闻数据向量化"""
    def __init__(self, dir_name):
        self.word_dict = {}
        self.vectors = []
        self.dir_name = dir_name
        # {'file_name':{word:3,word:4}}
        self.centers = []
        # 上一次中心点的损失
        self.last_cost = 0.0
        # 从指定目录加载文件
        for file_name in os.listdir(dir_name):
            v = Vector(file_name)
            v.loadFromFile(dir_name+'/'+file_name, self.word_dict)
            self.vectors.append(v)
    """ 分配初始中心点,计算初始损失，并开始聚类 """
    def start(self, class_num):
        # 从现有的所有文章中，随机选出class_num个点作为初始聚类中心
        for vector in random.sample(self.vectors, class_num):
            c = Center(vector)
            self.centers.append(c)
        # 初始划分，并计算初始损失
        print 'init center points'
        self.split()
        self.locateCenter()
        self.last_cost = self.costFunction()
        print 'start optimization'
        # 开始进行优化，不断的进行三步操作：划分、重新定位中心点、最小化损失
        i = 0
        while True:
            i += 1
            print '第 ',i,' 次优化:'
            self.split()
            self.locateCenter()
            current_cost = self.costFunction()
            print '损失降低(上一次 - 当前)：',self.last_cost,' - ',current_cost,' = ',(self.last_cost - current_cost)
            if self.last_cost - current_cost  <= 1:
                break
            else:
                self.last_cost = current_cost
        # 迭代优化损失函数，当损失函数与上一次损失相差非常小的时候，停止优化
        count = 0
        for center in self.centers:
            count += 1
            print '第', count, '组:'
            for s in ['business','it','sports','yule','auto']:
                s_count = 0
                for vector in center.objects:
                    if vector.label.find(s) > 0:
                        s_count += 1
                print s,' = ',s_count
            print '---------------------------------------'
    """
        根据每个聚类的中心点，计算每个对象与这些中心的距离，根据最小距离重新划分每个对象所属的分类
    """
    def split(self):
        print '划分对象... Objects : ', len(self.vectors)
        # 先清空上一次中心点表里的对象数据，需要重新划分
        for center in self.centers:
            center.objects = []
        # 遍历所有文件并分配向量到最近的中心点区域
        for vector in self.vectors:
            vector.addToNearestCenter(self.centers)
    """ 重新获得划分对象后的中心点 """
    def locateCenter(self):
        # 遍历中心点，使用每个中心点所包含的文件重新求中心点
        count = 0
        for center in self.centers:
            count += 1
            print '计算第 ', count, ' 类的新中心点...'
            files_count = float(len(center.objects))
            # 新的中心点，格式为 {word1:0,word2:5...}
            new_center = {}
            # 遍历所有该中心包含的文件
            for vector in center.objects:
                # 遍历该文件包含的单词
                for word in vector.words:
                    if word not in new_center:
                        new_center[word] = 1
                    else:
                      # 由于不使用词频计算，所以出现的词都是加1，最后再求平均
                      new_center[word] += 1
            for word in new_center:
                new_center[word] = new_center[word]/files_count
            # 中心点对象
            center.vector = Vector('center')
            center.vector.words = new_center
    """ 损失函数 """
    def costFunction(self):
        print '开始计算损失函数'
        total_cost = 0.0
        count = 0
        for center in self.centers:
            count += 1
            print '计算第 ', count, ' 类的损失 objects : ', len(center.objects)
            for vector in center.objects:
                # 求距离平方作为损失
                total_cost += math.pow(vector.distance(center.vector),2)
        print '本轮损失为：',total_cost
        return total_cost
if __name__ == '__main__':
    km = KMeans('allfiles')
    km.start(5)