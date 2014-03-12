# -*- coding: utf-8 -*-

import pickle
import random

import json

from scipy import linalg, array, dot, mat, zeros, random
from math import *

import numpy as np
import scikits.statsmodels.api as sm

import scipy.stats.stats as scistats

from essayreader import USTCReader
from essay import EssayPassage
import essayprepare
from essaymodel import EssayModel
from extractor import FeatherExtractor

import time

import logging
LOG_FILENAME ='general_rater.log'
logging.basicConfig(filename=LOG_FILENAME,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    level=logging.DEBUG)

class GeneralEssayRater():
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
        #fs.append(passage.lf.highLowLevelRatio)
#        fs.append((passage.lf.wordCountInLevels[3] + passage.lf.wordCountInLevels[4]) * 1.0 
#                  / (passage.lf.wordCountInLevels[1] + passage.lf.wordCountInLevels[2]))
        fs.append(passage.lf.overlyUseWordCount)
        fs.append(passage.lf.aclWordCount)
        #fs.append(passage.lf.aclWordRatio)
        fs.append(passage.lf.nominalizationCountUnique)
        #fs.append(passage.lf.pn_range_count[2])
        fs.append((passage.lf.pn_range_count[2] + passage.lf.pn_range_count[3])/passage.lf.pn_range_count[1])
        fs.append(passage.lf.top_sentence_length)
        return fs
    
    def train(self, passages):
        # pre-process passage
        i = 1
        for p in passages:
            print "======================="
            print "Passage", i, p.id
            if not p.preprocessed: essayprepare.processPassage(p)
            i += 1

        self.extractor = FeatherExtractor(None)
        for p in passages:
            p.lf = self.extractor.extractLangFeather(p)
            p.cf = self.extractor.extractContentFeather(p)
            p.sf = self.extractor.extractStructureFeather(p)   
        
        # save feathers
        f = open('fs_zhang_train.txt', 'w')
        for p in passages:   
            x = self.__getFeatherList(p)       
            f.write(p.id + ' ')
            f.write(str(p.score))
            for v in x:
                f.write(' ' + str(v))
            f.write('\n')
        f.close()
        
        # generate feather vector
        endog = []
        exog = []
        for p in passages:
            score = int(p.score)
            endog.append(score)
            x = self.__getFeatherList(p)
            exog.append(x)     
        
        # train model
        endog = np.array(endog)
        exog = np.array(exog)
        
        self.gls_model = sm.GLS(endog, exog)
        results = self.gls_model.fit()
        #print results.summary()
        print results.params
    
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

    def rate(self, passage):
        # 线性预测
        if not passage.preprocessed: essayprepare.processPassage(passage)
        passage.lf = self.extractor.extractLangFeather(passage)
        passage.cf = self.extractor.extractContentFeather(passage)
        passage.sf = self.extractor.extractStructureFeather(passage)

        exog = []
        x = self.__getFeatherList(passage)
        exog.append(x)
        exog = np.array(exog)
        endog = self.gls_model.predict(exog)
        passage.rateScore = endog[0]
        passage.endogScore = endog[0]
        
        passage.filters = []
        
        # 调整分数
        filter = self.tokenCountFilter(passage)
        passage.rateScore += filter
        passage.filters.append(filter)
            
        filter = self.sentenceLengthAverageFilter(passage)
        passage.rateScore += filter
        passage.filters.append(filter)
        
        filter = self.wordLengthAverageFilter(passage)
        passage.rateScore += filter  
        passage.filters.append(filter)
        
        filter = self.aclWordCountFilter(passage)
        passage.rateScore += filter
        passage.filters.append(filter)
        
        filter = self.noneStopWordLengthAverageFilter(passage)
        passage.rateScore += filter
        passage.filters.append(filter)
        
        filter = self.nounRatioFilter(passage)  
        passage.rateScore += filter      
        passage.filters.append(filter)
        
        filter = self.verbRatioFilter(passage)
        #passage.rateScore += filter     
        passage.filters.append(filter)
        
        filter = self.adjRatioFilter(passage)
        #passage.rateScore += filter  
        passage.filters.append(filter)
        
        filter = self.posRatioFilter(passage)
        #passage.rateScore += filter
        passage.filters.append(filter)
        
        passage.rated = True
        endog[0] = passage.rateScore
        return [passage.rateScore]
    
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
                   self.noneStopWordLengthAverageFilter, self.nounRatioFilter]
        
        for filter in filters:
            filter_score = filter(passage)
            passage.rateScore += filter_score
            passage.filter_scores.append(filter_score)
        
        passage.rated = True
        return [passage.rateScore]
    

def demo():
    print "rater demo" 

    # 读训练集
    essays = USTCReader.parseUSTCFile("essayreader/r1_265.txt")
    trains = []
    for essay in essays[:]:
        passage = EssayPassage()
        passage.passage = essay.cleanContent()
        passage.title = essay.title
        passage.score = essay.score    
        passage.id = essay.id
        passage.reviewerId = essay.reviewerId
        trains.append(passage)

     # 训练打分器
    r = GeneralEssayRater()
    r.train(trains)
    
    pkfile = open('zhang_trains.pkl', 'w')
    pickle.dump(trains, pkfile)
    pkfile.close()  


    # 读测试集
    essays = USTCReader.parseUSTCFile("USTC2011Jan_Parallel_Zhang.txt")
    tests = []
    for essay in essays[:]:
        passage = EssayPassage()
        passage.passage = essay.cleanContent()
        passage.title = essay.title
        passage.score = essay.score    
        passage.id = essay.id
        tests.append(passage)

    # 打分测试
    for p in tests:
        s = r.rate(p)
        p.newscore = s[0]
        print p.id, p.score, s
        
    for p in tests:
        print p.id, p.score, p.newscore

    
    pkfile = open('zhang_tests.pkl', 'w')
    pickle.dump(tests, pkfile)
    pkfile.close()  
        
    print "demo over!!!"

def demo_pickle():
    print "rater demo_pickle" 
    
    pkfile = open('zhang_trains.pkl', 'r')
    trains = pickle.load(pkfile)
    pkfile.close()
    
     # 训练打分器
    r = GeneralEssayRater()
    r.train(trains)

    # 读测试集
    pkfile = open('zhang_tests.pkl', 'r')
    tests = pickle.load(pkfile)
    pkfile.close()

    # 打分测试
    for p in tests:
        s = r.rate(p)
        p.newscore = s[0]
        print p.id, p.score, s
        
    for p in tests:
        print p.id, p.score, p.newscore, p.lf.pn_range_count, p.lf.top_sentence_length
        
    print "demo over!!!"
    
def demo_crossvalidate():
    print "rater demo_crossvalidate"
    
    pkfile = open('zhang_trains.pkl', 'r')
    passages = pickle.load(pkfile)
    pkfile.close()

    pkfile = open('zhang_tests.pkl', 'r')
    passages.extend(pickle.load(pkfile))
    pkfile.close()

    random.shuffle(passages)    
    
    scoreEssays = {}
    for p in passages:
        if p.score < 35: p.score = 35
        label = (int(p.score) + 2) / 5 - 4
        if label < 3: 
            label = 3
            #continue
        if label > 14: label = 14
        p.label = label
        if label not in scoreEssays:
            scoreEssays[label] = []
        scoreEssays[label].append(p)


    # cross validate

    ps = [[], [], [], [], []]
    left = []

    for k, v in scoreEssays.items():
        print k
        print len(v)
        if len(v) > 5:
            s = len(v) / 5
            for i in range(5):
                ps[i].extend(v[i*s: (i+1)*s])
            left.extend(v[5*s:])
        else:
            left.extend(v)
    for j in range(len(left)):
        ps[j % 5].append(left[j])
    
    print "data sets: "
    for v in ps:
        print len(v)
    

    for i in range(5):
        trains = []
        tests = []
        
        for j in range(5):
            if i == j:
                tests.extend(ps[j])
            else:
                trains.extend(ps[j])
        
        r = GeneralEssayRater()       
        r.train(trains)
        
        for p in tests:
            s = r.rate(p)
            p.newscore = s[0]
            print p.id, p.score, s
        
    s1 = []
    s2 = []    
    for p in passages:
        if p.label < 3: continue
        s1.append(int(p.score))
        s2.append(p.newscore)
        filters = ''
        #filters = ' '.join([str(int(round(filter))) for filter in p.filter_scores])
        print p.id, p.score, p.endogScore, int(round(p.newscore)), p.score - int(round(p.newscore)), \
        filters, \
        p.lf.tokenCount, \
        p.lf.sentenceLengthAverage, p.lf.wordLengthAverage, p.lf.noneStopWordLengthAverage, \
        p.lf.nounRatio, p.lf.sentenceLengthSD, \
        p.lf.aclWordCount, p.lf.aclWordRatio, p.lf.top_sentence_length
        
    print scistats.pearsonr(s1, s2)        
        
    print "demo_crossvalidate over!!!"  
    
def demo_parmas():
    print "rater demo_parmas" 

    # 读测试集
    pkfile = open('zhang_tests.pkl', 'r')
    tests = (pickle.load(pkfile))
    pkfile.close()
    
    r = GeneralEssayRater()

    # 打分测试
    for p in tests:
        s = r.rate_by_params(p)
        p.newscore = s[0]
        print p.id, p.score, s
        
    for p in tests:
        print p.id, p.score, p.newscore
        
    print "demo_parmas over!!!"  

if __name__ == "__main__":
    
    #demo()
    #demo_pickle()
    demo_crossvalidate()
    #demo_parmas()
    