from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain_core.runnables import RunnablePassthrough






# Load environment variables from .env file
load_dotenv()

embeddings_model = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))

app = FastAPI() 

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

transcript = ""

@app.post("/")
def get_item(youtube_link: dict):
    try: 
        loader = YoutubeLoader.from_youtube_url(
        youtube_link["youtubeLink"], add_video_info=False
        )
        transcript = loader.load()[0].page_content
        return transcript
    except Exception as e:
        print(f"Error: {e}")

@app.post("/summarize")
def summarize(text: dict):
    try: 
        #print(text["youtubeContent"])
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size=100,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False,
        )
        texts = text_splitter.split_text(text["youtubeContent"])

        template = """Provide the summary based only on the following YouTube video. Include all the important parts of the video and ignore the extra content. Ignore the video outro if it does not provide any information about the topic:

        {context}

        Summary:
        """
        prompt = ChatPromptTemplate.from_template(template)
        model = ChatOpenAI()

        chain = (
            {"context": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
        )

        response = chain.invoke(texts)
        return response

    except Exception as e:
        print(f"Error: {e}")


    
