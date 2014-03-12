
# -*- coding: utf-8 -*-

import pickle
import random

import json

from scipy import linalg, array, dot, mat, zeros, random
from math import *

#import matplotlib.mlab as mlab
import numpy as np
import scikits.statsmodels.api as sm

import scipy.stats.stats as scistats

#import svmutil

from essayreader import USTCReader
from essay import EssayPassage
import essayprepare
from essaymodel import EssayModel
from extractor import FeatherExtractor

#import pca

#from pca_module import *
import time

#import zmq

import threading

import logging
LOG_FILENAME ='rater.log'
logging.basicConfig(filename=LOG_FILENAME,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    level=logging.DEBUG)

class PCAEssayRater():
    """使用主成分分析的方法对特征进行转换
    """
    
    def __init__(self):
        pass

class CollegeEssayRater():
    
    def __init__(self):
        self.models = {} # 存放所有的作文模型
        self.gls_model = None # 线性回归模型
        self.extractor = None # 特征提取器
        self.svm_model = None # SVN分类器
        pass
    
    def __trainModel(self, passages, model):
        pass
    
    def __loadModel(self, modelFilename):
        pass
       
    def __getFeatherList(self, passage):
        fs = []
        fs.append(1)
        fs.append(passage.lf.sentenceErrorCount)
        fs.append(passage.lf.spellErrorCount)
        #fs.append(passage.lf.ltErrorCount)
        fs.append(passage.lf.prepositionUse)
        fs.append(passage.lf.definiteArticleUse)
        fs.append(passage.lf.wordCombRecurrentCount)  
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
         
        fs.append(passage.cf.lsaScore)   
        #fs.append(passage.cf.proceduralVocabularyCount) 
        fs.append(passage.cf.keywordCover)
        
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
    
    def train(self, passages):
        # 预处理文章
        i = 1
        for p in passages:
            #print "Passage ", i
            # 处理文章
            if not p.preprocessed: essayprepare.processPassage(p)
            i += 1
        
        # 训练模型
        passages.sort(cmp=lambda x,y: cmp(x.score, y.score), reverse=True)
        
        model = EssayModel()
        model.train(passages)
        self.models['1'] = model
        #print model.triGramDicts
        
        # 提取特征
        self.extractor = FeatherExtractor(model)
        for p in passages:
            p.lf = self.extractor.extractLangFeather(p)
            p.cf = self.extractor.extractContentFeather(p)
            p.sf = self.extractor.extractStructureFeather(p)   
        
        # 输出特征值
        f = open('fs_train.txt', 'w')
        
        # 生成特征向量
        endog = []
        exog = []
        labels = []
        for p in passages:
            score = int(p.score)
#            if score > 90: score = 90
#            if score < 35: score = 35
            endog.append(score)
            x = self.__getFeatherList(p)
            exog.append(x)

            labels.append(p.label)
            
            f.write(p.id + ' ')
            f.write(str(p.score))
            for v in x:
                f.write(' ' + str(v))
            f.write('\n')
        
        f.close()       
        
        # SVM分类器训练
        #self.svm_model = svmutil.svm_train(labels, exog, '-c 3')
        
        # 线性回归模型训练  
        endog = np.array(endog)
        exog = np.array(exog)
#        print endog
#        print exog
        
#        self.m = np.mean(exog,axis=0)
#        print self.m
#        
#        T, P, e_var = PCA_svd(exog)   
#        print T
#        print P
#        print e_var
#        
#        r, c = P.shape
#        print r, c
#        for i in xrange(11, r):
#            for j in xrange(0, c):
#                P[i, j] = 0
#        print P
#        self.p = P
#        
#        xexog = dot(P, exog.transpose())
#        print xexog
#        print xexog.shape
#        
#        xxexog = xexog.transpose() 
        
        self.gls_model = sm.GLS(endog, exog)
        self.gls_model.fit()
#        print self.gls_model.results.params
    
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
    
    def lsaFilter(self, passage):      
        # 根据内容相似度调整
        filter = 0
        if passage.cf.lsaSimilarity < 82:
            filter = (passage.cf.lsaSimilarity - 82) * 1.5
        return filter

    def rate(self, passage):
        # 线性预测
        if not passage.preprocessed: essayprepare.processPassage(passage)
        passage.lf = self.extractor.extractLangFeather(passage)
        passage.cf = self.extractor.extractContentFeather(passage)
        passage.sf = self.extractor.extractStructureFeather(passage)
        passage.lsaScore = passage.cf.lsaScore
        passage.lsaSimilarity = passage.cf.lsaSimilarity
        passage.lsaSimilarityAll = passage.cf.lsaSimilarityAll

        exog = []
        x = self.__getFeatherList(passage)
        exog.append(x)
#        for i, xx in enumerate(x):
#            x[i] -= self.m[i]
        exog = np.array(exog)
#        xxexog = dot(self.p, exog.transpose())
#        endog = self.gls_model.predict(xxexog.transpose())
        endog = self.gls_model.predict(exog)
        passage.rateScore = endog[0]
        passage.endogScore = endog[0]
        
        # 调整分数
        passage.filter_scores = []
        filters = [self.tokenCountFilter, self.sentenceLengthAverageFilter,
                   self.wordLengthAverageFilter, self.aclWordCountFilter,
                   self.noneStopWordLengthAverageFilter, self.nounRatioFilter,
                   self.verbRatioFilter, self.adjRatioFilter,
                   self.posRatioFilter, self.lsaFilter]
        
        for filter in filters:
            filter_score = filter(passage)
            passage.rateScore += filter_score
            passage.filter_scores.append(filter_score)
        
        self.generateRateResult(passage)
        
        passage.rated = True
        endog[0] = passage.rateScore
        return [passage.rateScore]
    
    def predict(self, passages):
        # 提取特征
        for p in passages:
            if not p.preprocessed: essayprepare.processPassage(p)
            p.lf = self.extractor.extractLangFeather(p)
            p.cf = self.extractor.extractContentFeather(p)
            p.sf = self.extractor.extractStructureFeather(p)

        # 输出特征值
        f = open('fs_test.txt', 'w')
        
        # 生成特征向量
        endog = []
        exog = []
        labels = []
        for p in passages:
            score = int(p.score)
            if score < 35: score = 35
            endog.append(score)
            x = self.__getFeatherList(p)
            exog.append(x)
            labels.append(p.label)
            
            f.write(p.id + ' ')
            f.write(p.score)
            for v in x:
                f.write(' ' + str(v))
            f.write('\n')
    
        f.close()
        
        p_label, p_acc, p_val = svmutil.svm_predict(labels, exog, self.svm_model)  
        print p_label, p_acc, p_val
        
    def generateRateResult(self, passage):
        rateResult = {}
        rateResult['score'] = passage.rateScore 
        rateResult['sentences'] = []
        for para in passage.paragraphs:
            for sent in para.sentences:
                sentence = {}
                sentence['sentenceNo'] = sent.sentenceNo
                sentence['sentence'] = sent.sentence
                tokens = [token.token for token in sent.tokens]
                tags = [token.pos for token in sent.tokens]
                errorTokens = [token.token for token in sent.tokens if token.isSpellError]
                sentence['tokens'] = tokens
                sentence['tags'] = tags
                sentence['spellerror'] = errorTokens
                sentence['ltCheckResults'] = sent.ltCheckResults
                sentence['lgCheckResult'] = sent.canParsed
                sentence['complexity'] = sent.complexity
                rateResult['sentences'].append(sentence)
        passage.rateResult = rateResult


class NeuroRater():
    
    def __init__(self):
        self.models = {} # ﾴ￦ﾷￅￋ￹ￓ￐ﾵￄￗ￷ￎￄￄﾣ￐ￍ
        self.gls_model = None # ￏ￟￐ￔﾻ￘ﾹ￩ￄﾣ￐ￍ
        self.extractor = None # ￌ￘ￕ￷ￌ￡￈ﾡￆ￷
        self.svm_model = None # SVNﾷￖ￀￠ￆ￷
        pass
    
    def __trainModel(self, passages, model):
        pass
    
    def __loadModel(self, modelFilename):
        pass
       
    def __getFeatherList(self, passage):
        fs = []
        fs.append(1)
        fs.append(passage.lf.sentenceErrorCount)
        fs.append(passage.lf.spellErrorCount)
        #fs.append(passage.lf.ltErrorCount)
        fs.append(passage.lf.prepositionUse)
        fs.append(passage.lf.definiteArticleUse)
        fs.append(passage.lf.wordCombRecurrentCount)  
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
         
        #fs.append(passage.cf.lsaSimilarity)   
        #fs.append(passage.cf.proceduralVocabularyCount) 
        fs.append(passage.cf.keywordCover)
        
        fs.append(passage.sf.connectiveCount)   
        #fs.append(passage.sf.connectiveRatio)   
        #fs.append(passage.sf.specialDemonstrativePronounCount)
        #fs.append(passage.sf.specialDemonstrativePronounUse)
        #fs.append(passage.sf.restPronounCount)
        #fs.append(passage.sf.restPronounUse)        
        fs.append(passage.lf.highLowLevelRatio)
        fs.append((passage.lf.wordCountInLevels[3] + passage.lf.wordCountInLevels[4]) * 1.0 
                  / (passage.lf.wordCountInLevels[1] + passage.lf.wordCountInLevels[2]))
        fs.append(passage.lf.overlyUseWordCount)
        return fs
    
    def train(self, passages):
        # ￔﾤﾴﾦ￀￭ￎￄￕￂ
        i = 1
        for p in passages:
            #print "Passage ", i
            # ﾴﾦ￀￭ￎￄￕￂ
            if not p.preprocessed: essayprepare.processPassage(p)
            i += 1
        
        # ￑ﾵ￁ﾷￄﾣ￐ￍ
        passages.sort(cmp=lambda x,y: cmp(x.score, y.score), reverse=True)
        
        model = EssayModel()
        model.train(passages)
        self.models['1'] = model
        #print model.triGramDicts
        
        # ￌ￡￈ﾡￌ￘ￕ￷
        self.extractor = FeatherExtractor(model)
        for p in passages:
            p.lf = self.extractor.extractLangFeather(p)
            p.cf = self.extractor.extractContentFeather(p)
            p.sf = self.extractor.extractStructureFeather(p)   
        
        # ￊ￤ﾳ￶ￌ￘ￕ￷ￖﾵ
        f = open('fs_train.txt', 'w')
        
        # ￉￺ﾳ￉ￌ￘ￕ￷ￏ￲￁﾿
        endog = []
        exog = []
        labels = []
        for p in passages:
            score = int(p.score)
            #if score > 95: score = 95
            if score < 40: score = 40
            endog.append(score)
            x = self.__getFeatherList(p)
            exog.append(x)

            labels.append(p.label)
            
            f.write(p.id + ' ')
            f.write(str(p.score))
            for v in x:
                f.write(' ' + str(v))
            f.write('\n')
        
        f.close()       
        
        # SVMﾷￖ￀￠ￆ￷￑ﾵ￁ﾷ
        #self.svm_model = svmutil.svm_train(labels, exog, '-c 3')
        
        # ￏ￟￐ￔﾻ￘ﾹ￩ￄﾣ￐ￍ￑ﾵ￁ﾷ  
        endog = np.array(endog)
        exog = np.array(exog)
#        print endog
#        print exog
        
#        self.m = np.mean(exog,axis=0)
#        print self.m
#        
#        T, P, e_var = PCA_svd(exog)   
#        print T
#        print P
#        print e_var
#        
#        r, c = P.shape
#        print r, c
#        for i in xrange(11, r):
#            for j in xrange(0, c):
#                P[i, j] = 0
#        print P
#        self.p = P
#        
#        xexog = dot(P, exog.transpose())
#        print xexog
#        print xexog.shape
#        
#        xxexog = xexog.transpose() 
        
        self.gls_model = sm.GLS(endog, exog)
        self.gls_model.fit()
#        print self.gls_model.results.params

    
    def rate(self, passage):
        # ￏ￟￐ￔￔﾤﾲ￢
        if not passage.preprocessed: essayprepare.processPassage(passage)
        passage.lf = self.extractor.extractLangFeather(passage)
        passage.cf = self.extractor.extractContentFeather(passage)
        passage.sf = self.extractor.extractStructureFeather(passage)
        exog = []
        x = self.__getFeatherList(passage)
        exog.append(x)
#        for i, xx in enumerate(x):
#            x[i] -= self.m[i]
        exog = np.array(exog)
#        xxexog = dot(self.p, exog.transpose())
#        endog = self.gls_model.predict(xxexog.transpose())
        endog = self.gls_model.predict(exog)
        passage.rateScore = endog[0]
        passage.endogScore = endog[0]
        
        # ﾵ￷ￕ￻ﾷￖￊ�
        # ﾸ￹ﾾ￝ￎￄￕￂￗￖￊ�ﾵ￷ￕ￻
        if (passage.lf.tokenCount < 100):
            passage.rateScore *= 0.8
        elif passage.lf.tokenCount < 120:
            passage.rateScore *= 0.9
            
        # ﾸ￹ﾾ￝ￆﾽﾾ￹ﾾ￤ﾳﾤﾵ￷ￕ￻
        filter = 0
        slv = passage.lf.sentenceLengthAverage
        if (slv < 10):
            filter = (10 - slv) * 2
            if filter > 6: filter = 6
        elif slv > 23:
            filter = (slv - 23) * 3
            if filter > 9: filter = 9
        passage.rateScore -= filter
        
        # ﾸ￹ﾾ￝ￆﾽﾾ￹ﾴￊﾳﾤﾵ￷ￕ￻ 
        filter = 0
        wlv = passage.lf.wordLengthAverage
        if wlv < 4:
            filter = (4 - wlv) * 10
        passage.rateScore -= filter  
        
        # ﾸ￹ﾾ￝ￊﾵﾴￊￆﾽﾾ￹ﾳﾤﾶ￈ﾵ￷ￕ￻
        filter = 0
        rwlv = passage.lf.noneStopWordLengthAverage
        if rwlv < 5.5:
            filter = (5.5 - rwlv) * 10  
        passage.rateScore -= filter
        
        # ﾸ￹ﾾ￝ﾴￊ￐ￔﾱ￈￀�ﾵ￷ￕ￻
        filter = 0
        nr = passage.lf.nounRatio
        if nr < 0.2:
            filter = (0.2 - nr) * 100
        elif nr > 0.35:
            filter = (nr - 0.35) * 100
        passage.rateScore -= filter        
        
        filter = 0
        vr = passage.lf.verbRatio
        if vr < 0.1:
            filter = (0.1 - vr) * 200
        elif vr > 0.2:
            filter = (vr - 0.2) * 200
        passage.rateScore -= filter     
        
        filter = 0
        ar = passage.lf.adjRatio
        if ar < 0.045:
            filter = (0.045 - ar) * 500
        passage.rateScore -= filter  
        
        filter = 0
        badRatioCount = 0   
        offsetRatio = 0       
        if (nr < 0.2) or (nr > 0.3):
            badRatioCount += 1
        else:
            offsetRatio += abs(nr - 0.25) / 0.1
        if (vr < 0.1) or (vr > 0.2):
            badRatioCount += 1
        else:
            offsetRatio += abs(vr - 0.15) / 0.1
        if (ar < 0.06) or (ar > 0.13):
            badRatioCount += 1
        else:
            offsetRatio += abs(ar - 0.095) / 0.14
        if badRatioCount == 0:
           if offsetRatio < 0.1:
                filter = passage.rateScore * 0.05
        elif badRatioCount == 1:
            if offsetRatio > 0.6:
                filter = - passage.rateScore * 0.05
        elif badRatioCount > 1:
            filter = - passage.rateScore * 0.02 * badRatioCount * badRatioCount
        passage.rateScore += filter
        passage.offsetRatio = offsetRatio
                            
        # ﾸ￹ﾾ￝ￄￚ￈￝ￏ￠ￋￆﾶ￈ﾵ￷ￕ￻
        if (passage.cf.lsaScore > 75) and (passage.cf.lsaSimilarity > 89) and (passage.rateScore > 75):
            passage.rateScore += 5
        if ((passage.cf.lsaScore < 70) and (passage.rateScore < 70)) and (passage.cf.lsaSimilarity > 89):
            passage.rateScore -=5
        filter = 0
        if ((passage.cf.lsaSimilarity <= 80) and (passage.cf.lsaSimilarity > 60)) or ((passage.cf.lsaSimilarityAll <= 56) and (passage.cf.lsaSimilarityAll > 32)):
            filter = (15 - abs(passage.cf.lsaSimilarity - 70) / 3.0)
#            if passage.rateScore < passage.cf.lsaScore:
#                passage.rateScore = passage.cf.lsaScore
        passage.rateScore += filter
        
        self.generateRateResult(passage)
        
        passage.rated = True
        endog[0] = passage.rateScore
        return [passage.rateScore]
    
    def predict(self, passages):
        # ￌ￡￈ﾡￌ￘ￕ￷
        for p in passages:
            if not p.preprocessed: essayprepare.processPassage(p)
            p.lf = self.extractor.extractLangFeather(p)
            p.cf = self.extractor.extractContentFeather(p)
            p.sf = self.extractor.extractStructureFeather(p)

        # ￊ￤ﾳ￶ￌ￘ￕ￷ￖﾵ
        f = open('fs_test.txt', 'w')
        
        # ￉￺ﾳ￉ￌ￘ￕ￷ￏ￲￁﾿
        endog = []
        exog = []
        labels = []
        for p in passages:
            score = int(p.score)
            if score < 35: score = 35
            endog.append(score)
            x = self.__getFeatherList(p)
            exog.append(x)
            labels.append(p.label)
            
            f.write(p.id + ' ')
            f.write(p.score)
            for v in x:
                f.write(' ' + str(v))
            f.write('\n')
    
        f.close()
        
        p_label, p_acc, p_val = svmutil.svm_predict(labels, exog, self.svm_model)  
        print p_label, p_acc, p_val
        
    def generateRateResult(self, passage):
        rateResult = {}
        rateResult['score'] = passage.rateScore 
        rateResult['sentences'] = []
        for para in passage.paragraphs:
            for sent in para.sentences:
                sentence = {}
                sentence['sentenceNo'] = sent.sentenceNo
                sentence['sentence'] = sent.sentence
                tokens = [token.token for token in sent.tokens]
                tags = [token.pos for token in sent.tokens]
                errorTokens = [token.token for token in sent.tokens if token.isSpellError]
                sentence['tokens'] = tokens
                sentence['tags'] = tags
                sentence['spellerror'] = errorTokens
                sentence['ltCheckResults'] = sent.ltCheckResults
                sentence['lgCheckResult'] = sent.canParsed
                sentence['complexity'] = sent.complexity
                rateResult['sentences'].append(sentence)
        passage.rateResult = rateResult


def demo2():
    print "rater demo2" 

    # 读训练集
    essays = USTCReader.parseUSTCFile("USTC2011Jan.txt")
    trains = []
    for essay in essays:
        passage = EssayPassage()
        passage.passage = essay.cleanContent()
        passage.title = essay.title
        passage.score = essay.score    
        passage.id = essay.id
        passage.reviewerId = essay.reviewerId
        trains.append(passage)

     # 训练打分器
    r = CollegeEssayRater()
    r.train(trains)
    
    pkfile = open('USTC2011Jan.pkl', 'w')
    pickle.dump(trains, pkfile)
    pkfile.close()  
    
    exit()    

    # 读测试集
    essays = USTCReader.parseUSTCFile("USTC2011Jan-tfidf.txt")
    tests = []
    for essay in essays:
        passage = EssayPassage()
        passage.passage = essay.cleanContent()
        passage.title = essay.title
        passage.score = essay.score    
        passage.id = essay.id
        tests.append(passage)

    # 打分测试
#    for p in tests:
#        s = r.rate(p)
#        p.newscore = s[0]
#        print p.id, p.score, s
#        
#    for p in tests:
#        print p.id, p.score, p.newscore
        
    print "SVM......"
    r.predict(tests)
    
    pkfile = open('ustc_test.pkl', 'w')
    pickle.dump(tests, pkfile)
    pkfile.close()  
        
    print "demo2 over!!!"

def demo():
    print "rater demo"
    
    pkfile = open('ustcpassages_503.pkl', 'r')
    passages = pickle.load(pkfile)
    pkfile.close()

    passages = [p for p in passages if p.reviewerId in [1, 2, 5]]

    random.shuffle(passages)    
    
    scoreEssays = {}
    for p in passages:
        label = (int(p.score) + 2) / 5 - 4
        if label <= 3: 
            label = 3
            continue
        if label > 14: label = 14
        p.label = label
        if label not in scoreEssays:
            scoreEssays[label] = []
        scoreEssays[label].append(p)

    trainEssays = []
    testEssays = []
      
    for k, v in scoreEssays.items():
        print k
        print len(v)
        if len(v) > 3:
            s = len(v) * 2 / 3
            trainEssays.extend(v[:s])
            testEssays.extend(v[s:])    
    
    #trains = passages[:260]
    #tests = passages[260:]
    
    trains = trainEssays
    tests = testEssays
    
    r = CollegeEssayRater()
    
    #r.train(passages)
    #return
    
    r.train(trains)
        
    pkfile = open('rater.pkl', 'w')
    pickle.dump(r, pkfile)
    pkfile.close()
    
    for p in tests:
        s = r.rate(p)
        p.newscore = s[0]
        print p.id, p.score, s
        
    s1 = []
    s2 = []    
    for p in tests:
        s1.append(int(p.score))
        s2.append(p.newscore)
        print p.id, p.score, p.newscore, p.lsaSimilarity
        
    print scistats.pearsonr(s1, s2)        
    	
    print "demo over!!!"
    
    
def demo_crossvalidate():
    print "rater demo_crossvalidate"
    
    pkfile = open('ustcpassages_503.pkl', 'r')
    passages = pickle.load(pkfile)
    pkfile.close()

    passages = [p for p in passages if p.reviewerId in [1, 2, 5]]# 2, 3, 5]]

    random.shuffle(passages)    
    
    scoreEssays = {}
    for p in passages:
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
        
        r = CollegeEssayRater()       
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
        print p.id, p.score, p.endogScore, int(round(p.newscore)), p.score - int(round(p.newscore)), \
        p.lsaScore, p.lsaSimilarity, p.lsaSimilarityAll, p.lf.tokenCount, \
        p.lf.sentenceLengthAverage, p.lf.wordLengthAverage, p.lf.noneStopWordLengthAverage, \
        p.lf.nounRatio, p.lf.verbRatio, p.lf.adjRatio, p.lf.sentenceLengthSD, p.offsetRatio, \
        p.lf.aclWordCount, p.lf.aclWordRatio
        
    print scistats.pearsonr(s1, s2)        
        
    print "demo_crossvalidate over!!!"   
    

def demo_crossvalidate_zhang_pkl():
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
        
        r = CollegeEssayRater()       
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
        filters = ' '.join([str(int(round(filter))) for filter in p.filter_scores])
        print p.id, p.score, p.endogScore, int(round(p.newscore)), p.score - int(round(p.newscore)), \
        filters, \
        p.lf.tokenCount, \
        p.lf.sentenceLengthAverage, p.lf.wordLengthAverage, p.lf.noneStopWordLengthAverage, \
        p.lf.nounRatio, p.lf.verbRatio, p.lf.adjRatio, p.lf.sentenceLengthSD, p.offsetRatio, \
        p.lf.aclWordCount, p.lf.aclWordRatio
        
    print scistats.pearsonr(s1, s2)        
        
    print "demo_crossvalidate over!!!"   


def demo_crossvalidate_zhang():
    print "rater demo_crossvalidate_zhang"
    
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
    

    passages = []
    passages.extend(trains)
    passages.extend(tests)

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
        
        r = CollegeEssayRater()       
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
        print p.id, p.score, p.endogScore, int(round(p.newscore)), p.score - int(round(p.newscore)), \
        p.lsaScore, p.lsaSimilarity, p.lsaSimilarityAll, p.lf.tokenCount, \
        p.lf.sentenceLengthAverage, p.lf.wordLengthAverage, p.lf.noneStopWordLengthAverage, \
        p.lf.nounRatio, p.lf.verbRatio, p.lf.adjRatio, p.lf.sentenceLengthSD, p.offsetRatio, \
        p.lf.aclWordCount, p.lf.aclWordRatio
        
    print scistats.pearsonr(s1, s2)      
    
    pkfile = open('zhang_all.pkl', 'w')
    pickle.dump(passages, pkfile)
    pkfile.close()    
        
    print "demo_crossvalidate over!!!"    



def demo3():
    print "rater demo3"
    
    pkfile = open('ustc_train.pkl', 'r')
    trains = pickle.load(pkfile)
    pkfile.close()
    
    pkfile = open('ustc_test.pkl', 'r')
    tests = pickle.load(pkfile)
    pkfile.close()
    
    r = CollegeEssayRater()
    
    r.train(trains)
    
    for p in tests:
        s = r.rate(p)
        p.newscore = s[0]
        print p.id, p.score, s
        
    for p in tests:
        print p.id, p.score, p.newscore, p.label
        
    print "demo3 over!!!"
    
def demo4():
    print "rater demo4"
    
    pkfile = open('ustc_train.pkl', 'r')
    trains = pickle.load(pkfile)
    pkfile.close()
    
    pkfile = open('ustc_test.pkl', 'r')
    tests = pickle.load(pkfile)
    pkfile.close()
    
    passages = []
    passages.extend(trains)
    passages.extend(tests)
    
    random.shuffle(passages)
    
    scoreEssays = {}
    for p in passages:
        label = (int(p.score) + 2) / 5 - 4
        if label < 3: 
            label = 3
            #continue
        #if label > 14: label = 14
        p.label = label
        if label not in scoreEssays:
            scoreEssays[label] = []
        scoreEssays[label].append(p)

    trainEssays = []
    testEssays = []
      
    for k, v in scoreEssays.items():
        print k
        print len(v)
        if len(v) > 3:
            s = len(v) * 2 / 3
            trainEssays.extend(v[:s])
            testEssays.extend(v[s:])    
    
    #trains = passages[:260]
    #tests = passages[260:]
    
    trains = trainEssays
    tests = testEssays
    
    r = CollegeEssayRater()
    
    #r.train(passages)
    #return
    
    r.train(trains)
    
    #exit()
    
    pkfile = open('rater.pkl', 'w')
    pickle.dump(r, pkfile)
    pkfile.close()
    
    for p in tests:
        s = r.rate(p)
        p.newscore = s[0]
        print p.id, p.score, s
        
    s1 = []
    s2 = []    
    for p in tests:
        s1.append(int(p.score))
        s2.append(p.newscore)
        print p.id, p.score, p.newscore, p.label
        
    print scistats.pearsonr(s1, s2)
        
#    print "SVM......"
#    r.predict(tests)
        
    print "demo4 over!!!"  
    
if __name__ == "__main__":
#    demo2()
    #demo()
    #demo_crossvalidate()
    demo_crossvalidate_zhang_pkl()
    exit()

