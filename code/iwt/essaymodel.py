
# -*- coding: utf-8 -*-

import pickle

from scipy import linalg, array, dot, mat, zeros
from math import *

from nltk.corpus import wordnet

from essay import *
from util import *

class EssayModel():
    """作文模型，针对每个作文试题，记录作文与试题相关的用于作文评分的数据
    """
    
    def __init__(self):
        self.triGramDicts = {}
        self.wordDict = {}
        self.keyWords = []
        pass
    
    def __calcCosine(self, vector1, vector2):
        """ related documents j and q are in the concept space by comparing the vectors :
            cosine  = ( V1 * V2 ) / ||V1|| x ||V2|| """
        return float(dot(vector1,vector2) / (linalg.norm(vector1) * linalg.norm(vector2)))

    
    def __trainWordComb(self, passages):
        """训练邻近词组模型
        """
        # 把所有的三元词组放到字典中，并统计个数
        for passage in passages:
            for triGram in passage.trigrams:
                self.triGramDicts[triGram] = self.triGramDicts.get(triGram, 0) + 1
        
        # 去掉只出现一次的三元词组
        for k, v in self.triGramDicts.items():
            if v < 2: del self.triGramDicts[k]
            
    def __getSynonyms(self, word):
        synonyms = []
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas:
                synonyms.append(lemma.name)
        return synonyms
            
    def __trainKeyWords(self, passages):
        """获得作文的关键字
        """
        tokens = []
        for p in passages:
            for para in p.paragraphs:
                for sent in para.sentences:
                    tokens.extend([token for token in sent.tokens 
                                   if ((not token.isStopWord) and (token.level > 0))])
        
        keyCounts = []
        
        lemmas = [token.lemma for token in tokens]
        for lemma in lemmas:
            synonyms = self.__getSynonyms(lemma)
            count = 0
            for l in lemmas:
                if (l == lemma) or (l in synonyms):
                    count += 1
            keyCounts.append((lemma, count))
            
        keyCounts.sort(cmp=lambda t1, t2: cmp(t1[1], t2[1]), reverse=True)
        self.keyWords = set([kc[0] for kc in keyCounts if kc[1] > 40])
        print self.keyWords
            
    def __trainLSA(self, passages):
        """训练LSA模型
        """
        
        # 找出模范作文
        goldenPassages = []
        for p in passages:
            if p.score >= 65:
                goldenPassages.append(p)

        # 从模范作文中提出词干列表，并将模范作文作为一篇文章加入词典
        tokens = []
        for p in goldenPassages:
            for para in p.paragraphs:
                for sent in para.sentences:
                    tokens.extend([token for token in sent.tokens])
        vtags = []
        vtags.extend(VerbTags)
        vtags.extend(NounTags)
        #vtags.extend(AdjectiveTags)            
        for token in tokens:
            if (token.level > 0) and (not token.isStopWord) and (token.pos in vtags):
                if token.stem in self.wordDict:
                    self.wordDict[token.stem].append(0)
                else:
                    self.wordDict[token.stem] = [0]
        
        # 将训练集中的所有文章加入词典
        for index, p in enumerate(passages):
            for para in p.paragraphs:
                for sent in para.sentences:
                    for token in sent.tokens:
		                if (token.level > 0) and (not token.isStopWord):
		                    if token.stem in self.wordDict:
		                        self.wordDict[token.stem].append(index + 1)


        # 生成词干-文档矩阵
        self.keys = [k for k in self.wordDict.keys() if len(self.wordDict[k]) > 0]
        self.keys.sort()
        #self.matrix = zeros([len(self.keys), len(passages) + 1])
        self.matrix = zeros([len(self.keys), len(passages)])
        for i, k in enumerate(self.keys):
            for d in self.wordDict[k]:
                if d > 0:
                    self.matrix[i, d-1] += 1
                
                
        # 整体数据
        rows, cols = self.matrix.shape
        self.documentTotal = cols
        self.opakiWordIDF = {}
        totalword = 0
        for k, v in self.wordDict.items():
            nq = len(set(v))
            opakiWordIDF = log((self.documentTotal-nq+0.5)/nq+0.5)
            self.opakiWordIDF[k] = opakiWordIDF
            totalword += nq
        self.avgdl = totalword * 1.0 / self.documentTotal
                
                
        # 计算权重
        #self.__tfidfTransform()
        self.__opakiTransform()
        
        # 奇异值分解
        self.u, self.sigma, self.vt = linalg.svd(self.matrix) #Sigma comes out as a list rather than a matrix

        print self.u.shape, self.sigma.shape, self.vt.shape
        print self.sigma
        self.sigma_ = [1/x for x in self.sigma]
        print self.sigma_
        
        dimensions = 120 # K
        
        ssigma = self.sigma_[:dimensions]
        
        self.sigma__ = linalg.diagsvd(ssigma, dimensions, dimensions)        
        
        # 保留U矩阵的前面的列
        self.u_k = zeros([len(self.keys), dimensions])  
              
        rows, cols= self.matrix.shape
        
        for r in xrange(0, rows):
            for c in xrange(0, dimensions):
                self.u_k[r, c] = self.matrix[r, c]

        #Dimension reduction, build SIGMA'
        for index in xrange(dimensions, len(self.sigma)):
            self.sigma[index]=0

        print linalg.diagsvd(self.sigma, len(self.matrix), len(self.vt))        

        #Reconstruct MATRIX'
        self.reconstructedMatrix= dot(dot(self.u, linalg.diagsvd(self.sigma,len(self.matrix),len(self.vt))), self.vt)

        # 完美范文
#        self.goldenEssay = []
#        for r in xrange(0, rows):
#            self.goldenEssay.append(self.matrix[r][0])
#        
#        self.goldenessayMatrix = zeros([1, len(self.goldenEssay)])
#        for i in xrange(0, len(self.goldenEssay)):
#            self.goldenessayMatrix[0, i] = self.goldenEssay[i]
#        self.goldenSpace = dot(self.goldenessayMatrix, self.u_k)
#
#        print self.goldenSpace

        for i, p in enumerate(passages):
            essayV = []
            for r in range(0, rows):
                essayV.append(self.matrix[r][i])
            essayM = array(essayV)
            essayM.reshape(1, -1)
            p.lsaSpace = dot(essayM, self.u_k) 
             

    def __getTermDocumentOccurences(self, row):
        termDocumentOccurences=0
        rows, cols = self.matrix.shape
        for n in xrange(0, cols):
            if self.matrix[row][n] > 0: #Term appears in document
                termDocumentOccurences += 1 
        return termDocumentOccurences
    
    def __tfidfTransform(self): 
        rows, cols = self.matrix.shape
        print rows, cols
        documentTotal = cols
        for col in xrange(0, cols): #For each document
            wordTotal= 0
            for row in xrange(0, rows):
                wordTotal += self.matrix[row, col]
            for row in xrange(0, rows): #For each term
                #For consistency ensure all self.matrix values are floats
                self.matrix[row][col] = float(self.matrix[row][col])
                if self.matrix[row][col] > 0:
                    termDocumentOccurences = self.__getTermDocumentOccurences(row)
                    termFrequency = self.matrix[row][col] / float(wordTotal)
                    inverseDocumentFrequency = log(documentTotal / float(termDocumentOccurences))
                    self.matrix[row][col]=termFrequency * inverseDocumentFrequency
                    
    def __opakiTransform(self):
        rows, cols = self.matrix.shape
        print rows, cols
        for col in xrange(0, cols): #For each document
            wordTotal= 0
            for row in xrange(0, rows):
                wordTotal += self.matrix[row, col]
            for row in xrange(0, rows): #For each term
                #For consistency ensure all self.matrix values are floats
                self.matrix[row][col] = float(self.matrix[row][col])
                if self.matrix[row][col] > 0:
                    termFrequency = 3 * self.matrix[row][col] / (self.matrix[row][col] + 0.5 + 1.5 * wordTotal / self.avgdl)
                    self.matrix[row][col]=termFrequency * self.opakiWordIDF[self.keys[row]]        
            
    
    def train(self, passages):
        """训练模型参数
        """
        self.passages = passages
        self.__trainKeyWords(passages[:40])
        self.__trainLSA(passages)
        self.__trainWordComb(passages[:40])
    
    def lsaScore(self, passage):
        """计算一篇文章的LSA得分
        """
        # 统计词频
        words = {}
        for para in passage.paragraphs:
            for sent in para.sentences:
                for token in sent.tokens:
                    if (token.level > 0) and (not token.isStopWord):
                            words.setdefault(token.stem, 0)
                            words[token.stem] = words[token.stem] + 1
        # 生成词干列表                    
        keyCount = []
        for i, k in enumerate(self.keys):
            if k in words:
                keyCount.append(words[k])
            else:
                keyCount.append(0)
                
        # 计算权重
        rows, cols = self.matrix.shape
        documentTotal = cols
        wordTotal = reduce(lambda x, y: x+y, keyCount)
        for i, k in enumerate(self.keys):
            # tfidf
#            termDocumentOccurences = len(self.wordDict[k])
#            termFrequency = keyCount[i] / float(wordTotal)
#            inverseDocumentFrequency = log(documentTotal / float(termDocumentOccurences))
#            keyCount[i] = termFrequency * inverseDocumentFrequency
            # opqki
            termFrequency = 3 * keyCount[i] / (keyCount[i] + 0.5 + 1.5 * wordTotal / self.avgdl)
            keyCount[i] = termFrequency * self.opakiWordIDF[k]  
            
        a = array(keyCount)
        a.reshape(1, -1)
        essaySpace = dot(a, self.u_k)
        #print essaySpace
        
        #score = self.__calcCosine(self.goldenSpace, essaySpace)

        scores = []
        for p in self.passages:
            scores.append((int(round(self.__calcCosine(essaySpace, p.lsaSpace) * 100)), p.score))
        
        scores.sort(cmp=lambda x, y: cmp(x[0], y[0]), reverse=True)
        print passage.score, scores
        
        if scores[0][0] < 100:
            scores5 = [score[1] for score in scores[:5]]
        else:
            scores5 = [score[1] for score in scores[1:6]]            
        mindiff = 100
        cscoreIndex = 0
        for i in range(0, 3):
            diff = abs(scores5[i] - scores5[i+1])
            if diff < mindiff:
                mindiff = diff
                cscoreIndex = i
        mean = (scores5[cscoreIndex] + scores5[cscoreIndex+1]) / 2
        vscores = [scores5[cscoreIndex], scores5[cscoreIndex+1]]
        mindiff = 100
        jscoreIndex = cscoreIndex
        for i in range(0, 4):
            if (i != cscoreIndex) and (i != cscoreIndex + 1):
                diff = abs(mean - scores5[i])
                if diff < mindiff:
                    mindiff = diff
                    jscoreIndex = i
        vscores.append(scores5[jscoreIndex])
        
        mean = (scores5[cscoreIndex] + scores5[cscoreIndex+1] + scores5[jscoreIndex]) / 3.0
        
        if scores[0][0] <= 100:
            sim = reduce(lambda x, y: x+y, [s[0] for s in scores[:5]])
        else:
            sim = reduce(lambda x, y: x+y, [s[0] for s in scores[1:6]])            
        sim /= 5.0
        allsim = reduce(lambda x, y: x+y, [s[0] for s in scores[:]])
        allsim = allsim * 1.0 / len(scores)
#        maxdiff = 0
#        for s in scores5:
#            diff = abs(s - mean)
#            if diff > abs(maxdiff):
#                maxdiff = s - mean
#        if scores[0][0] < 89:
#            mean += 0.1 * maxdiff * (89 - scores[0][0])
        
#        if scores[0][0] < 90:
#            mean -= 10
#        for s in scores[1:5]:
#            if s[0] < 90:
#                mean -= (90 - s[0])
            
        score = mean
        
#        score = 0
#        count = 0
#        for x, y in scores[:]:
#            if x >= 88:
#                score += y
#                count += 1
#        if count > 0:
#            score /= (count * 1.0)
#        else:
#            score = 40
        
        return score, sim, allsim
    
    def wordCombScore(self, passage):
        """计算邻近词组数
        """
        count = 0
        for triGram in passage.trigrams:
            if triGram in self.triGramDicts: 
                count += 1
        return count
    
    def keyWordScore(self, passage):
        count = 0
        lemmas = []
        for para in passage.paragraphs:
            for sent in para.sentences:
                for token in sent.tokens:
                    if (token.level > 0) and (not token.isStopWord):
                        lemmas.append(token.lemma)
#        for l in lemmas:
#            if l in self.keyWords:
#                count += 1
        for l in self.keyWords:
            if l in lemmas:
                count += 1
        return count
                            
    
if __name__ == "__main__":
    print "start..."
    
    pkfile = open('ustcpassages_503.pkl', 'r')
    passages = pickle.load(pkfile)
    pkfile.close()
    
    print len(passages)
    
    trains = passages[200:]
    trains.sort(cmp=lambda x,y: cmp(x.score, y.score), reverse=True)
    
    model = EssayModel()
    model.train(trains)
    print model.triGramDicts
    print model.keyWords
    
    for p in passages[:200]:
        c = model.wordCombScore(p)
        lsascore, sim, allsim = model.lsaScore(p)
        print p.score, len(p.trigrams), c, c*1.0/len(p.trigrams), lsascore, model.keyWordScore(p)
        
    print "...OVER"