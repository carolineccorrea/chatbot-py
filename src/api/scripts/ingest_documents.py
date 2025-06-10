from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

loader = TextLoader("app/data/dev_bio.txt", encoding="utf-8")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=100
)

docs = text_splitter.split_documents(documents)

vectorstore = FAISS.from_documents(
    docs,
    OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
)

vectorstore.save_local("faiss_index")
