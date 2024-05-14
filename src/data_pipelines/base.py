from langchain_core.document_loaders.base import BaseLoader
from langchain_text_splitters.base import TextSplitter
from langchain_core.vectorstores import VectorStore
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_core.documents.base import Document
from src.utils.dynamic_import import import_class


class BaseDataPipeline:
    
    pipeline_config: dict
    doc_store: VectorStore
    loaders: list[BaseLoader] = []
    splitters: list[TextSplitter] = []
    documents_list: list[Document] = []

    def __init__(self, config: dict, embedder_model_name: str, **kwargs) -> None:
        self.pipeline_config = config
        self.pipeline_config['model_name'] = embedder_model_name #TODO: add model parameters
        
        self.loaders = self.create_loaders(**kwargs)
        self.splitters = self.create_splitters(**kwargs)
        self.embedder_model = self.create_embedding_model(**kwargs)
        
        raw_documents = self.load_documents()
        self.documents_list = self.split_documents(raw_documents)

        self.doc_store = self.create_doc_store(**kwargs)

    def create_loaders(self, **kwargs):
        loaders = []
        for loader in self.pipeline_config['doc_loading']: #['doc_loading']
            LoaderClass = import_class(loader, BaseLoader)
            new_loader = LoaderClass(**loader['params'])
            loaders.append(new_loader)
        return loaders
    
    def create_splitters(self, **kwargs):
        splitters = []
        for splitter in self.pipeline_config['doc_splitting']: #['doc_splitting']
            SplitterClass = import_class(splitter, TextSplitter)
            new_splitter = SplitterClass.from_language(**splitter['params'])
            splitters.append(new_splitter)
        return splitters
    
    def create_embedding_model(self, **kwargs):
        return HuggingFaceEmbeddings(model_name=self.pipeline_config['model_name'])
    
    def create_doc_store(self, **kwargs):
        doc_store_conf = self.pipeline_config['doc_storing']
        doc_store_conf['params']['embedding'] = self.embedder_model
        doc_store_conf['params']['documents'] = self.documents_list
        DocStoreClass = import_class(doc_store_conf, VectorStore)
        return DocStoreClass.from_documents(**doc_store_conf['params'])
    
    def load_documents(self, **kwargs) -> list[Document]:
        raw_documents_list = []
        for loader in self.loaders:
            raw_documents_list.append(loader.load())
        return raw_documents_list
    
    def split_documents(self, loaded_documents: list[Document], **kwargs) -> list[Document]:
        documents_list = []
        for splitter, doc_list in zip(self.splitters, loaded_documents):
            documents_list.extend(splitter.split_documents(doc_list))
        return documents_list
    
    def add_documents(self, documents: list[Document]):
        self.doc_store.add_documents(documents)
        
    def delete_documents_by_path(self, path_prefix: str):
        all_documents = self.doc_store.get_all_documents()
        document_ids_to_delete = [doc.metadata['id'] for doc in all_documents if doc.metadata.get('file_path', '').startswith(path_prefix)]
        self.doc_store.delete_documents(document_ids_to_delete)
        
    def delete_documents(self, documents_id: list[str]):
        self.doc_store.delete_documents(documents_id)     
        