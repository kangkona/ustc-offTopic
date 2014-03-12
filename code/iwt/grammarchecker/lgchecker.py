
# -*- coding: utf-8 -*-

import re

import logging

from linkgrammar import lp, Sentence, Linkage


class LgChecker:
    
    def __init__(self):
        self.parser = lp()
        print "Using", self.parser.version
        self.clauseLinks = ["R","Rn","Bpj","Bsj","Mr","Mj","MX*r","RSe","QI*d","MVs","Ce","TH","Ci","THb","THi"]
        

    def load(self):
        pass
    
    def unload(self):
        pass
    
    def check(self, sentence):
        result = False
        s = sentence.encode('ascii')
        sent = Sentence(s)
        if sent.parse() > 0:
            result = True
        
        del sent
        return result
        
    def isClause(self, sentence):
        return False
    
    def checkSummary(self, sentence):
        logging.debug('checkSummary start')
        result = ""
        s = sentence.encode('ascii')
        sent = Sentence(s)
        lc = sent.parse()
        logging.debug('checkSummary sent parsed')      
        if lc > 0:  
            linkage = Linkage(0, sent)
            result = linkage.get_diagram()
            logging.debug('checkSummary OK')
            del linkage
        del sent
        logging.debug('checkSummary end')
        return result
    
    def complexity(self, sentence):
        logging.debug('complexity start')
        c = 0
        r = self.checkSummary(sentence)
        for l in self.clauseLinks:
            p = "[+-]" + l + "[+-]"
            x = re.search(p, r)
            if x: c += 1
        logging.debug('complexity OK')
        return c
    
if __name__ == "__main__":
    ck = LgChecker()
    ck.load()
    s = "Grammar is useless because there is nothing to say."
    print ck.check(s)
    print ck.checkSummary(s)
    print ck.complexity(s)


