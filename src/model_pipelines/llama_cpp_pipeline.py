from src.model_pipelines.base import BaseModelPipeline
from langchain_community.llms.llamacpp import LlamaCpp
from huggingface_hub import hf_hub_download
import os


class LlamaModelPipeline(BaseModelPipeline):
    
    def __init__(self, config: dict) -> None:
        self.llama_config = config['llm_model']
        super().__init__(config)
        
    def load_model(self) -> None:
        # Make sure the model path is correct for your system!
        if self.llama_config['remote_model']:
            self.download_model()
        else:
            llama_cpp_params = self.llama_config['llama_cpp']
            model = LlamaCpp(**llama_cpp_params)
            self.model = model
        
    def download_model(self) -> None:
        llama_cpp_params = self.llama_config['remote_model']
        
        if not os.path.exists(llama_cpp_params['local_dir']):
            os.makedirs(llama_cpp_params['local_dir'])
        
        model_filepath = hf_hub_download(
            repo_id=llama_cpp_params['repo_id'],
            filename=llama_cpp_params['filename'],
            local_dir=llama_cpp_params['local_dir'],
        )
        
        llama_cpp_params = self.llama_config['llama_cpp']
        llama_cpp_params['model_path'] = model_filepath
        
        model = LlamaCpp(**llama_cpp_params)
        self.model = model
        
    def create_pipeline(self):
        self.llm_pipeline = self.model
        
    def engine_not_implemented(self):
        pass
    
    
        
        #Example
        # model = LlamaCpp(
        #     model_path=llama_cpp_params['model_path'],
        #     n_gpu_layers=llama_cpp_params['n_gpu_layers'],
        #     n_batch=llama_cpp_params['n_batch']
        #     temperature=0.75,
        #     max_tokens=512,
        #     top_p=1,
        #     #callback_manager=callback_manager,
        #     verbose=True,  # Verbose is required to pass to the callback manager
        # )
