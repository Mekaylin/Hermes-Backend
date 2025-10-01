import os
from typing import Optional, List, Dict, Any
from openai import OpenAI

# Simple wrapper around OpenAI Retrieval/Vector Store operations
class SemanticClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise RuntimeError('OPENAI_API_KEY not set in environment')
        self.client = OpenAI(api_key=self.api_key)

    def create_vector_store(self, name: str) -> Dict[str, Any]:
        return self.client.vector_stores.create(name=name)

    def upload_file_to_store(self, vector_store_id: str, file_path: str, attributes: Dict[str, Any] = None) -> Dict[str, Any]:
        with open(file_path, 'rb') as f:
            # upload_and_poll convenience: create and wait for embedding
            return self.client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store_id,
                file=f,
                attributes=attributes or {}
            )

    def search(self, vector_store_id: str, query: str, max_results: int = 10, attribute_filter: Dict[str, Any] = None) -> Dict[str, Any]:
        return self.client.vector_stores.search(
            vector_store_id=vector_store_id,
            query=query,
            max_num_results=max_results,
            attribute_filter=attribute_filter
        )

    def synthesize_with_model(self, formatted_sources: str, query: str, model: str = 'gpt-4o-mini') -> str:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers using only the provided sources."},
            {"role": "user", "content": f"Sources: {formatted_sources}\n\nQuery: '{query}'"}
        ]
        resp = self.client.chat.completions.create(model=model, messages=messages)
        return resp.choices[0].message.content


semantic_client = None

def get_semantic_client() -> SemanticClient:
    global semantic_client
    if semantic_client is None:
        semantic_client = SemanticClient()
    return semantic_client
