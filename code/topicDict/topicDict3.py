# -*- coding: utf-8 -*-
"""
@author: kangkona
@version: 0.3
"""
from tool import *
import matplotlib.pyplot as plt
import re

class TopicDict(object):
    "class to determine weather an essay is off topic"
    def __init__(self):
        self.dict_texts = {}
        self.sum_freqs = 0
    
    def gen_dict(self, texts):
        dict_tmp = {}
        for text in texts:
            for word in text:
                if word in dict_tmp:
                    dict_tmp[word]+=1
                else:
                    dict_tmp[word] = 1
        self.dict_texts = {key:dict_tmp[key] for key in dict_tmp if dict_tmp[key] > 1}
        self.sum_freqs = sum([self.dict_texts[word] for word in self.dict_texts])*1.0
         
    
    def onTopic_goal(self, text):
        "compute the on-topic goals of a essay"
        goal = sum([self.dict_texts[word] for word in text if word in self.dict_texts])
        return goal/(len(text) * self.sum_freqs)  
        
     
    
def main():
    FILE = "data/src.txt"
    fin = open(FILE).read()
    texts = re.split("<start>", fin)
#     texts = [words2stemer(stopwords_filter(text_tokenizer(text))) for text in texts]
    texts = [stopwords_filter(text_tokenizer(text)) for text in texts]
    goals0 = []
    goals1 = []
    goals2 = []
    for i in range(3,len(texts)):
        texts0 = texts[:i]
        topic = TopicDict()
        topic.gen_dict(texts0)
        goals0.append(topic.onTopic_goal(texts0[0]))
        goals1.append(topic.onTopic_goal(texts0[1]))
        goals2.append(topic.onTopic_goal(texts0[2]))
        
    plt.plot(goals0,"^")
    plt.plot(goals1,"o")
    plt.plot(goals2,"s")
    plt.show()
        
#     topic = TopicDict()
#     topic.gen_dict(texts)
#     goals = []
#     for text in texts:
# #         print texts.index(text), onTopic_goal(text,sum_freqs)
#         goals.append(topic.onTopic_goal(text))
#     plt.plot(sorted(goals),'o')
#     plt.show()
#     for word in sorted(topic.dict_texts.iteritems(), key = lambda asd:asd[1], reverse = True):
#             print word
        
    
if __name__ == '__main__':
    main()    
    
    
    
    
    
    
    
    
    
            
