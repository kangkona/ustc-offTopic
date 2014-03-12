
# -*- coding:utf-8 -*-

from clinkgrammar import *

class SentenceInfo(object):
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

    def parse(self,dic,opts):
        if(dic==None):
            print "No Dictionary!"
            return
        if(opts==None):
            print "No Options Created!"
            return

        pErr = None
        szSent = self.sText

        sent = sentence_create(self.sText,dic)
        self.nwords = sentence_length(sent)

        parse_options_set_disjunct_cost(opts, 2)
        parse_options_set_min_null_count(opts, 0)
        parse_options_set_max_null_count(opts, 0)
        parse_options_set_islands_ok(opts, 0)
        parse_options_set_panic_mode(opts, 1)
        parse_options_reset_resources(opts)
        num_linkages = sentence_parse(sent, opts)

        res = (num_linkages >= 1)
        if(not res and (num_linkages == 0)):
            parse_options_set_min_null_count(opts, 1)
            parse_options_set_max_null_count(opts, sentence_length(sent))
            parse_options_set_islands_ok(opts, 1)
            parse_options_reset_resources(opts)
            num_linkages = sentence_parse(sent, opts)

        self.bGrammarChecked = 1
        self.bGrammarOK = res

        if(not res):
            if(num_linkages > 0):
                linkage = linkage_create(0, sent, opts)
                if(linkage != None):
                    i = 0
                    iLow= 0
                    iHigh= 0
                    iOff = self.iInLow
                    totlen = len(self.sText)
                    i = 1
                    while(i<sentence_length(sent) and (iLow < totlen)):
                        while((szSent[iLow] == ' ') and (iLow < totlen)):
                            iLow = iLow + 1
                        if(iLow >= totlen):
                            break
                        iHigh = iLow+len(sentence_get_nth_word(sent, i))
                        self.addVecMapOfWords(iLow,iHigh,i,sentence_get_nth_word(sent, i))
                        bNew = 0
                        if(not sentence_nth_word_has_disjunction(sent, i)):
                            if(not pErr):
                                pErr = {}
                                bNew = 1
                            if(bNew or (pErr["iWordNum"] + 1 < i)):
                                if(not bNew):
                                    if(pErr):
                                        pErr = None
                                    pErr = {}
                                iHigh = iLow + len(sentence_get_nth_word(sent, i))
                                pErr["iErrLow"] = iLow + iOff -1
                                pErr["iErrHigh"] = iHigh + iOff -1
                                if(pErr["iErrLow"] < 0):
                                    pErr["iErrLow"] = 0
                                if(pErr["iErrHigh"] < totlen-1):
                                    pErr["iErrHigh"] += 1
                                pErr["word"] = sentence_get_nth_word(sent, i)
                                pErr["iWordNum"] = i
                                self.grammarErrors.append(pErr)
                                pErr = None
                            else:
                                iHigh = iLow + strlen(sentence_get_nth_word(sent, i)) + iOff
                                pErr["iErrHigh"] = iHigh
                                if(pErr["iErrHigh"] < totlen-1):
                                    pErr["iErrHigh"] += 1
                                pErr["iWordNum"] = i
                        iLow += len(sentence_get_nth_word(sent, i))
                        i = i + 1

                    if(len(self.grammarErrors) == 0):
                        if(pErr):
                            pErr = None
                        pErr = {}
                        pErr["iErrLow"] = self.iInLow
                        pErr["iErrHigh"] = self.iInHigh
                        pErr["iWordNum"] = -1
                        pErr["sErrorDesc"] = linkage_get_violation_name(linkage)
                        if(pErr["iErrLow"] < 0):
                            pErr["iErrLow"] = 0
                        self.grammarErrors.append(pErr)
                        pErr = None
                    sErr = linkage_get_violation_name(linkage)
                    linkage_delete(linkage)
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

        sentence_delete(sent)


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



if __name__ == "__main__":
    sent = SentenceInfo(0,1,"I am a a student!")
    dic = dictionary_create("4.0.dict", "4.0.knowledge", None, "4.0.affix")
    if (dic == None):
	print "No dictionary!"
    else:
        opts = parse_options_create()
        if (opts == None):
            print "No options created!"
	else:
            sent.parse(dic,opts)
    sent.printSent()


