import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableSequence
from langchain_core.messages import AIMessage, HumanMessage

load_dotenv()

# Carrega o template externo
prompt_path = Path(__file__).parent / "prompt_template.txt"
prompt_str = prompt_path.read_text(encoding="utf-8")
prompt_template = PromptTemplate.from_template(prompt_str)

# Inicializa o modelo
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.2,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Carrega contexto dos arquivos .txt
data_dir = Path(__file__).parent.parent / "data"
_context = "\n\n".join(
    p.read_text(encoding="utf-8")
    for p in sorted(data_dir.glob("*.txt"))
)

# Memória e chains por sessão
session_memories: dict[str, ConversationBufferMemory] = {}
session_chains: dict[str, RunnableSequence] = {}

def ask_with_context(question: str, session_id: str) -> dict:
    """
    Executa o pipeline com contexto e memória de conversação por sessão.
    Injeta saudação apenas na primeira interação.
    """
    # Cria memória e pipeline se não existirem
    if session_id not in session_memories:
        memory = ConversationBufferMemory(
            memory_key="history",
            input_key="question",
            return_messages=True
        )
        session_memories[session_id] = memory
        session_chains[session_id] = prompt_template | llm

    memory = session_memories[session_id]
    chain = session_chains[session_id]

    # Verifica se é a primeira interação da sessão
    is_first_interaction = len(memory.buffer_as_messages) == 0

    # Executa chain com contexto e pergunta
    input_dict = {
        "context": _context,
        "question": question,
        "history": memory.buffer_as_messages
    }

    answer = chain.invoke(input_dict).content.strip()

    # Injeta saudação se for a primeira interação
    if is_first_interaction:
        saudacao = "Oi! Seja bem-vindo(a)! 🚀\n\n"
        answer = saudacao + answer

    # Atualiza memória com a conversa
    memory.chat_memory.add_user_message(question)
    memory.chat_memory.add_ai_message(answer)

    # Constrói histórico como lista de tuplas
    messages = memory.buffer_as_messages
    history_tuples = []
    for i in range(0, len(messages), 2):
        if i + 1 < len(messages):
            q = messages[i].content
            a = messages[i + 1].content
            history_tuples.append((q, a))

    return {
        "answer": answer,
        "history": history_tuples
    }
