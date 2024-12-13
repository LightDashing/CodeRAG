from src.data_pipelines.base import BaseDataPipeline
from src.utils.git_utils import GitManager, GitRepo
from src.utils.dynamic_import import import_class
from config_loader import Config

from langchain_core.documents.base import Document
from langchain_core.vectorstores import VectorStore
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.directory import DirectoryLoader
from langchain_community.document_loaders import GitLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.qdrant import Qdrant
from qdrant_client.http.models.models import Record as QdrantRecord
#from langchain_community

APP_CONFIG = Config.get_instance()

LANGUAGES = {
    ".cpp": ['CPP'],
    ".hpp": ['CPP'],
    ".cxx": ['CPP'],
    ".hxx": ['CPP'],
    ".cc": ['CPP'],
    ".hh": ['CPP'],
    ".go": ['GO'],
    ".java": ['JAVA'],
    ".kt": ['KOTLIN'],
    ".kts": ['KOTLIN'],
    ".js": ['JS'],
    ".ts": ['TS'],
    ".php": ['PHP'],
    ".phtml": ['PHP'],
    ".php3": ['PHP'],
    ".php4": ['PHP'],
    ".php5": ['PHP'],
    ".phps": ['PHP'],
    ".proto": ['PROTO'],
    ".py": ['PYTHON'],
    ".rst": ['RST'],
    ".rb": ['RUBY'],
    ".rs": ['RUST'],
    ".scala": ['SCALA'],
    ".sc": ['SCALA'],
    ".swift": ['SWIFT'],
    ".md": ['MARKDOWN'],
    ".markdown": ['MARKDOWN'],
    ".tex": ['LATEX'],
    ".html": ['HTML'],
    ".htm": ['HTML'],
    ".sol": ['SOL'],
    ".cs": ['CSHARP'],
    ".cob": ['COBOL'],
    ".cbl": ['COBOL'],
    ".ccp": ['COBOL'],
    ".cobol": ['COBOL'],
    ".c": ['C'],
    ".h": ['C'],
    ".lua": ['LUA'],
    ".pl": ['PERL'],
    ".pm": ['PERL'],
    ".t": ['PERL'],
}


class GitCodePipeline(BaseDataPipeline):

    def __init__(self, config: dict, embedder_model_name: str, 
                 manager: GitManager, **kwargs) -> None:
        
        self.manager = manager
        
        super().__init__(config, embedder_model_name, **kwargs)
        
    def create_loaders(self, **kwargs):
        loaders = []
        for repo in self.manager.repos:
            loader = GitLoader(repo.path, branch=repo.branch, **kwargs.get('loaders', {}))
            loaders.append(loader)
        return loaders
    
    def load_new_repo(self, repo: GitRepo, **kwargs) -> list[Document]:
        loader = GitLoader(repo.path, branch=repo.branch)
        self.loaders.append(loader)
        
        raw_documents = loader.load()
        split_documents = self.split_documents([raw_documents])
        self.documents_list.extend(split_documents)
        return split_documents
    
    def create_splitters(self, **kwargs):
        # Not needed there, logic already in split_documents
        pass
            
    def split_documents(self, loaded_documents: list[Document], **kwargs) -> list[Document]:
        split_documents = []
        for doc_list in loaded_documents:
            for doc in doc_list:
                filetype = doc.metadata['file_type']
                if filetype in LANGUAGES:
                    splitter = RecursiveCharacterTextSplitter.from_language(LANGUAGES[filetype][0].lower(),
                                                                            **kwargs.get('splitters', {}))
                else:
                    splitter = RecursiveCharacterTextSplitter(**kwargs.get('splitters', {}))
                
                split_doc = splitter.split_documents([doc])
                split_documents.extend(split_doc)
        return split_documents
            
    def create_doc_store(self, **kwargs):
        doc_store = self.pipeline_config['indexing']['doc_storing']
        DocStoreClass = import_class(doc_store, VectorStore)
        
        if kwargs.get('doc_store', {}).get('collection_exists'):
            qdrant_args = kwargs['doc_store']
            return DocStoreClass.from_existing_collection(self.embedder_model, 
                                                   qdrant_args['path'],
                                                   qdrant_args['collection_name'])
        self.pipeline_config['indexing']['doc_storing']['collection_exists'] = True
        APP_CONFIG.write_config(self.pipeline_config)
        return DocStoreClass.from_documents(
            embedding=self.embedder_model,
            documents=self.documents_list, 
            **kwargs.get('doc_store', {}))
        
    def delete_documents_by_path(self, path_prefix: str):
        if isinstance(self.doc_store, Qdrant):
            self.__delete_document_by_path_qdrant(path_prefix)
        else:
            raise NotImplementedError("Right now can delete documents only in Qdrant")
    
    def __delete_document_by_path_qdrant(self, path_prefix: str):
        # I HATE LANGCHAIN, THEY CHANGE THEIR API EACH SECOND
        # there is no reason that this ad-hoc code will work at all next time yo run it
        deletion_doc = []
        for item in self.doc_store.client.scroll("main"):
            if isinstance(item, list):
                for doc in item:
                    if isinstance(doc, QdrantRecord):
                        if doc.payload.get('metadata', {}).get('file_path', '').startswith(path_prefix):
                            deletion_doc.append(doc.payload.get('metadata')['id'])

        #if len(deletion_doc) == 0: TODO: find what is wrong with this
        #    raise ValueError(f"No documents were found by {path_prefix}!")
        self.doc_store.delete(deletion_doc)