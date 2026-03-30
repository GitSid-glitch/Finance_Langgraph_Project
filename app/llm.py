import os
from langchain_groq import ChatGroq
llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    temperature=float(os.getenv("GROQ_TEMPERATURE", "0.2")),
)