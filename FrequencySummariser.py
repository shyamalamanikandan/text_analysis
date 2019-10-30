from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
import urllib.request
import re
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import csv


lixifile="AFINN.txt"



class FrequencySummarizer:
    def __init__(self, min_cut=0.1, max_cut=0.9):
        self._min_cut = min_cut
        self._max_cut = max_cut
        self._stopwords = set(stopwords.words('english') + list(punctuation))

    def _compute_frequencies(self, word_sent):
        freq = defaultdict(int)
        for s in word_sent:
            for word in s:
                word = ''.join(re.findall("[a-zA-Z0-9]+", word))
                if word not in self._stopwords and word != '':
                    freq[word] += 1
        m = float(max(freq.values()))
        sents_idx = nlargest(10, freq, key=freq.get)
        #topwords = list(freq.values())
        #self._originalFreq = [topwords[i] for i in sents_idx]
        self._originalFreq = sents_idx
        for w in list(freq.keys()):
            freq[w] = freq[w]/m
            if freq[w] >= self._max_cut or freq[w] <= self._min_cut:
                del freq[w]
        return freq

    def summarize(self, text, n):
        lexi = {}
        total_score = []
        self._originalFreq = [0]
        with open(lixifile, 'r') as csvfile:
            lexiword = csv.reader(csvfile, delimiter='\t')
            for row in lexiword:
                lexi[row[0]] = int(row[1])
        sents = sent_tokenize(text)
        if len(sents) == 0:
            return ['Not enough content to perform analysis'], 0
        word_sent = [word_tokenize(s.lower()) for s in sents]
        print("word count",word_sent)
        self._freq = self._compute_frequencies(word_sent)
        ranking = defaultdict(int)
        for i,sent in enumerate(word_sent):
            for w in sent:
                if w in self._freq:
                    ranking[i] += self._freq[w]
                if w in lexi:
                    total_score.append(lexi[w])
        sents_idx = nlargest(n, ranking, key=ranking.get)
        polarity = 0 if len(total_score) == 0 else (sum(total_score) // len(total_score))
        return [sents[j] for j in sents_idx], polarity

    def getWordFreq(self):
        return self._originalFreq
    
                 

def Summariser(mytext):
    fs = FrequencySummarizer()
    print("fs",fs)
    summary, sentscore = fs.summarize(mytext, 1)
    """lenght_mytext=len(mytext.split(sep= " "))
    if(lenght_mytext < 10):
	    summary = "Not enough words" """
	    
    wordFreqs = fs.getWordFreq()
    return wordFreqs, summary, sentscore

    

if __name__ == '__main__':
    cmdargs = sys.argv
    result = Summariser(cmdargs[0])
    if result == [0]:
        print("Negative")
    else:
        print("Positive")
