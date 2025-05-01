import os
from dotenv import load_dotenv

from langchain.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain

load_dotenv()

# Carrega o prompt externo
with open("app/rag/prompt_template.txt", "r", encoding="utf-8") as f:
    prompt_str = f.read()

prompt_template = PromptTemplate.from_template(prompt_str)

# Inicializa o modelo LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.2,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Carrega índice FAISS
vectorstore = FAISS.load_local(
    folder_path="faiss_index",
    embeddings=OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY")),
    allow_dangerous_deserialization=True
)

# Cria o chain conversacional sem memória interna
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(search_type="similarity", k=3),
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt": prompt_template}
)

# Armazena histórico por sessão (em memória para teste)
session_histories = {}

def ask_with_context(question: str, session_id: str) -> dict:
    # Pré-processamento leve
    if len(question.strip().split()) <= 2:
        question = f"Continue falando sobre Caroline Correa. {question}"

    chat_history = session_histories.get(session_id, [])

    # Consulta com histórico
    response = qa_chain.invoke({
        "question": question,
        "chat_history": chat_history
    })

    answer = response["answer"].strip()
    sources = [doc.page_content for doc in response.get("source_documents", [])]

    # Atualiza histórico local
    session_histories[session_id] = chat_history + [(question, answer)]

    return {
        "answer": answer,
        "sources": sources
    }
