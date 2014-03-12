
# -*- coding: utf-8 -*-

import pickle

import nltk
from nltk.corpus import wordnet

# 语法检查器
from grammarchecker import grammarcheck
gc = grammarcheck.CmetGrammarCheck()
gc.load()
print gc.check("How long old are you.")
print gc.check("I am a student.")

class TopicAnalyst():

    def __getSynonyms(self, word):
        synonyms = []
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas:
                synonyms.append(lemma.name)
        return synonyms


    def analysePassage(self, passage, keywords):
        tokens = []
        for para in passage.paragraphs:
            for sent in para.sentences:
                tokens.extend([token for token in sent.tokens
                    if ((not token.isStopWord) and (token.level > 0))])

        lemmas = [token.lemma for token in tokens]
        
        moreKeywords = []
        for w in keywords:
            moreKeywords.extend(self.__getSynonyms(w))

        kwCount = 0
        for lemma in lemmas:
            if lemma in moreKeywords:
                kwCount += 1

        return kwCount
    
    def keywordSimilarity(self, passage, keywords):
        tokens = []
        for para in passage.paragraphs:
            for sent in para.sentences:
                tokens.extend([token for token in sent.tokens
                    if ((not token.isStopWord) and (token.level > 0))])

        lemmas = [token.lemma for token in tokens]
        
        keywordSyns = []
        for w in keywords:
            keywordSyns.append(wordnet.synsets(w))
        
        
        simLemmas = []
        synCount = 0
        for lemma in lemmas:
            find = False
            lsynsets = wordnet.synsets(lemma)
            #print len(lsynsets)
            if len(lsynsets) < 1:
                #print lemma
                continue
            #lemmaSyn = lsynsets[0]
            for lemmaSyn in lsynsets:
                if find: break
                for kwSyns in keywordSyns:
                    if find: break
                    for syn in kwSyns:
                        if find: break
                        sim = lemmaSyn.wup_similarity(syn)
                        simPath = lemmaSyn.path_similarity(syn)
                        if sim > 0.4 and simPath > 0.4:
                            synCount += 1
                            simLemmas.append((lemma, sim, simPath))
                            find = True
            
        return simLemmas
    
    
    def nptrunk(self, sentence):
        grammarNP = r"""
            NP: {<JJ|JJR|JJS>+<NN|NNS>+}
                {<JJ><NNS>}
        """
        grammarVP = r"""
            VP: {<VB|VBP><JJ|JJR|JJS>+<NN|NNS>+}
                {<VB|VBP><NN|NNS>+}
        """
        s = [(token.token, token.pos) for token in sentence.tokens]
        cp = nltk.RegexpParser(grammarVP)
        return cp.parse(s)
              

if __name__ == "__main__":
    print "start..."

    pkfile = open('ustcpassages_503.pkl', 'r')
    passages = pickle.load(pkfile)
    pkfile.close()    
    
    ta = TopicAnalyst()
    
    p = passages[0]
    for para in p.paragraphs:
        for sent in para.sentences:
            x = ta.nptrunk(sent)
            #print x
            for xx in x:
                if isinstance(xx, nltk.tree.Tree): 
                    if xx.node == "VP":
                        print "===", xx
    
    
    for para in p.paragraphs:
        for sent in para.sentences:
            x = gc.checkSummary(sent.sentence)
            print x
    
    exit()
    
    keywords1 = ['Chinese', 'English', 'language']
    keywords = ['private', 'tutor', 'teacher']

    for p in passages:
        kwCount = ta.analysePassage(p, keywords1)
        synLemmas = ta.keywordSimilarity(p, keywords1)
        #print synLemmas
        print str(p.score), str(kwCount), str(len(synLemmas)), str(len(set(synLemmas))) 

    print "end!!!"
