import os
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain

load_dotenv()

# Carrega template de prompt externo
with open("app/rag/prompt_template.txt", "r", encoding="utf-8") as f:
    prompt_str = f.read()

prompt_template = PromptTemplate.from_template(prompt_str)

# Inicializa o modelo LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.2,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Carrega o índice FAISS previamente criado
vectorstore = FAISS.load_local(
    "faiss_index",
    OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY")),
    allow_dangerous_deserialization=True
)

# Constrói a cadeia de recuperação conversacional
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(search_type="similarity", k=3),
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt": prompt_template}
)

# Histórico simples em memória por sessão
session_histories: dict[str, list[tuple[str, str]]] = {}

def ask_with_context(question: str, session_id: str) -> dict:
    """
    Executa o pipeline RAG mantendo o histórico de cada sessão.
    - question: pergunta do usuário
    - session_id: identificador único da sessão
    Retorna:
      {
        "answer": resposta gerada,
        "sources": lista de conteúdos dos documentos de origem
      }
    """
    chat_history = session_histories.get(session_id, [])

    result = qa_chain.invoke({
        "question": question,
        "chat_history": chat_history
    })

    answer = result["answer"].strip()
    sources = [doc.page_content for doc in result.get("source_documents", [])]

    session_histories[session_id] = chat_history + [(question, answer)]

    return {
        "answer": answer,
        "sources": sources
    }
