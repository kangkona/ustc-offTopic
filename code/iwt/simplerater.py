# -*- coding: utf-8 -*-

import pickle
import random

import json

from scipy import linalg, array, dot, mat, zeros, random
from math import *

import numpy as np

from essayreader import USTCReader
from essay import EssayPassage
import essayprepare
from essaymodel import EssayModel
from extractor import FeatherExtractor

import time

import logging
LOG_FILENAME ='simple_rater.log'
logging.basicConfig(filename=LOG_FILENAME,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    level=logging.DEBUG)

class SimpleEssayRater():
    """这是一个通用的评分器
    """
    
    def __init__(self):
        self.model_params = [30, -0.9, -0.55, -80, 50, -0.38, 8.0, -145,
                             16.8, 0.05, 0.4, -0.04, 35, -0.4, 0.35, -0.5]
        pass
       
    def __getFeatherList(self, passage):
        """Get feathers from preprocessed passage
        """

        fs = []
        fs.append(1) # const
        fs.append(passage.lf.sentenceErrorCount)
        fs.append(passage.lf.spellErrorCount)
        #fs.append(passage.lf.ltErrorCount)
        fs.append(passage.lf.prepositionUse)
        fs.append(passage.lf.definiteArticleUse)
        #fs.append(passage.lf.wordCombRecurrentCount)  
        #fs.append(passage.lf.tokenCount)
        #fs.append(passage.lf.wordTypeCount)
        fs.append(passage.lf.wordStemCount)
        fs.append(passage.lf.wordLengthAverage)
        #fs.append(passage.lf.wordLengthSD)
        fs.append(passage.lf.wordTypeRatio)
        fs.append(passage.lf.indexOfGuiraud)
        #for x in passage.lf.wordCountInLevels:
        #    fs.append(x)
        fs.append(passage.lf.gerundCount)
        #fs.append(passage.lf.gerundRatio)
        #fs.append(passage.lf.sentenceLengthAverage)
        #fs.append(passage.lf.sentenceLengthSD)
        #fs.append(passage.lf.automatedReadabilityIndex)  
        fs.append(passage.lf.sentenceComplexity)  
        #fs.append(passage.lf.sentenceComplexityScale) 
         
        #fs.append(passage.cf.lsaScore)   
        #fs.append(passage.cf.proceduralVocabularyCount) 
        #fs.append(passage.cf.keywordCover)
        
        fs.append(passage.sf.connectiveCount)   
        #fs.append(passage.sf.connectiveRatio)   
        #fs.append(passage.sf.specialDemonstrativePronounCount)
        #fs.append(passage.sf.specialDemonstrativePronounUse)
        #fs.append(passage.sf.restPronounCount)
        #fs.append(passage.sf.restPronounUse)        
        fs.append(passage.lf.highLowLevelRatio)
#        fs.append((passage.lf.wordCountInLevels[3] + passage.lf.wordCountInLevels[4]) * 1.0 
#                  / (passage.lf.wordCountInLevels[1] + passage.lf.wordCountInLevels[2]))
        fs.append(passage.lf.overlyUseWordCount)
        fs.append(passage.lf.aclWordCount)
        #fs.append(passage.lf.aclWordRatio)
        fs.append(passage.lf.nominalizationCountUnique)
        return fs
    
    def tokenCountFilter(self, passage):
        # 根据文章字数调整
        filter = 0
        if (passage.lf.tokenCount < 100):
            filter = passage.rateScore * 0.2
        elif passage.lf.tokenCount < 120:
            filter = passage.rateScore * 0.1   
        filter = - filter  
        return filter   
    
    def sentenceLengthAverageFilter(self, passage):
        # 根据平均句长调整
        filter = 0
        slv = passage.lf.sentenceLengthAverage
        if (slv < 10):
            filter = (10 - slv) * 2
            if filter > 6: filter = 6
        elif slv > 23:
            filter = (slv - 23) * 3
            if filter > 9: filter = 9
        filter = - filter
        return filter  
    
    def wordLengthAverageFilter(self, passage):
        # 根据平均词长调整 
        filter = 0
        wlv = passage.lf.wordLengthAverage
        if wlv < 4:
            filter = (4 - wlv) * 10
        filter = - filter
        return filter    
    
    def aclWordCountFilter(self, passage):
        # 根据学术词汇数调整
        filter = 0
        acl = passage.lf.aclWordCount
        if acl > 9:
            filter = passage.rateScore * 0.1
        return filter
    
    def noneStopWordLengthAverageFilter(self, passage):          
        # 根据实词平均长度调整
        filter = 0
        rwlv = passage.lf.noneStopWordLengthAverage
        if rwlv < 5.5:
            filter = (5.5 - rwlv) * 10  
        filter = -filter
        return filter
        
    def nounRatioFilter(self, passage):
        # 根据词性比例调整
        filter = 0
        nr = passage.lf.nounRatio
        if nr < 0.2:
            filter = (0.2 - nr) * 100
        elif nr > 0.35:
            filter = (nr - 0.35) * 100
        filter = - filter
        return filter
    
    def verbRatioFilter(self, passage):
        filter = 0
        vr = passage.lf.verbRatio
        if vr < 0.1:
            filter = (0.1 - vr) * 200
        elif vr > 0.2:
            filter = (vr - 0.2) * 200
        filter = - filter
        return filter
    
    def adjRatioFilter(self, passage):
        filter = 0
        ar = passage.lf.adjRatio
        if ar < 0.045:
            filter = (0.045 - ar) * 500
        filter = - filter
        return filter
    
    def posRatioFilter(self, passage):
        filter = 0
        badRatioCount = 0   
        offsetRatio = 0      
        nr = passage.lf.nounRatio
        vr = passage.lf.verbRatio
        ar = passage.lf.adjRatio
        if (nr < 0.2) or (nr > 0.3):
            badRatioCount += 1
        else:
            offsetRatio += abs(nr - 0.25) / 0.1
        if (vr < 0.1) or (vr > 0.2):
            badRatioCount += 1
        else:
            offsetRatio += abs(vr - 0.15) / 0.1
        if (ar < 0.06) or (ar > 0.15):
            badRatioCount += 1
        else:
            offsetRatio += abs(ar - 0.105) / 0.15
        if badRatioCount == 0:
           if offsetRatio < 0.1:
                filter = passage.rateScore * 0.05
        elif badRatioCount == 1:
            if offsetRatio > 0.6:
                filter = - passage.rateScore * 0.05
        elif badRatioCount > 1:
            filter = - passage.rateScore * 0.02 * badRatioCount * badRatioCount
        passage.offsetRatio = offsetRatio
        return filter  
    
    def total_score_filter(self, passage):
        filter = 0
        if passage.rateScore < 0:
            filter = 30 - (-1 * passage.rateScore) % 20 - passage.rateScore
        elif passage.rateScore > 95:
            filter = 95 - passage.rateScore
        return filter
    
    def rate_by_params(self, passage):
        # 线性预测
        extractor = FeatherExtractor(None)
        if not passage.preprocessed: essayprepare.processPassage(passage)
        passage.lf = extractor.extractLangFeather(passage)
        passage.cf = extractor.extractContentFeather(passage)
        passage.sf = extractor.extractStructureFeather(passage)

        exog = []
        x = self.__getFeatherList(passage)
        
        score = dot(x, self.model_params)
        
        passage.rateScore = score
        passage.endogScore = score
                
        # 调整分数
        passage.filter_scores = []
        filters = [self.tokenCountFilter, self.sentenceLengthAverageFilter,
                   self.wordLengthAverageFilter, self.aclWordCountFilter,
                   self.noneStopWordLengthAverageFilter, self.nounRatioFilter,
                   self.total_score_filter]
        
        for filter in filters:
            filter_score = filter(passage)
            passage.rateScore += filter_score
            passage.filter_scores.append(filter_score)
        
        passage.rated = True
        return [passage.rateScore]

    
def demo_parmas():
    print "rater demo_parmas" 

    # 读测试集
    pkfile = open('zhang_tests.pkl', 'r')
    tests = (pickle.load(pkfile))
    pkfile.close()
    
    r = SimpleEssayRater()

    # 打分测试
    for p in tests:
        s = r.rate_by_params(p)
        p.newscore = s[0]
        print p.id, p.score, s
        
    for p in tests:
        print p.id, p.score, p.newscore
        
    print "demo_parmas over!!!"  
    
def demo_one():
    content = """At present ,more and more students in the college are encouraged to go to the poor places for aid education . This activity is of great benefits for both our college students and the poor places. At present ,more and more students in the college are encouraged to go to the poor places for aid education . This activity is of great benefits for both our college students and the poor places. At present ,more and more students in the college are encouraged to go to the poor places for aid education . This activity is of great benefits for both our college students and the poor places. At present ,more and more students in the college are encouraged to go to the poor places for aid education . This activity is of great benefits for both our college students and the poor places."""

    # 文章
    passage = EssayPassage()
    passage.passage = content
    passage.title = 'title'
    passage.score = 5
    passage.id = '1'
    passage.reviewerId = 3
    passage.content = content
       
    r = SimpleEssayRater()
    s = r.rate_by_params(passage)
    passage.newscore = s[0]
    print passage.id, passage.score, s
    
    print 'OK'


if __name__ == "__main__":

    demo_one()
    #demo_parmas()
    