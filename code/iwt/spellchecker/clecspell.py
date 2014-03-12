# -*- coding: utf-8 -*-
import metaphone

MAX_EDIT_DISTANCE = 4
METAPHONE_KEY_LENGTH = 4
EDIT_WEIGHT = -4
PHONE_WEIGHT = -1
FIRST_WORD_WEIGHT = -2
FREQUENCY_WEIGHT = -10000

PREFIX = ['con', 'de', 'dis', 'in', 'pro', 're', 'un']
SUFFIX = ["'s", 'able', 'd', 'ed', 'en', 'ens', 'er', 'ers', 'es', 'est', 'ication', 'ications',
          'ied', 'ier', 'iers', 'ies', 'iest', 'ieth', 'iness', 'ing', 'ings', 'ion', 'ions',
          'ive', 'ly', 'ment', 'ness', 'r', 'rs', 's', 'st', 'th']

__metaclass__ = type

class Spell:
    
    def __init__(self):
        from os.path import join, dirname, abspath
        scroot = dirname(abspath(__file__))        	
        dicFilename = join(scroot, 'data/clec.dict')
        self.get_dict_words(dicFilename)
        
    def get_dict_words(self, dict):
        """Load the dict"""
        self.dict_words = {}
        with open(dict) as dict_file:
            for line in dict_file:
                word = line.strip('\n').split(',')
                self.dict_words[word[0]] = int(word[1])

    def get_edit_distance(self, first, second):
        """Find the Levenshtein distance between two strings."""
        if len(first) > len(second):
            first, second = second, first
        if len(second) == 0:
            return len(first)
        first_length = len(first) + 1
        second_length = len(second) + 1
        distance_matrix = [[0] * second_length for x in range(first_length)]
        for i in range(first_length):
            distance_matrix[i][0] = i
        for j in range(second_length):
            distance_matrix[0][j] = j
        for i in xrange(1, first_length):
            for j in range(1, second_length):
                deletion = distance_matrix[i - 1][j] + 1
                insertion = distance_matrix[i][j - 1] + 1
                substitution = distance_matrix[i - 1][j - 1]
                if first[i - 1] != second[j - 1]:
                    substitution += 1
                distance_matrix[i][j] = min(insertion, deletion, substitution)
        return distance_matrix[first_length - 1][second_length - 1]

    def get_edit_distance_score(self, distance):
        if distance <= MAX_EDIT_DISTANCE:
            return (MAX_EDIT_DISTANCE + 2 - distance) * EDIT_WEIGHT;
        return 0
    
    def get_metaphone_level(self, first, second):
        (first_pri, first_sec) = metaphone.dm(first)
        (second_pri, second_sec) = metaphone.dm(second)
        level = 0
        if first_pri == second_pri:
            level = 4
        if first_sec == second_pri or first_pri == second_sec:
            level = 2
        if first_sec == second_sec:
            level = 1
        return level

    def get_metaphone_level_score(self, level):
        return level * PHONE_WEIGHT
    
    def get_length_score(self, first, second):
        return - abs(len(first) - len(second));
    
    def get_inflexion_score(self, first, second):
        score = 1.0
        for pre in PREFIX:
            length = len(pre)
            if(first[0:length] == pre and second[0:length] == pre):
                score += 1
        for suf in SUFFIX:
            length = len(suf)
            if(first[-length:] == suf and second[-length:] == suf):
                score += 1
        return score
        
    def get_frequency_score(self, word):
        frequency = float(self.dict_words[word])
        return frequency / FREQUENCY_WEIGHT
    
    def get_candidate_words(self, error_word, result_num=1):
        candidates = []
        for word in self.dict_words:
            edit_distance = self.get_edit_distance(error_word, word)
            phone_level = self.get_metaphone_level(error_word, word)
            length_score = self.get_length_score(error_word, word)
            if error_word[0] == word[0]:
                first_score = FIRST_WORD_WEIGHT
            else:
                first_score = 0
            if phone_level != 0 or edit_distance <= MAX_EDIT_DISTANCE:
                score = self.get_frequency_score(word) + self.get_edit_distance_score(edit_distance) + self.get_metaphone_level_score(phone_level)
                + self.get_inflexion_score(error_word, word) + length_score + first_score
                candidates.append([word, score])
        candidates.sort(cmp=lambda t1, t2: cmp(t1[1], t2[1]))
        return candidates[0 : result_num]
        
    def check_word(self, word):
        word_lower = word.lower()
        #长度为一时直接认为正确，全数字认为正确
        if len(word) == 1 or word.isdigit():
            return True
        if self.dict_words.has_key(word_lower):
            return True
        else:
            return False
        
    def correct_word(self, word):
        word_lower = word.lower()
        if self.check_word(word_lower):
            return word_lower
        else:
            return self.get_candidate_words(word_lower)[0][0]
        
if __name__ == "__main__":
    sp = Spell()    
    print sp.check_word('123')
    print sp.correct_word('goos')
    print sp.get_candidate_words('gooss', 5)
