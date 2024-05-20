import pytest
import os
import shutil
import json
from src.model_pipelines.base import BaseModelPipeline
from src.model_pipelines.llama_cpp_pipeline import LlamaModelPipeline
from src.utils.git_utils import GitManager
from src.data_pipelines.base import BaseDataPipeline
from src.rag.llm_pipelines import BaseLLMPipeline  

#TODO: ADD torch.Generator for manual seed, pass CPU seed generator
#TODO: make more tests and make them look better  

def test_download_repos():
    manager = GitManager("data/unit_test/repos.json", "data/unit_test/remote_saved/")
    manager.add_repo("https://github.com/rasbt/LLMs-from-scratch.git", "LLMfromScratch", True)
    assert os.path.exists("data/unit_test/remote_saved/LLMs-from-scratch") == True
    assert os.path.exists("data/unit_test/remote_saved/fastfetch") == True
    shutil.rmtree("data/unit_test/remote_saved")
    
@pytest.fixture(scope="session")
def data_config():
    with open("data/unit_test/data_config.json") as f:
        config = json.load(f) 
    return config


@pytest.fixture(scope="session")
def model_config():
    with open("data/unit_test/model_config.json") as f:
        config = json.load(f) 
    return config


@pytest.fixture(scope="session")
def rag_config():
    with open("data/unit_test/rag_config.json") as f:
        config = json.load(f) 
    return config


@pytest.fixture(scope="session")
def data_pipe(data_config):
    return BaseDataPipeline(data_config, "mixedbread-ai/mxbai-embed-large-v1")


@pytest.fixture(scope="session")
def model_pipe(model_config):
    return LlamaModelPipeline(model_config)  

    
class TestLLM:

    @pytest.mark.dependency()
    def test_document_loading(self, data_config):
        BaseDataPipeline(data_config, "mixedbread-ai/mxbai-embed-large-v1")
        assert os.path.exists("data/unit_test/vector") == True
    
    @pytest.mark.dependency()    
    def test_model_loading(self, model_config):
        LlamaModelPipeline(model_config)
        assert os.path.exists("data/unit_test/cache_llm") == True  
    
    @pytest.mark.dependency(depends=['TestLLM::test_document_loading', 'TestLLM::test_model_loading'])
    @pytest.mark.parametrize(
        "test_question,expected_answer",
        [
            ("What splitter is used in sample.py for text splitting?", "RecursiveCharacterTextSplitter"),
            ("Which vectorstore is used in sample.py?", "Chroma"),
            ("What LLM model is used for RAG in sample.py?", "gpt-3.5-turbo")
        ])
    def test_llm_answering(self, test_question: str, expected_answer: str, rag_config, data_pipe, model_pipe):
        llm_pipeline = BaseLLMPipeline(rag_config, data_pipe, model_pipe)
        assert llm_pipeline.ask_question(test_question)['answer'].find(expected_answer) != -1
        
    def clear_data(self):
        shutil.rmtree("data/unit_test/vector")
        shutil.rmtree("data/unit_test/cache_llm")