
# -*- coding: utf-8 -*-

def stats(data):
    if not data: return (0, 0)
    sum = 0.0
    for value in data:
        sum += value
    mean = sum/len(data)
    sum = 0.0
    for value in data:
        sum += (value - mean)**2
    variance = 0
    if len(data) > 1:
        variance = sum/(len(data) - 1)
    return (mean, variance)

VerbTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
ProperNounTags = ['NNP', 'NNPS']
NounTags = ['NN', 'NNS', 'NNP', 'NNPS', 'Unk']
AdjectiveTags = ['JJ', 'JJR', 'JJS']
AdverbTags = ['RB', 'RBR', 'RBS']
PronounTags = ['PRP', 'PRP$', 'WP', 'WP$']
RestPronounTags = ['WP', 'WP$']
NumberTags = ['CD']

SpecialDemonstrativePronouns = ['this', 'that', 'these', 'those']

NoAsciiReplacer = '*'

IgnoredLtRuleIds = [
    'COMMA_PARENTHESIS_WHITESPACE',
    'WHITESPACE_RULE',
    'UPPERCASE_SENTENCE_START',
    'CAN_NOT',
    'EN_QUOTES',
    ]

def get_nominalization(word):
    result = False
    from nltk.corpus import wordnet as wn
    mword = wn.morphy(word, wn.NOUN)
    snames = []
    for sset in wn.synsets(word, 'n'):
        for lemma in sset.lemmas:
            if lemma.name == mword:
                snames.append(lemma)

    possible_lemmas = []
    for sname in snames:
        for k in sname.derivationally_related_forms():
            if k.synset.pos == 'v' and (len(k.name) < len(mword)):
                possible_lemmas.append(k)
                
    if not possible_lemmas:
        for sname in snames:
            for k in sname.derivationally_related_forms():
                if k.synset.pos == 'a' and (len(k.name) < len(mword)):
                    possible_lemmas.append(k)        
   
    #print word, '-->', mword         
    
    result = len(possible_lemmas) > 0
     
    if result:
        lemma_set = list(set(possible_lemmas))
        #print mword, '--->', lemma_set[0].name, lemma_set[0].synset.pos         
        return (result, (lemma_set[0].name, lemma_set[0].synset.pos))
    else:
        return (False, ())
    
if __name__ == "__main__":
    print get_nominalization("development")
