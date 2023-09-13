from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
import os
import glob

def load_documents(filepaths):
  documents = []
  for filepath in filepaths:
    if filepath.endswith(".pdf"):
      documents.extend(PyPDFLoader(filepath).load())
    if filepath.endswith(".txt"):
      documents.extend(TextLoader(filepath, encoding = 'UTF-8').load())
  return documents

def load_openai_key():
  with open("./openai_api_key", "r") as openai_key_file:
    os.environ['OPENAI_API_KEY'] = openai_key_file.read().strip()

if __name__ == "__main__":

  # Carrega chave da OpenAI 
  load_openai_key()

  # Cria e alimenta o Vector DB Chroma
  document_filepaths = glob.glob("input//*")
  documents = load_documents(document_filepaths)
  splitter = RecursiveCharacterTextSplitter(chunk_size=1800, chunk_overlap=200)
  pages = splitter.split_documents(documents)
  embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
  store = Chroma.from_documents(pages, embeddings, persist_directory="./chroma_db")

