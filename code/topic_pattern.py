# -*- coding: utf-8 -*-
"""
@author: kangkona
"""
import nltk as nk
import re
import tfidf
import math
import matplotlib.pyplot as plt
from scipy import linalg
import numpy as np  

def remove_no(infile,outfile):
    fin = open(infile,"r")
    fout = open(outfile,"w")
    while True:
        line  = fin.readline()
        if not line:break
        if line == '\n':
            continue
        if re.match('^[1-9]+\.',line):
            fout.write("<start>")
        else:
            fout.write(line)

def topic_pattern_percent(infile):
    texts = open(infile).read().lower()
    essays = re.split("<start>",texts)
    print "no\tsents\ttopic\tpercents"
    results = []
    for essay in essays:
        sents_count = len(nk.sent_tokenize(essay)) - 1
#         print essay
        topic_count = 1.0/3*len(re.findall("aid",essay))+1.0/3*len(re.findall("education",essay)) + 1.0/3*len(re.findall("china",essay))
#         topic_count =1.0/2*len(re.findall("private",essay)) + 1.0/2*len(re.findall("tutoring",essay))
        if topic_count != 0:
            percent = sents_count/topic_count*1.0
            results.append(percent)
            print "%d\t%d\t%.3f\t%.2f" % (essays.index(essay)+1, sents_count,topic_count,percent)
    print "on topic:",len(results),len(essays),len(results)*1.0/len(essays)
    return results

def  format21(table):
    """归一化处理"""
    max_Freq = table[0]
    min_Freq = table[-1] 
    scale = (max_Freq - min_Freq)
    result = []
    for item in table:
        temp = (item - min_Freq)*100.0/scale
        temp = int(round(temp))
        result.append(temp)
    return result

def  linalg_draw(index_freq):
    xx = [i+1 for i in range(len(index_freq))]
    fig = plt.figure()
    bx = fig.add_subplot(211)
    bx.plot(xx,index_freq)
    bx.set_xlabel('A')
    plt.title("Aid education in China")
    ax = fig.add_subplot(212)
    ax.loglog(xx,index_freq,'o') #real data curve
    lnx = [math.log(x,math.e) for x in xx]
    lny = [math.log(y,math.e) for y in index_freq]
    mx = np.mat([lnx,[1]*len(lnx)]).T
    my = np.mat(lny).T
    (t,res,rank,s) = linalg.lstsq(mx,my)
#     print res,rank,s
    r = t[0][0]
    c = t[1][0]
    x_ = xx
    y_ = [math.e**(r*a+c) for a in lnx]
    ax.loglog(x_,y_,'r-')
    line = 'y='+str(r)+'x+'+str(c)
    print line
#     plt.text(12,8,line)
    plt.text(9,1.5,line)
    ax.set_xlabel('B')
    plt.show() 


def mainElements(infile,keywords,outfile):
    texts = open(infile).read().lower()
    essays = re.split("<start>",texts)
    fout = open(outfile,"w")
    header = "no"
    for keyword in keywords:
        header = header + "," + keyword
    fout.write(header+"\n") 
    for essay in essays:
        sents_count = len(nk.sent_tokenize(essay)) - 1
        result = str(essays.index(essay))
        for keyword in keywords:
            coverage = len(re.findall(keyword,essay))*1.0 / sents_count
            result = result + "," + str(coverage)
        result+="\n"
        fout.write(result)
    fout.close()

if __name__ == '__main__':
#     keywords_aid = ["aid","educat","china"]
    keywords_ustc = ["privat","tutor"]
    mainElements("ustc/ustc.txt",keywords_ustc,"ustc/ustc.csv")
    #     remove_no("nlptest.txt","test.txt")
#     results = topic_pattern_percent("lib/test.txt")
#     linalg_draw(sorted(results))
    