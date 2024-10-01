from nltk.tokenize import word_tokenize
import nltk
from rank_bm25 import BM25Okapi
import os
import pathlib

root_dir = pathlib.Path(__file__).parent.parent

folder_path=str(root_dir /'data'/'en' )

            

def relavent_documents(query,top_n):
    documents = []
    doc_names = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                documents.append(file.read())
                doc_names.append(filename)


    print(len(documents))  
    # Tokenize documents
    tokenized_corpus = [word_tokenize(doc.lower()) for doc in documents]

    # Create BM25 model
    bm25 = BM25Okapi(tokenized_corpus)

    # Input query
    # query = "A 23-year-old pregnant woman at 22 weeks gestation presents with burning upon urination. She states it started 1 day ago and has been worsening despite drinking more water and taking cranberry extract. She otherwise feels well and is followed by a doctor for her pregnancy. Her temperature is 97.7°F (36.5°C), blood pressure is 122/77 mmHg, pulse is 80/min, respirations are 19/min, and oxygen saturation is 98 percent on room air. Physical exam is notable for an absence of costovertebral angle tenderness and a gravid uterus. Which of the following is the best treatment for this patient?"
    tokenized_query = word_tokenize(query.lower())

    # Get BM25 scores for the query
    doc_scores = bm25.get_scores(tokenized_query)

    # Get the top 3 most relevant documents based on BM25 score
    # top_n = 1  # Adjust as needed
    top_n_docs = sorted(enumerate(doc_scores), key=lambda x: x[1], reverse=True)[:top_n]

    print(top_n_docs)
    # Concatenate the content of the top-ranked documents
    relevant_docs = " ".join([documents[idx] for idx, score in top_n_docs])

    return relevant_docs
