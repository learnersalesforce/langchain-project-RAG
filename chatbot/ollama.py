#LANGCHAIN_API_KEY="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"
#OPENAI_API_KEY=""
#LANGCHAIN_PROJECT="Langchain Tutorials"

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama


import streamlit as st 
import os

from dotenv import load_dotenv

load_dotenv()


#langsmith
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]="true"

## creating chatbot

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant, Please provide the response to the user queries."),
        ("user", "Question : {question}")
    ]
)

## streamlit framwork

st.title("Langchain demo with Llama2 App")
input_text = st.text_input("Search the topic you want")

## Ollama2 llm call
llm = Ollama(model="llama2")
output_parser = StrOutputParser()

## chain
chain = prompt|llm|output_parser

if input_text: 
    st.write(chain.invoke({'question':input_text}))