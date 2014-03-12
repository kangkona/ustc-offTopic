
# -*- coding: utf-8 -*-

import re


class CLECEssay:
    """
    CLEC文章
    """

    id = None
    title = None
    score = None
    content = None
    

def parseCLECFile2(filename):
    essays = []
    stFile = open(filename, 'r')

    essayPattern = '^<ST \d>.*<TITLE (Global shortage of Fresh Water)> <SCORE (\d+)>(.*)'
    titlePattern = '<TITLE? (.*?)>'
    scorePattern = '<SCORE (.*?)>'
    
    for line in stFile.readlines():
        if len(line) < 100:
            continue
        title = None
        score = None

        rtitle = re.search(titlePattern, line, re.IGNORECASE)
        if rtitle: title = rtitle.groups(1)[0]
        rscore = re.search(scorePattern, line, re.IGNORECASE)
        if rscore:
            score = rscore.groups(1)[0]
        if title and score:
            essay = CLECEssay()
            essay.title = title
            essay.score = score
            essay.content = line
            essay.content = re.sub('\[.*?\] ', '', essay.content)
            essay.content = re.sub('<.*?> ', '', essay.content)
            if len(essay.content.strip()) > 0:
                essays.append(essay)
            print essay.title, essay.score
#            print r.groups(1)[1]
#            print r.groups(1)[2]
#            print r.groups(1)[3]
#            print essay.content
        else:
            if len(line.strip()) > 0:
                print line
                pass
    stFile.close()
    return essays
    

def parseCLECFile(filename):
    essays = []
    stFile = open(filename, 'r')

    essayPattern = '^<ST \d>.*<TITLE (Global shortage of Fresh Water)> <SCORE (\d+)>(.*)'
    
    for line in stFile.readlines():
        r = re.match(essayPattern, line, re.IGNORECASE)
        if r:
            essay = CLECEssay()
            essay.title = r.groups(1)[0]
            essay.score = r.groups(1)[1]
            essay.content = r.groups(1)[2]
            essay.content = re.sub('\[.*?\] ', '', essay.content)
            essay.content = re.sub('<.*?\> ', '', essay.content)
            if len(essay.content.strip()) > 0:
                essays.append(essay)
            print r.groups(1)[0]
#            print r.groups(1)[1]
#            print r.groups(1)[2]
#            print r.groups(1)[3]
#            print essay.content
        else:
            if len(line.strip()) > 0:
                #print line
                pass
    stFile.close()
    return essays


if __name__ == '__main__':
    print 'Testing...'
    essays = parseCLECFile2('ST3.txt')
    print len(essays)
    
    essayDict = {}
    
    for e in essays:
        if not essayDict.has_key(e.title):
            essayDict[e.title] = []
        essayDict[e.title].append(e)
        
    print essayDict.keys()
    
    for k, v in essayDict.items():
        print len(v), k
        
    f = open('gsfw.txt', 'w+')
    for e in essayDict['Global Shortage of Fresh Water']:
        f.write(e.title + '\n')
        f.write(e.score + '\n')
        f.write(e.content + '\n')
    f.close()
    
    print 'OK'
