from online_part import prompt_with_context
from offline_part import (
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
            middleware=[prompt_with_context]
        )
    
    def offline_pipeline(self, docs):
        splits = split_text(self.text_splitter, docs)
        doc_ids = update_db(self.vector_store, splits)
        
    def online_pipeline(self, query):
        for step in self.agent.stream(
            {"messages": [{"role": "user", "content": query}]},
            stream_model="values"
        ):
            step["messages"][-1].pretty_print()