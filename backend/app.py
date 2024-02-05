from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import YoutubeLoader

app = FastAPI() 

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
    loader = YoutubeLoader.from_youtube_url(
    youtube_link["youtubeLink"], add_video_info=False
)
    loader.load()
    return loader.load()[0].page_content
