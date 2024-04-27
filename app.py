#import argparse
import json
import os
from src.simple_rag_pipeline import main_v2, main

#[APP_CONIFG = json.load("config.json")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "your_token"
def app():
    pass

if __name__ == "__main__":
    main_v2() 
    #main(1)