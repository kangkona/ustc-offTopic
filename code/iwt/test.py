
# -*- coding: utf-8 -*-

import rater

import pickle
import random

import json

from essay import EssayPassage

import time

import zmq

import threading

import logging

from rater import CollegeEssayRater

from essayreader import CLECReader

import scipy.stats.stats as scistats


def demo_crossvalidate():
    print "rater demo_crossvalidate"
    
#    essays = CLECReader.parseCLECFile2('clecst/ST3.txt')
#    print len(essays)
#    
#    essayDict = {}
#    
#    for e in essays:
#        if not essayDict.has_key(e.title):
#            essayDict[e.title] = []
#        essayDict[e.title].append(e)
#        
#    print essayDict.keys()
#    
#    for k, v in essayDict.items():
#        print len(v), k
#        
#    passages = []
#    count = 0 
#    for e in essayDict['Global Shortage of Fresh Water'][:]:  
#        count += 1     
#        newpassage = EssayPassage()
#        newpassage.passage = e.content
#        newpassage.id = str(count) 
#        newpassage.score = int(e.score)
#        newpassage.processStatus = 0
#        passages.append(newpassage)

    pkfile = open('GSFW_passages.pkl', 'r')
    passages = pickle.load(pkfile)
    pkfile.close()

    random.shuffle(passages)    
    
    scoreEssays = {}
    for p in passages:
        label = p.score
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
        s1.append(int(p.score))
        s2.append(p.newscore)
        print p.id, p.score, p.endogScore, int(round(p.newscore)), p.score - int(round(p.newscore)), \
        p.lsaScore, p.lsaSimilarity, p.lsaSimilarityAll, p.lf.tokenCount, \
        p.lf.sentenceLengthAverage, p.lf.wordLengthAverage, p.lf.noneStopWordLengthAverage, \
        p.lf.nounRatio, p.lf.verbRatio, p.lf.adjRatio, p.lf.sentenceLengthSD, p.offsetRatio, \
        p.lf.aclWordCount, p.lf.aclWordRatio
        
    print scistats.pearsonr(s1, s2)   
    
#    pkfile = open('GSFW_passages.pkl', 'w')
#    pickle.dump(passages, pkfile)
#    pkfile.close()  
        
    print "demo_crossvalidate over!!!"    
    
def simlarityTest():
    pkfile = open('rater.pkl', 'r')
    rater = pickle.load(pkfile)
    pkfile.close()
    
    essays = CLECReader.parseCLECFile2('clecst/ST3.txt')
    print len(essays)
    
    essayDict = {}
    
    for e in essays:
        if not essayDict.has_key(e.title):
            essayDict[e.title] = []
        essayDict[e.title].append(e)
        
    print essayDict.keys()
    
    for k, v in essayDict.items():
        print len(v), k
        
    passages = []
    count = 0 
    for e in essayDict['Global Shortage of Fresh Water'][:120]:  
        count += 1     
        newpassage = EssayPassage()
        newpassage.passage = e.content
        newpassage.id = str(count) 
        newpassage.score = e.score
        newpassage.processStatus = 0
        passages.append(newpassage)
        rater.rate(newpassage)

    for p in passages:
        print p.score, p.rateScore, p.lsaSimilarity, p.lsaSimilarityAll
    
    print "OK"


if __name__ == "__main__":
    print "Starting..."
    demo_crossvalidate()
    print "OK!!!"
    
