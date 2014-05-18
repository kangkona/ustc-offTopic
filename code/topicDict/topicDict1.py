# -*- coding: utf-8 -*-
"""
@author: kangkona
@version: 0.1
"""

from tool import *
from collections import OrderedDict
import re

dict_texts = tree()
 
def gen_dict0(texts):
    '''gen dict from all essays.'''
    for text in texts:
        for word in text:
            if word in dict_texts:
                dict_texts[word]['freq']+=1
            else:
                dict_texts[word]['freq'] = 1

dict_texts = {}
def gen_dict(texts):
    ''''''
    for text in texts:
        for word in text:
            if word in dict_texts:
                dict_texts[word]+=1
            else:
                dict_texts[word] = 1

# Todo: Remove some words which freq is only 1.
    
def freq2goals(dictionary):
    '''convert word frequence to a goal, which stand for 
    the percents of current word in dictionary 
    '''
    sum_freqs = sum([dict_texts[word]['freq'] for word in dict_texts])*1.0
    
    for word in dictionary:
        dictionary[word]['goal'] = dictionary[word]['freq'] / sum_freqs
    
    
def onTopic_goal(text):
    '''compute the on-topic goals of a essay'''
    
    goal = 0
    for word in text:
            if word in dict_texts:
                goal += dict_texts[word]['goal']
    return goal/len(text)
    
    
def main():
    FILE = "data/test.txt"
    fin = open(FILE).read().lower()
    texts = re.split("<start>", fin)
#     texts = [words2stemer(stopwords_filter(text_tokenizer(text))) for text in texts]
    texts = [stopwords_filter(text_tokenizer(text)) for text in texts]
    gen_dict(texts)
    freq2goals(dict_texts)
    
    for text in texts:
        print onTopic_goal(text)
    
    word_counts = {}
    for word in dict_texts:
        word_counts[word] = dict_texts[word]['freq']
    print word_counts
    for word in sorted(word_counts.iteritems(), key = lambda asd:asd[1], reverse = True):
            print word
        
    
if __name__ == '__main__':
    main()    
    
    
    
    
    
    
    
    
    
            
