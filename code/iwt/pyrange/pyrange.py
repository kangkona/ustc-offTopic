
# -*- coding: utf-8 -*-


class PyRange():
    
    def __init__(self):
        # read the word list
        self.basewrd1 = {}
        self.basewrd2 = {}
        self.basewrd3 = {}
        self.__load_basewrds__()
        pass
    
    def __load_basewrds__(self):
        from os.path import join, dirname, abspath
        scroot = dirname(abspath(__file__))  
          
        word_filename = join(scroot, 'basewrd1.txt')
        self.__load_basewrd__(self.basewrd1, word_filename)
        word_filename = join(scroot, 'basewrd2.txt')
        self.__load_basewrd__(self.basewrd2, word_filename)
        word_filename = join(scroot, 'basewrd3.txt')
        self.__load_basewrd__(self.basewrd3, word_filename)
        
    def __load_basewrd__(self, word_dict, word_filename):
        f = open(word_filename, 'r')
        family = ''
        for line in f.readlines():
            oline = line
            if len(line) > 0:
                word = oline.strip().split()[0]
                if not line[0].isspace():
                   family = word
                word_dict[word] = family
                
        f.close()
        
    
    def range_word(self, word):
        word_range = 0
        upper_word = word.upper()
        family = upper_word
        if upper_word in self.basewrd1:
            word_range = 1
            family = self.basewrd1[upper_word]
        elif upper_word in self.basewrd2:
            word_range = 2
            family = self.basewrd2[upper_word]
        elif upper_word in self.basewrd3:
            word_range = 3
            family = self.basewrd3[upper_word]
        return (word_range, family)


if __name__ == "__main__":
    r = PyRange()
    print r.range_word('about')
    print r.range_word('YOUTHS')
    print r.range_word('VISIBLY')
    print r.range_word('WORM')
