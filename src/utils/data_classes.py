from pydantic import BaseModel

class AddRepoRequest(BaseModel):
    repo_path: str
    repo_name: str
    auto_pull: bool