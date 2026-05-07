TOKEN = ""
PROXY_URL = ""
# CHANNEL_ID = ""
MAX_MESSAGES = 5

import warnings

OPENROUTER_API_KEY = ""
GROQ_API_KEY = ""
DEEPSEEK_API_KEY = ""

OPENROUTER_MODELS = [
  "deepseek/deepseek-chat",
  "openai/gpt-oss-20b",                    # 20B, быстрая
  "openai/gpt-oss-120b",                   # 120B, мощная
  "meta-llama/llama-3.3-70b-instruct:free", # Llama 3.3 70B бесплатно
  "mistralai/mistral-7b-instruct:free",    # Mistral 7B бесплатно
  "qwen/qwen3-next-80b-a3b-instruct:free",  # Qwen 3 Next бесплатно
  "google/gemini-2.0-flash-lite-preview-02-05:free",  # Gemini Flash
]

GROQ_MODELS = [
  "llama-3.3-70b-versatile",    # вместо llama3-70b-8192
  "mixtral-8x7b-32768",
  "llama-3.1-8b-instant",        # быстрая
]

warnings.filterwarnings("ignore", category=UserWarning)
