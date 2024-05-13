#import argparse
import json
import os
from src.simple_rag_pipeline import main_v2, main, git_test


#[APP_CONIFG = json.load("config.json")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "your_token"
def app():
    pass

if __name__ == "__main__":
    #manager = GitManager()
    git_test()