MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
SIMILARITY_THRESHOLD = 0.5

CONFERENCES = [
{
"event_name": "<название_мероприятия>", # "Bioinformatics Summit 2026"
"topics": [
"<тема_1>", # "обработка естественного языка"
"<тема_2>", # "робототехника"
"<тема_3>", # "биоинформатика"
# ... произвольное количество тем
]
},
# ... произвольное количество конференций
]

USER_INPUT = "<key_words>" # "медицина, Биология"