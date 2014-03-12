
# -*- coding: utf-8 -*-

import pickle

from scipy import linalg, array, dot, mat, zeros
from math import *
from pprint import pprint

import essay


class EssayLSA():
    """简单的LSA
    用来计算文章相似"""
    
    def __init__(self, passages):
        self.matrix = array([[],])
        self.wordDict = {}
        self.passages = passages


    def __repr__(self):
        """ Make the matrix look pretty """
        stringRepresentation=""

        rows, cols = self.matrix.shape

        for row in xrange(0,rows):
            stringRepresentation += "["

            for col in xrange(0, cols):
                stringRepresentation += "%+0.2f " % self.matrix[row][col]
            stringRepresentation += "]\n"

        return stringRepresentation
    
    
    def __parse(self, passage, passageIdx):
        """读取文章，生成文章的词频列表"""
        tokens = []
        for para in passage.paragraphs:
            for sent in para.sentences:
                tokens.extend([token for token in sent.tokens])
                
        for token in tokens:
            if (token.level > 0) and (not token.isStopWord):
                if token.stem in self.wordDict:
                    self.wordDict[token.stem].append(passageIdx)
                else:
                    self.wordDict[token.stem] = [passageIdx]

                    
    def __build(self, docCount):
        self.keys = [k for k in self.wordDict.keys() if len(self.wordDict[k]) > 1]
        self.keys.sort()
        self.matrix = zeros([len(self.keys), docCount + 1])
        for i, k in enumerate(self.keys):
            for d in self.wordDict[k]:
                self.matrix[i, d] += 1
        print self.keys
               
        # Ideal Essay
        # 理想的作文内容，取X分以上的作文（不包含10分）        
        idealmin = -1
        idealmax = -1
        for index, p in enumerate(self.passages):
            if p.score >= 12:
                if idealmin < 0: idealmin = index
                if idealmax < index: idealmax = index
        
        print "ideal ", idealmin, idealmax
        
        rows, cols = self.matrix.shape        
        for row in xrange(0, rows):
            count = 0
            for col in xrange(idealmin, idealmax + 1):
                count = self.matrix[row][col] + count
            self.matrix[row][docCount] = count

    def __getTermDocumentOccurences(self,col):
        """ Find how many documents a term occurs in"""

        termDocumentOccurences=0
        
        rows, cols = self.matrix.shape

        for n in xrange(0, rows):
            if self.matrix[n][col]>0: #Term appears in document
                termDocumentOccurences+=1 
        return termDocumentOccurences
    
    
    def train(self):
        # make word-doc vector
        for index, passage in enumerate(self.passages):
            self.__parse(passage, index)
        self.__build(len(self.passages))
        
        print self.matrix.shape
        
        print self
        self.tfidfTransform()
        #print self
        
        # SVD
        self.u, self.sigma, self.vt = linalg.svd(self.matrix)
        print self.u.shape
        print len(self.sigma)
        print self.vt.shape
        
        self.sigma_1 = linalg.diagsvd(self.sigma,len(self.sigma), len(self.sigma)) ** -1
        
        print self.sigma_1
        
        print self.sigma_1 * self.sigma
        
        print linalg.diagsvd(self.sigma,len(self.sigma), len(self.sigma))
        
        # calculate doc concpets
        pass
    
    
    def score(self, passage):
        # make word-doc vector
        # calculate doc concept
        # calculate VSMs
        # get score
        pass
    
    
    def similarity(self, passage1, passage2):
        # make word-doc vector
        # calculate doc concept
        # calculate VSM
        pass


    def calcCosine(self, vector1, vector2):
        """ related documents j and q are in the concept space by comparing the vectors :
            cosine  = ( V1 * V2 ) / ||V1|| x ||V2|| """
        return float(dot(vector1,vector2) / (linalg.norm(vector1) * linalg.norm(vector2)))


    def tfidfTransform(self):    
        """ Apply TermFrequency(tf)*inverseDocumentFrequency(idf) for each matrix element. 
            This evaluates how important a word is to a document in a corpus
               
            With a document-term matrix: matrix[x][y]
            tf[x][y] = frequency of term y in document x / frequency of all terms in document x
            idf[x][y] = log( abs(total number of documents in corpus) / abs(number of documents with term y)  )
            Note: This is not the only way to calculate tf*idf
        """

        documentTotal = len(self.matrix)
        rows,cols = self.matrix.shape

        for row in xrange(0, rows): #For each document
           
            wordTotal= reduce(lambda x, y: x+y, self.matrix[row] )

            for col in xrange(0,cols): #For each term
            
                #For consistency ensure all self.matrix values are floats
                self.matrix[row][col] = float(self.matrix[row][col])

                if self.matrix[row][col]!=0:

                    termDocumentOccurences = self.__getTermDocumentOccurences(col)

                    termFrequency = self.matrix[row][col] / float(wordTotal)
                    inverseDocumentFrequency = log(abs(documentTotal / float(termDocumentOccurences)))
                    self.matrix[row][col]=termFrequency*inverseDocumentFrequency


    def lsaTransform(self,dimensions=1):
        """ Calculate SVD of objects matrix: U . SIGMA . VT = MATRIX 
            Reduce the dimension of sigma by specified factor producing sigma'. 
            Then dot product the matrices:  U . SIGMA' . VT = MATRIX'
        """
        rows,cols= self.matrix.shape

        if dimensions <= rows: #Its a valid reduction

            #Sigma comes out as a list rather than a matrix
            #u,sigma,vt = linalg.svd(self.matrix)

            #Dimension reduction, build SIGMA'
            for index in xrange(dimensions, len(self.sigma)):
                self.sigma[index]=0

            print linalg.diagsvd(self.sigma,len(self.matrix), len(self.vt))        

            #Reconstruct MATRIX'
            reconstructedMatrix= dot(dot(self.u, linalg.diagsvd(self.sigma,len(self.matrix),len(self.vt))),self.vt)

            #Save transform
            self.matrix=reconstructedMatrix

        else:
            print "dimension reduction cannot be greater than %s" % rows
            
    
    def getDocumentSpace(self):
        documents = []
        rows, cols= self.matrix.shape
        for c in xrange(0, cols):
            document = []
            for r in xrange(0, rows):
                document.append(self.matrix[r][c])
            documents.append(document)
        return documents


if __name__ == '__main__':

    print "Testing..."
    
    pkfile = open('passages.pkl', 'r')
    passages = pickle.load(pkfile)
    pkfile.close()
    print len(passages)
    
    lsa = EssayLSA(passages[:194])
    lsa.train()
    
    lsa.lsaTransform(80)
    ds = lsa.getDocumentSpace()
    
    d = ds[99]
    for index, di in enumerate(ds):
        if index < 194:
            print lsa.passages[index].score, lsa.calcCosine(d, di)
    
    print lsa.calcCosine([1, 1], [1, 1])
    
    print len(lsa.sigma)
    #print lsa
    
    print "Over"