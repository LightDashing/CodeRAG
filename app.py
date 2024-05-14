#import argparse
import json
import os
from src.simple_rag_pipeline import base_test, git_test
from config_loader import Config
from src.model_pipelines.base import BaseModelPipeline
from src.model_pipelines.llama_cpp_pipeline import LlamaModelPipeline
from src.rag.llm_pipelines import BaseLLMPipeline
from src.utils.git_utils import GitManager
from src.utils.commands_parser import GitCommandsParser
from src.data_pipelines.git_code_pipeline import GitCodePipeline


app_config = Config.get_instance().config


#[APP_CONIFG = json.load("config.json")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "your_token"
def app():
    if app_config['mode_testing']:
       base_test()
    else:
        manager = GitManager()
        manager.update_config()
        doc_store_conf = app_config['indexing']['doc_storing']
        data_pipeline = GitCodePipeline(app_config, "mixedbread-ai/mxbai-embed-large-v1",
                                manager, doc_store={"path": doc_store_conf['params']['path'],
                                                    "collection_name": doc_store_conf['params']['collection_name'],
                                                    "collection_exists": doc_store_conf['collection_exists']})
        
        if app_config['generation']['model']['loader'] == 'huggingface':
            model_pipeline = BaseModelPipeline(app_config['generation']['model'])
        elif app_config['generation']['model']['loader'] == 'llamacpp':
            model_pipeline = LlamaModelPipeline(app_config['generation']['model'])
        llm_pipeline = BaseLLMPipeline(app_config['generation']['llm_pipeline'],
                                   data_pipeline, model_pipeline)
        use_memory = app_config['generation']['llm_pipeline']['use_memory']
        command_manager = GitCommandsParser(manager, llm_pipeline, data_pipeline)
    
        while True:
            print("Input your questions. \nCommands starts with / \nYou can get list of available commands using /help")
            question = input("Enter: ")
            if question.startswith('/'):
                command_manager.parse_command(question)
            else:
                answer = llm_pipeline.ask_question(question)
                if use_memory:
                    print(f"Question: {answer['question']}\nHistory: {answer['chat_history']}\nAnswer: {answer['answer']}")
                else:
                    print(f"Question: {answer['question']}\nAnswer: {answer['answer']}")
                #if use_memory and len(llm_pipeline.memory) > 20: # More than 15 messages?
                #    #llm_pipeline.llm_pipeline.memory.clear()
                #    pass

if __name__ == "__main__":
    #manager = GitManager()
    #app()
    #Main entry point of app.
    manager = GitManager()
    manager.update_config()
    doc_store_conf = app_config['indexing']['doc_storing']
    data_pipeline = GitCodePipeline(app_config, "mixedbread-ai/mxbai-embed-large-v1",
                            manager, doc_store={"path": doc_store_conf['params']['path'],
                                                "collection_name": doc_store_conf['params']['collection_name'],
                                                "collection_exists": doc_store_conf['collection_exists']})
    print(data_pipeline.doc_store.similarity_search('Which observation space is used in flappy bird reinforcement learning project?'))
