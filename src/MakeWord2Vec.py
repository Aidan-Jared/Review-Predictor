import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from gensim.models.word2vec import Word2Vec
import spacy
from keras.models import Sequential
from keras.layers import LSTM, Dense, Bidirectional, Embedding
from keras.layers import TimeDistributed
from VectorPipeline import Corpus2Vecs
import argparse
import json

class Word2Vect(object):
    def __init__(self, nlp, fileName=None):
        self.nlp = nlp
        self.fileName = fileName
    
    def _clean_text(self,X):
        cleaned_text = Corpus2Vecs(nlp, modelFile=None).clean_text(X)
        return cleaned_text
    
    def fit(self, X, min_count = 1, window = 5, epoch = 200, size = 100, load = None):
        cleaned_text = self._clean_text(X)
        if load is None:
            word_model = Word2Vec(
                cleaned_text,
                min_count=min_count,
                window=window,
                iter=epoch,
                size=size)
            if self.fileName != None:
                word_model.save(self.fileName)
            else:
                return word_model
        else:
            word_model = Word2Vec.load(load)
            word_model.train(cleaned_text, total_examples=word_model.corpus_count, epochs = epoch)
            if self.fileName != None:
                word_model.save(self.fileName)
            else:
                return word_model



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read in Files to make word2vec model')
    parser.add_argument('--config', type=str)
    parser.add_argument('--corpusFile', type=str)
    parser.add_argument('--modelFile', type=str)
    parser.add_argument('--load', type=str)
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)['Word2Vec']

    nlp = spacy.load('en_core_web_sm', disable=["parser", "tagger"])
    table = pq.read_table(args.corpusFile)
    df = table.to_pandas()
    corpus = df['review_body'].values

    W2V = Word2Vect(nlp, fileName=args.modelFile)
    W2V.fit(corpus, min_count=config['min_count'], window=config['window'], epoch=config['epoch'], size=config['size'], load=args.load)