from git import Repo

class GitRepo:
    
    repo: Repo
    branch: str
    path: str
    
    def __init__(self, path: str) -> None:
        self.repo = Repo(path)
    
    def change_branch(self, branch_name: str) -> None:
        self.branch = branch_name
        self.repo.active_branch = branch_name
        
        
class RemoteGitRepo(GitRepo):
    pass