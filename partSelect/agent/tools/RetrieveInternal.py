import json
import numpy as np
from langchain_openai import OpenAIEmbeddings
import json
import faiss

class RetrieveInternal:
    embeddings_model = OpenAIEmbeddings(openai_api_key="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")
    
    def __init__(self, path) -> None:
        with open(path + "/scrapData.json","r") as file:
            self.internal_docs = json.load(file)
        self.vecStore = faiss.read_index(path + '/vecStore.faiss')
            
    
    def retrieve_internal(self, input: str, max_length: int = 1000, max_size: int = 1) -> str:
        input_embedding = self.embeddings_model.embed_documents([input])
        _, indices = self.vecStore.search(np.array(input_embedding), max_size)
        ret = ''
        append_idx = 0
        while len(ret) < max_length and append_idx < max_size:
            ret += self.internal_docs[indices[0][append_idx]] + '\n'
            append_idx += 1
        return ret

if __name__ == "__main__":
    retriever = RetrieveInternal(path='../data')
    print(retriever.retrieve_internal("my dishwasher will not dry"))