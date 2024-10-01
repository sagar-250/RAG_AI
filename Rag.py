from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
# from langchain.chains import RetrievalQA
from langchain.chains import LLMChain
from nltk.tokenize import word_tokenize
from dotenv import load_dotenv
import os 
import pathlib
from utils import hybrid_search,text_split
import time
# import pickle


load_dotenv()
os.getenv("PINECONE_API_ENV")
pinecone_api=os.getenv("PINECONE_API_KEY")
os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0.3,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)



root_dir = pathlib.Path(__file__).parent

folder_path=str(root_dir /'data'/'en' )

            

def init():
    documents = []
    doc_names = []

    start_time = time.time()
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                documents.append(file.read())
                doc_names.append(filename)
    print(len(documents))  
    # Tokenize documents

    chunks=text_split(documents)
    print(len(chunks))

        
    tokenized_corpus = [word_tokenize(chunk.lower()) for chunk in chunks]
        
    end_time = time.time()
    execution_time = end_time - start_time  # Calculate the difference
    print(f"Execution Time: {execution_time:.4f} seconds")

    return chunks,tokenized_corpus

chunks,tokenized_corpus=init()

##not feasable to integratte for hybrid search as have to get similarities score with all embeded vectors to combine score, very high computation 

# # save chunks as vector list takes time did this and saved it as .plk 

# start_time = time.time()
# word2vec(chunks)
# end_time = time.time()
# execution_time = end_time - start_time  # Calculate the difference
# print(f"Execution Time: {execution_time:.4f} seconds")

# # loading vector list

# vector_file_path=str(root_dir /'vector_db.pkl' )


# with open('C:/Sagar/AI/Hackathon/Task1/vector_db.pkl', 'rb') as file:
#     chunk_vecs = pickle.load(file)

template_for_accuracy="""
query:{query}
COntext:{retrived_document_information}
You are a Medical expert MCQ answer teller. Given the above context, it is your job to tell The correct option.return only the index of correct annswer

Example-
C
D
A

**DONT ANSWER QUESTION IF THERE IS NO RELAVANT CONTEXT AND REPLY THAT YOU DONT HAVE RELAVANT DOCUMENT**
dont give excess information further to it
"""

template="""
query:{query}
COntext:{retrived_document_information}
You are a Medical expert MCQ answer teller. Given the above context, it is your job to tell The correct answer.
**DONT ANSWER QUESTION IF THERE IS NO RELAVANT CONTEXT **
"""
quiz_generation_prompt = PromptTemplate(
input_variables=["retrived_document_information", "query"],
template=template)
chain=LLMChain(llm=llm,prompt=quiz_generation_prompt,output_key="answer")


def RAG(query,top_n=10,alpha=0.4):
    
    info=hybrid_search(query,top_n,chunks,tokenized_corpus,alpha)
    
    response=chain({
                    "retrived_document_information":info,
                    "query":query})
                
    print(response.get("answer"))
    return response.get("answer")

    