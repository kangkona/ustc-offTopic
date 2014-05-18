# -*- coding: utf-8 -*-
"""
@author: kangkona
@version: 0.2
"""

from tool import *
from collections import OrderedDict
import re

dict_texts = {}

def gen_dict(texts):
    ''''''
    for text in texts:
        for word in text:
            if word in dict_texts:
                dict_texts[word]+=1
            else:
                dict_texts[word] = 1        
    
def onTopic_goal(text,sum_freqs):
    '''compute the on-topic goals of a essay'''
    
    goal = 0
    for word in text:
            if word in dict_texts:
                goal += dict_texts[word]
    return goal/(len(text)*sum_freqs)
    
    
def main():
    FILE = "data/test.txt"
    fin = open(FILE).read().lower()
    texts = re.split("<start>", fin)
#     texts = [words2stemer(stopwords_filter(text_tokenizer(text))) for text in texts]
    texts = [stopwords_filter(text_tokenizer(text)) for text in texts]
    gen_dict(texts)
    dict_texts2 =  {key:dict_texts[key] for key in dict_texts if dict_texts[key] > 1}
    sum_freqs = sum([dict_texts2[word] for word in dict_texts2])*1.0
    for text in texts:
        print onTopic_goal(text,sum_freqs=1.0)
    

    for word in sorted(dict_texts2.iteritems(), key = lambda asd:asd[1], reverse = True):
            print word
        
    
if __name__ == '__main__':
    main()    
    
    
    
    
    
    
    
    
    
            
