from config_loader import Config
from src.data_pipelines.base import BaseDataPipeline
from src.model_pipelines.base import BaseModelPipeline
from src.model_pipelines.llama_cpp_pipeline import LlamaModelPipeline
from src.rag.llm_pipelines import BaseLLMPipeline
from src.utils.git_utils import GitManager
from src.data_pipelines.git_code_pipeline import GitCodePipeline


app_config = Config.get_instance().config

def git_test():
    manager = GitManager()
    manager.update_config()
    data_pipeline = GitCodePipeline(app_config, "mixedbread-ai/mxbai-embed-large-v1",
                                manager, doc_store={"path": "data/local_qdrant/",
                                                       "collection_name": "main",
                                                       "collection_exists": True})
    #model_pipeline = BaseModelPipeline(app_config['generation']['model'])
    model_pipeline = LlamaModelPipeline(app_config['generation']['model'])
    llm_pipeline = BaseLLMPipeline(app_config['generation']['llm_pipeline'],
                                   data_pipeline, model_pipeline)
    print(llm_pipeline.ask_question('What types of encryption is used in async-rsa-chat project?'))
    #print([document.metadata['file_path'] for document in data_pipe.doc_store.similarity_search("class server asyncio")])


def base_presentation():
    data_pipeline = BaseDataPipeline(config=app_config['indexing'],
                        embedder_model_name='mixedbread-ai/mxbai-embed-large-v1')
    model_pipeline = BaseModelPipeline(app_config['generation']['model'])
    llm_pipeline = BaseLLMPipeline(app_config['generation']['llm_pipeline'],
                                   data_pipeline, model_pipeline)
    print(llm_pipeline.ask_question('What splitter is used in sample.py for text splitting?')['answer'])