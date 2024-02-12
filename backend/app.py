from fastapi import FastAPI, Depends
from typing import Optional
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.schema import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain import hub
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain



# Load environment variables from .env file
load_dotenv()

embeddings_model = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))

chat = ChatOpenAI(openai_api_key=os.getenv('OPENAI_API_KEY'))

app = FastAPI() 


# Define a global variable
global_variable = "Hello, Global Variable!"
def get_global_variable():
    return global_variable


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)


@app.post("/")
def get_item(youtube_link: dict):
    try: 
        print(youtube_link)
        loader = YoutubeLoader.from_youtube_url(
        youtube_link["youtubeLink"], add_video_info=False
        )

        docs = loader.load()
        global global_variable
        global_variable = docs
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size=100,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False,
        )
        splits = text_splitter.split_documents(docs)
        vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(), persist_directory="./chroma_db")
        
        # # Assign to the singleton instance
        # vector_store_instance.vectorstore = vectorstore

        # retriever = vectorstore.as_retriever()

        transcript = docs[0].page_content  
        return transcript
    except Exception as e:
        print(f"Error: {e}")

@app.post("/summarize")
def summarize(global_var: str = Depends(get_global_variable)):
    try: 
        chain = load_summarize_chain(chat, chain_type="stuff") 
        docs = global_var
        response = chain.invoke(docs)
        print(response)
        return response

    except Exception as e:
        print(f"Error: {e}")


@app.post("/askquestions")
def askquestions(question: dict, global_var: str = Depends(get_global_variable)):
    try:
        REDIS_URL = "redis://localhost:6379/0"
        print(question['question'])

        #this docs is for context   
        docs = global_var
        vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=OpenAIEmbeddings())
        retriever = vectorstore.as_retriever()

        template = """Use the following pieces of context to answer the questions.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Use three sentences maximum and keep the answer as concise as possible.
        Always say "thanks for asking!" at the end of the answer.

        {context}

        Helpful Answer:"""

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", template),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),
            ]
        )
        
        chain = prompt | ChatOpenAI()

        chain_with_history = RunnableWithMessageHistory(
            chain,
            lambda session_id: RedisChatMessageHistory(session_id, url=REDIS_URL),
            input_messages_key="question",
            history_messages_key="history",
        )

        response = chain_with_history.invoke(
            {"context": retriever, "question": question["question"]},
            config={"configurable": {"session_id": "bafsa"}}
        )
        print (response)
    except Exception as e:
        print(f"Error: {e}")
        