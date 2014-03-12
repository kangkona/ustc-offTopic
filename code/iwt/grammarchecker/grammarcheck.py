
from ctypes import *
from ctypes.util import find_library

import sys,os 
import shutil
import re


class CmetGrammarCheck():
    grammardll = None
    
    def __init__(self):
        self.clauseLinks = ["R","Rn","Bpj","Bsj","Mr","Mj","MX*r","RSe","QI*d","MVs","Ce","TH","Ci","THb","THi"]
        pass
    
    def load(self):
        from os.path import join, dirname, abspath
        gcroot = dirname(abspath(__file__))        	
        dllFilename = join(gcroot, 'grammarcheck.dll')
        workPath = sys.path[0]
        enPath = os.path.join(workPath, 'en')
        if not os.path.exists(enPath):
            shutil.copytree(join(gcroot, 'data/en',), enPath, ignore=shutil.ignore_patterns('.svn'))
        dicFilename = join(enPath, '4.0.dict')
        ppFilename = join(enPath, '4.0.knowledge')
        consFilename = join(enPath, '4.0.dict')
        affixFilename = join(enPath, '4.0.affix')
        self.grammardll = cdll.LoadLibrary(dllFilename)
        self.grammardll.GrammarCheckInitialize(dicFilename, ppFilename, None, affixFilename)
        
    def unload(self):
        self.grammardll.GrammarCheckUninitialize()
    
    def check(self, sentence):
        try:
            s = sentence.encode('ascii')
        except:
            return 0
        x = self.grammardll.GrammarCheckJudge_right_or_wrong(s)
        return x
    
    def isClause(self, sentence):
        try:
            s = sentence.encode('ascii')
        except: 
            return 0
        x = self.grammardll.GrammarCheckIs_clause(s)
        return x
    
    def checkSummary(self, sentence):
        try:
            s = sentence.encode('ascii')
        except: 
            return ""
        gcr = self.grammardll.GrammarCheckResult
        gcr.restype = c_char_p
        r = gcr(s)
        
        rrs = []
        rs = r.split('\n\n')
        for x in rs:
            xs = x.split('\n')
            for i, xx in enumerate(xs):
                while len(rrs) <= i:
                    rrs.append("")
                rrs[i] = rrs[i] + xx
        r = '\n'.join(rrs)
        return r
    
    def complexity(self, sentence):
        c = 0
        r = self.checkSummary(sentence)
        for l in self.clauseLinks:
            p = "[+-]" + l + "[+-]"
            x = re.search(p, r)
            if x: c += 1
        print "complexity", c
        return c
    
if __name__ == "__main__":
    print "Start..."
    
    gc = CmetGrammarCheck()
    gc.load()
#    print gc.check("How long old are you.")
#    print gc.check("I am a student.")
    print gc.checkSummary("I think that this is a good idea.")
#    print gc.checkSummary("How long old are you.")
#    print gc.checkSummary("How long old are you doing the bad like.")
#    print gc.check("How long old are you.")
#    print gc.isClause("I think that this is a good idea.")
#    print gc.isClause("Some suppose private tutoring has benefits to teachers and children.")
#    print gc.isClause("I am a student.")
#    print gc.complexity("Some suppose private tutoring has benefits to teachers and children.")
#    print gc.complexity("I think that this is a good idea.")
#    print gc.complexity("Though children are well educated in schools, to make progress or to make up for what's missed out in the school, parents will choose to employ a private tutoring teacher to instruct their childrens in home.")
#    print gc.complexity("Some suppose private tutoring has benefits to teachers and children.")
#    print gc.complexity("I think that this is a good idea.")
#    print gc.complexity("Though children are well educated in schools, to make progress or to make up for what's missed out in the school, parents will choose to employ a private tutoring teacher to instruct their childrens in home.")
#    print gc.check("How long old are you.")
    r = gc.checkSummary("They think it will prevent the student from learning things by themselves, even the children will fail to think questions by themselves.")
    print r
#    rrs = []
#    rs = r.split('\n\n')
#    for x in rs:
#        xs = x.split('\n')
#        for i, xx in enumerate(xs):
#            while len(rrs) <= i:
#                rrs.append("")
#            rrs[i] = rrs[i] + xx
#    for rr in rrs:
#        print rr
    
    gc.unload()

    print "...OVER"