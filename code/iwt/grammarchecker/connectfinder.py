
# -*- coding: utf-8 -*-

import datetime

import linkgr

import nltk

def analyseConnects():
    print "analyse connects START..."
    lables = {}
    lwords = {}
    rwords = {}
    
    connfile = open('reutersconns.txt', 'r')
    for line in connfile.readlines():
        if line.startswith("***") or line.startswith("###"):
            continue
        items = line.split()
        lable = items[0]
        lw = items[1]
        rw = items[2]
        span = items[5]
        
        if not lable in lables:
            lables[lable] = {}
        lables[lable][(lw, rw)] = lables[lable].get((lw, rw), 0) + 1 
        if not lw in lwords:
            lwords[lw] = {}
        lwords[lw][(lw, rw)] = lwords[lw].get((lw, rw), 0) + 1 
        if not rw in rwords:
            rwords[rw] = {}
        rwords[rw][(lw, rw)] = rwords[rw].get((lw, rw), 0) + 1 
    connfile.close()
        
    # 输出
    lablefile = open('reuterslables.txt', 'w')
    lable_list = []
    for k, v in lables.items():
        lable_list.append((k, v))
    lable_list.sort(cmp=lambda a, b: cmp(a[0], b[0]))
    for k, v in lable_list:
        lablefile.write(k + '\n')
        for conn, count in v.items():
            lablefile.write(k + ' ' + str(count) + ' ' + str(conn) + '\n')
    lablefile.close()
    
    lwordfile = open('reuterslwords.txt', 'w')
    lable_list = []
    for k, v in lwords.items():
        lable_list.append((k, v))
    lable_list.sort(cmp=lambda a, b: cmp(a[0], b[0]))
    for k, v in lable_list:
        lwordfile.write(k + '\n')
        for conn, count in v.items():
            lwordfile.write(str(count) + ' ' + str(conn) + '\n')
    lwordfile.close()
    
    rwordfile = open('reutersrwords.txt', 'w')
    for k, v in rwords.items():
        rwordfile.write(k + '\n')
        for conn, count in v.items():
            rwordfile.write(str(count) + ' ' + str(conn) + '\n')
    rwordfile.close()
    
    print "analyse connects OVER!!!"

def getConnects():
    sents = nltk.corpus.reuters.sents()[:]
    
    f = open("reutersconns.txt", "w")

    ck = linkgr.LinkGr()
    ck.load()
    for idx, sent in enumerate(sents):
        n = "*** " + str(idx)
        f.write(n + '\n')
        s = ' '.join(sent)
        print "### " + s
        f.write("### " + s + '\n')
        if len(s) > 200:
            continue
        conns = ck.getAllConnects(s)
        for c in conns:
            ww = ' '.join([c[0], c[3], c[4], str(c[1]), str(c[2]), str(c[2] - c[1])])
            ww += '\n'
            f.write(ww)
    
    f.close()
    print "OVER!!!"  
    
def retrieveConnects(sents, outfile):
    f = open(outfile, "w")

    ck = linkgr.LinkGr()
    ck.load()
    for idx, sent in enumerate(sents):
        n = "*** " + str(idx)
        f.write(n + '\n')
        s = sent
        print "### " + s
        f.write("### " + s + '\n')
        if len(s) > 200:
            continue
        conns = ck.getAllConnects(s)
        for c in conns:
            ww = ' '.join([c[0], c[3], c[4], str(c[1]), str(c[2]), str(c[2] - c[1])])
            ww += '\n'
            f.write(ww)
    
    f.close()

if __name__ == "__main__":
    #getConnects()
    analyseConnects()