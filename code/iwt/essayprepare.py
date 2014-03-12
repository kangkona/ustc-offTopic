
# -*- coding: utf-8 -*-

import sys
import math
import pickle
import logging
import time

import urllib, urllib2 
import xml.dom
from xml.dom.minidom import parse, parseString

import nltk

from util import *
from essayreader import CLECReader
from essay import *

from os.path import join, dirname, abspath
eproot = dirname(abspath(__file__))
    	
college4DicFilename = join(eproot, 'rdata/college4.dic')
college6DicFilename = join(eproot, 'rdata/college6.dic')
schoolDicFilename = join(eproot, 'rdata/school.dic')

def profile_me(func):
    def newFunc(*args, **args2):
        t0 = time.time()
        log_str =  "@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__)
        logging.debug(log_str)
        back = func(*args, **args2)
        log_str =  "@%s, {%s} end" % (time.strftime("%X", time.localtime()), func.__name__)
        logging.debug(log_str)
        log_str =  "@%.3fs taken for {%s}" % (time.time() - t0, func.__name__)
        logging.debug(log_str)
        return back
    return newFunc

class ParagraphTokenizer():
    """
    把文章分成段落列表
    """
    
    def __init__(self):
        pass

    def tokenize(self, text):
        paras = text.split('\n')
        return [para for para in paras if len(para.strip()) > 0]

para_tokenizer = ParagraphTokenizer()
sent_tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
regex_tokenizer = nltk.tokenize.RegexpTokenizer("[\w']+")
lancasterStemmer = nltk.stem.LancasterStemmer()
porterStemmer = nltk.stem.PorterStemmer()

from nltk.corpus import treebank
train_sents = treebank.tagged_sents()[:3000]
test_sents = treebank.tagged_sents()[3000:]

train_brown = nltk.corpus.brown.tagged_sents()[0:5000]
test_brown = nltk.corpus.brown.tagged_sents()[5000:]

from nltk.tag import DefaultTagger, UnigramTagger, BigramTagger, TrigramTagger

def backoff_tagger(train_sents, tagger_classes, backoff=None):
    for cls in tagger_classes:
        backoff = cls(train_sents, backoff=backoff)
        return backoff

backoff = DefaultTagger('NN')
btagger = backoff_tagger(train_sents, [UnigramTagger, BigramTagger, 
                                      TrigramTagger], backoff=backoff)

#print tagger.evaluate(test_sents)

tnt_tagger = nltk.tag.tnt.TnT()
tnt_tagger.train(train_sents)

t_tagger_brown = nltk.tag.tnt.TnT()
t_tagger_brown.train(train_brown)

def readEssays(filename):
    infile = open(filename, 'r')
    lines = infile.readlines()
    c = len(lines) / 4
    
    essays = []
    for i in range(c):
        essay = CLECReader.CLECEssay()
        essay.title = lines[4 * i].strip()
        essay.score = int(lines[4 * i + 1].strip())
        essay.content = lines[4 * i + 2].strip()
        essays.append(essay)
        
    infile.close()
    
    return essays

def markedSentenceTokenize(paragraph):
    """切分带有标注的段落文本为句子
    """
    sents = sent_tokenizer.tokenize(paragraph)  
    sents.reverse()
    for i, sent in enumerate(sents):
        if i == len(sents) - 1: break
        if len(sent) > 0:
            lp = sent.find('[')
            rp = sent.find(']')
            if (rp > -1) and ((rp < lp) or (lp < 0)):
                # 形如[sn .]，会被切成两个句子，应连在一起
                sents[i+1] = sents[i+1] + sent
                sent = ''
        while len(sent.strip()) > 0 and sent.lstrip()[0] == '[':
            # 以[sn, ]之类开头的，应该放到上一句
            end = sent.find(']')
            if end > 0:
                sents[i+1] = sents[i+1] + ' ' + sent[:end+1]
                sent = sent[end+1:]
            else:
                break
        # 开头的引号合并
        if sent.lstrip().startswith("\"") and (sent.count("\"") % 2 == 1):
            pos = sent.find('"')
            sents[i+1] = sents[i+1] + sent[:pos+1]
            sent = sent[pos+1:]
        sents[i] = sent
    sents = [sent.strip() for sent in sents if len(sent.strip()) > 0]
    sents.reverse()
    
    # 句中的引号合并
    for i, sent in enumerate(sents):
        if i == 0: continue
        if sents[i-1].count('"') % 2 == 1 and sent.count('"') % 2 == 1:
            sents[i-1] = sents[i-1] + ' ' + sent
        sents[i] == ""
    sents = [sent.strip() for sent in sents if len(sent.strip()) > 0]

    return sents

CET6Words = []
cet6wordsFile = open(college6DicFilename)
for line in cet6wordsFile.readlines():
    CET6Words.append(line.split()[0])
cet6wordsFile.close()

CET4Words = []
cet4wordsFile = open(college4DicFilename)
for line in cet4wordsFile.readlines():
    CET4Words.append(line.split()[0])
cet4wordsFile.close()

SchoolWords = []
schoolWordsFile = open(schoolDicFilename)
for line in schoolWordsFile.readlines():
    SchoolWords.append(line.split()[0])
schoolWordsFile.close()

EnglishStops = set(nltk.corpus.stopwords.words("english"))
print EnglishStops

from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

# 拼写检查器
from spellchecker import clecspell
clecSpellChecker = clecspell.Spell()
x = clecSpellChecker.get_candidate_words('wether', 5)
if len(x) > 0:
    print "Spell Checker Loaded"
else:
    print "Spell Checker Loading Failed"
    exit()

# 语法检查器
if sys.platform == 'win32':
    #from grammarchecker import grammarcheck
    #gc = grammarcheck.CmetGrammarCheck()
    from grammarchecker import linkgr
    gc = linkgr.LinkGr()
else:
    #from grammarchecker import lgchecker
    #gc = lgchecker.LgChecker()
    from grammarchecker import linkgr
    gc = linkgr.LinkGr()
gc.load()
print gc.check("How long old are you.")
print gc.check("I am a student.")

EnglishPunct = ['.', ',', '?', '!', ';', ':', '%', '"', '\'', '-']
SpecialWords = ["'s", "'m", "'re", "ca", "n't", "'d", "'ll", "'ve", "isn", "hasn", "havn", "wouldn", "shouldn", "wasn", "aren", "doesn", "weren", "won", "needn"]


def levelToken(essayToken):
    w = essayToken.token
    lw = essayToken.token.lower()
    lemma = essayToken.lemma
    if w in EnglishPunct or essayToken.pos in NumberTags:
        essayToken.level = 0
    elif (w in SchoolWords) or (lw in SchoolWords) or (lemma in SchoolWords) or (w in SpecialWords):
        essayToken.level = 1
    elif (w in CET4Words) or (lw in CET4Words) or (lemma in CET4Words):
        essayToken.level = 2
    elif (w in CET6Words) or (lw in CET6Words) or (lemma in CET6Words):
        essayToken.level = 3
    else:
        essayToken.level = 4
        
def lemmatizeToken(essayToken):
    if essayToken.pos in VerbTags:
        essayToken.lemma = lemmatizer.lemmatize(essayToken.token, pos='v')
    elif (essayToken.pos in NounTags) or (essayToken.pos == 'Unk'):
        essayToken.lemma = lemmatizer.lemmatize(essayToken.token, pos='n')
    elif essayToken.pos in AdjectiveTags:
        essayToken.lemma = lemmatizer.lemmatize(essayToken.token, pos='a')  
    elif essayToken.pos in AdverbTags:
        essayToken.lemma = lemmatizer.lemmatize(essayToken.token, pos='r')   
    else:
        essayToken.lemma = essayToken.token      
        
def stemToken(essayToken):
    essayToken.stem = porterStemmer.stem(essayToken.token)
        
def checkStopWord(essayToken):
    w = essayToken.token
    lw = essayToken.token.lower()
    lemma = essayToken.lemma
    essayToken.isStopWord = (w in EnglishStops) or (lemma in EnglishStops) or (w in SpecialWords)

@profile_me    
def checkSpell(essayToken):
    if essayToken.level == 4:
        #checkResult = clecSpellChecker.check_word(essayToken.token.lower())
        try:
            #word = essayToken.token.encode('ascii')
            #checkResult = clecSpellChecker.check(essayToken.token.encode('ascii'))
            checkResult = clecSpellChecker.check_word(essayToken.token.lower())
            if not checkResult:
                if "-" in essayToken.token:
                    words = essayToken.token.split("-")
                    for w in words:
                        checkResult = clecSpellChecker.check_word(w.lower())
                        if not checkResult:
                            essayToken.candidates = clecSpellChecker.get_candidate_words(essayToken.w.lower(), 3)
                            break
                else:
                    essayToken.candidates = clecSpellChecker.get_candidate_words(essayToken.token.lower(), 3)
            essayToken.isSpellError = not checkResult
            if essayToken.isSpellError: 
                essayToken.level = -2 # 错误词的level可以换成其建议词的level
                print essayToken.token
        except:
            print essayToken.token

@profile_me            
def checkNominalization(essayToken):
    if essayToken.isStopWord or essayToken.isSpellError or not essayToken.pos in NounTags:
        return
    essayToken.nominalization = get_nominalization(essayToken.token.lower())
            
def parseSentence(essaySentence):
    logging.debug("parseSentence start.")
    parsed = gc.check(essaySentence.sentence)
    if not parsed:
        logging.debug("sent not parsed")
        spe_count = 0
        for token in essaySentence.tokens:
            if token.isSpellError:
                spe_count += 1
        if spe_count == 1:
            s = essaySentence.sentence
            for token in essaySentence.tokens:
                if token.isSpellError:
                    print token.token
                    s = s.replace(token.token, token.candidates[0][0])
            parsed = gc.check(s)
    essaySentence.canParsed = parsed
    logging.debug("parseSentence end.")

@profile_me
def checkSentence(essaySentence):
    """Check the sentence usage errors using LanguageTool.
    """
    logging.debug("checkSentence start.")
    essaySentence.ltCheckResults = []
    params = (('language', 'en'), ('text', essaySentence.sentence))
    req = 'http://localhost:8081/?' + urllib.urlencode(params)
    try:
        rep = urllib2.urlopen(req)
    except:
        logging.error("checkSentence error")
        return
    repstr = rep.read()
    dom = parseString(repstr)
    errors = dom.getElementsByTagName('error')
    for error in errors:
        checkResult ={}
        checkResult['fromy'] = error.attributes["fromy"].nodeValue
        checkResult['fromx'] = error.attributes["fromx"].nodeValue
        checkResult['toy'] = error.attributes["toy"].nodeValue
        checkResult['tox'] = error.attributes["tox"].nodeValue
        checkResult['ruleId'] = error.attributes["ruleId"].nodeValue
        checkResult['msg'] = error.attributes["msg"].nodeValue
        checkResult['replacements'] = error.attributes["replacements"].nodeValue
        checkResult['context'] = error.attributes["context"].nodeValue
        checkResult['contextoffset'] = error.attributes["contextoffset"].nodeValue
        checkResult['errorlength'] = error.attributes["errorlength"].nodeValue
        checkResult['errorbefore'] = checkResult['context'][:int(checkResult['contextoffset'])]
        checkResult['errorme'] = checkResult['context'][int(checkResult['contextoffset']):int(checkResult['contextoffset'])+int(checkResult['errorlength'])]
        checkResult['errorafter'] = checkResult['context'][int(checkResult['contextoffset'])+int(checkResult['errorlength']):]
        if not checkResult['ruleId'] in IgnoredLtRuleIds:
            essaySentence.ltCheckResults.append(checkResult)
    logging.debug("checkSentence end.")
    
@profile_me
def checkSentenceProblem(essaySentence):
    """Check the grammar problems using Link Grammar.
    """
    logging.debug("checkSentenceProblem start.")
    essaySentence.lgCheckResults = []
    errors = gc.getGrammarErrors(essaySentence.sentence)
    
    checkResult = {}
    last_error_word = -4
    for error in errors:
        if error['iWordNum'] > -1:
            if (error['iWordNum'] - last_error_word) == 1:
                tox = error['iErrHigh']
                if tox > len(essaySentence.sentence):
                    tox = len(essaySentence.sentence)
                checkResult['tox'] = tox
                checkResult['errorme'] = essaySentence.sentence[checkResult['fromx']:checkResult['tox']]
                checkResult['errorlength'] = len(checkResult['errorme'])
                last_error_word = error['iWordNum']
            else:
                checkResult = {}
                essaySentence.lgCheckResults.append(checkResult)
                fromx = error['iErrLow']
                while essaySentence.sentence[fromx] == ' ':
                    fromx += 1
                tox = error['iErrHigh']
                if tox > len(essaySentence.sentence):
                    tox = len(essaySentence.sentence)
                checkResult['fromx'] = fromx
                checkResult['tox'] = tox
                print checkResult['fromx'], checkResult['tox']
                checkResult['errorme'] = essaySentence.sentence[int(checkResult['fromx']):int(checkResult['tox'])]
                if len(checkResult['errorme']) > 50:
                    checkResult['errorme'] = checkResult['errorme'][:50]
                checkResult['errorlength'] = len(checkResult['errorme'])
                checkResult['replacements'] = ""
                checkResult['msg'] = ""
                checkResult['context'] = ""
                last_error_word = error['iWordNum']
        else:
            # 句子有问题
            checkResult = {}
            essaySentence.lgCheckResults.append(checkResult)
            checkResult['fromx'] = 0
            checkResult['tox'] = 0
            print checkResult['fromx'], checkResult['tox']
            checkResult['errorme'] = ""
            checkResult['errorlength'] = len(checkResult['errorme'])
            checkResult['replacements'] = ""
            checkResult['msg'] = ""
            checkResult['context'] = ""
            last_error_word = error['iWordNum']

    logging.debug("checkSentenceProblem end.")

def getTrigrams(sent):
    """生成三元词组列表
    """
    grams = []
    for i in range(len(sent.tokens) - 3):
        tokens = sent.tokens[i:i+3]
        if (tokens[0].level > 0) and (tokens[1].level > 0) and (tokens[2].level > 0):
            gram = [token.lemma for token in tokens]
            triGram = TriGram(gram[0], gram[1], gram[2])
            grams.append(triGram)
    return grams

@profile_me
def retagSentence(sent):
    logging.debug("retagSentence start.")
    errorTokens = [token for token in sent.tokens if token.isSpellError]
    if len(errorTokens) > 0:
        s = sent.sentence
        for token in errorTokens:
            if len(token.candidates) > 0:
                s = s.replace(token.token, token.candidates[0][0])
        tokens = nltk.wordpunct_tokenize(s)
        if len(tokens) != len(sent.tokens): return
        if tokens[0] != 'I':
            tokens[0] = tokens[0].lower()
        tokenTags = tnt_tagger.tag(tokens)
        bTags = t_tagger_brown.tag(tokens)
        print tokenTags
        for i, t in enumerate(sent.tokens):
            if t.isSpellError:
                print "UUUUUU", t.pos, t.token
                if t.pos != tokenTags[i][1]:
                    print "TTTTTT", t.pos, tokenTags[i][1]
                    t.pos = tokenTags[i][1]
                elif t.pos != bTags[i][1]:
                    print "BBBBBB", t.pos, bTags[i][1]
                    t.pos = bTags[i][1]
    logging.debug("retagSentence end.")

def processPassage(passage, fn_progress=None):
    logging.debug("process passage start...")
    if passage.preprocessed: return
    # 转换类别
    label = (int(passage.score) + 2) / 5 - 4
    if label < 3: label = 3
    if label > 14: label = 14
    passage.label = label
    
    # 替换非英文字符
    text = passage.passage
    text = text.replace(u'，', ',')
    text = text.replace(u'。', '.')
    text = text.replace(u'；', ';')
    text = text.replace(u'？', '?')
    text = text.replace(u'！', '!')
    text = text.replace(u'、', ',')
    text = text.replace(u'——', '-')
    text = text.replace(u'—', '-')
    text = text.replace(u'……', '...')
    text = text.replace(u'’', "'")
    text = text.replace(u'‘', "'")
    text = text.replace(u'“', '"')
    text = text.replace(u'”', '"')
    # 标点后增加空格
    text = text.replace('?', '? ')
    text = text.replace('!', '! ')
    for i in range(len(text)):
        if i > 0 and text[i] == '.' and i+1<len(text) and text[i+1] != ' ' and (ord(text[i-1]) < ord('A') or ord(text[i-1]) > ord('Z')):
            text = text.replace(text[i], '. ')    
        if not ord(text[i]) <= 0xff:
            text = text.replace(text[i], NoAsciiReplacer)
    passage.passage = text
    
    # 拆分段落
    paras = para_tokenizer.tokenize(passage.passage)
    paraNo = 1
    for para in paras:
        paragraph = EssayParagraph(paraNo, para)
        passage.paragraphs.append(paragraph)
        paraNo += 1
    logging.debug("split paragraphs end.")
    
    # 对每一段落拆分句子
    sentNo = 1
    for para in passage.paragraphs:
        sents = sent_tokenizer.tokenize(para.paragraph)  
        paraSentNo = 1   
        for sent in sents: 
            sentence = EssaySentence(sentNo)
            sentence.sentence = sent.strip()
            sentence.paragraphSentenceNo = paraSentNo
            para.sentences.append(sentence)
            sentNo += 1
            paraSentNo += 1
    logging.debug("split sentences end.")
    sentCount = sentNo - 1

    # 对每一段落，每一句子，拆分词次
    tokenNo = 1
    for para in passage.paragraphs:
        paraTokenNo = 1
        logging.debug("process paragraph %d ..." % para.paragraphNo)
        for sent in para.sentences:
            logging.debug("process sentence start %d ..." % sent.sentenceNo)            
            tokens = nltk.wordpunct_tokenize(sent.sentence)
            logging.debug("sentence tokenized")   
#            if tokens[0] != 'I':
#                tokens[0] = tokens[0].lower()
            tokenTags = tnt_tagger.tag(tokens)
            logging.debug("after tnt_tagger") 
            bTags = t_tagger_brown.tag(tokens)
            logging.debug("after brown_tagger") 
            sentTokenNo = 1
            ti = 0
            logging.debug("process every token start ...")    
            token_start = 0          
            for (token, tag) in tokenTags:
                essayToken = EssayToken(token)
                essayToken.tokenNo = tokenNo
                # 确定这个词在句子原文中的精确位置
                start = sent.sentence.find(token, token_start)
                if start < 0:
                    logging.error('cannot find token %s in sentence %s' % (token, sent.sentence))
                    essayToken.startAt = -1
                    essayToken.endAt = -1
                else:
                    essayToken.startAt = start
                    essayToken.endAt = start + len(token)
                    token_start = start + len(token)

                essayToken.paragraphTokenNo = paraTokenNo
                essayToken.sentenceTokenNo = sentTokenNo
                essayToken.pos = tag
                if essayToken.pos == 'Unk':
                    essayToken.pos = bTags[ti][1]
                if essayToken.pos == 'Unk':
                    if essayToken.token[-2:] == 'ed':
                        essayToken.pos = 'VBD'
                # 取词元
                lemmatizeToken(essayToken)
                # 取词干
                stemToken(essayToken)
                # 标词的级别
                levelToken(essayToken)
                # 是否停用词
                checkStopWord(essayToken)
                # 拼写检查
                checkSpell(essayToken)
                sent.tokens.append(essayToken)
                # 检查是否名词化
                checkNominalization(essayToken)
                if essayToken.level != 0: 
                    sent.wordCount += 1
                    if (not essayToken.isStopWord): 
                        sent.realWordCount += 1
                        if essayToken.lemma in passage.realWordFreq:
                            passage.realWordFreq[essayToken.lemma] = 1 + passage.realWordFreq[essayToken.lemma]
                        else:
                            passage.realWordFreq[essayToken.lemma] = 1
                sentTokenNo += 1
                paraTokenNo += 1
                tokenNo += 1
                ti += 1
            logging.debug("process every token end ...")  

            sent.tokenCount = len(tokens)
            spell_error_count = 0
            for token in sent.tokens:
                if token.isSpellError:
                    spell_error_count += 1  

            passage.trigrams.extend(getTrigrams(sent))
            
            # 用Link Grammar分析句子
            parseSentence(sent)
            # 用LanguageTool检查句子中的错误
            checkSentence(sent)
            # 用Link Grammar检查句子中的错误
            checkSentenceProblem(sent)
            #  句子的复杂性
            logging.debug('get complexity ...')
            if sent.canParsed:
                sent.complexity = gc.complexity(sent.sentence)
            else:
                if spell_error_count < 2:
                    sent.complexity = gc.complexity(sent.sentence) - 1
                else:
                    sent.complexity = 0
            if sent.complexity < 0:
                sent.complexity = 0     
            logging.debug('get complexity end')  
            
            sent.links = []
            if spell_error_count < 2:
                sent.links = gc.getValidConnects(sent.sentence)        

            retagSentence(sent)    

            logging.debug("process sentence end %d ..." % sent.sentenceNo)
            passage.processStatus = sent.sentenceNo * 100 / sentCount
            print "*********** ", passage.processStatus
            if fn_progress:
                fn_progress(passage.processStatus)
    passage.preprocessed = True
    logging.debug("process passage end.")
    
def demo_passage():
    
    #content = """That was 90% of commands I use every day. I suggest you to learn no more than one or two new command per day. After two to three weeks you’ll start to feel the power of vim in your hands. Learning Vim is more a matter of training than plain memorization. Fortunately vim comes with some very good tools and an excellent documentation. Run vimtutor until you are familiar with most basic commands. Also, you should read carefully this page: :help usr_02.txt. Then, you will learn about !, folds, registers, the plugins and many other features. Learn vim like you’d learn piano and all should be fine."""
    content = "I am a studet. It's no doubt that. A family teacher can help you to study welll. He can help you to check your work and. find out the woring in your homework. Then, you can spend more time in the knowledge where you are weak in.\n"
    content2 = "Surrounded by more and more action movies or TV dramas with action scenes, peolple have found out that the scenes resullt in the rising crime rate of violence. As a result, they call on to let the scenes to be banned.I support the claim. Scenes such as kungfu or boxing are imortant elements of action movies, which are used to attract the audience, and get tremendous profits.As a result, lots of kungfu stars and beefcake stars become famous, such as Li Xiaolong, Cheng Long, and also foreign stars. The beauty of boxing fascinates a great many of people, especially teenagers. They learn boxing, and they learn to play nunchucks as Li Xiaolong so as to be as powerful as their stars. However, the popularity of kungfu and boxing leads to many problems which are uneasy to resolve. After seeing action movies, peolpe of all ages are effected. For instance, little kids may destory furniture, teenagers may hurt kids for pocket money, and husbands may use violence in the family, and some can even do greater harm to the society. The harmony of the society is broken, people don't feel safe, and much worse results may happen and who konws? Therefore, these action scenes should be banned, or at least they should be controlled with effective methods. The ban doesn't make action movies lose market or die out, instead, it forces action movies to do more work on their plot.That is to say, new action movies attract audience by interesting plots instead of violence scenes. People will not be so violence after watching new action movies if the ban goes on successfully.I believe that the market of action movies will turn out to be more fascinating than any time before."

    # 文章
    passage = EssayPassage()
    passage.passage = content2
    passage.title = "title"
    passage.score = 1
    passage.id = '1'
    passage.reviewerId = 1
    
    # 处理文章
    processPassage(passage)
    
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
            print sent.lgCheckResults
    
    print "三元词组", passage.trigrams
    
    print "demo_passage OVER"

if __name__ == "__main__":
    print "Start..."    

    demo_passage()
    exit()

    LOG_FILENAME ='log.log'
    logging.basicConfig(filename=LOG_FILENAME,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        level=logging.DEBUG)
    
    essays = readEssays("gsfw.txt")
    
    scoreEssays = {}
    for essay in essays:
        if essay.score not in scoreEssays:
            scoreEssays[essay.score] = []
        scoreEssays[essay.score].append(essay)

    trainEssays = []
    testEssays = []
      
    for k, v in scoreEssays.items():
        print k
        print len(v)
        if len(v) > 16:
            s = len(v) * 5 / 6
            trainEssays.extend(v[:s])
            testEssays.extend(v[s:])

    print "Train essays: %d" % len(trainEssays)
    print "Test essays: %d" % len(testEssays)
    
    essay = essays[0]   
    
    # 文章
    passage = EssayPassage()
    passage.passage = essay.content
    passage.title = essay.title
    passage.score = essay.score
    
    # 处理文章
    processPassage(passage)
    
    # 输出来看看是啥样子    
    print "PASSAGE========================================="        
    print passage
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
            nominals = [token.nominalization[1] for token in sent.tokens]
            print tokens
            print tags
            print lemmas
            print stems
            print levels
            print sentNos
            print paraNos
            print nos
            print nominals
            print sent.tokenCount
            print sent.wordCount
            print sent.realWordCount
        
    print "...OVER"