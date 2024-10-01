from rank_bm25 import BM25Okapi
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import pathlib


def normalize_list(values):
    min_val = min(values)
    max_val = max(values)
    
    # Handle the case when all values are the same to avoid division by zero
    if max_val == min_val:
        return [0 for _ in values]  # or [1 for _ in values], depending on the use case

    # Apply min-max normalization
    return [(x - min_val) / (max_val - min_val) for x in values]


def text_split(documents,chunk_size=200,chunk_overlap = 20):
    all_documents_concatenated = "\n".join(documents)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap = chunk_overlap)
    text_chunks = text_splitter.split_text(all_documents_concatenated)
    return text_chunks



    
def BM25_search(query,tokenized_corpus):
    

    bm25 = BM25Okapi(tokenized_corpus)

    # Input query
  
    tokenized_query = word_tokenize(query.lower())

    # Get BM25 scores for the query
    doc_scores = bm25.get_scores(tokenized_query)

    # Get the top 3 most relevant documents based on BM25 score
    # top_n = 1  # Adjust as needed
    print()

    return normalize_list(doc_scores)



def TF_IDF(query,chunks):
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(chunks)
    query_vector=tfidf_vectorizer.transform([query])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    # print(cosine_similarities)
    return(cosine_similarities)
    

    
    
        
        
def hybrid_search(query,top_n,chunks,tokenized_corpus,alpha):

    score1=TF_IDF(query,chunks)

    # print(score1)
    score2=BM25_search(query,tokenized_corpus)
    
    # print(score2)
    score_hybrid= alpha*np.array(score1) + (1-alpha)*np.array(score2)
    
    # print(score_hybrid)
    top_n_docs = sorted(enumerate(score_hybrid), key=lambda x: x[1], reverse=True)[:top_n]

    print(type(top_n_docs))
    # Concatenate the content of the top-ranked documents
    relevant_docs = ".".join([chunks[idx] for idx, score in top_n_docs])
    print(relevant_docs)
    return relevant_docs
    
       
# chunk=['my name is sagar bag,i live in delhi',' i like to play basket ball,and watch anime','i study at indian institute of technology Madras']

# query='where do i study'

# hybrid_search(query,2,chunk,0.5)