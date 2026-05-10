import os

os.environ["NO_PROXY"] = "127.0.0.1,localhost"
os.environ["no_proxy"] = "127.0.0.1,localhost"


LLM_BASE_URL = "http://127.0.0.1:11434/v1"
LLM_MODEL = "glm4"
LLM_API_KEY = "ollama"
