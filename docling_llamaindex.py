import os
from pathlib import Path
from tempfile import mkdtemp
from warnings import filterwarnings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from dotenv import load_dotenv
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.readers.docling import DoclingReader
from llama_index.vector_stores.milvus import MilvusVectorStore

load_dotenv()

filterwarnings(action="ignore", category=UserWarning, module="pydantic")
filterwarnings(action="ignore", category=FutureWarning, module="easyocr")
os.environ["TOKENIZERS_PARALLELISM"] = "false"


hugging_face_api_key = os.getenv("HUGGING_FACE_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=pinecone_api_key)

EMBED_MODEL = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
MILVUS_URI = str(Path(mkdtemp()) / "docling.db")
GEN_MODEL = HuggingFaceInferenceAPI(
    token=hugging_face_api_key,
    model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
)
SOURCE = "https://arxiv.org/pdf/2408.09869"  # Docling Technical Report
QUERY = "Which are the main AI models in Docling?"

embed_dim = len(EMBED_MODEL.get_text_embedding("hi"))

reader = DoclingReader()
node_parser = MarkdownNodeParser()

vector_store = MilvusVectorStore(
    uri=str(Path(mkdtemp()) / "docling.db"),  # or set as needed
    dim=embed_dim,
    overwrite=True,
)
index = VectorStoreIndex.from_documents(
    documents=reader.load_data(SOURCE),
    transformations=[node_parser],
    storage_context=StorageContext.from_defaults(vector_store=vector_store),
    embed_model=EMBED_MODEL,
)
result = index.as_query_engine(llm=GEN_MODEL).query(QUERY)
print(f"Q: {QUERY}\nA: {result.response.strip()}\n\nSources:")
display([(n.text, n.metadata) for n in result.source_nodes])