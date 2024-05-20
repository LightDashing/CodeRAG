from src.utils.git_utils import GitManager
from src.rag.llm_pipelines import BaseLLMPipeline
from src.data_pipelines.git_code_pipeline import GitCodePipeline
import sys

class GitCommandsParser:
    
    llm_pipe : BaseLLMPipeline
    git_manager: GitManager
    
    def __init__(self, git_manager: GitManager, llm_pipeline: BaseLLMPipeline, 
                 data_pipeline: GitCodePipeline) -> None:\
                     
        self.git_manager = git_manager
        self.llm_pipe = llm_pipeline
        self.data_pipeline = data_pipeline
    
    def parse_command(self, command: str):
        command_args = command.split(" ")
        if command_args[0].lower().startswith("/add"):
            repo_path = command_args[1]
            repo_name, auto_pull = None, None
            if len(command_args) == 3:
                repo_name = command_args[2]
            elif len(command_args) == 4:
                auto_pull = command_args[3]
            self.add_repo(repo_path, repo_name, auto_pull)
        elif command_args[0].lower().startswith("/del"):
            repo_path = command_args[1]
            repo_name = None
            if len(command_args) == 3:
                repo_name = command_args[2]
            self.delete_repo(repo_path, repo_name)
        elif command_args[0].lower().startswith("/pull"):
            repo_path = command_args[1]
            repo_name = None
            if len(command_args) == 3:
                repo_name = command_args[2]
            self.pull_repo(repo_path, repo_name)
        elif command_args[0].lower().startswith("/exit") or command_args[0].lower().startswith("/quit"):
            sys.exit(0)
        elif command_args[0].lower().startswith("/fetch"):
            repo_path = command_args[1]
            repo_name = None
            if len(command_args) == 3:
                repo_name = command_args[2]
            self.pull_repo(repo_path, repo_name)
        elif command_args[0].lower().startswith("/branch"):
            repo_path = command_args[1]
            repo_name = None
            if len(command_args) == 3:
                repo_name = command_args[2]
                branch = command_args[3]
            else:
                branch = command_args[2]
            self.change_branch(repo_path, branch, repo_name)


          
    
    def add_repo(self, repo_path: str, repo_name: str = None, auto_pull: bool = False):
        repo = self.git_manager.add_repo(repo_path, repo_name, auto_pull)
        self.git_manager.update_config()
        documents = self.data_pipeline.load_new_repo(repo)
        self.data_pipeline.add_documents(documents)
        self.llm_pipe.create_chain()
        
    def pull_repo(self, repo_path: str, repo_name: str = None):
        self.git_manager.pull_repo(repo_path, repo_name)
        repo = self.data_pipeline.delete_documents(repo_path)
        documents = self.data_pipeline.load_new_repo(repo)
        self.data_pipeline.add_documents(documents)
    
    def delete_repo(self, repo_path: str, repo_name: str = None):
        self.git_manager.remove_repo(repo_path, repo_name)
        self.data_pipeline.delete_documents_by_path(repo_path)
        self.llm_pipe.create_chain()
        self.git_manager.update_config()
        
    def fetch_repo(self, repo_path: str, repo_name: str = None):
        self.git_manager.fetch_repo(repo_path, repo_name)
        
    def change_branch(self, repo_path: str, branch: str, repo_name: str = None):
        self.git_manager.change_branch(repo_path, branch, repo_name)
        self.git_manager.update_config()