import importlib

from src.rag.ModelPipeline import BaseModelPipeline
from src.rag.DataPipeline import BaseDataPipeline
from src.utils.dynamic_import import import_class
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.memory.summary import BaseChatMemory
from langchain.chains.base import Chain
import re


class BaseLLMPipeline:
    
    def __init__(self, pipeline_config: dict, data_pipeline: BaseDataPipeline, 
                 model_pipeline: BaseModelPipeline) -> None:
        
        self.model_pipeline = model_pipeline
        self.data_pipeline = data_pipeline
        
        self.config = pipeline_config
        self.llm = None
        self.memory = None
        
        self.chain_config = self.config['chain']['params']
        
        self.create_llm()
        
        if self.config['use_memory']:
            self.create_memory()
            
        self.create_chain()
            
    def create_llm(self) -> None:
        self.llm = HuggingFacePipeline(pipeline=self.model_pipeline.transformers_pipeline)
    
    def create_memory(self) -> None:
        LLMMemory = import_class(self.config['llm_memory'], BaseChatMemory)
        self.memory = LLMMemory(llm=self.llm, **self.config['llm_memory']['params'])
        self.chain_config['memory'] = self.memory
    
    def create_chain(self) -> None:
        LLMChain = import_class(self.config['chain'], Chain)
        self.chain = LLMChain.from_llm(self.llm, retriever=self.data_pipeline.doc_store.as_retriever(), **self.chain_config)
    
    def ask_question(self, question: str) -> str:
        template = self.config['QA_prompt']
        template = re.sub(r"<QUESTION>", template, question, flags=re.MULTILINE)
        return self.chain(template)