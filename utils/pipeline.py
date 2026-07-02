from utils.online_part import make_prompt_with_context
from utils.offline_part import (
    create_model,
    create_embeddings,
    create_text_splitter,
    connect_to_pgvector,
    split_text,
    update_db,
)
from langchain.agents import create_agent


class Pipeline:
    def __init__(self):
        self.model = create_model()
        self.embeddings = create_embeddings()
        self.text_splitter = create_text_splitter()
        self.vector_store = connect_to_pgvector(
            self.embeddings,
            "my-docs",
        )
        self.agent = create_agent(
            self.model,
            tools=[],
            middleware=[make_prompt_with_context(self.vector_store)]
        )
    
    def offline_pipeline(self, docs):
        splits = split_text(self.text_splitter, docs)
        doc_ids = update_db(self.vector_store, splits)
        return len(splits)
        
    def online_pipeline(self, query):
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": query}]}
        )
        return result["messages"][-1].content