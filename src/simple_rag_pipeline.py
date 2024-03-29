from config_loader import Config
import importlib
from langchain_core.document_loaders.base import BaseLoader
from langchain_text_splitters.base import TextSplitter
from langchain_core.vectorstores import VectorStore
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
#from langchain_community.document_loaders.text import TextLoader
#from langchain.vectorstores.qdrant import Qdrant


app_config = Config.get_instance().config


def main(run_config):
    Loader = create_loader(file_path="data/sample.py")
    Splitter = create_code_splitter(language='python', chunk_size=512)
    Embedding_model = create_huggingface_embedder(model_name="mixedbread-ai/mxbai-embed-large-v1")
    docs = Loader.load()
    docs = Splitter.split_documents(docs)
    Qdrant = create_doc_store(documents=docs, embedding=Embedding_model,
                              path="data/local_qdrant", collection_name='my_docs')
    
    #LD = TextLoader("data/sample.py").load()


def create_loader(**loader_args: dict):
    document_conf = app_config['indexing']['doc_loading']
    
    loader_module = importlib.import_module(document_conf['module'])
    loader_args.update(document_conf['config'])
    
    DocumentLoader = getattr(loader_module, document_conf['name'])
    
    if not issubclass(DocumentLoader, BaseLoader):
        raise TypeError(f"{DocumentLoader.__name__} is not subclass of langchain's BaseLoader")
    
    return DocumentLoader(**loader_args)


def create_code_splitter(**splitter_args: dict):
    splitter_conf = app_config['indexing']['doc_splitting']
    
    splitter_module = importlib.import_module(splitter_conf['module'])
    splitter_args.update(splitter_conf['config'])
    
    SplitterLoader = getattr(splitter_module, splitter_conf['name'])
    
    if not issubclass(SplitterLoader, TextSplitter):
        print(SplitterLoader.__base__)
        raise TypeError(f"{SplitterLoader.__name__} is not subclass of langchain's TextSplitter")
    
    return SplitterLoader.from_language(**splitter_args)


def create_splitter() -> None:
    raise NotImplemented("Only code splitters for now")


def create_huggingface_embedder(**embedder_args: dict):
     return HuggingFaceEmbeddings(model_name=embedder_args['model_name'])
 

def create_doc_store(**document_store_args: dict):

    document_store_conf = app_config['indexing']['doc_storing']
    document_module = importlib.import_module(document_store_conf['module'])
    document_store_args.update(document_store_conf['config'])
    
    DocumentStore = getattr(document_module, document_store_conf['name'])
    if not issubclass(DocumentStore, VectorStore):
        raise TypeError(f"{DocumentStore.__name__} is not subclass of langchain's VectorStore")
    
    return DocumentStore.from_documents(**document_store_args)

 
 
def create_embedder(**embedder_args: dict):
    raise NotImplementedError("Only HuggingFaceEmbeddings works for now")