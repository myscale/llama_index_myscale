from typing import Dict, List
from pathlib import Path

from llama_index import download_loader
from llama_index import Document
UnstructuredReader = download_loader("MarkdownReader")
loader = UnstructuredReader()
def load_and_parse_files(file_row: Dict[str, Path]) -> List[Dict[str, Document]]:
    documents = []
    file = file_row["path"]
    if file.is_dir():
        return []
    # Skip all non-html files like png, jpg, etc.
    if file.suffix.lower() == ".md":
        loaded_doc = loader.load_data(file=file)
        loaded_doc[0].extra_info = {"path": str(file)}
        documents.extend(loaded_doc)
    return [{"doc": doc} for doc in documents]


from llama_index.node_parser import MarkdownNodeParser
from llama_index.data_structs import Node
def convert_documents_into_nodes(documents: Dict[str, Document]) -> List[Dict[str, Node]]:
    parser = MarkdownNodeParser()
    document = documents["doc"]
    nodes = parser.get_nodes_from_documents([document])
    return [{"node": node} for node in nodes]


from langchain.embeddings.huggingface import HuggingFaceEmbeddings
class EmbedNodes:
    def __init__(self):
        self.embedding_model = HuggingFaceEmbeddings(
            # Use all-mpnet-base-v2 Sentence_transformer.
            # This is the default embedding model for LlamaIndex/Langchain.
            model_name="sentence-transformers/all-mpnet-base-v2",
            model_kwargs={},
            # Use GPU for embedding and specify a large enough batch size to maximize GPU utilization.
            # Remove the "device": "cuda" to use CPU instead.
            encode_kwargs={"batch_size": 100}
        )

    def __call__(self, node_batch: Dict[str, List[Node]]) -> Dict[str, List[Node]]:
        nodes = node_batch["node"]
        text = [node.text for node in nodes]
        embeddings = self.embedding_model.embed_documents(text)
        assert len(nodes) == len(embeddings)

        for node, embedding in zip(nodes, embeddings):
            node.embedding = embedding
        return {"embedded_nodes": nodes}