from langchain_openrouter import ChatOpenRouter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Инициализация модели
def create_model(model_name: str = "owl-alpha") -> ChatOpenRouter:
    return ChatOpenRouter(
        model_name,
        )

# Инициализация эмбединг модели
def create_embeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        encode_kwargs={"normalize_embeddings": True}
    ) -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=model_name,
        encode_kwargs=encode_kwargs,
        )

# Создание подключения к векторной дб
def connect_to_pgvector(embeddings, collection_name: str) -> PGVector:
    return PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection="postgresql+psycopg://...",
    )

# текст сплитер
def create_text_splitter(
    chunk_size: int=1000,  # chunk size (characters)
    chunk_overlap: int=200,  # chunk overlap (characters)
    add_start_index: bool=True,  # track index in original document
) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=add_start_index, 
    )
    
def split_text(text_splitter, docs: list[Document]):
    return text_splitter.split_documents(docs)

def update_db(vector_store, all_splits):
    return vector_store.add_documents(documents=all_splits)