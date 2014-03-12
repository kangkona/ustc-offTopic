
# -*- coding: utf-8 -*-

import urllib, urllib2 
import time
import random
import logging

LOG_FILENAME ='iwtustcserver.log'
logging.basicConfig(filename=LOG_FILENAME,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    level=logging.DEBUG)   

import json

from essay import EssayPassage
import essayprepare
import extractor
import simplerater

TUTOR_NAME = 'eva'
CO_URL = 'http://localhost:8000/task/aestask/co/'
CI_URL = 'http://localhost:8000/task/aestask/ci/'

current_task = None

rater = simplerater.SimpleEssayRater()

def checkout_task():
    # 从管理中心取任务
    task = {}
    params = (('tutor_name', TUTOR_NAME), )
    rep = urllib2.urlopen(CO_URL+'?'+urllib.urlencode(params))
    repstr = rep.read()
    print repstr
    repobj = json.loads(repstr)
    if repobj:
        print repobj["input"]
        input = json.loads(repobj["input"])
        print input["title"].encode('UTF-8')
        task['id'] = repobj['task_id']
        task['input'] = input
    return task

def commit_task(task):
    # 向管理中心提交任务状态及结果
    params = [('task_id', task['id']), ('status', task['status']), 
        ('progress', task['progress']), ('output', task['output']), 
        ('simple_output', task['simple_output']),
        ('detail_output', task['detail_output']), ]
    rep = urllib2.urlopen(CI_URL, urllib.urlencode(params))
    repstr = rep.read()
    print repstr
    
def fn_prepare_progress(progressStatus):
    current_task['progress'] = progressStatus - 1
    current_task['status'] = 'DOING'
    current_task['output'] = ''
    current_task['simple_output'] = ''
    current_task['detail_output'] = ''
    commit_task(current_task)

def do_task(task):
    newpassage = EssayPassage()
    newpassage.passage = task['input']['content']
    newpassage.orderId = task['id']
    newpassage.score = 0
    newpassage.processStatus = 0
    try:
        essayprepare.processPassage(newpassage, fn_prepare_progress)
        fe = extractor.FeatherExtractor()
        lf = fe.extractLangFeather(newpassage)
        newpassage.lf = lf
        cf = fe.extractContentFeather(newpassage)
        newpassage.cf = cf
        sf = fe.extractStructureFeather(newpassage) 
        newpassage.sf = sf
        newpassage.score = rater.rate_by_params(newpassage)[0]
    except:
        task['progress'] = -2
        task['status'] = 'TUTERR'
        task['output'] = ""
        task['simple_output'] = ""
        task['detail_output'] = ""
        commit_task(task)
        return

    # 生成最终结果
    output = {}
    passage = {}
    passage['score'] = newpassage.score
    passage['token_count'] = lf.tokenCount
    passage['word_count'] = lf.wordCount
    passage['word_type_count'] = lf.wordTypeCount
    passage['word_lemma_count'] = lf.wordLemmaCount
    passage['word_stem_count'] = lf.wordStemCount
    passage['average_word_length'] = lf.wordLengthAverage
    passage['average_sentence_length'] = lf.sentenceLengthAverage
    passage['overly_use_word_count'] = lf.overlyUseWordCount
    passage['paragraph_count'] = len(newpassage.paragraphs)
    passage['sentence_count'] = newpassage.sentenceCount
    passage['sentences'] = []
    for para in newpassage.paragraphs:
        for sent in para.sentences:
            sentence = {}
            sentence['no'] = sent.sentenceNo
            sentence['para_no'] = para.paragraphNo
            sentence['original'] = sent.sentence
            sentence['score'] = 0
            spell_errors = []
            fs = []
            for token in sent.tokens:
                if token.isSpellError:
                    fs.append('<ESP>' + token.token + '</ESP>')
                    spell_error = {}
                    spell_error['token'] = token.token
                    spell_error['lemma'] = token.lemma
                    spell_error['suggest'] = token.candidates
                    spell_error['start_at'] = token.startAt
                    spell_error['end_at'] = token.endAt
                    spell_errors.append(spell_error)
                else:
                    fs.append(token.token)
            sentence['spell_errors'] = spell_errors
            sentence['marked'] = ' '.join(fs)
            sentence['lt_result'] = sent.ltCheckResults   
            sentence['lg_result'] = sent.lgCheckResults
            sentence['links'] = []
            passage['sentences'].append(sentence)
           
    output['passage'] = passage
    task['progress'] = 100
    task['status'] = 'DONE'
    task['output'] = json.dumps(output)
    task['simple_output'] = json.dumps(output)    
    task['detail_output'] = json.dumps(generate_detail_output(newpassage))   
        
    commit_task(task)
    
def generate_detail_output(passage):

    detail_output = {}
    detail_passage = {}
    
    detail_passage['title'] = passage.title
    detail_passage['passage'] = passage.passage
    detail_passage['score'] = passage.score
    detail_passage['paragraph_count'] = len(passage.paragraphs)
    detail_passage['paragraphs'] = []
    for para in passage.paragraphs:
        paragraph = {}
        paragraph['no'] = para.paragraphNo
        paragraph['paragraph'] = para.paragraph
        paragraph['sentences'] = []
        for sent in para.sentences:
            sentence = {}
            sentence['no'] = sent.sentenceNo
            sentence['paragraph_sentence_no'] = sent.paragraphSentenceNo
            sentence['sentence'] = sent.sentence
            sentence['score'] = 0
            
            tokens = [token.token for token in sent.tokens]
            tags = [token.pos for token in sent.tokens]
            lemmas = [token.lemma for token in sent.tokens]
            stems = [token.stem for token in sent.tokens]
            levels = [token.level for token in sent.tokens]
            nos = [token.tokenNo for token in sent.tokens]
            sentNos = [token.sentenceTokenNo for token in sent.tokens]
            paraNos = [token.paragraphTokenNo for token in sent.tokens]  
            
            sentence['tokens'] = tokens
            sentence['tags'] = tags
            sentence['lemmas'] = lemmas
            sentence['stems'] = stems
            sentence['levels'] = levels
            sentence['nos'] = nos
            sentence['sent_nos'] = sentNos
            sentence['para_nos'] = paraNos       
            
            spell_errors = []
            fs = []
            for token in sent.tokens:
                if token.isSpellError:
                    fs.append('<ESP>' + token.token + '</ESP>')
                    spell_error = {}
                    spell_error['token'] = token.token
                    spell_error['lemma'] = token.lemma
                    spell_error['suggest'] = token.candidates
                    spell_error['start_at'] = token.startAt
                    spell_error['end_at'] = token.endAt
                    spell_errors.append(spell_error)
                else:
                    fs.append(token.token)
            sentence['spell_errors'] = spell_errors
            sentence['marked'] = ' '.join(fs)
            sentence['lt_result'] = sent.ltCheckResults   
            sentence['links'] = sent.links
            paragraph['sentences'].append(sentence)
            
        detail_passage['paragraphs'].append(paragraph)
        
    language_feather = {}
    language_feather['spell_error_count'] = (u'拼写错误', passage.lf.spellErrorCount)
    language_feather['grammar_error_count'] = (u'语法错误', passage.lf.sentenceErrorCount)        
    language_feather['preposition_use'] = (u'介词使用度量值', passage.lf.prepositionUse)
    language_feather['article_use'] = (u'冠词使用度量值', passage.lf.articleUse)
    language_feather['preposition_count'] = (u'介词个数', passage.lf.prepositionCount)
    language_feather['pereposition_ratio'] = (u'介词比例', passage.lf.prepositionRatio)
    language_feather['article_count'] = (u'冠词个数', passage.lf.articleCount)
    language_feather['article_ratio'] = (u'冠词比例', passage.lf.articleRatio)
    language_feather['definite_article_count'] = (u'定冠词个数', passage.lf.definiteArticleCount)        
    language_feather['definite_article_ratio'] = (u'定冠词比例', passage.lf.definiteArticleRatio)
    language_feather['definite_article_use'] = (u'定冠词使用度量值', passage.lf.definiteArticleUse)
    language_feather['word_combination_recurrent_count'] = (u'词块重现数', passage.lf.wordCombRecurrentCount)
    language_feather['word_combination_reccurent'] = (u'词块重现度量值', passage.lf.wordCombRecurrent)      
    language_feather['token_count'] = (u'文章长度', passage.lf.tokenCount)
    language_feather['word_type_count'] = (u'异形词总数', passage.lf.wordTypeCount)
    language_feather['word_stem_count'] = (u'文章源长度', passage.lf.wordStemCount)
    language_feather['word_length_average'] = (u'平均词长', passage.lf.wordLengthAverage)        
    language_feather['word_length_sd'] = (u'词长标准差', passage.lf.wordLengthSD)
    language_feather['nonestopword_length_average'] = (u'非停用词平均词长', passage.lf.noneStopWordLengthAverage)
    language_feather['nonestopword_length_sd'] = (u'非停用词长标准差', passage.lf.noneStopWordLengthSD)
    language_feather['word_type_ratio'] = (u'不同单词个数与单词总数比值', passage.lf.wordTypeRatio)
    language_feather['index_of_guiraud'] = (u'不同单词个数与单词总数平方根的比值', passage.lf.indexOfGuiraud)
    language_feather['uccr'] = (u'非常用单词和常用单词个数比例', passage.lf.uccr)
    language_feather['nouning_verb_count'] = (u'名词化词数', passage.lf.nouningVerbCount)
    language_feather['nouning_verb_ratio'] = (u'名词化词比例', passage.lf.nouningVerbRatio)  
         
    for idx, wcil in enumerate(passage.lf.wordCountInLevels):
        language_feather['word_count_level_' + str(idx)] = (u'单词计数_级别' + str(idx), wcil)
    for idx, wril in enumerate(passage.lf.wordCountRatioBetweenLevels):
        language_feather['word_ratio_level_' + str(idx)] = (u'单词比例_级别' + str(idx), wril)
                
    language_feather['gerund_count'] = (u'动名词数', passage.lf.gerundCount)
    language_feather['gerund_ration'] = (u'动名词比例', passage.lf.gerundRatio)
    language_feather['sentence_length_average'] = (u'平均句子长度', passage.lf.sentenceLengthAverage)
    language_feather['sentence_length_sd'] = (u'平均句子长度标准差', passage.lf.sentenceLengthSD)
    language_feather['automated_readability_index'] = (u'可读性测量', passage.lf.automatedReadabilityIndex)
    language_feather['sentence_complexity'] = (u'句子结构复杂度', passage.lf.sentenceComplexity)
    language_feather['sentence_complexity_scale'] = (u'名子结构复杂指标', passage.lf.sentenceComplexityScale)
    language_feather['high_low_level_ratio'] = (u'高低级别词比例', passage.lf.highLowLevelRatio)        
    language_feather['level_count'] = (u'词汇覆盖的级别数', passage.lf.levelCount)
    language_feather['word_count'] = (u'单词个数', passage.lf.wordCount)
    language_feather['word_lemma_count'] = (u'Lemmatize后的不同单词个数', passage.lf.wordLemmaCount)        
    language_feather['word_lemma_ratio'] = (u'词元数与单词总数比值', passage.lf.wordLemmaRatio)
    language_feather['real_word_count'] = (u'非停用词的单词个数', passage.lf.realWordCount)
    language_feather['real_word_ratio'] = (u'非停用词的单词个数与所有单词个数比值', passage.lf.realWordRatio)        
    language_feather['real_word_lemma_count'] = (u'非停用词Lemmatize后的不同单词个数', passage.lf.realWordLemmaCount)
    language_feather['overly_use_word_count'] = (u'过度重复使用单词数', passage.lf.overlyUseWordCount)
    
    detail_passage['use_word_info'] = (u'使用单词信息', passage.lf.lemmaUseInfo)
    
    detail_passage['language_feather'] = language_feather
    detail_passage['content_feather'] = passage.cf.generate_feather_dict()    
    detail_passage['structure_feather'] = passage.sf.generate_feather_dict()
    
    detail_output['passage'] = detail_passage
    
    return detail_output


MAX_TIME_WAIT = 15 # 最大取任务等待间隔

if __name__ == "__main__":

    time_wait = 1
    while True:
        current_task = None
        try:
            current_task = checkout_task()
        except:
            pass
        if current_task:
            time_wait = 1
            do_task(current_task)
            print "================"
        else:
            if time_wait < MAX_TIME_WAIT:
                time_wait = time_wait + 1
            print "no task"
        time.sleep(time_wait)
