from config import load_env_config
from utils.pipeline import Pipeline
from utils.service import exctract_from_md, exctract_from_pdf
from fastapi import FastAPI, File, UploadFile, HTTPException
from contextlib import asynccontextmanager
import shutil
from pydantic import BaseModel
import logging
logger = logging.getLogger(__name__)

load_env_config()

class Query(BaseModel):
    user_query: str = ""

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pipeline = Pipeline()
    app.state.UPLOAD_DIRECTORY = "data"
    yield
    
    
app = FastAPI(lifespan=lifespan)


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"{app.state.UPLOAD_DIRECTORY}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    if file.content_type == "application/pdf":
        try:
            docs = exctract_from_pdf(file_location)
        except Exception as e:
            logger.exception("PDF exctraction failed for %s", file_location)
            raise HTTPException(status_code=422, detail="Could not read the PDF file") 
    else:
        raise HTTPException(status_code=415, detail="Only PDF files are supported")
    
    chunks = app.state.pipeline.offline_pipeline(docs)
    return {
        "status": "ok",
        "chunks": chunks,
    }
    

@app.post("/ask/")
def ask(query: Query):
    user_query = query.user_query
    if user_query == '':
        raise HTTPException(400, detail="Empty user query")
    else:
        answer = app.state.pipeline.online_pipeline(user_query)
        return {
            "status": "ok",
            "answer": answer,
            }

