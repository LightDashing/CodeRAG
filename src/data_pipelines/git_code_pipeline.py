from langchain_core.documents.base import Document
from src.data_pipelines.base import BaseDataPipeline
from src.utils.git_utils import GitManager
from src.indexer.indexer import BaseIndexer

from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.directory import DirectoryLoader
from langchain_community.document_loaders import GitLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.qdrant import Qdrant
#from langchain_community

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
    
    def create_splitters(self, **kwargs):
        pass
        # splitters = {}
        # for index in self.manager.index_repos:
        #     for filetype, paths in index.items():
                
        #         if splitter.get(filetype):
        #             continue
                
        #         if filetype in LANGUAGES:
        #             splitter = RecursiveCharacterTextSplitter.from_language(LANGUAGES.get(filetype),
        #                                                                     **kwargs.get('splitters', {}))
        #         else:
        #             splitter = RecursiveCharacterTextSplitter(**kwargs.get('splitters', {}))
                    
        #         splitters[filetype] = splitter
            
    def split_documents(self, loaded_documents: list[Document], **kwargs) -> None:
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
        if kwargs.get('doc_store', {}).get('collection_exists'):
            qdrant_args = kwargs['doc_store']
            return Qdrant.from_existing_collection(self.embedder_model, 
                                                   qdrant_args['path'],
                                                   qdrant_args['collection_name'])
        return Qdrant.from_documents(
            embedding=self.embedder_model,
            documents=self.documents_list, 
            **kwargs.get('doc_store', {}))
        
    def add_documents(self, documents: list[Document]):
        self.doc_store.add_documents(documents)
        
    def delete_documents(self, path_prefix: str):
        all_documents = self.doc_store.get_all_documents()
        document_ids_to_delete = [doc.metadata['id'] for doc in all_documents if doc.metadata.get('file_path', '').startswith(path_prefix)]
        self.qdrant_vector_store.delete_documents(document_ids_to_delete)