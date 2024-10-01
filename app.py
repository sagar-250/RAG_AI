from fastapi import FastAPI,File, UploadFile
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pathlib
import os
import uvicorn 
import PyPDF2
from Rag import RAG,init

root_dir = pathlib.Path(__file__).parent

pdf_path=str(root_dir /'data'/'en'/'extra.pdf' )
txt_path=str(root_dir /'data'/'en'/'extra.txt' )


app= FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    query:str

class PDF(BaseModel):
    text:str    
@app.post('/rag/query')
def get_response(req:Query):
    response=RAG(req.query)
    return{"Response":response}

@app.post("/rag/savepdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Save the uploaded PDF file
        pdf_file_location = pdf_path
        with open(pdf_file_location, "wb") as pdf_file:
            pdf_file.write(await file.read())

        # Read the content of the PDF and clean it
        cleaned_content = ""
        with open(pdf_file_location, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text() or ''  # Extract text from each page
                # Remove non-UTF-8 characters
                cleaned_content += ''.join(char for char in text if ord(char) < 128)  # Keep only ASCII characters

        # Save the cleaned content as a text file
        txt_file_location = txt_path
        with open(txt_file_location, "w", encoding="utf-8") as txt_file:
            txt_file.write(cleaned_content)
        
        init()   

        return JSONResponse(content={"message": "PDF uploaded and cleaned successfully.", "txt_file": str(txt_file_location)})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    


uvicorn.run(app,host="127.0.0.1",port=8000)        