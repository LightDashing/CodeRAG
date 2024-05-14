import torch
from langchain_core.documents.base import Document
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline

class BaseModelPipeline:
    
    def __init__(self, config: dict) -> None:
        self.model_config = config
        self.model = None
        self.tokenizer = None
        self.quant_config = None
        
        self.engine_not_implemented()
        
        self.load_model()
        
        self.create_pipeline()
        
    def engine_not_implemented(self):
        if self.model_config['loader'] != 'huggingface':
            raise NotImplementedError('BaseModelPipeline allows only huggingface!')
    
    def load_model(self) -> None:
        if self.model_config['use_quantization']:
            self.quant_config = BitsAndBytesConfig(bnb_4bit_compute_dtype=torch.bfloat16,
                                                   **self.model_config['quantization_config'])
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_config['llm_model']['name'])
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_config['llm_model']['name'],
                quantization_config=self.quant_config,
                **self.model_config['llm_model']['params'])
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_config['llm_model']['name'])
            self.model = AutoModelForCausalLM.from_pretrained(self.model_config['llm_model']['name'],
                                                              **self.model_config['llm_model']['params'])
    def create_pipeline(self):
        self.model_pipeline = pipeline(
            self.model_config['task'],
            model=self.model,
            tokenizer=self.tokenizer,
            **self.model_config['pipeline_params']
        )
        self.llm_pipeline = HuggingFacePipeline(pipeline=self.model_pipeline)
    