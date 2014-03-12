
# -*- coding: utf-8 -*-

import pickle
import math
import re

from essay import *
from essaymodel import EssayModel
from pyrange import pyrange

from util import *

MAX_SENTENCE_LENGTH = 45

from os.path import join, dirname, abspath
exroot = dirname(abspath(__file__))
        
pvwordsFilename = join(exroot, 'rdata/pvwords.txt')
connwordsFilename = join(exroot, 'rdata/connwords.txt')
aclwordsFilename = join(exroot, 'rdata/acl.txt')

# 程序词条字典
pvwords = {}
f = open(pvwordsFilename)
lines = f.readlines()
f.close()
for line in lines:
    if line[0] == '#':
        c = line.strip()
        pvwords[c] = []
    else:
        pvwords[c].append(line.strip().replace('*', '[a-z]*'))

# 衔接词表
connwords = []
f = open(connwordsFilename)
lines = f.readlines()
f.close()
for line in lines:
    connwords.append(line.strip())
connwordsSet = set([x for x in connwords if len(x.split()) > 0])
print connwordsSet

# 学术词汇表
aclwords = []
f = open(aclwordsFilename)
lines = f.readlines()
f.close()
for line in lines:
    if len(line.strip()) > 0:
        aclwords.append(line.strip().split()[0].lower())
print aclwords

class FeatherExtractor():
    """特征提取器
    """
	
    def __init__(self, essayModel=None):
		self.model = essayModel
        
    def __calcLemmaOverlap(self, sent1, sent2):
        count = 0
        lemmas1 = [token.lemma for token in sent1.tokens 
                   if (token.pos in NounTags) or (token.pos in PronounTags)]
        lemmas2 = [token.lemma for token in sent2.tokens 
                   if (token.pos in NounTags) or (token.pos in PronounTags)]
        for lemma in lemmas1:
            if lemma in lemmas2: count += 1
        return count
    
    def __calcStemOverlap(self, sent1, sent2):
        count = 0
        stems1 = [token.stem for token in sent1.tokens 
                   if (token.pos in NounTags) or (token.pos in PronounTags)]
        stems2 = [token.stem for token in sent2.tokens 
                   if (token.pos in NounTags) or (token.pos in PronounTags)]
        for stem in stems1:
            if stem in stems2: count += 1
        return count
    
    def __wordRepetitiveRadio(self, lemma, tokens):
        count = len([t for t in tokens if t.lemma == lemma])
        if count == 0: return 0
        return count * 1.0 / len(tokens)


    def extractLangFeather(self, passage):
    	"""提取语言特征
    	"""

        langFeather = LanguageFeather()
        
        sentLens = []
        allTokens = []
        validTokens = []
        errorTokens = []
        for para in passage.paragraphs:
            for sent in para.sentences:
                allTokens.extend(sent.tokens)
                validTokens.extend([token for token in sent.tokens 
                                    if token.level > 0])
                errorTokens.extend([token for token in sent.tokens 
                                    if token.isSpellError])
                sentLens.append(sent.wordCount)
                langFeather.tokenCount += sent.tokenCount
                if not sent.canParsed or len(sent.tokens) > MAX_SENTENCE_LENGTH:
                    langFeather.sentenceErrorCount += 1
                ltc = len(sent.ltCheckResults)
                for cr in sent.ltCheckResults:
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
                langFeather.ltErrorCount = ltc
                langFeather.sentenceErrorCount += ltc
                langFeather.sentenceComplexity += sent.complexity
        passage.sentenceCount = len(sentLens)
        
        # 拼写错误
        langFeather.spellErrorCount = len(set(token.token for token in errorTokens))
                
        # 单词个数
        langFeather.wordCount = len(validTokens)
        langFeather.wordLemmaCount = len(set([token.lemma for token
                                             in validTokens]))
        langFeather.wordTypeCount = len(set([token.token for token
                                             in validTokens]))
        langFeather.wordStemCount = len(set([token.stem for token
                                             in validTokens]))
        langFeather.wordTypeRatio = langFeather.wordTypeCount * 1.0 / langFeather.tokenCount
        langFeather.indexOfGuiraud = langFeather.wordTypeCount * 1.0 / math.sqrt(langFeather.tokenCount * 1.0)
        langFeather.wordLemmaRatio = langFeather.wordLemmaCount * 1.0 / langFeather.tokenCount
#        print u"词次总数", langFeather.tokenCount
#        print langFeather.wordCount
#        print langFeather.wordLemmaCount
#        print langFeather.wordTypeCount
#        print langFeather.wordTypeRatio
#        print langFeather.indexOfGuiraud
#        print langFeather.wordLemmaRatio

        # 计算学术词汇个数及比例
        aclTokens = [token for token in validTokens
                     if token.token.lower() in aclwords 
                     or token.lemma in aclwords]
        acllemmas = [token.lemma for token in aclTokens]
        langFeather.aclWordCount = len(set(acllemmas))
        langFeather.aclWordRatio = len(acllemmas) * 1.0 / langFeather.tokenCount
        
        # 计数高低级别单词数比值
        highTokens = [token.token for token in validTokens 
                      if token.level >= 2]
        lowTokens = [token.token for token in validTokens 
                     if (token.level == 1)]
        highWordCount = len(highTokens)
        lowWordCount = len(lowTokens)
        if lowWordCount > 0:
            langFeather.highLowLevelRatio = highWordCount * 1.0 / lowWordCount
        #print langFeather.highLowLevelRatio
        
        # 单词级别数
        levels = [token.level for token in validTokens]
        langFeather.levelCount = len(set(levels))
        #print langFeather.levelCount
        
        # 各级别单词数及比例
        for l in [0, 1, 2, 3, 4]:
            c = len([token.level for token in allTokens if token.level == l])
            langFeather.wordCountInLevels.append(c)
        
        # 单词长度
        tokenLens = [len(token.token) for token in validTokens] 
        langFeather.wordLengthAverage, langFeather.wordLengthSD = stats(tokenLens)
        #print langFeather.wordLengthAverage
        #print langFeather.wordLengthSD
        
        # 非停用词词长
        noneStopWordLens = [len(token.token) for token in validTokens
                            if not token.isStopWord]
        langFeather.noneStopWordLengthAverage, langFeather.noneStopWordLengthSD = stats(noneStopWordLens)

        nounTokens = [token for token in validTokens if token.pos in NounTags]
        verbTokens = [token for token in validTokens if token.pos in VerbTags]
        adjTokens = [token for token in validTokens if token.pos in AdjectiveTags]
        if len(validTokens) > 0:
            langFeather.nounRatio = len(nounTokens) * 1.0 / len(validTokens)
            langFeather.verbRatio = len(verbTokens) * 1.0 / len(validTokens)
            langFeather.adjRatio = len(adjTokens) * 1.0 / len(validTokens)
        
        # 非停用词
        realTokens = [token for token in validTokens if token.isStopWord == False]
        langFeather.realWordCount = len(realTokens)
        langFeather.realWordLemmaCount = len(set([token.lemma for token in realTokens]))
        langFeather.realWordRatio = langFeather.realWordCount * 1.0 / langFeather.tokenCount
#        print langFeather.realWordCount
#        print langFeather.realWordRatio
#        print langFeather.readWordLemmaCount
        
        # 动名词
        langFeather.gerundCount = len([token for token in validTokens
                                           if token.pos == 'VBG'])
        langFeather.gerundRatio = langFeather.gerundCount * 1.0 / langFeather.tokenCount
#        print langFeather.gerundCount

        # 名词化词数
        nominal_count = 0
        nominals = []
        for token in validTokens:
            #if not token.nominalization:
            token.nominalization = get_nominalization(token.token.lower())
            if token.nominalization[0]:
                nominal_count += 1
                nominals.append(token.nominalization[1][1])
        langFeather.nominalizationCount = nominal_count
        langFeather.nominalizationCountUnique = len(set(nominals))
            
        
        # 句子长度
        langFeather.sentenceLengthAverage, langFeather.sentenceLengthSD = stats(sentLens)
#        print langFeather.sentenceLengthAverage
#        print langFeather.sentenceLengthSD
        sentLens.sort(reverse=True)
        top_sent_lens = sentLens[1:4]
        top_sent_len_total = 0
        for sent_len in top_sent_lens:
            top_sent_len_total += sent_len
        langFeather.top_sentence_length = top_sent_len_total / 3.0
        
        # 句子结构复杂指标
        langFeather.sentenceComplexityScale = langFeather.sentenceComplexity * 1.0 / len(sentLens)
        
        # 介词
        prepTokens = [token.token for token in validTokens if token.pos == 'IN']
        langFeather.prepositionCount = len(prepTokens)
        langFeather.prepositionRatio = langFeather.prepositionCount * 1.0 / langFeather.tokenCount
        langFeather.prepositionUse = abs(langFeather.prepositionRatio - 0.1321)
#        print u"介词列表", prepTokens
#        print u"介词个数", langFeather.prepositionCount
#        print u"介词比例", langFeather.prepositionRatio
#        print u"介词使用", langFeather.prepositionUse
        
        # 定冠词
        langFeather.definiteArticleCount = len([token for token in validTokens
                                                if token.token.lower() == 'the'])
        langFeather.definiteArticleRatio = langFeather.definiteArticleCount * 1.0 / langFeather.tokenCount
        langFeather.definiteArticleUse = abs(langFeather.definiteArticleRatio - 0.065)
        
        # 限定词
        langFeather.articleCount = len([token for token in validTokens
                                        if token.pos == 'DT'])
        langFeather.articleRatio = langFeather.articleCount * 1.0 / langFeather.tokenCount
#        print langFeather.articleCount
#        print langFeather.articleRatio
        
        # 邻近词组数
        # 不能从文章中直接提取，需要基于样本的模型来计算
        if self.model:
        	langFeather.wordCombRecurrentCount = self.model.wordCombScore(passage)
#        print u"邻近词组数", langFeather.wordCombRecurrentCount
        
        # 可读性测量
        langFeather.automatedReadabilityIndex = 0.47 * langFeather.wordLengthAverage + 0.5 * langFeather.sentenceLengthAverage - 21.43
        
        # 单词过度重复使用
        overlyUseCount = 0
        lemmaUseInfo = []
        realTokens = [token for token in validTokens if token.isStopWord == False]
        lemmaDict = {}
        for token in realTokens:
            if not token.lemma in lemmaDict:
                lemmaDict[token.lemma] = 0
            lemmaDict[token.lemma] += 1
        essayLen = len(validTokens)
        avgParaLen = essayLen / len(passage.paragraphs)
        for k, v in lemmaDict.items():
            absCount = v
            essayRatio = absCount * 1.0 / essayLen
            avgParaRatio = absCount * 1.0 / avgParaLen
            paraRatios = []
            for para in passage.paragraphs:
                paraValidTokens = []
                for sent in para.sentences:
                    paraValidTokens.extend([token for token in sent.tokens 
                                    if token.level > 0])
                paraRatios.append(self.__wordRepetitiveRadio(k, paraValidTokens))
            highestParaRatio = paraRatios[0]
            for ratio in paraRatios:
                if highestParaRatio < ratio:
                    highestParaRatio = ratio
            wordLength = len(k)
        
            lemmaUseInfo.append((k, absCount, essayRatio, avgParaRatio, highestParaRatio, wordLength))
            
            if absCount > 11:
                overlyUseCount += 1
            if essayRatio > 0.052:
                overlyUseCount += 1
            if avgParaRatio > 0.19:
                overlyUseCount += 1
            if highestParaRatio > 0.09:
                overlyUseCount += 1
            
        langFeather.lemmaUseInfo = lemmaUseInfo
        langFeather.overlyUseWordCount = overlyUseCount
        
        # Paul Nation词级
        pn_ranges = [[], [], [], []]
        pn_range = pyrange.PyRange()
        for token in allTokens:
            token.pn_range, token.word_family = pn_range.range_word(token.token)
            pn_ranges[token.pn_range].append((token.token, token.word_family))
        langFeather.pn_range_count = [len(item) for item in pn_ranges]
        
        return langFeather
    
    def extractContentFeather(self, passage):
        """提取内容特征
        """

        contentFeather = ContentFeather()

        # 程序词条数
        sentences = []
        for para in passage.paragraphs:
            for sent in para.sentences:
                sentences.append(sent.sentence.lower())
        for s in sentences:
            for k, v in pvwords.items():
                for x in v:
                    if re.match(x, s): contentFeather.proceduralVocabularyCount += 1
#        print u"程序词条数", contentFeather.proceduralVocabularyCount            
        

        if self.model:
            contentFeather.lsaScore, contentFeather.lsaSimilarity, contentFeather.lsaSimilarityAll = self.model.lsaScore(passage)
            
        # 关键词覆盖
        if self.model:
            contentFeather.keywordCover = self.model.keyWordScore(passage)
            
        return contentFeather

    def extractStructureFeather(self, passage):
    	"""提取结构特征
    	"""

        structureFeather = StructureFeather()
        
        # 衔接词
        sentences = []
        for para in passage.paragraphs:
            for sent in para.sentences:
                sentences.append(sent.sentence.lower())
        for s in sentences:
            for x in connwordsSet:
                if s.find(x) >= 0: 
                    structureFeather.connectiveCount += 1
                    continue
        structureFeather.connectiveRatio = structureFeather.connectiveCount * 1.0 / passage.lf.tokenCount
#        print u"衔接词数", structureFeather.connectiveCount 
        
        count = 0
        rpcount = 0
        for para in passage.paragraphs:
            for sent in para.sentences:
                for token in sent.tokens:
                    if token.lemma in SpecialDemonstrativePronouns:
                        count += 1
                    if token.pos in RestPronounTags:
                        rpcount += 1
        structureFeather.specialDemonstrativePronounCount = count                
        structureFeather.specialDemonstrativePronounUse = count * 1.0 / passage.lf.tokenCount
        structureFeather.restPronounCount = rpcount
        structureFeather.restPronounUse = rpcount * 1.0 / passage.lf.tokenCount
#        print u"特定指示代词数", structureFeather.specialDemonstrativePronounCount
#        print u"其余代词数", structureFeather.restPronounCount
        
        
        # 相邻论元重叠计算
        lemmaOverlapCount = 0
        sentPairCount = 0
        for para in passage.paragraphs:
            sentPairCount += (len(para.sentences) - 1)
            for index, sent in enumerate(para.sentences[:-1]):
                if self.__calcLemmaOverlap(sent, para.sentences[index+1]) > 0:
                    lemmaOverlapCount += 1
        if lemmaOverlapCount > 0:
            structureFeather.adjacentLemmaOverlapRatio = lemmaOverlapCount * 1.0 / sentPairCount
        
        # 相邻词干重叠计算
        stemOverlapCount = 0
        sentPairCount = 0
        for para in passage.paragraphs:
            sentPairCount += (len(para.sentences) - 1)
            for index, sent in enumerate(para.sentences[:-1]):
                if self.__calcStemOverlap(sent, para.sentences[index+1]) > 0:
                    stemOverlapCount += 1
        if stemOverlapCount > 0:
            structureFeather.adjacentStemOverlapRatio = stemOverlapCount * 1.0 / sentPairCount
    
        # 段落内论元重叠
        for para in passage.paragraphs:
            paraLemmaOverlapCount = 0
            for index, sent in enumerate(para.sentences[:-1]):
                for anotherIndex in range (index + 1, len(para.sentences)):
                    if self.__calcLemmaOverlap(sent, para.sentences[anotherIndex]) > 0:
                        paraLemmaOverlapCount += 1
            structureFeather.paraLemmaOverlapRatios.append(paraLemmaOverlapCount * 1.0 / len(para.sentences))
        
        # 段落内词干重叠
        for para in passage.paragraphs:
            paraStemOverlapCount = 0
            for index, sent in enumerate(para.sentences[:-1]):
                for anotherIndex in range (index + 1, len(para.sentences)):
                    if self.__calcStemOverlap(sent, para.sentences[anotherIndex]) > 0:
                        paraStemOverlapCount += 1
            structureFeather.paraStemOverlapRatios.append(paraStemOverlapCount * 1.0 / len(para.sentences))
        
        return structureFeather
    
def demo():
    pkfile = open('ustcpassages_503.pkl', 'r')
    passages = pickle.load(pkfile)
    pkfile.close()
    
    print len(passages)
    
    passages.sort(cmp=lambda x,y: cmp(x.score, y.score), reverse=True)
    
    model = EssayModel()
    model.train(passages)
    print model.triGramDicts
    
    for p in passages:
        c = model.wordCombScore(p)
        print p.score, len(p.trigrams), c, c*1.0/len(p.trigrams)
        
    extractor = FeatherExtractor(model)
    extractor.extractLangFeather(passages[-1])
    extractor.extractContentFeather(passages[-1])
    extractor.extractStructureFeather(passages[-1]) 
    
def demo_onepassage():
    pkfile = open('ustcpassages_503.pkl', 'r')
    passages = pickle.load(pkfile)
    pkfile.close()
    
    print len(passages)
        
    extractor = FeatherExtractor()
    lf = extractor.extractLangFeather(passages[-1])
    cf = extractor.extractContentFeather(passages[-1])
    sf = extractor.extractStructureFeather(passages[-1])   

    print lf.tokenCount
    print lf.wordCount
    print lf.wordTypeCount
    print lf.wordLemmaCount
    print lf.wordStemCount
    print lf.lemmaUseInfo
    print lf.aclWordCount
    print lf.aclWordRatio
    print lf.sentenceLengthAverage
    print lf.wordLengthAverage
    print lf.spellErrorCount
    print lf.sentenceErrorCount
    
def demo_get_feather():
    pkfile = open('ustcpassages_503.pkl', 'r')
    passages = pickle.load(pkfile)
    pkfile.close()
    
    print len(passages)
        
    extractor = FeatherExtractor(None)
    
    for p in passages:
        print p.id
        lf = extractor.extractLangFeather(p)
        p.lf = lf
        cf = extractor.extractContentFeather(p)
        p.cf = cf
        sf = extractor.extractStructureFeather(p)
        p.sf = sf

    for p in passages:
        print '---', p.id, '---'
        for para in p.paragraphs:
            for sent in para.sentences:
                for token in sent.tokens:
                    try:
                        if token.nominalization[0]:
                            print token.nominalization[1]
                    except:
                        pass
        
    for p in passages:
        print p.id, p.score, p.lf.gerundCount, p.lf.gerundRatio, \
            p.lf.nominalizationCount, p.lf.nominalizationCount*1.0/p.lf.tokenCount, \
            p.lf.nominalizationCountUnique, p.lf.nominalizationCountUnique * 1.0 / p.lf.tokenCount
        
    print "OVER!!!"

if __name__ == "__main__":
    print "start..."
   
    #demo_onepassage()
    #demo()
    demo_get_feather()

    print "...OVER"
