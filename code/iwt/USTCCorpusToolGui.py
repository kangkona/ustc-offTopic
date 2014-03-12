
# -*- coding: utf-8 -*-

import sys
from math import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import pickle

from essayreader import USTCReader
from essay import EssayPassage
import essayprepare
from extractor import FeatherExtractor

class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.resize(800, 600)
        self.browser = QTextBrowser()
        self.lineedit = QLineEdit("Type an essay id here")
        self.lineedit.selectAll()
        self.processButton = QPushButton("Process")
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.lineedit)
        layout.addWidget(self.processButton)
        self.setLayout(layout)
        self.lineedit.setFocus()
        #self.connect(self.lineedit, SIGNAL("returnPressed()"), self.updateUi)
        self.connect(self.processButton, SIGNAL("clicked()"), self.processEssay)
        self.setWindowTitle("Calculate")
        self.essays = None
        self.essayDict = {}
        self.__loadEssays()
    
    def __loadEssays(self):
        self.essays = USTCReader.parseUSTCFile('USTC2011Jan.txt')
        print len(self.essays)
        for e in self.essays:
            self.essayDict[e.id] = e
        print len(self.essayDict)

    def updateUi(self):
        try:
            text = unicode(self.lineedit.text())
            self.browser.append("%s = <b>%s</b>" % (text, eval(text)))
        except:
            self.browser.append("<font color=red>%s is invalid!</font>" % text)
            
    def processEssay(self):
        self.browser.clear()
        id = unicode(self.lineedit.text())
        essay = self.essayDict.get(id)
        if not essay:
            self.browser.append("<font color=red>%s is not found!</font>" % id)
            return
        
        self.browser.append(essay.content)
        
        # 文章
        passage = EssayPassage()
        passage.passage = essay.cleanContent()
        passage.title = essay.title
        passage.score = essay.score
        passage.id = essay.id
        
        # 处理文章
        essayprepare.processPassage(passage)
        
        # 输出来看看是啥样子    
        self.browser.append("PASSAGE=========================================")        
        self.browser.append(passage.id)
        #self.browser.append(passage.title)
        self.browser.append(passage.score)
        self.browser.append(passage.passage)
        self.browser.append(str(len(passage.paragraphs)))
        self.browser.append("PARAGRAPHS---------------------------------------")
        for para in passage.paragraphs:
            self.browser.append(str(para.paragraphNo))
            self.browser.append(para.paragraph)
            for sent in para.sentences:
                self.browser.append(str(sent.sentenceNo))
                self.browser.append(str(sent.paragraphSentenceNo))
                self.browser.append(sent.sentence)
                tokens = [token.token for token in sent.tokens]
                tags = [token.pos for token in sent.tokens]
                lemmas = [token.lemma for token in sent.tokens]
                stems = [token.stem for token in sent.tokens]
                levels = [token.level for token in sent.tokens]
                nos = [token.tokenNo for token in sent.tokens]
                sentNos = [token.sentenceTokenNo for token in sent.tokens]
                paraNos = [token.paragraphTokenNo for token in sent.tokens]
                errorTokens = [token.token for token in sent.tokens if token.isSpellError]
                if not sent.canParsed:
                    self.browser.append("<font color=red>SENTENCE ERROR</font>")
                self.browser.append("<font color=red>SPELLERROR %s</font>" % str(errorTokens))
                self.browser.append(str(tokens))
                self.browser.append(str(tags))
                self.browser.append(str(lemmas))
                self.browser.append(str(stems))
                self.browser.append(str(levels))
                self.browser.append(str(sentNos))
                self.browser.append(str(paraNos))
                self.browser.append(str(nos))
                self.browser.append(str(sent.tokenCount))
                self.browser.append(str(sent.wordCount))
                self.browser.append(str(sent.realWordCount))
        
        self.browser.append(u"三元词组" + ' ' + str(passage.trigrams))
    
    
        e = FeatherExtractor()
    
        # 提取语言特征    
        languageFeather = e.extractLangFeather(passage)  
        
        print u"词次总数", languageFeather.tokenCount
        print u"单词总数", languageFeather.wordCount
        print u"词形总数", languageFeather.wordTypeCount
        print u"词元总数", languageFeather.wordLemmaCount
        
        print u"介词个数", languageFeather.prepositionCount
        print u"介词比例", languageFeather.prepositionRatio
        print u"介词使用", languageFeather.prepositionUse
        
        print u"定冠词个数", languageFeather.definiteArticleCount
        print u"定冠词比例", languageFeather.definiteArticleRatio
        print u"定冠词使用", languageFeather.definiteArticleUse
        
        # 提取结构特征  
        #structureFeather = e.extractStructureFeather(passage)
        
        #generateUSTCFeathers('USTC2011Jan.txt', 'USTCFeathers_503.txt')
            
        print "...OVER"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    app.exec_()
    pass