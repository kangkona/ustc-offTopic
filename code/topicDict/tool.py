# -*- coding: utf-8 -*-
"""
@author: kangkona
"""

import nltk as nk
from nltk.corpus import stopwords 
from nltk.stem.lancaster import LancasterStemmer
from collections import defaultdict

def tree():
    return defaultdict(tree)

def text_tokenizer0(text):
    words_raw = nk.word_tokenize(text)
    words_tokenized = []
    for word in words_raw:
        if word.endswith('.'):
            word = word[:-1]
        if word is not None:
            word = word.lower()
            words_tokenized.append(word)
    return words_tokenized

def text_tokenizer(text):
    def tsplit(string, delimiters=(' ',',', '/', '-','.','"',"'",'\t','\n')):
        """Behaves str.split but supports multiple delimiters."""
        delimiters = tuple(delimiters)
        stack = [string.lower()]
        
        for delimiter in delimiters:
            for i, substring in enumerate(stack):
                substack = substring.split(delimiter)
                stack.pop(i)
                for j, _substring in enumerate(substack):
                    stack.insert(i+j, _substring)
        return stack
    return tsplit(text)
        
def stopwords_filter(words):
    filter_stopwords = lambda x: len(x) < 2 or x in stopwords.words("english")
    words_filted = [word for word in words if not filter_stopwords(word)]
    return words_filted
    

def words2stemer(words):
    st = LancasterStemmer()
    words_stemmed = [st.stem(word) for word in words]
    return words_stemmed
    

def main():
    pass    
    
if __name__ == '__main__':
    main()