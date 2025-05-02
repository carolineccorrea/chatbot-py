# app/rag/rag_pipeline.py

import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()

# 1) Carrega o template externo
prompt_path = Path(__file__).parent / "prompt_template.txt"
prompt_str = prompt_path.read_text(encoding="utf-8")
prompt_template = PromptTemplate.from_template(prompt_str)

# 2) Inicializa o LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.2,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# 3) Cria a cadeia simples, definindo explicitamente a saída como "answer"
chain = LLMChain(
    llm=llm,
    prompt=prompt_template,
    output_key="answer"
)

# 4) Carrega todo o contexto estático (arquivos .txt em app/data)
data_dir = Path(__file__).parent.parent / "data"
_context = "\n\n".join(
    p.read_text(encoding="utf-8")
    for p in sorted(data_dir.glob("*.txt"))
)

# Histórico em memória por sessão
session_histories: dict[str, list[tuple[str, str]]] = {}

def ask_with_context(question: str, session_id: str) -> dict:
    """
    Executa o LLMChain injetando `context` + `question` no prompt.
    Mantém histórico de cada sessão em memória.
    """
    # 1) Recupera histórico (não usado no prompt, mas salva o diálogo)
    chat_history = session_histories.get(session_id, [])

    # 2) Prepara inputs para o template
    inputs = {
        "context": _context,
        "question": question
    }

    # 3) Invoke retorna um dict com chave "answer"
    result: dict = chain.invoke(inputs)
    answer = result["answer"].strip()

    # 4) Salva no histórico
    session_histories[session_id] = chat_history + [(question, answer)]

    return {
        "answer": answer,
        "history": session_histories[session_id]
    }
