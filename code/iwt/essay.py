
# -*- coding: utf-8 -*-

class LanguageFeather():
    
    def __init__(self):
        # 语言准确性
        self.spellErrorCount = 0 # 拼写错误
        self.sentenceErrorCount = 0 # 句子错误
        # 语言恰当性
        self.prepositionUse = 0.0 # 介词使用度量值
        self.articleUse = 0.0 # 冠词使用度量值
        self.prepositionCount = 0 # 介词个数
        self.prepositionRatio = 0.0 # 介词个数与单词总数的比值
        self.articleCount = 0 # 冠词个数
        self.articleRatio = 0.0 # 冠词个数与单词总数的比值
        self.definiteArticleCount = 0 # 定冠词个数
        self.definiteArticleRatio = 0.0 # 定冠词比例
        self.definiteArticleUse = 0.0 # 定冠词使用度量值
        self.wordCombRecurrentCount = 0 # 词块重现数
        self.wordCombRecurrent = 0.0 # 词块重现度量值
        # 语言流利性
        self.tokenCount = 0 # 文章长度，词次总数，包括标点符号
        self.wordTypeCount = 0 # 异形词总数
        self.wordStemCount = 0.0 # 文章源长度
        # 词汇复杂性
        self.wordLengthAverage = 0.0 # 平均词长
        self.wordLengthSD = 0.0 # 词长标准差
        self.noneStopWordLengthAverage = 0.0 # 非停用词平均词长
        self.noneStopWordLengthSD = 0.0 # 非停用词长标准差
        self.wordTypeRatio = 0.0 # Type-Tokens Ratio，不同单词个数与单词总数比值
        self.indexOfGuiraud = 0.0 # 不同单词个数与单词总数平方根的比值
        self.wordCountInLevels = [] # 各级别词汇计数
        self.wordCountRatioBetweenLevels = [] # 各级别词汇比例
        self.uccr = 0.0 # UC-CR，非常用单词和常用单词个数比例
        self.nouningVerbCount = 0 # 名词化词数，将动词通过变形在作文中当做名词使用的词汇个数
        self.nouningVerbRatio = 0.0 # 名词化词比例
        # 句子复杂性
        self.gerundCount = 0 # 动名词数
        self.gerundRatio = 0.0 # 动名词比例
        self.sentenceLengthAverage = 0 # 平均句子长度
        self.sentenceLengthSD = 0 # 平均句子长度标准差
        self.automatedReadabilityIndex = 0.0 # 可读性测量
        self.sentenceComplexity = 0 # 句子结构复杂度
        self.sentenceComplexityScale = 0.0 # 名子结构复杂指标

        # 其他
        self.highLowLevelRatio = 0.0 # 高低级别词比例
        self.levelCount = 0 # 词汇覆盖的级别数
        self.wordCount = 0 # 作文长度（总单词个数）
        self.wordLemmaCount = 0 # Lemmatize后的不同单词个数
        self.wordLemmaRatio = 0.0 # 词元数与单词总数比值
        self.realWordCount = 0 # 非停用词的单词个数
        self.realWordRatio = 0.0 #  非停用词的单词个数与所有单词个数比值
        self.realWordLemmaCount = 0 # 非停用词Lemmatize后的不同单词个数
        self.overlyUseWordCount = 0 # 过度重复使用单词数
        
    def __repr__(self):
        stringRepresentation="%d %d %d %f %d %d %f %d %d %f %f %f %f %d %f %f %f %f %d %f %d %f %f %f %f" % (
            self.tokenCount, self.wordCount, self.wordTypeCount, self.wordTypeRatio,  
            self.wordLemmaCount, self.realWordCount, self.realWordRatio, 
            self.spellErrorCount, self.nouningVerbCount, self.highLowLevelRatio,
            self.wordLengthAverage, self.wordLengthSD, self.indexOfGuiraud,
            self.sentenceErrorCount, self.sentenceLengthAverage, self.sentenceLengthSD, 
            self.prepositionUse, self.definiteArticleUse,
            self.prepositionCount, self.prepositionRatio, self.definiteArticleCount, 
            self.definiteArticleRatio, self.automatedReadabilityIndex, self.noneStopWordLengthAverage, self.noneStopWordLengthSD)
        return stringRepresentation
    
class ContentFeather():
    
    def __init__(self):
        # LSA
        self.lsaScore = 0.0 # LSA分数
        self.lsaSimilarity = 0.0 # LSA相似度
        self.keywordCover = 0.0 # 关键词覆盖
        self.proceduralVocabularyCount = 0 # 程序词条数
        
    def generate_feather_dict(self):
        result = {}
        result['lsa_score'] = (u'LSA分数', self.lsaScore)
        result['lsa_similarity'] = (u'LSA相似度', self.lsaSimilarity)
        result['keyword_cover'] = (u'关键词覆盖', self.keywordCover)
        result['procedure_vocabulary_count'] = (u'程序词条数', self.proceduralVocabularyCount)
        return result

class StructureFeather():
    
    def __init__(self):
        # 衔接性
        self.connectiveCount = 0 # 衔接词个数
        self.connectiveRatio = 0.0 # 衔接词比例
        self.connectiveTypeCount = 0 # 衔接词种类
        self.specialDemonstrativePronounCount = 0 # 特定指示代词个数
        self.specialDemonstrativePronounUse = 0.0 # 特定指示代词使用
        self.restPronounCount = 0 # 其余代词个数
        self.restPronounUse = 0.0 # 其余代词使用
        # 局部连贯性
        self.adjacentLemmaOverlapRatio = 0.0 # 相邻论元重叠
        self.adjacentStemOverlapRatio = 0.0 # 相信词干重叠
        # 全局连贯怀
        self.paraLemmaOverlapRatios = [] # 段落内论元重叠
        self.paraStemOverlapRatios = [] # 段落内词干重叠
        
    def generate_feather_dict(self):
        result = {}
        result['connective_count'] = (u'衔接词个数', self.connectiveCount)
        result['connective_ratio'] = (u'衔接词比例', self.connectiveRatio)
        result['connective_type_count'] = (u'衔接词种类', self.connectiveTypeCount)
        result['special_demonstrative_pronoun_count'] = (u'特定指示代词个数', self.specialDemonstrativePronounCount)
        result['special_demonstrative_pronoun_use'] = (u'特定指示代词使用', self.specialDemonstrativePronounUse)
        result['rest_pronoun_count'] = (u'其余代词个数', self.restPronounCount)
        result['rest_pronoun_use'] = (u'其余代词使用', self.restPronounUse)
        return result


class EssayToken():
    """
    文章中的词次
    对于文章中的每 个切分出来的词次，需要列出其原始字符串、词性、(词元)词次的原型、是否错误、
    拼写改错建议列表，该词次在文章中的出现的序号，该词次相同出现的序号，词的级别
    """

    def __init__(self, token):
        self.token = token # 词次内容
        self.pos = "" # 词性
        self.lemma = "" # 词元
        self.isSpellError = False # 是否有拼写错误
        self.suggests = [] # 拼写错误后的建议拼写
        self.sentenceTokenNo = 0 # 词次在句子中的序号，从1开始
        self.paragraphTokenNo = 0 # 词次在段落中的序号，从1开始
        self.tokenNo = 0 # 词次在文章中的序号，从1开始
        self.sameTokenNo = 0 # 相同词次出现的序号，从1开始
        self.level = -1 # 词的级别
        self.isStopWord = False # 是否停用词
        self.stem = "" # 词干
        self.nominalization = (False, ()) # 是否名词化
        self.startAt = -1 # 在句子原文中的起始位置
        self.endAt = -1 # 在句子原文中的结束位置
        
        

class EssaySentence():
    """
    文章中的句子
    包括句子原文、以及对应的词次列表、以及句子分析结果
    """
    
    def __init__(self, no):
        self.sentenceNo = no # 句子在文章中的序号
        self.paragraphSentenceNo = 0 # 句子在段落中的序号
        self.sentence = "" # 句子原文
        self.tokens = [] # 句子包含的词次列表
        self.tokenCount = 0 # 句子中包含的词次个数
        self.wordCount = 0 # 句子包含的单词个数
        self.realWordCount = 0 # 句子中除停用词外的单词个数
        self.canParsed = False # 能否正确解析，如果不能正确解析，判定为语法错误
        self.complexity = 0 # 句子结构复杂程度
        
class EssayParagraph():
    """
    文章中的段落
    包含段落原文、句子列表
    """
    
    def __init__(self, no, paragraph):
        self.paragraphNo = no
        self.paragraph = paragraph
        self.sentences = []
        
class EssayPassage():
    """
    文章
    包含段落列表、文章基本信息
    """
    def __init__(self):
        self.content = ""
        self.passage = ""
        self.paragraphs = []
        self.title = ""
        self.passageType = ""
        self.score = ""
        self.realWordFreq = {}
        self.trigrams = []
        self.preprocessed = False
        self.rated = False
        
class TriGram():
    """三元词组
    """
    def __init__(self, newT1, newT2, newT3):
        self.t1 = newT1
        self.t2 = newT2
        self.t3 = newT3

    def __cmp__(self, other):
        return cmp(self.t1, other.t1) or cmp(self.t2, other.t2) or cmp(self.t3, other.t3)

    def __hash__(self):
        seed = 0;
        seed ^= hash(self.t1) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
        seed ^= hash(self.t2) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
        seed ^= hash(self.t3) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
        return seed;
       
    def __repr__(self):
    	return ' '.join(['(', self.t1, self.t2, self.t3, ')'])

if __name__ == "__main__":
    print "Start..."     
    print "...OVER"