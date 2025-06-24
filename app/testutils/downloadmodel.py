from transformers import AutoModelForCausalLM, AutoTokenizer
import os
os.environ["HTTP_PROXY"] = "http://proxy.example.com:8080"
# 下载ChatGLM模型（国内模型，无需科学上网）
model = AutoModelForCausalLM.from_pretrained(
    "本地ChatGLM路径",
    trust_remote_code=True
)
tokenizer = AutoTokenizer.from_pretrained(
    "本地ChatGLM路径",
    trust_remote_code=True
)