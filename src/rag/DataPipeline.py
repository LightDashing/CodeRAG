from langchain_core.document_loaders.base import BaseLoader
from langchain_text_splitters.base import TextSplitter
from langchain_core.vectorstores import VectorStore
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import importlib


class BaseDataPipeline:

    def __init__(self, config: dict, embedder_model_name: str) -> None:
        self.pipeline_config = config
        self.pipeline_config['model_name'] = embedder_model_name #TODO: add model parameters

        self.loaders = []
        self.splitters = []
        self.doc_store = None

        if isinstance(config['doc_loading'], list):
            for loader in config['doc_loading']:
                new_loader = self.create_loader(loader)
                self.loaders.append(new_loader)
        else:
            self.loaders.append(self.create_loader(config['doc_loading']))

        if isinstance(config['doc_splitting'], list):
            for splitter in config['doc_splitting']:
                new_loader = self.create_code_splitter(splitter)
                self.loaders.append(new_loader)
        else:
            self.splitters.append(self.create_code_splitter(config['doc_splitting']))

        print(self.pipeline_config['model_name'])
        self.embedder_model = self.create_huggingface_embedder(self.pipeline_config)
        config['doc_storing']['params']['embedding'] = self.embedder_model

        raw_documents_list = []
        self.documents_list = []

        for loader in self.loaders:
            raw_documents_list.append(loader.load())

        #TODO: make better logic for splitting, now 1 doc sublist = 1 splitter

        for splitter, doc_list in zip(self.splitters, raw_documents_list):
            self.documents_list.extend(splitter.split_documents(doc_list))

        config['doc_storing']['params']['documents'] = self.documents_list

        self.doc_store = self.create_doc_store(config['doc_storing'])

    @staticmethod
    def create_loader(loader_args: dict) -> BaseLoader:
        loader_module = importlib.import_module(loader_args['module'])

        DocumentLoader = getattr(loader_module, loader_args['name'])

        if not issubclass(DocumentLoader, BaseLoader):
            raise TypeError(f"{DocumentLoader.__name__} is not subclass of langchain's BaseLoader")

        return DocumentLoader(**loader_args['params'])

    @staticmethod
    def create_code_splitter(splitter_args: dict) -> TextSplitter:
        splitter_module = importlib.import_module(splitter_args['module'])

        SplitterLoader = getattr(splitter_module, splitter_args['name'])

        if not issubclass(SplitterLoader, TextSplitter):
            print(SplitterLoader.__base__)
            raise TypeError(f"{SplitterLoader.__name__} is not subclass of langchain's TextSplitter")

        return SplitterLoader.from_language(**splitter_args['params'])

    def create_splitter(self) -> None:
        raise NotImplemented("Only code splitters for now")

    @staticmethod
    def create_huggingface_embedder(config: dict):
        return HuggingFaceEmbeddings(model_name=config['model_name'])

    def create_embedder(self):
        raise NotImplementedError("Only HuggingFaceEmbeddings works for now")

    @staticmethod
    def create_doc_store(document_store_args: dict) -> VectorStore:
        document_module = importlib.import_module(document_store_args['module'])

        DocumentStore = getattr(document_module, document_store_args['name'])
        if not issubclass(DocumentStore, VectorStore):
            raise TypeError(f"{DocumentStore.__name__} is not subclass of langchain's VectorStore")

        return DocumentStore.from_documents(**document_store_args['params'])
