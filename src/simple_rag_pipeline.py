from config_loader import Config
import importlib
from langchain.document_loaders.base import BaseLoader
from langchain_text_splitters.base import TextSplitter
from langchain.embeddings.huggingface import HuggingFaceEmbeddings


app_config = Config.get_instance().config


def main(run_config):
    loader = create_loader()


def create_loader(**loader_args: dict):
    document_conf = app_config['indexing']['doc_loading']
    
    loader_module = importlib.import_module(document_conf['module'])
    loader_args.update(document_conf['config'])
    
    DocumentLoader = getattr(loader_module, document_conf['name'])
    
    if not issubclass(BaseLoader, DocumentLoader):
        raise TypeError(f"{DocumentLoader.__name__} is not subclass of langchain.BaseLoader")
    
    return DocumentLoader(**loader_args)


def create_code_splitter(**splitter_args: dict):
    splitter_conf = app_config['indexing']['doc_loading']
    
    splitter_module = importlib.import_module(splitter_conf['module'])
    splitter_args.update(splitter_conf['config'])
    
    SplitterLoader = getattr(splitter_module, splitter_conf['name'])
    
    if not issubclass(TextSplitter, SplitterLoader):
        raise TypeError(f"{SplitterLoader.__name__} is not subclass of langchain.TextSplitter")
    
    return SplitterLoader.from_language(**splitter_args)


def create_splitter() -> None:
    raise NotImplemented("Only code splitters for now")


def create_huggingface_embedder(**embedder_args: dict):
     return HuggingFaceEmbeddings(model_name=embedder_args['model_name'])
 
 
def create_embedder(**embedder_args: dict):
    raise NotImplementedError("Only HuggingFaceEmbeddings works for now")