import os
from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# Carrega variáveis de ambiente (.env)
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Caminho do documento
file_path = "app/data/dev_bio.txt"

# Carrega e divide o texto
loader = TextLoader(file_path)
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)
chunks = splitter.split_documents(documents)

# Gera embeddings com OpenAI
embeddings = OpenAIEmbeddings(api_key=openai_api_key)

# Cria e salva índice FAISS
vectorstore = FAISS.from_documents(chunks, embeddings)
vectorstore.save_local("faiss_index")

print("✅ Documento vetorizado e salvo em: faiss_index/")
