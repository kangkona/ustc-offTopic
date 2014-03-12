
# -*- coding: utf-8 -*-

import re

MarkTypes = ['fm1', 'fm2', 'sw', 'vp1', 'vp2', 'vp3', 'vp4', 'vp5', 'np1', 'np2',
             'a1', 'wd1', 'wd2', 'sn1', 'sn2', 'sn3', 'sn4', 'sn4', 'sn5', 'sn6', 'unc']

class USTCEssay:
    """
    CLEC文章
    """
    def __init__(self):
        self.id = None
        self.title = None
        self.score = None
        self.contentscore = None
        self.languagescore = None
        self.structurescore = None
        self.comment = None
        self.reviewerId = None
        self.classType = None
        self.content = ''
        
    def cleanContent(self):
        return re.sub('\[.*?\]', '', self.content)
    
    def findMarks(self):
        marks = []
        end = 0
        while end >= 0:
            start = self.content.find('[', end)
            if start >= 0:
                end = self.content.find(']', start)
                if end >= start:
                    markTag = self.content[start:end + 1]
                    markType = markTag.split(',')[0].strip()[1:]
                    markType = markType.split()[0]
                    if markType[-1] == ']': markType = markType[:-1]
                    contextStart = start - 20
                    if contextStart < 0: contextStart = 0
                    markContext = self.content[contextStart:end + 20]
                    marks.append((markType, markTag, markContext, ))
            else:
                break
        return marks


def findMarks(sentence):
    # 找出一个句子的错误标注
    marks = []
    end = 0
    while end >= 0:
        start = sentence.find('[', end)
        if start >= 0:
            end = sentence.find(']', start)
            if end >= start:
                markTag = sentence[start:end + 1]
                markType = markTag.split(',')[0].strip()[1:]
                markType = markType.split()[0]
                if markType[-1] == ']': markType = markType[:-1]
                contextStart = start - 20
                if contextStart < 0: contextStart = 0
                markContext = sentence[contextStart:end + 20]
                marks.append((markType, markTag, markContext, ))
        else:
            break
    return marks    
        
      
        
def parseUSTCFile(filename):
    """
    读取USTC语料库文件，生成文章列表
    """
    
    ustcFile = open(filename, 'r')
    essays = []
    
    essayMetaPattern = '<TITLE (.*?)> <ID (\d+?)> <SCORE (\d+?)> \
<CONTENTSCORE (\d+?)> <LANGUAGESCORE (\d+?)> <STRUCTURESCORE (\d+?)> \
<COMMENT (.+?)> <REVIEWERID (\d+?)> <STUDENTNO (.*?)> <CLASSTYPE (\d+?)>'
    
    essay = None
    for line in ustcFile.readlines():    
        r = re.match(essayMetaPattern, line)
        if r:
            #if essay: print essay.cleanContent()
            essay = USTCEssay()
            essay.metaline = line
            essay.title = r.groups(1)[0]
            essay.id = r.groups(1)[1]
            essay.score = int(r.groups(1)[2])
            essay.contentscore = int(r.groups(1)[3])
            essay.languagescore = int(r.groups(1)[4])
            essay.structurescore = int(r.groups(1)[5])
            essay.comment = r.groups(1)[6]
            essay.reviewerId = int(r.groups(1)[7])
            essay.classType = int(r.groups(1)[9])
            #print essay.id, essay.score, essay.comment, essay.reviewerId, \
            #    essay.classType
            essays.append(essay)
        else:
            #print line
            if essay: essay.content += line
    
    return essays


def splitCorpusByReviewer(filename):
    """按不同的阅卷人分成不同的文件
    """

    essays = parseUSTCFile(filename)
    dict = {}
    for e in essays:
        if not e.reviewerId in dict:
            dict[e.reviewerId] = []
        dict[e.reviewerId].append(e)
        
    for k, v in dict.items():
        f = open('r' + str(k) + '_' + str(len(v)) + '.txt', 'w')
        for e in v:
            f.write(e.metaline)
            f.write(e.content)
            f.write('\n')
        f.close()
    return essays


def splitCorpusByClasstype(filename):
    """分成基础班和普通班两个文件
    """
    
    essays = parseUSTCFile(filename)
    dict = {}
    for e in essays:
        if not e.classType in dict:
            dict[e.classType] = []
        dict[e.classType].append(e)
        
    for k, v in dict.items():
        f = open('c' + str(k) + '_' + str(len(v)) + '.txt', 'w')
        for e in v:
            f.write(e.metaline)
            f.write(e.content)
            f.write('\n')
        f.close()
    return essays

def splitCorpusByPassage(filename):
    essays = parseUSTCFile(filename)
    dict = {}
    for e in essays:
        if not e.classType in dict:
            dict[e.classType] = []
        dict[e.classType].append(e)
        
    for k, v in dict.items():
        if k == 1:
            filenamePre = "../USTC2011PS/C"
        else:
            filenamePre = "../USTC2011PS/B"
        for e in v:
            f = open(filenamePre + str(e.id) + '.txt', 'w+')
            f.write(e.metaline)
            f.write(e.content)
            f.write('\n')
            f.close()
    return essays

def getCorpusBeyondScore(filename, score):
    """提取出大于 某个分数的作文
    """
    
    essays = parseUSTCFile(filename)
    essays.sort(key=lambda e: e.score, reverse=True)
    f = open('s' + str(score) + '.txt', 'w')
    for e in essays:
        if e.score <= score: break;
        f.write(e.metaline)
        f.write(e.content)
        f.write('\n')
    f.close()
    return essays

def getMarks(essays):
    marks = {}
    for mt in MarkTypes: marks[mt] = []
    for e in essays:
        for m in e.findMarks():
            mt = m[0]
            if not m[0] in marks:
                mt = MarkTypes[-1]
            marks[mt].append(m)
    for mt in MarkTypes:
        print mt, len(marks[mt])
    for mt in MarkTypes:
        print mt, len(marks[mt])
        for m in marks[mt]:
            print m
            pass


if __name__ == '__main__':
    print 'Testing...'
    #essays = parseUSTCFile('../USTC2011Jan.txt')
    #essays = getCorpusBeyondScore('../USTC2011Jan.txt', 85)
    #getMarks(essays)
    splitCorpusByPassage('../USTC2011Jan.txt')
    
    print 'OK'
