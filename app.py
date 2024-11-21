import uvicorn
from fastapi import FastAPI
from config_loader import Config
from src.model_pipelines.base import BaseModelPipeline
from src.model_pipelines.llama_cpp_pipeline import LlamaModelPipeline
from src.rag.llm_pipelines import BaseLLMPipeline
from src.utils.git_utils import GitManager
from src.utils.commands_parser import GitCommandsParser
from src.data_pipelines.git_code_pipeline import GitCodePipeline


app = FastAPI()
app_llm_config = Config.get_instance().config

manager = GitManager()
manager.update_config()
doc_store_conf = app_llm_config['indexing']['doc_storing']
data_pipeline = GitCodePipeline(app_llm_config, "mixedbread-ai/mxbai-embed-large-v1",
                        manager, doc_store={"path": doc_store_conf['params']['path'],
                                            "collection_name": doc_store_conf['params']['collection_name'],
                                            "collection_exists": doc_store_conf['collection_exists']})

if app_llm_config['generation']['model']['loader'] == 'huggingface':
    model_pipeline = BaseModelPipeline(app_llm_config['generation']['model'])
elif app_llm_config['generation']['model']['loader'] == 'llamacpp':
    model_pipeline = LlamaModelPipeline(app_llm_config['generation']['model'])
llm_pipeline = BaseLLMPipeline(app_llm_config['generation']['llm_pipeline'],
                            data_pipeline, model_pipeline)
use_memory = app_llm_config['generation']['llm_pipeline']['use_memory']
command_manager = GitCommandsParser(manager, llm_pipeline, data_pipeline)

@app.post("/add_repo")
async def add_repo(repo_path: str, repo_name: str, auto_pull:bool):
    command_manager.add_repo(repo_path, repo_name, auto_pull)
    return {"success": True}

@app.delete("/remove_repo")
async def remove_repo(repo_path: str, repo_name: str = None):
    command_manager.delete_repo(repo_path, repo_name)
    return {"success": True}

@app.patch("/pull_repo")
async def pull_repo(repo_path: str, repo_name: str = None):
    command_manager.pull_repo(repo_path, repo_name)
    return {"sucess": True}

@app.patch("/fetch")
async def fetch_repo(repo_path: str, repo_name: str = None):
    command_manager.fetch_repo(repo_path, repo_name)
    return {"sucess": True}

@app.patch("/branch")
async def change_branch(repo_path: str, repo_name: str = None):
    command_manager.change_branch(repo_path, repo_name)
    return {"success": True}
    
@app.get("/generate")
async def generate_response(user_input: str):
    answer = llm_pipeline.ask_question(user_input)
    return {"success": True, "generated": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)