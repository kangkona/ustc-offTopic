
# -*- coding: utf-8 -*-

import locale
import clinkgrammar as clg
import atexit
import sys

import re

import logging

class ParseOptions():
    def __init__(self):
        self._po = clg.parse_options_create()
        clg.parse_options_set_screen_width(self._po, 200)
    
    def __del__(self):
        print "Deleting",self.__class__
        if self._po is not None:
            clg.parse_options_delete(self._po)
            self._po = None
            
    def set_verbosity(verbosity):
        clg.parse_options_set_verbosity(self._po, verbosity)
        
    def get_verbosity(self):
        return clg.parse_options_get_verbosity(self._po)
    

class Dictionary():
    def __init__(self, lang):
        self._dict = clg.dictionary_create_lang(lang)
    
    def __del__(self):
        print "Deleting",self.__class__
        if self._dict is not None:
            clg.dictionary_delete(self._dict)
            self._dict = None
            
    def set_dictioanry_dir(self, dir):
        clg.dictionary_set_data_dir(dir)
        
class Sentence():
    
    def __init__(self, s, dictionary):
        self.s = s
        self._sent = clg.sentence_create(s, dictionary._dict)
    
    def __del__(self):
        print "Deleting",self.__class__
        if self._sent is not None:
            clg.sentence_delete(self._sent)
            #print "Calling sentence_delete will cause a segfault"
            self._sent = None

    def parse(self, parse_options):
        self.num_links = clg.sentence_parse(self._sent, parse_options._po)
        return self.num_links
    
class Linkage(object):
    def __init__(self, idx, sentence, parse_options):
        self.idx = idx
        self.sent = sentence
        self._link = clg.linkage_create(idx, sentence._sent, parse_options._po)
        
    def __del__(self):
        print "Deleting",self.__class__
        if self._link is not None:
            clg.linkage_delete(self._link)
            self._link = None
        
    def print_diagram(self):
        print clg.linkage_print_diagram(self._link)
        
    def get_diagram(self):
        return clg.linkage_print_diagram(self._link)
    
class SentenceInfo():
    #iInLow表示该句子开始字符在文章中的字符的位置，如果只分析一个句子，可将其置为0
    #iInHigh表示句子结束字符在文章中的位置，目前程序未进行使用
    #nwords表示句子中单词的个数，当前程序未对其进行赋值，与iInHigh一样，如需要该值，可在分析句子时进行赋值
    #sText表示该句子的内容
    #bGrammarChecked表示是否进行过语法检查
    #bGrammarOK表示语法检查结果是否正确
    #grammarErrors表示各错误具体信息的数组，每个数组项包括的属性：iInLow表示错误单词在该句子中开始位置的字符标号，iInHigh表示
        #错误单词在该句子中结束位置的字符标号，iWordNum表示错误单词是该句子的第几个单词，word是错误单词的字符串
    #suggestion表建议，目前基本为None
    def __init__(self,ilow,ihigh,sentstr):
        self.iInLow = ilow
        self.iInHigh = ihigh
        self.nwords = 0
        self.sText = sentstr
        self.bGrammarChecked = 0 
        self.bGrammarOK = 0
        self.vecMapOfWords = []
        self.grammarErrors = [] 
        self.suggestion = None

    def __del__(self):
        del self.grammarErrors
        del self.vecMapOfWords

    def addVecMapOfWords(self,iInLow,iInHigh,iWordNum,wordstr):
        word = {}
        word["iInLow"] = iInLow
        word["iInHigh"] = iInHigh
        word["iWordNum"] = iWordNum
        word["word"] = wordstr
        self.vecMapOfWords.append(word)

    def parse(self, dic):
        pErr = None
        szSent = self.sText

        sent = clg.sentence_create(self.sText,dic)
        self.nwords = clg.sentence_length(sent)
        
        opts = clg.parse_options_create()
        clg.parse_options_set_disjunct_cost(opts, 2)
        clg.parse_options_set_min_null_count(opts, 0)
        clg.parse_options_set_max_null_count(opts, 0)
        clg.parse_options_set_islands_ok(opts, 0)
        clg.parse_options_set_panic_mode(opts, 1)
        clg.parse_options_reset_resources(opts)
        num_linkages = clg.sentence_parse(sent, opts)

        res = (num_linkages >= 1)
        if(not res and (num_linkages == 0)):
            clg.parse_options_set_min_null_count(opts, 1)
            clg.parse_options_set_max_null_count(opts, clg.sentence_length(sent))
            clg.parse_options_set_islands_ok(opts, 1)
            clg.parse_options_reset_resources(opts)
            num_linkages = clg.sentence_parse(sent, opts)

        self.bGrammarChecked = 1
        self.bGrammarOK = res

        if(not res):
            if(num_linkages > 0):
                linkage = clg.linkage_create(0, sent, opts)
                if(linkage != None):
                    i = 0
                    iLow= 0
                    iHigh= 0
                    iOff = self.iInLow
                    totlen = len(self.sText)
                    i = 1
                    while(i<clg.sentence_length(sent) and (iLow < totlen)):
                        while((szSent[iLow] == ' ') and (iLow < totlen)):
                            iLow = iLow + 1
                        if(iLow >= totlen):
                            break
                        iHigh = iLow+len(clg.sentence_get_nth_word(sent, i))
                        self.addVecMapOfWords(iLow,iHigh,i,clg.sentence_get_nth_word(sent, i))
                        bNew = 0
                        if(not clg.sentence_nth_word_has_disjunction(sent, i)):
                            if(not pErr):
                                pErr = {}
                                bNew = 1
                            if(bNew or (pErr["iWordNum"] + 1 < i)):
                                if(not bNew):
                                    if(pErr):
                                        pErr = None
                                    pErr = {}
                                iHigh = iLow + len(clg.sentence_get_nth_word(sent, i))
                                pErr["iErrLow"] = iLow + iOff -1
                                pErr["iErrHigh"] = iHigh + iOff -1
                                if(pErr["iErrLow"] < 0):
                                    pErr["iErrLow"] = 0
                                if(pErr["iErrHigh"] < totlen-1):
                                    pErr["iErrHigh"] += 1
                                pErr["word"] = clg.sentence_get_nth_word(sent, i)
                                pErr["iWordNum"] = i
                                self.grammarErrors.append(pErr)
                                pErr = None
                            else:
                                iHigh = iLow + strlen(clg.sentence_get_nth_word(sent, i)) + iOff
                                pErr["iErrHigh"] = iHigh
                                if(pErr["iErrHigh"] < totlen-1):
                                    pErr["iErrHigh"] += 1
                                pErr["iWordNum"] = i
                        iLow += len(clg.sentence_get_nth_word(sent, i))
                        i = i + 1

                    if(len(self.grammarErrors) == 0):
                        if(pErr):
                            pErr = None
                        pErr = {}
                        pErr["iErrLow"] = self.iInLow
                        pErr["iErrHigh"] = self.iInHigh
                        pErr["iWordNum"] = -1
                        pErr["sErrorDesc"] = clg.linkage_get_violation_name(linkage)
                        if(pErr["iErrLow"] < 0):
                            pErr["iErrLow"] = 0
                        self.grammarErrors.append(pErr)
                        pErr = None
                    sErr = clg.linkage_get_violation_name(linkage)
                    clg.linkage_delete(linkage)
            else:
                if(pErr):
                    pErr = None
                pErr = {}
                pErr["iErrLow"] = self.iInLow
                pErr["iErrHigh"] = self.iInHigh
                if(pErr["iErrLow"]< 0):
                    pErr["iErrLow"] = 0
                self.grammarErrors.append(pErr)
                pErr = None
            if(pErr):
                pErr = None
        clg.parse_options_delete(opts)
        clg.sentence_delete(sent)


    def printSent(self):
        print "iInLow:",self.iInLow
        print "iInHigh:",self.iInHigh
        print "nwords:",self.nwords
        print "sText:",self.sText
        print "bGrammarChecked:",self.bGrammarChecked
        print "bGrammarOK:",self.bGrammarOK
        print "vecMapOfWords:",self.vecMapOfWords
        print "grammarErrors:",self.grammarErrors
        print "suggestion:",self.suggestion

class LinkGr():

    def __init__(self):
        if not sys.platform == 'win32':
            locale.setlocale(locale.LC_ALL,"en_US.UTF8")
        
        self.parse_options = ParseOptions()
        self.dictionary = Dictionary("en")

        self.clauseLinks = ["R","Rn","Bpj","Bsj","Mr","Mj","MX*r","RSe","QI*d","MVs","Ce","TH","Ci","THb","THi"]
        self.exlucdeLinks = ["Xp", "RW", "Wd"]
        self.validLinks = ["A", "AN", "K", "MVa", "MVp", "Op", "Os", "Ou", "J"]
    
    def __del__(self):
        print "Deleting",self.__class__
        del self.parse_options
        del self.dictionary
    
    @property
    def version(self):
        return clg.linkgrammar_get_version()

    def load(self):
        pass
    
    def unload(self):
        pass
    
    def check(self, sentence):
        result = False
        s = sentence.encode('ascii')
        sent = Sentence(s, self.dictionary)
        if sent.parse(self.parse_options) > 0:
            result = True
        
        del sent
        return result
        
    def isClause(self, sentence):
        return False
    
    def checkSummary(self, sentence):
        logging.debug('checkSummary start')
        result = ""
        s = sentence.encode('ascii')
        sent = Sentence(s, self.dictionary)
        lc = sent.parse(self.parse_options)
        logging.debug('checkSummary sent parsed')      
        if lc > 0:  
            linkage = Linkage(0, sent, self.parse_options)
            result = linkage.get_diagram()
            logging.debug('checkSummary OK')
            del linkage
        else:
            options = ParseOptions()
            clg.parse_options_set_min_null_count(options._po, 1)
            clg.parse_options_set_max_null_count(options._po, clg.sentence_length(sent._sent))
            lc = sent.parse(options)
            if lc > 0:
                linkage = Linkage(0, sent, options)
                result = linkage.get_diagram()
                logging.debug('checkSummary OK')
                del linkage
            del options
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
    
    def getGrammarErrors(self, sentence):
        s = sentence.encode('ascii')
        sent = SentenceInfo(0, 1, s)
        sent.parse(self.dictionary._dict)
        return sent.grammarErrors
        pass
    
    def getAllConnects(self, sentence):
        logging.debug('getAllConnects start')
        result = []
        options = ParseOptions()
        try:
            s = sentence.encode('ascii', 'ignore')
        except:
            return result
        sent = Sentence(s, self.dictionary)
        lc = sent.parse(options)
        logging.debug('checkSummary sent parsed')      
        if lc == 0: 
            clg.parse_options_set_min_null_count(options._po, 1)
            clg.parse_options_set_max_null_count(options._po, clg.sentence_length(sent._sent))
            lc = sent.parse(options)
        
        if lc > 0:
            linkage = Linkage(0, sent, options)
            num_links = clg.linkage_get_num_links(linkage._link)
            for i in range(num_links): 
                label = clg.linkage_get_link_label(linkage._link, i)
                lword = clg.linkage_get_link_lword(linkage._link, i)
                rword = clg.linkage_get_link_rword(linkage._link, i)
                lw = clg.sentence_get_word(sent._sent, lword)
                rw = clg.sentence_get_word(sent._sent, rword)
                result.append((label, lword, rword, lw, rw))
            del linkage  
  
        del options
        del sent
        logging.debug('getAllConnects end')
        return result
    
    def getValidConnects(self, sentence):
        conns = self.getAllConnects(sentence)
        return [conn for conn in conns if conn[0] in self.validLinks]    
    
def cleanup():
    print "Cleaning up linkgrammar..."

atexit.register(cleanup)

def demo_test():
    ck = LinkGr()
    ck.load()
    s = "The University of Science and Technology of China is useless because there is nothing to say."
    s2 = "action scenes don't equal to violent scenes."
    print ck.check(s)
    print ck.checkSummary(s)
    #print ck.complexity(s)
    print ck.check(s2)
    print ck.checkSummary(s2)
    print ck.getAllConnects(s2)
    print ck.getGrammarErrors(s2)
    print "OVER!!!"    
    
if __name__ == "__main__":
    demo_test()
    print "OVER!!!"


