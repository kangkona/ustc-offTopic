
# -*- coding: utf-8 -*-


import os

import nltk

from grammarchecker import connectfinder


def oancconns(dir):
    sent_tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
    for root, dirs, files in os.walk(dir):
        for name in files:
            filename = os.path.join(root, name)
            if filename.endswith('.para'):
                print filename
                outfilename = filename + '.conns'
                
                sents = []
                fi = open(filename, 'r')
                lines = fi.readlines()
                for line in lines:
                    print line
                    for sent in sent_tokenizer.tokenize(line.strip()):
                        print "XXX", sent
                        try:
                            s = sent
                            sents.append(s)
                        except:
                            pass
                connectfinder.retrieveConnects(sents, outfilename)
                
if __name__ == "__main__":
    print "START"
    #oancconns(r"D:\essayscoring\trunk\data\OANC-GrAF\data\spoken\face-to-face")
    oancconns(r"D:\essayscoring\trunk\data\OANC-GrAF\data\written_1")
    print "OVER"