import nltk
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer, word_tokenize
from nltk.stem import PorterStemmer
import base64
import requests
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from gensim.models import KeyedVectors
from scipy import spatial
import gurobipy as gp
from gurobipy import GRB

import gensim.downloader as api
model = api.load('word2vec-google-news-300')


def preprocess(doc):
    tagged_doc = nltk.tag.pos_tag(doc.split()) # Split each document into words (or "tags")
    edited_sentence = [word for word,tag in tagged_doc if tag not in ['NNP','NNPS']] # remove the proper nouns, given by the classification NNP (for singular proper nouns) and NNPS (for plural proper nouns)
    
    # remove all the punctuation marks.
    tokenizer = RegexpTokenizer(r'\w+') 
    processed_doc = tokenizer.tokenize(' '.join(edited_sentence))

    # remove all the stop words.
    processed_doc = [x.lower() for x in processed_doc]  
    processed_doc = [i for i in processed_doc if i not in stopwords.words('english')]

    return processed_doc


def frequency_D_calc(doc):
    processed_doc = preprocess(doc)
    # frequency of occurrences of each word.
    freqency_D = {i: processed_doc.count(i)/len(processed_doc) for i in processed_doc}
    D = set(processed_doc)
    return freqency_D, D

def distance(D1, D2):

    # cosine distance between D1 and D2 
    distance = {(i,j): spatial.distance.cosine(model[i],model[j]) for i in D1 for j in D2}
    return distance


def score_dissimilarity(D1, D2):
    
    D1 = set(D1)
    D2 = set(D2)
    D2 = D2 - set([i for i in D2 if i not in model]) # in case some of the words from the book are not in the word2vec data
    D1 = D1 - set([i for i in D1 if i not in model])

    freqency_D1 = {i: list(D1).count(i)/len(D1) for i in D1}
    freqency_D2 = {i: list(D2).count(i)/len(D2) for i in D2}

    if len(D2) < 5: # if the sentence is too small, we set a high dissimilarity, effectively ignoring it
        return 1

    m = gp.Model("Text_similarity")
    distance = {(i,j): spatial.distance.cosine(model[i],model[j]) for i in D1 for j in D2}

    # Variables. Adjust the bounds here
    f = m.addVars(D1,D2,name="f",lb=0,ub=1)

    # Minimize
    m.ModelSense = GRB.MINIMIZE
    m.setObjective(sum(f[w,w_prime]*distance[w,w_prime] for w in D1 for w_prime in D2))

    # Add the constraints
    m.addConstrs(f.sum(w, '*') ==  freqency_D1[w] for w in D1)
    m.addConstrs(f.sum('*', w_prime) == freqency_D2[w_prime] for w_prime in D2)

    m.setParam('OutputFlag', 0)
    m.optimize()

    return m.ObjVal


def read_and_preprocess_book():
    master = "https://raw.githubusercontent.com/Gurobi/modeling-examples/master/text_dissimilarity/PG1661_raw.txt"
    content = requests.get(master)
    content = content.text
    content = content.replace('\n',' ')
    content = content.replace('_',' ')
    content = content.replace('\r','')
    sentences = list(map(str.strip, content.split(".")))[19:]
    processed_sentences = [] # list of all sentences

    for s in sentences:
        processed_sentences.append(preprocess(s))
    return sentences, processed_sentences

    










    