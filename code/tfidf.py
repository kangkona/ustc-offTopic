# -*- coding: utf-8 -*-
"""
@author: kangkona
"""

import nltk as nk
from nltk.corpus import stopwords 
from nltk.stem.lancaster import LancasterStemmer
from gensim import corpora, models, similarities
import logging


def text_tokenizer(text):
    words_raw = nk.word_tokenize(text)
    words_tokenized = []
    for word in words_raw:
        if word.endswith('.'):
            word = word[:-1]
        if word is not None:
            word = word.lower()
            words_tokenized.append(word)
    return words_tokenized
        
def token_filter(words):
    filter_stopwords = lambda x: len(x) < 2 or x in stopwords.words("english")
    words_filted = [word for word in words if not filter_stopwords(word)]
    return words_filted

def token_stemer(words):
    st = LancasterStemmer()
    words_stemmed = [st.stem(word) for word in words]
    return words_stemmed
    
def texts_remove_once(texts):
    all_stems = sum(texts, [])
    stems_once = set(stem for stem in set(all_stems) if all_stems.count(stem) == 1)
    texts_removed_once = [[stem for stem in text if stem not in stems_once] for text in texts_stemmed]
    return texts_removed_once

def model(texts):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=10)
    index = similarities.MatrixSimilarity(lsi[corpus])
    ml_course = texts[210]
    ml_bow = dictionary.doc2bow(ml_course)
    ml_lsi = lsi[ml_bow]
    sims = index[ml_lsi]
    sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
    return sort_sims
    
    
if __name__ == '__main__':
    courses = [line.strip() for line in file('coursera_corpus')]
    print courses[0]
    courses_name = [course.split('\t')[0] for course in courses]
    print courses_name[0]
    
    texts_tokenized = [[word for word in text_tokenizer(document)] 
                                          for document in courses]
    print texts_tokenized[0]
    
    texts_filtered = [[word for word in token_filter(document)] 
                               for document in texts_tokenized]
    texts_stemmed = [[word for word in token_stemer(docment)] 
                               for docment in texts_filtered]
   
    texts_required = texts_remove_once(texts_stemmed)
    print texts_required[0]
    sort_sims = model(texts_required)
    print sort_sims
    for i in range(10):
        print courses_name[sort_sims[i][0]]
     
    
#     text = open("nlptest.txt","r").read()
#     words_raw = text_tokenizer(text)
#     words_filted = token_filter(words_raw)
#     words_stemed = token_stemer(words_filted)