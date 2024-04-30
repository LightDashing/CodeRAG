#from git import Repo
import uuid
import json
import subprocess
import os
import copy


class GitRepo:
    
    #repo: Repo
    branch: str
    path: str
    local_name: str
    
    def __init__(self, path: str, name: str = None,
                 auto_pull: bool = False, branch: str = None) -> None:
        
        self.path = path
            
        if name:
            self.local_name = name
        else:
            self.local_name = uuid.uuid4()
            
        self.branch = self.get_current_branch()
        
        if auto_pull:
            self.pull_repo()
        
        if branch:
            self.change_branch(branch)
    
    def change_branch(self, branch_name: str) -> None:
        output = subprocess.run(['git', '-C', self.path, 'checkout', branch_name], capture_output=True)
        self.branch = branch_name
        print(output.stdout.decode().strip())
            
    def pull_repo(self) -> None:
        output = subprocess.run(['git', '-C', self.path, 'pull'], capture_output=True)
        print(output.stdout.decode().strip())
        
    def get_current_branch(self) -> None:
        output = subprocess.run(['git', '-C', self.path, 'branch', '--show-current'], capture_output=True)
        self.branch = output.stdout.decode('utf-8').strip()
        
    def fetch_repo(self) -> None:
        output = subprocess.run(['git', '-C', self.path, 'fetch'], capture_output=True)
        print(output.stdout.decode().strip())
        
    def __repr__(self) -> str:
        return f"({self.local_name})@({self.path}):({self.branch})"
    
    
class GitManager:
    
    repos: list[GitRepo]
    repos_cfg_path: str = './data/repos.json'
    remote_save_path: str = './data/remote_saved/'
    repo_config: dict
    generated_repo: dict
    
    def __init__(self, repos_cfg_path: str = None, remote_save_path: str = None) -> None:
        
        if repos_cfg_path:
            self.repos_cfg_path = repos_cfg_path
        if remote_save_path:
            self.remote_save_path 
        
        self.load_config()
        self.repos, self.generated_repo = self.load_repos()
    
    def load_config(self) -> None:
        with open(self.repos_cfg_path, "r") as f:
            self.repo_config = json.load(f)
            
    def load_repos(self) -> tuple[list[GitRepo], dict[list[dict]]]:
        """_summary_

        Returns:
            tuple[list[GitRepo], list[dict]]: _description_
        """
        repos_list = []
        generated_repo = copy.copy(self.repo_config)
        generated_repo['repos'] = []
        for repo in self.repo_config['repos']:
            
            if repo.get('remote_path'):
                repo_path = repo.get('remote_path')
                
                local_path = repo.get(
                    'local_path', 
                    f"{self.remote_save_path}")
                
                if not os.path.exists(local_path):
                    os.makedirs(local_path)
                
                #TODO: in future rewrite for local input and then running subprocess
                output = subprocess.run(['git', '-C', local_path, 'clone', repo_path], 
                                      input=self.repo_config['passphrase'].encode('utf-8'), capture_output=True)
                print(output.stdout.decode())
                print(output.stderr.decode())
                
                repo['path'] = local_path + repo_path[repo_path.rfind('/') + 1:repo_path.rfind('.')]
                repo['remote_path'] = ''
    
            new_repo = GitRepo(repo['path'], repo.get('name'), repo.get('pull'))
            repos_list.append(new_repo)
            
            repo['name'] = new_repo.local_name
            generated_repo['repos'].append(repo)
            
        return repos_list, generated_repo
    
    def update_config(self) -> None:
        with open("data/repos.generated.json", "w") as f:
            json.dump(self.generated_repo, f)
            
    
if __name__ == "__main__":
    pass