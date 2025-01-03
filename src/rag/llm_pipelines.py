from src.model_pipelines.base import BaseModelPipeline
from src.data_pipelines.base import BaseDataPipeline
from src.utils.dynamic_import import import_class
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.memory.summary import BaseChatMemory
from langchain.chains.base import Chain
from langchain_core.prompts import PromptTemplate


class BaseLLMPipeline:
    
    base_prompt: PromptTemplate
    
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
            
        self.base_prompt = PromptTemplate(input_variables=["context", "question"], template=self.config['QA_prompt'])
        self.chain_config['combine_docs_chain_kwargs'] = {"prompt":self.base_prompt}
        self.create_chain()
       
            
    def create_llm(self) -> None:
        self.llm = self.model_pipeline.llm_pipeline
    
    def create_memory(self) -> None:
        LLMMemory = import_class(self.config['llm_memory'], BaseChatMemory)
        self.memory = LLMMemory(llm=self.llm, **self.config['llm_memory']['params'])
        self.chain_config['memory'] = self.memory
    
    def create_chain(self) -> None:
        LLMChain = import_class(self.config['chain'], Chain)
        self.chain = LLMChain.from_llm(self.llm, retriever=self.data_pipeline.doc_store.as_retriever(), **self.chain_config)
    
    def ask_question(self, question: str) -> str:
        response = self.chain.invoke({"question": question})
        return response