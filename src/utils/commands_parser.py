from src.utils.git_utils import GitManager
from src.rag.llm_pipelines import BaseLLMPipeline

class CommandsParser:
    
    llm_pipe : BaseLLMPipeline
    git_manager: GitManager
    
    def __init__(self, git_manager: GitManager, llm_pipeline: BaseLLMPipeline) -> None:
        self.git_manager = git_manager
        self.llm_pipe = llm_pipeline
    
    def parse_command(self):
        pass  
    
    def add_repo(self, repo_path: str, repo_name: str = None, auto_pull: bool = False):
        self.git_manager.add_repo(repo_path, repo_name, auto_pull)
    
    def delete_repo(self, repo_path: str, repo_name: str = None):
        self.git_manager.remove_repo(self, repo_path, repo_name)
    
    def rescan_documents(self):
        pass
    
    def __add_document(self):
        pass
    
    def __remove_document(self):
        pass