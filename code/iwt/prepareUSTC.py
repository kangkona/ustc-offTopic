
# -*- coding: utf-8 -*-

import pickle

import nltk

from essayreader import USTCReader
from essay import EssayPassage
import essayprepare
from extractor import FeatherExtractor

def generatePassageFeathers(passages, outFilename):
    f = open(outFilename, 'w')
    
    e = FeatherExtractor()    
    
    i = 1
    
    for p in passages:
        print "Passage ", i
        # 处理文章
        essayprepare.processPassage(p)
        # 提取语言特征    
        languageFeather = e.extractLangFeather(p)  
        p.lf = languageFeather
        # 提取结构特征  
        structureFeather = e.extractStructureFeather(p)
        p.sf = structureFeather
        
        f.write(p.id + ' ')
        f.write(str(p.score))
        f.write(' ' + str(languageFeather))
        f.write('\n')
        i += 1
    f.close()
    
    
def generateUSTCFeathers(ustcFilename, outFilename):
    essays = USTCReader.parseUSTCFile(ustcFilename)
    
    passages = []
    
    for essay in essays:
        passage = EssayPassage()
        passage.passage = essay.cleanContent()
        passage.title = essay.title
        passage.score = essay.score    
        passage.id = essay.id
        passage.reviewerId = essay.reviewerId
        passage.content = essay.content
        passages.append(passage)

    generatePassageFeathers(passages[:], outFilename)
    
    pkfile = open('ustcpassages_503_lt.pkl', 'w')
    pickle.dump(passages, pkfile)
    pkfile.close()  
    

def wordRepetitiveDemo():
    print "wordRepetitiveDemo start..."
    pkfile = open('ustcpassages_503.pkl', 'r')
    passages = pickle.load(pkfile)
    pkfile.close()
    
    f = FeatherExtractor()
    for p in passages[:]:
        lf = f.extractLangFeather(p)
        p.lf = lf
        
    f = open('wordrep.txt', 'w')
    for p in passages[:]:
        if p.lf:
            for l in p.lf.lemmaUseInfo:
                print p.id, p.score, l[0], l[1], l[2], l[3], l[4], l[5]
                s = ' '.join([str(p.id), str(p.score), str(p.lf.overlyUseWordCount), l[0], str(l[1]), str(l[2]), str(l[3]), str(l[4]), str(l[5])])
                f.write(s)
                f.write('\n')
    f.close()
        
    print "wordRepetitiveDemo over!!!"


def sentenceCheckStatsDemo():
    print "sentenceCheckStatsDemo start..."
    pkfile = open('ustcpassages_503_lt.pkl', 'r')
    passages = pickle.load(pkfile)
    pkfile.close()
    
    sentCount = 0
    errorcount = 0
    lgcorrect = 0
    lgtotal = 0
    ltcorrect = 0
    lttotal = 0
    allcorrect = 0
    
    for p in passages:
        pltc = 0
        osents = []
        for para in p.paragraphs:
            osents.extend(para.sentences)
    
        msents = []
        paras = essayprepare.para_tokenizer.tokenize(p.content)
        for para in paras:
            msents.extend(essayprepare.markedSentenceTokenize(para))
        
        if len(osents) != len(msents):
            print "sentence count not equal", p.id
            print osents
            print msents
            continue
        
        for si, os in enumerate(osents):
            ms = msents[si]
            mkerror = 1
            lgerror = 1
            lterror = 1
            ltc = 0
            
            marks = USTCReader.findMarks(ms)
            onlysperror = True
            for mark in marks:
                if not mark[0] in ['fm1', 'fm2', 'sw']:
                    onlysperror = False
                    break
            if onlysperror: mkerror = 0
            #if ms.find('[') < 0 and ms.find(']') < 0:
            #    mkerror = 0
            if os.canParsed:
                lgerror = 0
            if len(os.ltCheckResults) == 0:
                lterror = 0
            else:
                ltc = len(os.ltCheckResults)
                for cr in os.ltCheckResults:
                    if cr['ruleId'] == 'WHITESPACE_RULE':
                        ltc = ltc - 1
                    elif cr['ruleId'] == 'COMMA_PARENTHESIS_WHITESPACE':
                        ltc = ltc - 1
                    elif cr['ruleId'] == 'UPPERCASE_SENTENCE_START':
                        ltc = ltc - 1
                    elif cr['ruleId'] == 'CAN_NOT':
                        ltc = ltc - 1
                    elif cr['ruleId'] == 'EN_QUOTES':
                        ltc = ltc - 1
                if ltc == 0:
                    lterror = 0
                
            sentCount += 1
            if mkerror == 1: errorcount += 1
            if lgerror == 1: 
                lgtotal += 1
                if lgerror == mkerror:
                    lgcorrect += 1
            if lterror == 1:
                lttotal += 1
                if lterror == mkerror:
                    ltcorrect += 1
                    if lterror == lgerror:
                        allcorrect += 1
            pltc += ltc      
            #print p.id, p.score, len(os.tokens), mkerror, lgerror, lterror, ltc
#            print ms #, #ms, os.sentence
#            print os.sentence
#            if len(os.ltCheckResults) > 0:
#                for cr in os.ltCheckResults:
#                    print cr
        print p.id, p.score, pltc
    print sentCount, errorcount, lgtotal, lgcorrect, lttotal, ltcorrect, allcorrect
        
    print "sentenceCheckStatsDemo over!!!"  
    
def demo():
    pkfile = open('ustcpassages_503.pkl', 'r')
    passages = pickle.load(pkfile)
    pkfile.close()
    
    for p in passages:
        for para in p.paragraphs:
            for sent in para.sentences:
                essayprepare.retagSentence(sent)
                
    print "demo over"
    
def demo2():
    essays = USTCReader.parseUSTCFile("USTC2011Jan.txt")
    trains = []
    for essay in essays:
        passage = EssayPassage()
        passage.passage = essay.cleanContent()
        passage.title = essay.title
        passage.score = essay.score    
        passage.id = essay.id
        passage.reviewerId = essay.reviewerId
        passage.content = essay.content
        trains.append(passage)
        
#    for p in trains[:30]:
#        essayprepare.processPassage(p)
        
    for p in trains[:100]:
        # 拆分段落
        print "+++++++++++++++++++++++"
        paras = essayprepare.para_tokenizer.tokenize(p.content)
        pcount1 = len(paras)
        scount1 = 0
        for para in paras:
            sents = essayprepare.markedSentenceTokenize(para)  
#            for sent in sents:
#            	print "### ", sent
            scount1 += len(sents)
        print "-----------------------"
        paras = essayprepare.para_tokenizer.tokenize(p.passage)
        pcount2 = len(paras)
        scount2 = 0
        for para in paras:
            sents = essayprepare.sent_tokenizer.tokenize(para)  
#            for sent in sents:
#            	print "### ", sent
            scount2 += len(sents)
        if pcount1 != pcount2 or scount1 != scount2:
            print p.content
            print p.passage
        print "\n"
            	
#    for i, p in enumerate(trains[:30]):
#    	for para in p.paragraphs:
#    		for sent in para.sentences:
#    			for token in sent.tokens:
#    				if token.isSpellError:
#    					print token.token, token.candidates
#    	for m in essays[i].findMarks():
#    		if m[0] == 'fm1' or m[0] == 'fm2' or m[0] == 'sw':
#    			print m
        
#    egrammar_vp1 = "EVP1: {<NN><RB>?<VB>}"
#    parser_evp1 = nltk.RegexpParser(egrammar_vp1)    
#
#    for p in trains[:50]:
#        for para in p.paragraphs:
#            for sent in para.sentences:
#                sentence = [(token.token, token.pos) for token in sent.tokens]
#                result = parser_evp1.parse(sentence)
#                r = str(result)
#                if r.find('EVP1') > 0: print r
        
    print "demo2 over" 
    
def demo_one_sentence():
    # 文章
    passage = EssayPassage()
    passage.passage = 'I am a students.'
    passage.title = 'title'
    passage.score = 5
    passage.id = '1'
    passage.reviewerId = 3
    passage.content = 'I am a students.'
    
    # 处理文章
    essayprepare.processPassage(passage)
    
    extractor = FeatherExtractor()
    lf = extractor.extractLangFeather(passage)
    passage.lf = lf
    cf = extractor.extractContentFeather(passage)
    sf = extractor.extractStructureFeather(passage)   
    
    print 'OK'


if __name__ == "__main__":
    print "Start..."  
    #sentenceCheckStatsDemo()
    #wordRepetitiveDemo()
    #demo2()
    demo_one_sentence()
    exit() 
    
    essays = USTCReader.parseUSTCFile('USTC2011Jan.txt')
    print len(essays)
    
    essay = None
    for e in essays:
        if e.id == "0092":
            essay = e
            break  
    
    # 文章
    passage = EssayPassage()
    passage.passage = essay.cleanContent()
    passage.title = essay.title
    passage.score = essay.score
    passage.id = essay.id
    passage.reviewerId = essay.reviewerId
    passage.content = essay.content
    
    # 处理文章
    essayprepare.processPassage(passage)
    
    # 输出来看看是啥样子    
    print "PASSAGE========================================="        
    print passage
    print passage.id
    print passage.title
    print passage.score
    print passage.passage
    print len(passage.paragraphs)
    print "PARAGRAPHS---------------------------------------"
    for para in passage.paragraphs:
        print para.paragraphNo
        print para.paragraph
        for sent in para.sentences:
            print sent.sentenceNo
            print sent.paragraphSentenceNo
            print sent.sentence
            tokens = [token.token for token in sent.tokens]
            tags = [token.pos for token in sent.tokens]
            lemmas = [token.lemma for token in sent.tokens]
            stems = [token.stem for token in sent.tokens]
            levels = [token.level for token in sent.tokens]
            nos = [token.tokenNo for token in sent.tokens]
            sentNos = [token.sentenceTokenNo for token in sent.tokens]
            paraNos = [token.paragraphTokenNo for token in sent.tokens]
            errorTokens = [token.token for token in sent.tokens if token.isSpellError]
            print "SPELLERROR", errorTokens
            print tokens
            print tags
            print lemmas
            print stems
            print levels
            print sentNos
            print paraNos
            print nos
            print sent.tokenCount
            print sent.wordCount
            print sent.realWordCount
    
    print "三元词组", passage.trigrams


    e = FeatherExtractor()

    # 提取语言特征    
    languageFeather = e.extractLangFeather(passage)  
    
    print u"词次总数", languageFeather.tokenCount
    print u"单词总数", languageFeather.wordCount
    print u"词形总数", languageFeather.wordTypeCount
    print u"词元总数", languageFeather.wordLemmaCount
    
    print u"介词个数", languageFeather.prepositionCount
    print u"介词比例", languageFeather.prepositionRatio
    print u"介词使用", languageFeather.prepositionUse
    
    print u"定冠词个数", languageFeather.definiteArticleCount
    print u"定冠词比例", languageFeather.definiteArticleRatio
    print u"定冠词使用", languageFeather.definiteArticleUse
    
    # 提取结构特征  
    #structureFeather = e.extractStructureFeather(passage)
    
    generateUSTCFeathers('USTC2011Jan.txt', 'USTCFeathers_503_lt.txt')
        
    print "...OVER"